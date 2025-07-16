import requests
from datetime import datetime
from flask import jsonify
from ..Models import Usuario, Colaborador
from .. import db


class ColaboradorController:
    """Controller para gerenciar colaboradores da API da Auvo"""
    
    @staticmethod
    def fetch_and_save_collaborators(user_id):
        """
        Busca colaboradores da API da Auvo e salva no banco de dados
        
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
        
        
        from .auth_api import AuthController
        token_validation = AuthController.validate_token(usuario.chave_app)
        
        if not token_validation.get('valid'):
            return {
                'success': False,
                'message': 'Token expirado. Faça login novamente.',
                'data': None
             }
        
        
        
        
        # URL da API de colaboradores
        url = "https://api.auvo.com.br/v2/users/?pageSize=999999999"
        
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
                    print(f"DEBUG: Resposta da API recebida com sucesso")
                    print(f"DEBUG: Estrutura da resposta: {list(data.keys()) if data else 'Resposta vazia'}")
                    
                    # Verifica se a estrutura da resposta está correta
                    if 'result' in data and 'entityList' in data['result']:
                        collaborators_list = data['result']['entityList']
                        print(f"DEBUG: Encontrados {len(collaborators_list)} colaboradores na API")
                        
                        # Log dos primeiros colaboradores para debug
                        for i, collab in enumerate(collaborators_list[:3]):
                            print(f"DEBUG: Colaborador {i+1}: {collab}")
                        
                        # Salva os colaboradores no banco
                        save_result = ColaboradorController._save_collaborators_to_database(collaborators_list, usuario.id)
                        
                        return {
                            'success': True,
                            'message': f'Colaboradores sincronizados com sucesso. {save_result["saved"]} colaboradores salvos, {save_result["updated"]} atualizados.',
                            'data': {
                                'total_collaborators': len(collaborators_list),
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
    def _save_collaborators_to_database(collaborators_list, usuario_id):
        """
        Salva ou atualiza colaboradores no banco de dados
        
        Args:
            collaborators_list (list): Lista de colaboradores da API
            usuario_id (int): ID do usuário dono dos colaboradores
            
        Returns:
            dict: Estatísticas da operação
        """
        saved_count = 0
        updated_count = 0
        error_count = 0
        errors = []
        
        print(f"DEBUG: Processando {len(collaborators_list)} colaboradores")
        
        try:
            for collaborator_data in collaborators_list:
                try:
                    # Extrai os dados necessários
                    # A API retorna 'userID' (com maiúsculas), não 'userId'
                    user_id = collaborator_data.get('userID')
                    name = collaborator_data.get('name', '').strip()
                    
                    print(f"DEBUG: Processando colaborador - userID: {user_id}, name: {name}")
                    
                    # Validação básica
                    if not user_id:
                        error_count += 1
                        errors.append(f"Colaborador sem userID: {collaborator_data}")
                        print(f"DEBUG: Erro - colaborador sem userID: {collaborator_data}")
                        continue
                    
                    if not name:
                        name = f"Colaborador {user_id}"
                        print(f"DEBUG: Nome vazio, usando nome padrão: {name}")
                    
                    # Busca colaborador existente para este usuário
                    colaborador_existente = Colaborador.query.filter_by(
                        id=user_id, 
                        usuario_id=usuario_id
                    ).first()
                    
                    if colaborador_existente:
                        # Atualiza colaborador existente
                        colaborador_existente.nome = name
                        updated_count += 1
                        print(f"DEBUG: Colaborador atualizado - ID: {user_id}, Nome: {name}")
                    else:
                        # Cria novo colaborador
                        novo_colaborador = Colaborador(
                            id=user_id,
                            usuario_id=usuario_id,
                            nome=name
                        )
                        db.session.add(novo_colaborador)
                        saved_count += 1
                        print(f"DEBUG: Novo colaborador criado - ID: {user_id}, Nome: {name}")
                        
                except Exception as e:
                    error_count += 1
                    error_msg = f"Erro ao processar colaborador {collaborator_data.get('userID', 'unknown')}: {str(e)}"
                    errors.append(error_msg)
                    print(f"DEBUG: {error_msg}")
                    continue
            
            # Commit das alterações
            db.session.commit()
            print(f"DEBUG: Commit realizado - {saved_count} salvos, {updated_count} atualizados, {error_count} erros")
            
            return {
                'saved': saved_count,
                'updated': updated_count,
                'errors': error_count,
                'error_details': errors
            }
            
        except Exception as e:
            db.session.rollback()
            error_msg = f"Erro geral no banco de dados: {str(e)}"
            print(f"DEBUG: {error_msg}")
            return {
                'saved': 0,
                'updated': 0,
                'errors': len(collaborators_list),
                'error_details': [error_msg]
            }
    
    @staticmethod
    def get_collaborators_from_database(limit=None):
        """
        Recupera colaboradores do banco de dados
        
        Args:
            limit (int, optional): Limite de colaboradores a retornar
            
        Returns:
            dict: Lista de colaboradores
        """
        try:
            query = Colaborador.query
            
            if limit:
                query = query.limit(limit)
            
            colaboradores = query.all()
            print(f"DEBUG: Encontrados {len(colaboradores)} colaboradores no banco")
            
            collaborators_list = []
            for colaborador in colaboradores:
                collaborators_list.append({
                    'id': colaborador.id,
                    'nome': colaborador.nome
                })
                print(f"DEBUG: Colaborador no banco - ID: {colaborador.id}, Nome: {colaborador.nome}")
            
            return {
                'success': True,
                'message': f'{len(collaborators_list)} colaboradores encontrados',
                'data': collaborators_list
            }
            
        except Exception as e:
            print(f"DEBUG: Erro ao buscar colaboradores: {str(e)}")
            return {
                'success': False,
                'message': 'Erro ao buscar colaboradores no banco',
                'data': None
            }
    
    @staticmethod
    def get_collaborator_by_id(collaborator_id):
        """
        Busca um colaborador específico por ID
        
        Args:
            collaborator_id (int): ID do colaborador
            
        Returns:
            dict: Dados do colaborador
        """
        try:
            colaborador = Colaborador.query.filter_by(id=collaborator_id).first()
            
            if not colaborador:
                return {
                    'success': False,
                    'message': 'Colaborador não encontrado',
                    'data': None
                }
            
            return {
                'success': True,
                'message': 'Colaborador encontrado',
                'data': {
                    'id': colaborador.id,
                    'nome': colaborador.nome
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': 'Erro ao buscar colaborador',
                'data': None
            }
    
    @staticmethod
    def update_collaborator_name(collaborator_id, nome):
        """
        Atualiza nome de um colaborador
        
        Args:
            collaborator_id (int): ID do colaborador
            nome (str): Novo nome do colaborador
            
        Returns:
            dict: Resultado da operação
        """
        try:
            colaborador = Colaborador.query.filter_by(id=collaborator_id).first()
            
            if not colaborador:
                return {
                    'success': False,
                    'message': 'Colaborador não encontrado',
                    'data': None
                }
            
            # Atualiza o nome
            colaborador.nome = nome
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Colaborador atualizado com sucesso',
                'data': {
                    'id': colaborador.id,
                    'nome': colaborador.nome
                }
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': 'Erro ao atualizar colaborador',
                'data': None
            }
