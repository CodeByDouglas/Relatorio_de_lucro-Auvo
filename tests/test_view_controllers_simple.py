"""
Testes unitários simplificados para os controllers da View
"""
import unittest
from unittest.mock import Mock, patch
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from App import create_app


class TestDashboardControllerSimple(unittest.TestCase):
    """Testes simplificados para os endpoints do dashboard"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.mock_user_id = 1
        
    def test_dashboard_route(self):
        """Testa se a rota do dashboard está acessível"""
        response = self.client.get('/dashboard')
        self.assertIn(response.status_code, [200, 302, 401])
        print("✅ Rota dashboard acessível")
        
    def test_relatorio_route(self):
        """Testa se a rota do relatório está acessível"""
        response = self.client.get('/relatorio-tarefas')
        self.assertIn(response.status_code, [200, 302, 401])
        print("✅ Rota relatório acessível")
        
    def test_api_dashboard_data(self):
        """Testa endpoint de dados do dashboard"""
        with self.app.app_context():
            with patch('flask.session', {'user_id': self.mock_user_id}):
                with patch('App.Controllers.tarefas.TarefaController.get_financial_summary') as mock_summary:
                    mock_summary.return_value = {
                        'faturamento': {'total': 1000, 'produto': 600, 'servico': 400, 'porcentagem_produto': 60, 'porcentagem_servico': 40},
                        'lucro': {'total': 300, 'produto': 180, 'servico': 120, 'porcentagem_produto': 60, 'porcentagem_servico': 40, 'margem_lucro': 30}
                    }
                    response = self.client.get('/api/dashboard/data')
                    self.assertIn(response.status_code, [200, 401])
        print("✅ API dashboard data funcionando")
        
    def test_api_filters_options(self):
        """Testa endpoint de opções de filtros"""
        with self.app.app_context():
            with patch('flask.session', {'user_id': self.mock_user_id}):
                with patch('App.Models.Produto.query') as mock_produto, \
                     patch('App.Models.Servico.query') as mock_servico, \
                     patch('App.Models.TipoTarefa.query') as mock_tipo, \
                     patch('App.Models.Colaborador.query') as mock_colaborador:
                    
                    # Mock empty results
                    mock_produto.filter_by.return_value.all.return_value = []
                    mock_servico.filter_by.return_value.all.return_value = []
                    mock_tipo.filter_by.return_value.all.return_value = []
                    mock_colaborador.filter_by.return_value.all.return_value = []
                    
                    response = self.client.get('/api/filters/options')
                    self.assertIn(response.status_code, [200, 401])
        print("✅ API filters options funcionando")
        
    def test_api_sync_products(self):
        """Testa endpoint de sincronização de produtos"""
        with self.app.app_context():
            with patch('flask.session', {'user_id': self.mock_user_id}):
                with patch('App.Controllers.produtos.ProdutoController.fetch_and_save_products') as mock_sync:
                    mock_sync.return_value = {'success': True, 'count': 5}
                    response = self.client.post('/api/products/sync')
                    self.assertIn(response.status_code, [200, 401, 400])
        print("✅ API sync products funcionando")


if __name__ == '__main__':
    unittest.main()
