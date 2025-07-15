import requests
from datetime import datetime
from flask import jsonify
from ..Models import Usuario
from .. import db


class AuthController:
    """Controller para autenticação com a API da Auvo"""
    
    @staticmethod
    def authenticate_auvo(api_key, api_token):
        """
        Autentica com a API da Auvo
        
        Args:
            api_key (str): Chave da API
            api_token (str): Token da API
            
        Returns:
            dict: Resposta da autenticação
        """
        
        # Validações básicas
        if not api_key or not api_token:
            return {
                'success': False,
                'message': 'API Key e API Token são obrigatórios',
                'data': None
            }
        
        # URL da API de autenticação
        url = f"https://api.auvo.com.br/v2/login/?apiKey={api_key}&apiToken={api_token}"
        
        # Headers da requisição
        headers = {
            'Content-Type': 'application/json'
        }
        
        try:
            # Faz a requisição para a API
            response = requests.get(url, headers=headers, timeout=30)
            
            # Verifica se a resposta foi bem-sucedida
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Verifica se a estrutura da resposta está correta
                    if 'result' in data and data['result'].get('authenticated'):
                        result = data['result']
                        
                        # Salva ou atualiza as credenciais no banco
                        auth_data = AuthController._save_user_credentials(
                            api_key=api_key,
                            api_token=api_token,
                            access_token=result.get('accessToken'),
                            token_expiration=result.get('expiration')
                        )
                        
                        return {
                            'success': True,
                            'message': 'Autenticação realizada com sucesso',
                            'data': {
                                'authenticated': True,
                                'access_token': result.get('accessToken'),
                                'expiration': result.get('expiration'),
                                'created': result.get('created'),
                                'user_id': auth_data.get('user_id')
                            }
                        }
                    else:
                        return {
                            'success': False,
                            'message': 'Credenciais inválidas',
                            'data': None
                        }
                        
                except ValueError as e:
                    return {
                        'success': False,
                        'message': 'Erro ao processar resposta da API',
                        'data': None
                    }
            else:
                return {
                    'success': False,
                    'message': 'Credenciais inválidas',
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
    def _save_user_credentials(api_key, api_token, access_token, token_expiration):
        """
        Salva ou atualiza as credenciais do usuário no banco de dados
        
        Args:
            api_key (str): Chave da API
            api_token (str): Token da API
            access_token (str): Token de acesso retornado pela API
            token_expiration (str): Data de expiração do token
            
        Returns:
            dict: Dados do usuário salvo
        """
        try:
            # Busca o usuário existente
            usuario = Usuario.query.filter_by(chave_app=api_key).first()
            
            # Converte a data de expiração para datetime
            token_obtido_em = datetime.now()
            
            if usuario:
                # Atualiza o usuário existente
                usuario.token_api = api_token
                usuario.token_bearer = access_token
                usuario.token_obtido_em = token_obtido_em
            else:
                # Cria um novo usuário
                usuario = Usuario(
                    chave_app=api_key,
                    token_api=api_token,
                    token_bearer=access_token,
                    token_obtido_em=token_obtido_em
                )
                db.session.add(usuario)
            
            # Salva as alterações
            db.session.commit()
            
            return {
                'user_id': usuario.id,
                'api_key': usuario.chave_app,
                'success': True
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'user_id': None,
                'api_key': None,
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def get_user_credentials(api_key):
        """
        Recupera as credenciais do usuário do banco de dados
        
        Args:
            api_key (str): Chave da API
            
        Returns:
            dict: Credenciais do usuário
        """
        try:
            usuario = Usuario.query.filter_by(chave_app=api_key).first()
            
            if usuario:
                return {
                    'success': True,
                    'data': {
                        'id': usuario.id,
                        'api_key': usuario.chave_app,
                        'api_token': usuario.token_api,
                        'access_token': usuario.token_bearer,
                        'token_obtained_at': usuario.token_obtido_em.isoformat()
                    }
                }
            else:
                return {
                    'success': False,
                    'message': 'Usuário não encontrado',
                    'data': None
                }
        except Exception as e:
            return {
                'success': False,
                'message': 'Erro ao buscar credenciais',
                'data': None
            }
    
    @staticmethod
    def validate_token(api_key):
        """
        Valida se o token do usuário ainda está válido
        
        Args:
            api_key (str): Chave da API
            
        Returns:
            dict: Status de validação do token
        """
        try:
            usuario = Usuario.query.filter_by(chave_app=api_key).first()
            
            if not usuario:
                print(f"DEBUG: Usuário não encontrado para api_key: {api_key}")
                return {
                    'success': False,
                    'message': 'Usuário não encontrado',
                    'valid': False
                }
            
            print(f"DEBUG: Usuário encontrado. Token obtido em: {usuario.token_obtido_em}")
            print(f"DEBUG: Hora atual: {datetime.now()}")
            
            # verificar se passou mais de 28 minutos desde token_obtido_em
            time_diff = datetime.now() - usuario.token_obtido_em
            print(f"DEBUG: Diferença de tempo: {time_diff.total_seconds()} segundos")
            
            # Considerando que o token expira em 30 minutos (1680 segundos mantendo 2 min de margem de erro)
            if time_diff.total_seconds() > 1680:
                print(f"DEBUG: Token expirado - diferença: {time_diff.total_seconds()} > 1680")
                return {
                    'success': True,
                    'message': 'Token expirado',
                    'valid': False
                }
            
            print(f"DEBUG: Token válido - diferença: {time_diff.total_seconds()} <= 1680")
            return {
                'success': True,
                'message': 'Token válido',
                'valid': True,
                'access_token': usuario.token_bearer
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': 'Erro ao validar token',
                'valid': False
            }
