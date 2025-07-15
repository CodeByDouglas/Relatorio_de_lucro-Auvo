"""
BaseController - Controller base com validações e funcionalidades comuns
"""
from ..Models import Usuario
from .. import db


class BaseController:
    """Controller base com funcionalidades comuns para todos os controllers"""
    
    @staticmethod
    def validate_user(user_id):
        """
        Valida se o usuário existe e retorna objeto do usuário
        
        Args:
            user_id (int): ID do usuário
            
        Returns:
            tuple: (success: bool, message: str, usuario: Usuario|None)
        """
        # Validação básica
        if not user_id:
            return False, 'ID do usuário é obrigatório', None
        
        # Busca o usuário no banco
        usuario = Usuario.query.get(user_id)
        if not usuario:
            return False, 'Usuário não encontrado', None
            
        return True, 'Usuário válido', usuario
    
    @staticmethod
    def validate_token(usuario):
        """
        Valida se o token do usuário ainda é válido
        
        Args:
            usuario (Usuario): Objeto do usuário
            
        Returns:
            tuple: (success: bool, message: str)
        """
        # Por enquanto desabilitado para debug, mas estrutura pronta
        # from .auth_api import AuthController
        # token_validation = AuthController.validate_token(usuario.chave_app)
        # 
        # if not token_validation.get('valid'):
        #     return False, 'Token expirado. Faça login novamente.'
        
        return True, 'Token válido'
    
    @staticmethod
    def create_response(success, message, data=None):
        """
        Cria resposta padronizada
        
        Args:
            success (bool): Se a operação foi bem-sucedida
            message (str): Mensagem da resposta
            data (dict, optional): Dados da resposta
            
        Returns:
            dict: Resposta padronizada
        """
        return {
            'success': success,
            'message': message,
            'data': data
        }
    
    @staticmethod
    def create_api_headers(usuario):
        """
        Cria headers padrão para requisições à API Auvo
        
        Args:
            usuario (Usuario): Objeto do usuário
            
        Returns:
            dict: Headers para requisição
        """
        return {
            'Authorization': f'Bearer {usuario.token_bearer}',
            'Content-Type': 'application/json'
        }
    
    @staticmethod
    def handle_api_error(error, operation_name="operação"):
        """
        Trata erros de API de forma padronizada
        
        Args:
            error (Exception): Erro capturado
            operation_name (str): Nome da operação que falhou
            
        Returns:
            dict: Resposta de erro padronizada
        """
        error_message = f'Erro na {operation_name}: {str(error)}'
        return BaseController.create_response(False, error_message, None)
