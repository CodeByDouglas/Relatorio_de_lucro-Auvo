"""
Testes unitários para o TipoTarefaController
"""
import unittest
from unittest.mock import Mock, patch
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from App.Controllers.tipo_de_tarefas import TipoTarefaController


class TestTipoTarefaController(unittest.TestCase):
    """Testes para o controller de tipos de tarefa"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.user_id = 1
        self.mock_usuario = Mock()
        self.mock_usuario.id = self.user_id
        self.mock_usuario.chave_app = 'test_app_key'
        self.mock_usuario.token_bearer = 'test_bearer_token'
        
        # Mock dos tipos de tarefa da API
        self.mock_api_task_types = [
            {
                'id': 1,
                'description': 'Desenvolvimento'
            },
            {
                'id': 2,
                'description': 'Consultoria'
            },
            {
                'id': 3,
                'description': ''  # Descrição vazia para testar fallback
            }
        ]
        
        # Mock da resposta da API
        self.mock_api_response = {
            'result': {
                'entityList': self.mock_api_task_types,
                'pagedSearchReturnData': {
                    'totalItems': 3,
                    'page': 1
                }
            }
        }
    
    @patch('App.Controllers.tipo_de_tarefas.Usuario')
    @patch('App.Controllers.tipo_de_tarefas.AuthController')
    @patch('App.Controllers.tipo_de_tarefas.requests')
    @patch('App.Controllers.tipo_de_tarefas.db')
    def test_fetch_and_save_task_types_success(self, mock_db, mock_requests, mock_auth, mock_usuario_model):
        """Testa a sincronização bem-sucedida de tipos de tarefa"""
        # Configuração dos mocks
        mock_usuario_model.query.get.return_value = self.mock_usuario
        mock_auth.validate_token.return_value = {'valid': True}
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.mock_api_response
        mock_requests.get.return_value = mock_response
        
        # Mock do método _save_task_types_to_database
        with patch.object(TipoTarefaController, '_save_task_types_to_database') as mock_save:
            mock_save.return_value = {
                'saved': 2,
                'updated': 1,
                'errors': 0,
                'error_details': []
            }
            
            # Executa o método
            resultado = TipoTarefaController.fetch_and_save_task_types(self.user_id)
            
            # Verificações
            self.assertTrue(resultado['success'])
            self.assertIn('Tipos de tarefa sincronizados com sucesso', resultado['message'])
            self.assertEqual(resultado['data']['total_task_types'], 3)
            self.assertEqual(resultado['data']['saved'], 2)
            self.assertEqual(resultado['data']['updated'], 1)
    
    @patch('App.Controllers.tipo_de_tarefas.Usuario')
    def test_fetch_and_save_task_types_user_not_found(self, mock_usuario_model):
        """Testa erro quando usuário não é encontrado"""
        mock_usuario_model.query.get.return_value = None
        
        resultado = TipoTarefaController.fetch_and_save_task_types(self.user_id)
        
        self.assertFalse(resultado['success'])
        self.assertEqual(resultado['message'], 'Usuário não encontrado')
    
    def test_fetch_and_save_task_types_no_user_id(self):
        """Testa erro quando user_id não é fornecido"""
        resultado = TipoTarefaController.fetch_and_save_task_types(None)
        
        self.assertFalse(resultado['success'])
        self.assertEqual(resultado['message'], 'ID do usuário é obrigatório')
    
    @patch('App.Controllers.tipo_de_tarefas.Usuario')
    @patch('App.Controllers.tipo_de_tarefas.AuthController')
    def test_fetch_and_save_task_types_invalid_token(self, mock_auth, mock_usuario_model):
        """Testa erro quando token é inválido"""
        mock_usuario_model.query.get.return_value = self.mock_usuario
        mock_auth.validate_token.return_value = {'valid': False}
        
        resultado = TipoTarefaController.fetch_and_save_task_types(self.user_id)
        
        self.assertFalse(resultado['success'])
        self.assertEqual(resultado['message'], 'Token expirado. Faça login novamente.')
    
    @patch('App.Controllers.tipo_de_tarefas.Usuario')
    @patch('App.Controllers.tipo_de_tarefas.AuthController')
    @patch('App.Controllers.tipo_de_tarefas.requests')
    def test_fetch_and_save_task_types_api_error_403(self, mock_requests, mock_auth, mock_usuario_model):
        """Testa erro 403 da API"""
        mock_usuario_model.query.get.return_value = self.mock_usuario
        mock_auth.validate_token.return_value = {'valid': True}
        
        mock_response = Mock()
        mock_response.status_code = 403
        mock_requests.get.return_value = mock_response
        
        resultado = TipoTarefaController.fetch_and_save_task_types(self.user_id)
        
        self.assertFalse(resultado['success'])
        self.assertEqual(resultado['message'], 'Acesso negado. Verifique suas permissões')
    
    @patch('App.Controllers.tipo_de_tarefas.Usuario')
    @patch('App.Controllers.tipo_de_tarefas.AuthController')
    @patch('App.Controllers.tipo_de_tarefas.requests')
    def test_fetch_and_save_task_types_malformed_response(self, mock_requests, mock_auth, mock_usuario_model):
        """Testa resposta malformada da API"""
        mock_usuario_model.query.get.return_value = self.mock_usuario
        mock_auth.validate_token.return_value = {'valid': True}
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'invalid': 'structure'}
        mock_requests.get.return_value = mock_response
        
        resultado = TipoTarefaController.fetch_and_save_task_types(self.user_id)
        
        self.assertFalse(resultado['success'])
        self.assertEqual(resultado['message'], 'Formato de resposta inválido da API')
    
    @patch('App.Controllers.tipo_de_tarefas.TipoTarefa')
    @patch('App.Controllers.tipo_de_tarefas.db')
    def test_save_task_types_to_database(self, mock_db, mock_tipo_tarefa_model):
        """Testa o salvamento de tipos de tarefa no banco"""
        # Mock de tipo de tarefa existente
        mock_tipo_existente = Mock()
        mock_tipo_tarefa_model.query.filter_by.return_value.first.return_value = mock_tipo_existente
        
        resultado = TipoTarefaController._save_task_types_to_database(
            self.mock_api_task_types, 
            self.user_id
        )
        
        # Verifica se retorna estatísticas
        self.assertIn('saved', resultado)
        self.assertIn('updated', resultado)
        self.assertIn('errors', resultado)
    
    def test_save_task_types_handles_empty_descriptions(self):
        """Testa o tratamento de descrições vazias"""
        task_types_with_empty_descriptions = [
            {'id': 1, 'description': ''},
            {'id': 2, 'description': None},
            {'id': 3, 'description': 'Descrição Válida'}
        ]
        
        with patch('App.Controllers.tipo_de_tarefas.TipoTarefa') as mock_tipo_tarefa, \
             patch('App.Controllers.tipo_de_tarefas.db') as mock_db:
            
            mock_tipo_tarefa.query.filter_by.return_value.first.return_value = None
            
            resultado = TipoTarefaController._save_task_types_to_database(
                task_types_with_empty_descriptions, 
                self.user_id
            )
            
            # Verifica que processou todos os tipos
            self.assertEqual(resultado['saved'], 3)
            self.assertEqual(resultado['errors'], 0)
    
    def test_save_task_types_handles_missing_id(self):
        """Testa o tratamento de tipos sem ID"""
        task_types_with_missing_ids = [
            {'id': None, 'description': 'Tipo sem ID'},
            {'description': 'Tipo sem campo ID'},
            {'id': 1, 'description': 'Tipo válido'}
        ]
        
        with patch('App.Controllers.tipo_de_tarefas.TipoTarefa') as mock_tipo_tarefa, \
             patch('App.Controllers.tipo_de_tarefas.db') as mock_db:
            
            mock_tipo_tarefa.query.filter_by.return_value.first.return_value = None
            
            resultado = TipoTarefaController._save_task_types_to_database(
                task_types_with_missing_ids, 
                self.user_id
            )
            
            # Verifica que salvou apenas o tipo válido
            self.assertEqual(resultado['saved'], 1)
            self.assertEqual(resultado['errors'], 2)
    
    @patch('App.Controllers.tipo_de_tarefas.TipoTarefa')
    def test_get_task_types_for_user(self, mock_tipo_tarefa_model):
        """Testa a busca de tipos de tarefa do usuário"""
        # Mock dos tipos de tarefa do banco
        mock_tipos = [
            Mock(id=1, descricao='Desenvolvimento', usuario_id=1),
            Mock(id=2, descricao='Consultoria', usuario_id=1)
        ]
        mock_tipo_tarefa_model.query.filter_by.return_value.all.return_value = mock_tipos
        
        resultado = TipoTarefaController.get_task_types_for_user(self.user_id)
        
        self.assertEqual(len(resultado), 2)
        self.assertEqual(resultado[0]['id'], 1)
        self.assertEqual(resultado[0]['descricao'], 'Desenvolvimento')
        self.assertEqual(resultado[1]['id'], 2)
        self.assertEqual(resultado[1]['descricao'], 'Consultoria')
    
    @patch('App.Controllers.tipo_de_tarefas.TipoTarefa')
    def test_get_task_types_for_user_error(self, mock_tipo_tarefa_model):
        """Testa erro na busca de tipos de tarefa"""
        mock_tipo_tarefa_model.query.filter_by.side_effect = Exception('Database error')
        
        resultado = TipoTarefaController.get_task_types_for_user(self.user_id)
        
        # Deve retornar lista vazia em caso de erro
        self.assertEqual(resultado, [])
    
    @patch('App.Controllers.tipo_de_tarefas.session')
    def test_sync_task_types_endpoint_success(self, mock_session):
        """Testa o endpoint de sincronização com usuário autenticado"""
        mock_session.get.return_value = self.user_id
        
        with patch.object(TipoTarefaController, 'fetch_and_save_task_types') as mock_fetch:
            mock_fetch.return_value = {
                'success': True,
                'message': 'Tipos sincronizados com sucesso',
                'data': {'saved': 5, 'updated': 2}
            }
            
            resultado = TipoTarefaController.sync_task_types_endpoint()
            
            self.assertTrue(resultado['success'])
            self.assertIn('Tipos sincronizados com sucesso', resultado['message'])
    
    @patch('App.Controllers.tipo_de_tarefas.session')
    def test_sync_task_types_endpoint_no_auth(self, mock_session):
        """Testa o endpoint de sincronização sem autenticação"""
        mock_session.get.return_value = None
        
        resultado = TipoTarefaController.sync_task_types_endpoint()
        
        self.assertFalse(resultado['success'])
        self.assertEqual(resultado['message'], 'Usuário não autenticado')
    
    @patch('App.Controllers.tipo_de_tarefas.TipoTarefa')
    @patch('App.Controllers.tipo_de_tarefas.db')
    def test_database_rollback_on_error(self, mock_db, mock_tipo_tarefa_model):
        """Testa rollback em caso de erro crítico"""
        # Simula erro durante commit
        mock_db.session.commit.side_effect = Exception('Database error')
        
        resultado = TipoTarefaController._save_task_types_to_database(
            self.mock_api_task_types, 
            self.user_id
        )
        
        # Verifica que houve rollback
        mock_db.session.rollback.assert_called_once()
        
        # Verifica resposta de erro
        self.assertEqual(resultado['saved'], 0)
        self.assertEqual(resultado['updated'], 0)
        self.assertEqual(resultado['errors'], len(self.mock_api_task_types))


if __name__ == '__main__':
    unittest.main()
