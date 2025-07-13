"""
Testes unitários para o ServicoController
"""
import unittest
from unittest.mock import Mock, patch
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from App.Controllers.serviço import ServicoController


class TestServicoController(unittest.TestCase):
    """Testes para o controller de serviços"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.user_id = 1
        self.mock_usuario = Mock()
        self.mock_usuario.id = self.user_id
        self.mock_usuario.chave_app = 'test_app_key'
        self.mock_usuario.token_bearer = 'test_bearer_token'
        
        # Mock dos serviços da API
        self.mock_api_services = [
            {
                'id': 1,
                'description': 'Consultoria em TI',
                'price': 150.50,
                'salePrice': 200.00
            },
            {
                'id': 2,
                'description': 'Desenvolvimento de Software',
                'price': 300.75,
                'salePrice': 450.00
            },
            {
                'id': 3,
                'description': '',  # Descrição vazia
                'price': None,  # Preço nulo
                'salePrice': 100.00
            }
        ]
        
        # Mock da resposta da API
        self.mock_api_response = {
            'result': {
                'entityList': self.mock_api_services,
                'pagedSearchReturnData': {
                    'totalItems': 3,
                    'page': 1
                }
            }
        }
    
    @patch('App.Controllers.serviço.Usuario')
    @patch('App.Controllers.serviço.AuthController')
    @patch('App.Controllers.serviço.requests')
    @patch('App.Controllers.serviço.db')
    def test_fetch_and_save_services_success(self, mock_db, mock_requests, mock_auth, mock_usuario_model):
        """Testa a sincronização bem-sucedida de serviços"""
        # Configuração dos mocks
        mock_usuario_model.query.get.return_value = self.mock_usuario
        mock_auth.validate_token.return_value = {'valid': True}
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.mock_api_response
        mock_requests.get.return_value = mock_response
        
        # Mock do método _save_services_to_database
        with patch.object(ServicoController, '_save_services_to_database') as mock_save:
            mock_save.return_value = {
                'saved': 2,
                'updated': 1,
                'errors': 0,
                'error_details': []
            }
            
            # Executa o método
            resultado = ServicoController.fetch_and_save_services(self.user_id)
            
            # Verificações
            self.assertTrue(resultado['success'])
            self.assertIn('Serviços sincronizados com sucesso', resultado['message'])
            self.assertEqual(resultado['data']['total_services'], 3)
            self.assertEqual(resultado['data']['saved'], 2)
            self.assertEqual(resultado['data']['updated'], 1)
    
    @patch('App.Controllers.serviço.Usuario')
    def test_fetch_and_save_services_user_not_found(self, mock_usuario_model):
        """Testa erro quando usuário não é encontrado"""
        mock_usuario_model.query.get.return_value = None
        
        resultado = ServicoController.fetch_and_save_services(self.user_id)
        
        self.assertFalse(resultado['success'])
        self.assertEqual(resultado['message'], 'Usuário não encontrado')
    
    def test_fetch_and_save_services_no_user_id(self):
        """Testa erro quando user_id não é fornecido"""
        resultado = ServicoController.fetch_and_save_services(None)
        
        self.assertFalse(resultado['success'])
        self.assertEqual(resultado['message'], 'ID do usuário é obrigatório')
    
    @patch('App.Controllers.serviço.Usuario')
    @patch('App.Controllers.serviço.AuthController')
    def test_fetch_and_save_services_invalid_token(self, mock_auth, mock_usuario_model):
        """Testa erro quando token é inválido"""
        mock_usuario_model.query.get.return_value = self.mock_usuario
        mock_auth.validate_token.return_value = {'valid': False}
        
        resultado = ServicoController.fetch_and_save_services(self.user_id)
        
        self.assertFalse(resultado['success'])
        self.assertEqual(resultado['message'], 'Token expirado. Faça login novamente.')
    
    @patch('App.Controllers.serviço.Usuario')
    @patch('App.Controllers.serviço.AuthController')
    @patch('App.Controllers.serviço.requests')
    def test_fetch_and_save_services_api_error_500(self, mock_requests, mock_auth, mock_usuario_model):
        """Testa erro 500 da API"""
        mock_usuario_model.query.get.return_value = self.mock_usuario
        mock_auth.validate_token.return_value = {'valid': True}
        
        mock_response = Mock()
        mock_response.status_code = 500
        mock_requests.get.return_value = mock_response
        
        resultado = ServicoController.fetch_and_save_services(self.user_id)
        
        self.assertFalse(resultado['success'])
        self.assertEqual(resultado['message'], 'Erro interno do servidor')
    
    @patch('App.Controllers.serviço.Usuario')
    @patch('App.Controllers.serviço.AuthController')
    @patch('App.Controllers.serviço.requests')
    def test_fetch_and_save_services_request_exception(self, mock_requests, mock_auth, mock_usuario_model):
        """Testa exceção de rede"""
        mock_usuario_model.query.get.return_value = self.mock_usuario
        mock_auth.validate_token.return_value = {'valid': True}
        
        mock_requests.get.side_effect = Exception('Network error')
        
        resultado = ServicoController.fetch_and_save_services(self.user_id)
        
        self.assertFalse(resultado['success'])
        self.assertIn('Erro de conexão', resultado['message'])
    
    @patch('App.Controllers.serviço.Servico')
    @patch('App.Controllers.serviço.db')
    def test_save_services_to_database(self, mock_db, mock_servico_model):
        """Testa o salvamento de serviços no banco"""
        # Mock de serviço existente
        mock_servico_existente = Mock()
        mock_servico_model.query.filter_by.return_value.first.return_value = mock_servico_existente
        
        resultado = ServicoController._save_services_to_database(
            self.mock_api_services, 
            self.user_id
        )
        
        # Verifica se retorna estatísticas
        self.assertIn('saved', resultado)
        self.assertIn('updated', resultado)
        self.assertIn('errors', resultado)
    
    def test_save_services_handles_empty_descriptions(self):
        """Testa o tratamento de descrições vazias"""
        services_with_empty_descriptions = [
            {'id': 1, 'description': '', 'price': 100.0, 'salePrice': 150.0},
            {'id': 2, 'description': None, 'price': 200.0, 'salePrice': 250.0},
            {'id': 3, 'description': 'Serviço Válido', 'price': 300.0, 'salePrice': 350.0}
        ]
        
        with patch('App.Controllers.serviço.Servico') as mock_servico, \
             patch('App.Controllers.serviço.db') as mock_db:
            
            mock_servico.query.filter_by.return_value.first.return_value = None
            
            resultado = ServicoController._save_services_to_database(
                services_with_empty_descriptions, 
                self.user_id
            )
            
            # Verifica que processou todos os serviços
            self.assertEqual(resultado['saved'], 3)
            self.assertEqual(resultado['errors'], 0)
    
    def test_save_services_handles_invalid_prices(self):
        """Testa o tratamento de preços inválidos"""
        services_with_invalid_prices = [
            {'id': 1, 'description': 'Serviço 1', 'price': None, 'salePrice': 100.0},
            {'id': 2, 'description': 'Serviço 2', 'price': 'invalid', 'salePrice': 200.0},
            {'id': 3, 'description': 'Serviço 3', 'price': 300.0, 'salePrice': None},
            {'id': 4, 'description': 'Serviço 4', 'price': 400.0, 'salePrice': 450.0}
        ]
        
        with patch('App.Controllers.serviço.Servico') as mock_servico, \
             patch('App.Controllers.serviço.db') as mock_db:
            
            mock_servico.query.filter_by.return_value.first.return_value = None
            
            resultado = ServicoController._save_services_to_database(
                services_with_invalid_prices, 
                self.user_id
            )
            
            # Verifica que salvou apenas os serviços válidos
            self.assertEqual(resultado['saved'], 4)  # Todos são salvos com preços tratados
            self.assertEqual(resultado['errors'], 0)
    
    @patch('App.Controllers.serviço.Servico')
    def test_get_services_for_user(self, mock_servico_model):
        """Testa a busca de serviços do usuário"""
        # Mock dos serviços do banco
        mock_servicos = [
            Mock(id=1, descricao='Consultoria', preco_custo=100.0, preco_venda=150.0, usuario_id=1),
            Mock(id=2, descricao='Desenvolvimento', preco_custo=200.0, preco_venda=300.0, usuario_id=1)
        ]
        mock_servico_model.query.filter_by.return_value.all.return_value = mock_servicos
        
        resultado = ServicoController.get_services_for_user(self.user_id)
        
        self.assertEqual(len(resultado), 2)
        self.assertEqual(resultado[0]['id'], 1)
        self.assertEqual(resultado[0]['descricao'], 'Consultoria')
        self.assertEqual(resultado[0]['preco_custo'], 100.0)
    
    @patch('App.Controllers.serviço.Servico')
    def test_get_services_for_user_error(self, mock_servico_model):
        """Testa erro na busca de serviços"""
        mock_servico_model.query.filter_by.side_effect = Exception('Database error')
        
        resultado = ServicoController.get_services_for_user(self.user_id)
        
        # Deve retornar lista vazia em caso de erro
        self.assertEqual(resultado, [])
    
    def test_parse_price_valid_formats(self):
        """Testa a conversão de preços em diferentes formatos"""
        # Testa valores numéricos
        self.assertEqual(ServicoController._parse_price(100.50), 100.50)
        self.assertEqual(ServicoController._parse_price(200), 200.0)
        
        # Testa strings numéricas
        self.assertEqual(ServicoController._parse_price("150.75"), 150.75)
        self.assertEqual(ServicoController._parse_price("100"), 100.0)
        
        # Testa formato monetário brasileiro
        self.assertEqual(ServicoController._parse_price("1.234,56"), 1234.56)
        self.assertEqual(ServicoController._parse_price("R$ 500,00"), 500.0)
    
    def test_parse_price_invalid_formats(self):
        """Testa a conversão de preços em formatos inválidos"""
        # Testa valores inválidos
        self.assertEqual(ServicoController._parse_price(None), 0.0)
        self.assertEqual(ServicoController._parse_price(""), 0.0)
        self.assertEqual(ServicoController._parse_price("texto"), 0.0)
        self.assertEqual(ServicoController._parse_price("R$"), 0.0)
    
    @patch('App.Controllers.serviço.session')
    def test_sync_services_endpoint_success(self, mock_session):
        """Testa o endpoint de sincronização com usuário autenticado"""
        mock_session.get.return_value = self.user_id
        
        with patch.object(ServicoController, 'fetch_and_save_services') as mock_fetch:
            mock_fetch.return_value = {
                'success': True,
                'message': 'Serviços sincronizados com sucesso',
                'data': {'saved': 10, 'updated': 5}
            }
            
            resultado = ServicoController.sync_services_endpoint()
            
            self.assertTrue(resultado['success'])
            self.assertIn('Serviços sincronizados com sucesso', resultado['message'])
    
    @patch('App.Controllers.serviço.session')
    def test_sync_services_endpoint_no_auth(self, mock_session):
        """Testa o endpoint de sincronização sem autenticação"""
        mock_session.get.return_value = None
        
        resultado = ServicoController.sync_services_endpoint()
        
        self.assertFalse(resultado['success'])
        self.assertEqual(resultado['message'], 'Usuário não autenticado')
    
    @patch('App.Controllers.serviço.Servico')
    @patch('App.Controllers.serviço.db')
    def test_database_transaction_rollback(self, mock_db, mock_servico_model):
        """Testa rollback da transação em caso de erro"""
        # Simula erro durante commit
        mock_db.session.commit.side_effect = Exception('Database error')
        
        resultado = ServicoController._save_services_to_database(
            self.mock_api_services, 
            self.user_id
        )
        
        # Verifica que houve rollback
        mock_db.session.rollback.assert_called_once()
        
        # Verifica resposta de erro
        self.assertEqual(resultado['saved'], 0)
        self.assertEqual(resultado['updated'], 0)
        self.assertEqual(resultado['errors'], len(self.mock_api_services))
    
    def test_update_existing_service(self):
        """Testa atualização de serviço existente"""
        with patch('App.Controllers.serviço.Servico') as mock_servico, \
             patch('App.Controllers.serviço.db') as mock_db:
            
            # Mock de serviço existente
            mock_existing_service = Mock()
            mock_existing_service.descricao = 'Descrição Antiga'
            mock_existing_service.preco_custo = 100.0
            mock_existing_service.preco_venda = 150.0
            
            mock_servico.query.filter_by.return_value.first.return_value = mock_existing_service
            
            # Dados atualizados
            updated_service = {
                'id': 1,
                'description': 'Descrição Nova',
                'price': 200.0,
                'salePrice': 300.0
            }
            
            resultado = ServicoController._save_services_to_database([updated_service], self.user_id)
            
            # Verifica se o serviço foi atualizado
            self.assertEqual(mock_existing_service.descricao, 'Descrição Nova')
            self.assertEqual(mock_existing_service.preco_custo, 200.0)
            self.assertEqual(mock_existing_service.preco_venda, 300.0)
            self.assertEqual(resultado['updated'], 1)
    
    def test_service_validation(self):
        """Testa validação de dados do serviço"""
        invalid_services = [
            {'description': 'Sem ID', 'price': 100.0, 'salePrice': 150.0},
            {'id': None, 'description': 'ID Nulo', 'price': 100.0, 'salePrice': 150.0},
            {'id': '', 'description': 'ID Vazio', 'price': 100.0, 'salePrice': 150.0}
        ]
        
        with patch('App.Controllers.serviço.Servico') as mock_servico, \
             patch('App.Controllers.serviço.db') as mock_db:
            
            mock_servico.query.filter_by.return_value.first.return_value = None
            
            resultado = ServicoController._save_services_to_database(invalid_services, self.user_id)
            
            # Verifica que nenhum serviço foi salvo devido à falta de ID válido
            self.assertEqual(resultado['saved'], 0)
            self.assertEqual(resultado['errors'], 3)


if __name__ == '__main__':
    unittest.main()
