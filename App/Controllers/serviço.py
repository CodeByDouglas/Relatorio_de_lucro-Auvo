import requests
from datetime import datetime
from flask import jsonify
from ..Models import Usuario, Servico
from .. import db


class ServicoController:
    """Controller para gerenciar serviços da API da Auvo"""
    
    @staticmethod
    def fetch_and_save_services(user_id):
        """
        Busca serviços da API da Auvo e salva no banco de dados
        
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
        
        # URL da API de serviços
        url = "https://api.auvo.com.br/v2/services/?pageSize=999999999"
        
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
                        services_list = data['result']['entityList']
                        
                        # Salva os serviços no banco
                        save_result = ServicoController._save_services_to_database(services_list, usuario.id)
                        
                        return {
                            'success': True,
                            'message': f'Serviços sincronizados com sucesso. {save_result["saved"]} serviços salvos, {save_result["updated"]} atualizados.',
                            'data': {
                                'total_services': len(services_list),
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
    def _save_services_to_database(services_list, usuario_id):
        """
        Salva ou atualiza serviços no banco de dados
        
        Args:
            services_list (list): Lista de serviços da API
            usuario_id (int): ID do usuário dono dos serviços
            
        Returns:
            dict: Estatísticas da operação
        """
        saved_count = 0
        updated_count = 0
        error_count = 0
        errors = []
        
        try:
            for service_data in services_list:
                try:
                    # Extrai os dados necessários
                    service_id = service_data.get('id')
                    title = service_data.get('title', '').strip()
                    price_str = service_data.get('price', '0.00')
                    
                    # Validação básica
                    if not service_id:
                        error_count += 1
                        errors.append(f"Serviço sem ID: {service_data}")
                        continue
                    
                    if not title:
                        title = f"Serviço {service_id}"
                    
                    # Converte o preço de string para float
                    # Remove vírgulas e converte para float (formato: "12.34" -> 12.34)
                    try:
                        price = float(price_str.replace(',', '.')) if price_str else 0.0
                    except (ValueError, AttributeError):
                        price = 0.0
                    
                    # Busca serviço existente para este usuário
                    servico_existente = Servico.query.filter_by(
                        id=service_id,
                        usuario_id=usuario_id
                    ).first()
                    
                    if servico_existente:
                        # Atualiza serviço existente
                        servico_existente.nome = title
                        servico_existente.custo_unitario = price
                        updated_count += 1
                    else:
                        # Cria novo serviço
                        novo_servico = Servico(
                            id=service_id,
                            usuario_id=usuario_id,
                            nome=title,
                            custo_unitario=price
                        )
                        db.session.add(novo_servico)
                        saved_count += 1
                        
                except Exception as e:
                    error_count += 1
                    errors.append(f"Erro ao processar serviço {service_data.get('id', 'unknown')}: {str(e)}")
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
                'errors': len(services_list),
                'error_details': [f"Erro geral no banco de dados: {str(e)}"]
            }
    
    @staticmethod
    def get_services_from_database(limit=None):
        """
        Recupera serviços do banco de dados
        
        Args:
            limit (int, optional): Limite de serviços a retornar
            
        Returns:
            dict: Lista de serviços
        """
        try:
            query = Servico.query
            
            if limit:
                query = query.limit(limit)
            
            servicos = query.all()
            
            services_list = []
            for servico in servicos:
                services_list.append({
                    'id': servico.id,
                    'nome': servico.nome,
                    'custo_unitario': servico.custo_unitario
                })
            
            return {
                'success': True,
                'message': f'{len(services_list)} serviços encontrados',
                'data': services_list
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': 'Erro ao buscar serviços no banco',
                'data': None
            }
    
    @staticmethod
    def update_service_cost(service_id, custo_unitario):
        """
        Atualiza custo de um serviço
        
        Args:
            service_id (str): ID do serviço (UUID)
            custo_unitario (float): Custo unitário do serviço
            
        Returns:
            dict: Resultado da operação
        """
        try:
            servico = Servico.query.filter_by(id=service_id).first()
            
            if not servico:
                return {
                    'success': False,
                    'message': 'Serviço não encontrado',
                    'data': None
                }
            
            # Atualiza o valor
            servico.custo_unitario = custo_unitario
            
            db.session.commit()
            
            return {
                'success': True,
                'message': 'Serviço atualizado com sucesso',
                'data': {
                    'id': servico.id,
                    'nome': servico.nome,
                    'custo_unitario': servico.custo_unitario
                }
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': 'Erro ao atualizar serviço',
                'data': None
            }
    
    @staticmethod
    def get_service_by_id(service_id):
        """
        Busca um serviço específico por ID
        
        Args:
            service_id (str): ID do serviço (UUID)
            
        Returns:
            dict: Dados do serviço
        """
        try:
            servico = Servico.query.filter_by(id=service_id).first()
            
            if not servico:
                return {
                    'success': False,
                    'message': 'Serviço não encontrado',
                    'data': None
                }
            
            return {
                'success': True,
                'message': 'Serviço encontrado',
                'data': {
                    'id': servico.id,
                    'nome': servico.nome,
                    'custo_unitario': servico.custo_unitario
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': 'Erro ao buscar serviço',
                'data': None
            }
