"""
Testes unitários para o ProdutoController
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from App.Controllers.produtos import ProdutoController


class TestProdutoController(unittest.TestCase):
    """Testes para o controller de produtos"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.user_id = 1
        self.mock_usuario = Mock()
        self.mock_usuario.id = self.user_id
        self.mock_usuario.chave_app = 'test_app_key'
        self.mock_usuario.token_bearer = 'test_bearer_token'
        
        # Mock dos produtos da API
        self.mock_api_products = [
            {
                'productId': 'prod-123',
                'name': 'Produto Teste 1',
                'unitaryCost': '10.50'
            },
            {
                'productId': 'prod-456',
                'name': 'Produto Teste 2',
                'unitaryCost': '$25.00'
            },
            {
                'productId': 'prod-789',
                'name': 'Produto Teste 3',
                'unitaryCost': '5,75'  # Formato brasileiro
            }
        ]
        
        # Mock da resposta da API
        self.mock_api_response = {
            'result': {
                'entityList': self.mock_api_products,
                'pagedSearchReturnData': {
                    'totalItems': 3,
                    'page': 1
                }
            }
        }
    
    @patch('App.Controllers.produtos.Usuario')
    @patch('App.Controllers.produtos.AuthController')
    @patch('App.Controllers.produtos.requests')
    @patch('App.Controllers.produtos.db')
    def test_fetch_and_save_products_success(self, mock_db, mock_requests, mock_auth, mock_usuario_model):
        """Testa a sincronização bem-sucedida de produtos"""
        # Configuração dos mocks
        mock_usuario_model.query.get.return_value = self.mock_usuario
        mock_auth.validate_token.return_value = {'valid': True}
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.mock_api_response
        mock_requests.get.return_value = mock_response
        
        # Mock do método _save_products_to_database
        with patch.object(ProdutoController, '_save_products_to_database') as mock_save:
            mock_save.return_value = {
                'saved': 2,
                'updated': 1,
                'errors': 0,
                'error_details': []
            }
            
            # Executa o método
            resultado = ProdutoController.fetch_and_save_products(self.user_id)
            
            # Verificações
            self.assertTrue(resultado['success'])
            self.assertIn('Produtos sincronizados com sucesso', resultado['message'])
            self.assertEqual(resultado['data']['total_products'], 3)
            self.assertEqual(resultado['data']['saved'], 2)
            self.assertEqual(resultado['data']['updated'], 1)
    
    @patch('App.Controllers.produtos.Usuario')
    def test_fetch_and_save_products_user_not_found(self, mock_usuario_model):
        """Testa erro quando usuário não é encontrado"""
        mock_usuario_model.query.get.return_value = None
        
        resultado = ProdutoController.fetch_and_save_products(self.user_id)
        
        self.assertFalse(resultado['success'])
        self.assertEqual(resultado['message'], 'Usuário não encontrado')
    
    def test_fetch_and_save_products_no_user_id(self):
        """Testa erro quando user_id não é fornecido"""
        resultado = ProdutoController.fetch_and_save_products(None)
        
        self.assertFalse(resultado['success'])
        self.assertEqual(resultado['message'], 'ID do usuário é obrigatório')
    
    @patch('App.Controllers.produtos.Usuario')
    @patch('App.Controllers.produtos.AuthController')
    def test_fetch_and_save_products_invalid_token(self, mock_auth, mock_usuario_model):
        """Testa erro quando token é inválido"""
        mock_usuario_model.query.get.return_value = self.mock_usuario
        mock_auth.validate_token.return_value = {'valid': False}
        
        resultado = ProdutoController.fetch_and_save_products(self.user_id)
        
        self.assertFalse(resultado['success'])
        self.assertEqual(resultado['message'], 'Token expirado. Faça login novamente.')
    
    @patch('App.Controllers.produtos.Usuario')
    @patch('App.Controllers.produtos.AuthController')
    @patch('App.Controllers.produtos.requests')
    def test_fetch_and_save_products_api_error_401(self, mock_requests, mock_auth, mock_usuario_model):
        """Testa erro 401 da API"""
        mock_usuario_model.query.get.return_value = self.mock_usuario
        mock_auth.validate_token.return_value = {'valid': True}
        
        mock_response = Mock()
        mock_response.status_code = 401
        mock_requests.get.return_value = mock_response
        
        resultado = ProdutoController.fetch_and_save_products(self.user_id)
        
        self.assertFalse(resultado['success'])
        self.assertEqual(resultado['message'], 'Token de autorização inválido ou expirado')
    
    @patch('App.Controllers.produtos.Usuario')
    @patch('App.Controllers.produtos.AuthController')
    @patch('App.Controllers.produtos.requests')
    def test_fetch_and_save_products_api_timeout(self, mock_requests, mock_auth, mock_usuario_model):
        """Testa timeout da API"""
        mock_usuario_model.query.get.return_value = self.mock_usuario
        mock_auth.validate_token.return_value = {'valid': True}
        
        mock_requests.get.side_effect = mock_requests.exceptions.Timeout()
        
        resultado = ProdutoController.fetch_and_save_products(self.user_id)
        
        self.assertFalse(resultado['success'])
        self.assertEqual(resultado['message'], 'Timeout na conexão com a API')
    
    @patch('App.Controllers.produtos.Produto')
    @patch('App.Controllers.produtos.db')
    def test_save_products_to_database(self, mock_db, mock_produto_model):
        """Testa o salvamento de produtos no banco"""
        # Mock de produto existente
        mock_produto_existente = Mock()
        mock_produto_model.query.filter_by.return_value.first.return_value = mock_produto_existente
        
        resultado = ProdutoController._save_products_to_database(
            self.mock_api_products, 
            self.user_id
        )
        
        # Verifica se retorna estatísticas
        self.assertIn('saved', resultado)
        self.assertIn('updated', resultado)
        self.assertIn('errors', resultado)
    
    def test_parse_unitary_cost_formats(self):
        """Testa o parsing de diferentes formatos de custo"""
        # Testa dentro do contexto do _save_products_to_database
        test_products = [
            {'productId': 'test1', 'name': 'Test 1', 'unitaryCost': '10.50'},  # Americano
            {'productId': 'test2', 'name': 'Test 2', 'unitaryCost': '$25.00'},  # Com símbolo
            {'productId': 'test3', 'name': 'Test 3', 'unitaryCost': '5,75'},   # Brasileiro
            {'productId': 'test4', 'name': 'Test 4', 'unitaryCost': 'R$ 15,30'}, # Brasileiro com símbolo
            {'productId': 'test5', 'name': 'Test 5', 'unitaryCost': ''},       # Vazio
            {'productId': 'test6', 'name': 'Test 6', 'unitaryCost': None},     # None
        ]
        
        with patch('App.Controllers.produtos.Produto') as mock_produto, \
             patch('App.Controllers.produtos.db') as mock_db:
            
            mock_produto.query.filter_by.return_value.first.return_value = None
            
            resultado = ProdutoController._save_products_to_database(test_products, self.user_id)
            
            # Verifica que processou todos os produtos
            self.assertEqual(resultado['saved'], 6)
            self.assertEqual(resultado['errors'], 0)
    
    @patch('App.Controllers.produtos.Produto')
    def test_get_products_from_database(self, mock_produto_model):
        """Testa a busca de produtos do banco"""
        # Mock dos produtos do banco
        mock_produtos = [
            Mock(id='prod-1', nome='Produto 1', custo_unitario=10.0),
            Mock(id='prod-2', nome='Produto 2', custo_unitario=20.0)
        ]
        mock_produto_model.query.limit.return_value.all.return_value = mock_produtos
        mock_produto_model.query.all.return_value = mock_produtos
        
        # Testa sem limite
        resultado = ProdutoController.get_products_from_database()
        self.assertTrue(resultado['success'])
        self.assertEqual(len(resultado['data']), 2)
        
        # Testa com limite
        resultado_limitado = ProdutoController.get_products_from_database(limit=1)
        self.assertTrue(resultado_limitado['success'])
    
    @patch('App.Controllers.produtos.Produto')
    @patch('App.Controllers.produtos.db')
    def test_update_product_cost(self, mock_db, mock_produto_model):
        """Testa a atualização do custo de um produto"""
        mock_produto = Mock()
        mock_produto_model.query.get.return_value = mock_produto
        
        resultado = ProdutoController.update_product_cost('prod-123', 15.75, 30.00)
        
        self.assertTrue(resultado['success'])
        self.assertEqual(mock_produto.custo_unitario, 15.75)
        self.assertEqual(mock_produto.preco_unitario, 30.00)
    
    @patch('App.Controllers.produtos.Produto')
    def test_update_product_cost_not_found(self, mock_produto_model):
        """Testa atualização de produto inexistente"""
        mock_produto_model.query.get.return_value = None
        
        resultado = ProdutoController.update_product_cost('prod-inexistente', 15.75)
        
        self.assertFalse(resultado['success'])
        self.assertEqual(resultado['message'], 'Produto não encontrado')
    
    @patch('App.Controllers.produtos.Produto')
    def test_get_product_by_id(self, mock_produto_model):
        """Testa a busca de produto por ID"""
        mock_produto = Mock()
        mock_produto.id = 'prod-123'
        mock_produto.nome = 'Produto Teste'
        mock_produto.custo_unitario = 10.0
        mock_produto_model.query.get.return_value = mock_produto
        
        resultado = ProdutoController.get_product_by_id('prod-123')
        
        self.assertTrue(resultado['success'])
        self.assertEqual(resultado['data']['id'], 'prod-123')
        self.assertEqual(resultado['data']['nome'], 'Produto Teste')
    
    @patch('App.Controllers.produtos.Produto')
    def test_get_product_by_id_not_found(self, mock_produto_model):
        """Testa busca de produto inexistente"""
        mock_produto_model.query.get.return_value = None
        
        resultado = ProdutoController.get_product_by_id('prod-inexistente')
        
        self.assertFalse(resultado['success'])
        self.assertEqual(resultado['message'], 'Produto não encontrado')


if __name__ == '__main__':
    unittest.main()
