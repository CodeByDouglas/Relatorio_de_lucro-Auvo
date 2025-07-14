"""
Testes simplificados para o ProdutoController
"""
import unittest
from unittest.mock import Mock, patch
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from App.Controllers.produtos import ProdutoController
from run import create_app


class TestProdutoControllerSimple(unittest.TestCase):
    """Testes simplificados para o controller de produtos"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
    def tearDown(self):
        """Limpeza após cada teste"""
        self.app_context.pop()
    
    def test_fetch_and_save_products_no_user_id(self):
        """Testa erro quando user_id não é fornecido"""
        resultado = ProdutoController.fetch_and_save_products(None)
        
        self.assertFalse(resultado['success'])
        self.assertEqual(resultado['message'], 'ID do usuário é obrigatório')
    
    @patch('App.Controllers.produtos.Usuario')
    def test_fetch_and_save_products_user_not_found(self, mock_usuario_model):
        """Testa erro quando usuário não é encontrado"""
        mock_usuario_model.query.get.return_value = None
        
        resultado = ProdutoController.fetch_and_save_products(1)
        
        self.assertFalse(resultado['success'])
        self.assertEqual(resultado['message'], 'Usuário não encontrado')
    
    @patch('App.Controllers.produtos.Produto')
    def test_get_products_from_database(self, mock_produto_model):
        """Testa a busca de produtos do banco"""
        mock_products = [
            Mock(id='prod-123', nome='Produto 1', custo_unitario=10.50),
            Mock(id='prod-456', nome='Produto 2', custo_unitario=25.00)
        ]
        mock_produto_model.query.all.return_value = mock_products
        
        resultado = ProdutoController.get_products_from_database()
        
        self.assertTrue(resultado['success'])
        self.assertEqual(len(resultado['data']), 2)
    
    @patch('App.Controllers.produtos.Produto')
    def test_get_product_by_id_success(self, mock_produto_model):
        """Testa a busca de produto por ID"""
        mock_product = Mock()
        mock_product.id = 'prod-123'
        mock_product.nome = 'Produto Teste'
        mock_product.custo_unitario = 10.50
        
        mock_produto_model.query.filter_by.return_value.first.return_value = mock_product
        
        resultado = ProdutoController.get_product_by_id('prod-123')
        
        self.assertTrue(resultado['success'])
        self.assertEqual(resultado['data']['id'], 'prod-123')
        self.assertEqual(resultado['data']['nome'], 'Produto Teste')
    
    @patch('App.Controllers.produtos.Produto')
    def test_get_product_by_id_not_found(self, mock_produto_model):
        """Testa busca de produto inexistente"""
        mock_produto_model.query.filter_by.return_value.first.return_value = None
        
        resultado = ProdutoController.get_product_by_id('prod-inexistente')
        
        self.assertFalse(resultado['success'])
        self.assertEqual(resultado['message'], 'Produto não encontrado')


if __name__ == '__main__':
    unittest.main()
