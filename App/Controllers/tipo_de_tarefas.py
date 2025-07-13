import requests
from datetime import datetime
from flask import jsonify
from ..Models import Usuario, TipoTarefa
from .. import db


class TipoTarefaController:
    """Controller para gerenciar tipos de tarefa da API da Auvo"""
    
    @staticmethod
    def fetch_and_save_task_types(user_id):
        """
        Busca tipos de tarefa da API da Auvo e salva no banco de dados
        
        Args:
            user_id (int): ID do usuário no banco de dados
            
        Returns:
            dict: Resultado da operação
        """
        
        # Validação básica
        if not user_id:
            return {
                'success': False,
                'message': 'ID do usuário é obrigatório',
                'data': None
            }
        
        # Busca o usuário no banco
        usuario = Usuario.query.get(user_id)
        if not usuario:
            return {
                'success': False,
                'message': 'Usuário não encontrado',
                'data': None
            }
        
        # Verifica se o token ainda é válido
        from .auth_api import AuthController
        token_validation = AuthController.validate_token(usuario.chave_app)
        
        if not token_validation.get('valid'):
            return {
                'success': False,
                'message': 'Token expirado. Faça login novamente.',
                'data': None
            }
        
        # URL da API de tipos de tarefa
        url = "https://api.auvo.com.br/v2/taskTypes/?pageSize=999999999"
        
        # Headers da requisição
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {usuario.token_bearer}'
        }
        
        try:
            # Faz a requisição para a API
            response = requests.get(url, headers=headers, timeout=30)
            
            # Verifica se a resposta foi bem-sucedida
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Verifica se a estrutura da resposta está correta
                    if 'result' in data and 'entityList' in data['result']:
                        task_types_list = data['result']['entityList']
                        
                        # Salva os tipos de tarefa no banco
                        save_result = TipoTarefaController._save_task_types_to_database(task_types_list, usuario.id)
                        
                        return {
                            'success': True,
                            'message': f'Tipos de tarefa sincronizados com sucesso. {save_result["saved"]} tipos salvos, {save_result["updated"]} atualizados.',
                            'data': {
                                'total_task_types': len(task_types_list),
                                'saved': save_result['saved'],
                                'updated': save_result['updated'],
                                'errors': save_result['errors']
                            }
                        }
                    else:
                        return {
                            'success': False,
                            'message': 'Formato de resposta inválido da API',
                            'data': None
                        }
                        
                except ValueError as e:
                    return {
                        'success': False,
                        'message': 'Erro ao processar resposta da API',
                        'data': None
                    }
            elif response.status_code == 401:
                return {
                    'success': False,
                    'message': 'Token de autorização inválido ou expirado',
                    'data': None
                }
            elif response.status_code == 403:
                return {
                    'success': False,
                    'message': 'Acesso negado. Verifique suas permissões',
                    'data': None
                }
            else:
                return {
                    'success': False,
                    'message': f'Erro na API: {response.status_code}',
                    'data': None
                }
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'message': 'Timeout na conexão com a API',
                'data': None
            }
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'message': 'Erro de conexão com a API',
                'data': None
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'message': 'Erro na requisição para a API',
                'data': None
            }
    
    @staticmethod
    def _save_task_types_to_database(task_types_list, usuario_id):
        """
        Salva ou atualiza tipos de tarefa no banco de dados
        
        Args:
            task_types_list (list): Lista de tipos de tarefa da API
            usuario_id (int): ID do usuário dono dos tipos de tarefa
            
        Returns:
            dict: Estatísticas da operação
        """
        saved_count = 0
        updated_count = 0
        error_count = 0
        errors = []
        
        try:
            for task_type_data in task_types_list:
                try:
                    # Extrai os dados necessários
                    task_type_id = task_type_data.get('id')
                    description = task_type_data.get('description', '').strip()
                    
                    # Validação básica
                    if not task_type_id:
                        error_count += 1
                        errors.append(f"Tipo de tarefa sem ID: {task_type_data}")
                        continue
                    
                    if not description:
                        description = f"Tipo {task_type_id}"
                    
                    # Busca tipo de tarefa existente para este usuário
                    tipo_existente = TipoTarefa.query.filter_by(
                        id=task_type_id,
                        usuario_id=usuario_id
                    ).first()
                    
                    if tipo_existente:
                        # Atualiza tipo existente
                        tipo_existente.descricao = description
                        updated_count += 1
                    else:
                        # Cria novo tipo de tarefa
                        novo_tipo = TipoTarefa(
                            id=task_type_id,
                            usuario_id=usuario_id,
                            descricao=description
                        )
                        db.session.add(novo_tipo)
                        saved_count += 1
                        
                except Exception as e:
                    error_count += 1
                    errors.append(f"Erro ao processar tipo de tarefa {task_type_data.get('id', 'unknown')}: {str(e)}")
                    continue
            
            # Commit das alterações
            db.session.commit()
            
            return {
                'saved': saved_count,
                'updated': updated_count,
                'errors': error_count,
                'error_details': errors
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'saved': 0,
                'updated': 0,
                'errors': len(task_types_list),
                'error_details': [f"Erro crítico: {str(e)}"]
            }
    
    @staticmethod
    def get_task_types_for_user(user_id):
        """
        Busca tipos de tarefa do usuário no banco de dados local
        
        Args:
            user_id (int): ID do usuário
            
        Returns:
            list: Lista de tipos de tarefa do usuário
        """
        try:
            task_types = TipoTarefa.query.filter_by(usuario_id=user_id).all()
            
            task_types_data = []
            for task_type in task_types:
                task_types_data.append({
                    'id': task_type.id,
                    'descricao': task_type.descricao,
                    'usuario_id': task_type.usuario_id
                })
            
            return task_types_data
            
        except Exception as e:
            return []
    
    @staticmethod
    def sync_task_types_endpoint():
        """
        Endpoint para sincronização de tipos de tarefa via API REST
        
        Returns:
            dict: Resultado da sincronização
        """
        from flask import session
        
        user_id = session.get('user_id')
        
        if not user_id:
            return {
                'success': False,
                'message': 'Usuário não autenticado',
                'data': None
            }
        
        result = TipoTarefaController.fetch_and_save_task_types(user_id)
        return result
