"""
Testes unitários para o ColaboradorController
"""
import unittest
from unittest.mock import Mock, patch
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from App.Controllers.Colaborador import ColaboradorController


class TestColaboradorController(unittest.TestCase):
    """Testes para o controller de colaboradores"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.user_id = 1
        self.mock_usuario = Mock()
        self.mock_usuario.id = self.user_id
        self.mock_usuario.chave_app = 'test_app_key'
        self.mock_usuario.token_bearer = 'test_bearer_token'
        
        # Mock dos colaboradores da API
        self.mock_api_collaborators = [
            {
                'userId': 123,
                'name': 'João Silva'
            },
            {
                'userId': 456,
                'name': 'Maria Santos'
            },
            {
                'userId': 789,
                'name': ''  # Nome vazio para testar fallback
            }
        ]
        
        # Mock da resposta da API
        self.mock_api_response = {
            'result': {
                'entityList': self.mock_api_collaborators,
                'pagedSearchReturnData': {
                    'totalItems': 3,
                    'page': 1
                }
            }
        }
    
    @patch('App.Controllers.Colaborador.Usuario')
    @patch('App.Controllers.Colaborador.AuthController')
    @patch('App.Controllers.Colaborador.requests')
    @patch('App.Controllers.Colaborador.db')
    def test_fetch_and_save_collaborators_success(self, mock_db, mock_requests, mock_auth, mock_usuario_model):
        """Testa a sincronização bem-sucedida de colaboradores"""
        # Configuração dos mocks
        mock_usuario_model.query.get.return_value = self.mock_usuario
        mock_auth.validate_token.return_value = {'valid': True}
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.mock_api_response
        mock_requests.get.return_value = mock_response
        
        # Mock do método _save_collaborators_to_database
        with patch.object(ColaboradorController, '_save_collaborators_to_database') as mock_save:
            mock_save.return_value = {
                'saved': 2,
                'updated': 1,
                'errors': 0,
                'error_details': []
            }
            
            # Executa o método
            resultado = ColaboradorController.fetch_and_save_collaborators(self.user_id)
            
            # Verificações
            self.assertTrue(resultado['success'])
            self.assertIn('Colaboradores sincronizados com sucesso', resultado['message'])
            self.assertEqual(resultado['data']['total_collaborators'], 3)
            self.assertEqual(resultado['data']['saved'], 2)
            self.assertEqual(resultado['data']['updated'], 1)
    
    @patch('App.Controllers.Colaborador.Usuario')
    def test_fetch_and_save_collaborators_user_not_found(self, mock_usuario_model):
        """Testa erro quando usuário não é encontrado"""
        mock_usuario_model.query.get.return_value = None
        
        resultado = ColaboradorController.fetch_and_save_collaborators(self.user_id)
        
        self.assertFalse(resultado['success'])
        self.assertEqual(resultado['message'], 'Usuário não encontrado')
    
    def test_fetch_and_save_collaborators_no_user_id(self):
        """Testa erro quando user_id não é fornecido"""
        resultado = ColaboradorController.fetch_and_save_collaborators(None)
        
        self.assertFalse(resultado['success'])
        self.assertEqual(resultado['message'], 'ID do usuário é obrigatório')
    
    @patch('App.Controllers.Colaborador.Usuario')
    @patch('App.Controllers.Colaborador.AuthController')
    def test_fetch_and_save_collaborators_invalid_token(self, mock_auth, mock_usuario_model):
        """Testa erro quando token é inválido"""
        mock_usuario_model.query.get.return_value = self.mock_usuario
        mock_auth.validate_token.return_value = {'valid': False}
        
        resultado = ColaboradorController.fetch_and_save_collaborators(self.user_id)
        
        self.assertFalse(resultado['success'])
        self.assertEqual(resultado['message'], 'Token expirado. Faça login novamente.')
    
    @patch('App.Controllers.Colaborador.Usuario')
    @patch('App.Controllers.Colaborador.AuthController')
    @patch('App.Controllers.Colaborador.requests')
    def test_fetch_and_save_collaborators_api_error_403(self, mock_requests, mock_auth, mock_usuario_model):
        """Testa erro 403 da API"""
        mock_usuario_model.query.get.return_value = self.mock_usuario
        mock_auth.validate_token.return_value = {'valid': True}
        
        mock_response = Mock()
        mock_response.status_code = 403
        mock_requests.get.return_value = mock_response
        
        resultado = ColaboradorController.fetch_and_save_collaborators(self.user_id)
        
        self.assertFalse(resultado['success'])
        self.assertEqual(resultado['message'], 'Acesso negado. Verifique suas permissões')
    
    @patch('App.Controllers.Colaborador.Usuario')
    @patch('App.Controllers.Colaborador.AuthController')
    @patch('App.Controllers.Colaborador.requests')
    def test_fetch_and_save_collaborators_connection_error(self, mock_requests, mock_auth, mock_usuario_model):
        """Testa erro de conexão com a API"""
        mock_usuario_model.query.get.return_value = self.mock_usuario
        mock_auth.validate_token.return_value = {'valid': True}
        
        mock_requests.get.side_effect = mock_requests.exceptions.ConnectionError()
        
        resultado = ColaboradorController.fetch_and_save_collaborators(self.user_id)
        
        self.assertFalse(resultado['success'])
        self.assertEqual(resultado['message'], 'Erro de conexão com a API')
    
    @patch('App.Controllers.Colaborador.Colaborador')
    @patch('App.Controllers.Colaborador.db')
    def test_save_collaborators_to_database(self, mock_db, mock_colaborador_model):
        """Testa o salvamento de colaboradores no banco"""
        # Mock de colaborador existente
        mock_colaborador_existente = Mock()
        mock_colaborador_model.query.filter_by.return_value.first.return_value = mock_colaborador_existente
        
        resultado = ColaboradorController._save_collaborators_to_database(
            self.mock_api_collaborators, 
            self.user_id
        )
        
        # Verifica se retorna estatísticas
        self.assertIn('saved', resultado)
        self.assertIn('updated', resultado)
        self.assertIn('errors', resultado)
    
    def test_save_collaborators_handles_empty_names(self):
        """Testa o tratamento de nomes vazios"""
        collaborators_with_empty_names = [
            {'userId': 123, 'name': ''},
            {'userId': 456, 'name': None},
            {'userId': 789, 'name': 'Nome Válido'}
        ]
        
        with patch('App.Controllers.Colaborador.Colaborador') as mock_colaborador, \
             patch('App.Controllers.Colaborador.db') as mock_db:
            
            mock_colaborador.query.filter_by.return_value.first.return_value = None
            
            resultado = ColaboradorController._save_collaborators_to_database(
                collaborators_with_empty_names, 
                self.user_id
            )
            
            # Verifica que processou todos os colaboradores
            self.assertEqual(resultado['saved'], 3)
            self.assertEqual(resultado['errors'], 0)
    
    @patch('App.Controllers.Colaborador.Colaborador')
    def test_get_collaborators_from_database(self, mock_colaborador_model):
        """Testa a busca de colaboradores do banco"""
        # Mock dos colaboradores do banco
        mock_colaboradores = [
            Mock(id=123, nome='João Silva'),
            Mock(id=456, nome='Maria Santos')
        ]
        mock_colaborador_model.query.limit.return_value.all.return_value = mock_colaboradores
        mock_colaborador_model.query.all.return_value = mock_colaboradores
        
        # Testa sem limite
        resultado = ColaboradorController.get_collaborators_from_database()
        self.assertTrue(resultado['success'])
        self.assertEqual(len(resultado['data']), 2)
        
        # Testa com limite
        resultado_limitado = ColaboradorController.get_collaborators_from_database(limit=1)
        self.assertTrue(resultado_limitado['success'])
    
    @patch('App.Controllers.Colaborador.Colaborador')
    def test_get_collaborator_by_id(self, mock_colaborador_model):
        """Testa a busca de colaborador por ID"""
        mock_colaborador = Mock()
        mock_colaborador.id = 123
        mock_colaborador.nome = 'João Silva'
        mock_colaborador_model.query.get.return_value = mock_colaborador
        
        resultado = ColaboradorController.get_collaborator_by_id(123)
        
        self.assertTrue(resultado['success'])
        self.assertEqual(resultado['data']['id'], 123)
        self.assertEqual(resultado['data']['nome'], 'João Silva')
    
    @patch('App.Controllers.Colaborador.Colaborador')
    def test_get_collaborator_by_id_not_found(self, mock_colaborador_model):
        """Testa busca de colaborador inexistente"""
        mock_colaborador_model.query.get.return_value = None
        
        resultado = ColaboradorController.get_collaborator_by_id(999)
        
        self.assertFalse(resultado['success'])
        self.assertEqual(resultado['message'], 'Colaborador não encontrado')
    
    @patch('App.Controllers.Colaborador.Colaborador')
    @patch('App.Controllers.Colaborador.db')
    def test_update_collaborator_name(self, mock_db, mock_colaborador_model):
        """Testa a atualização do nome de um colaborador"""
        mock_colaborador = Mock()
        mock_colaborador_model.query.get.return_value = mock_colaborador
        
        resultado = ColaboradorController.update_collaborator_name(123, 'Novo Nome')
        
        self.assertTrue(resultado['success'])
        self.assertEqual(mock_colaborador.nome, 'Novo Nome')
    
    @patch('App.Controllers.Colaborador.Colaborador')
    def test_update_collaborator_name_not_found(self, mock_colaborador_model):
        """Testa atualização de colaborador inexistente"""
        mock_colaborador_model.query.get.return_value = None
        
        resultado = ColaboradorController.update_collaborator_name(999, 'Novo Nome')
        
        self.assertFalse(resultado['success'])
        self.assertEqual(resultado['message'], 'Colaborador não encontrado')
    
    def test_update_collaborator_name_invalid_data(self):
        """Testa atualização com dados inválidos"""
        # Nome vazio
        resultado = ColaboradorController.update_collaborator_name(123, '')
        self.assertFalse(resultado['success'])
        self.assertEqual(resultado['message'], 'Nome é obrigatório')
        
        # ID inválido
        resultado = ColaboradorController.update_collaborator_name(None, 'Nome Válido')
        self.assertFalse(resultado['success'])
        self.assertEqual(resultado['message'], 'ID do colaborador é obrigatório')


if __name__ == '__main__':
    unittest.main()
