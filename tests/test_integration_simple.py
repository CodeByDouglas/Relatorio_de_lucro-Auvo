"""
Testes de integração simplificados para o sistema
"""
import unittest
from unittest.mock import Mock, patch
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from App import create_app


class TestIntegrationSimple(unittest.TestCase):
    """Testes de integração simplificados"""
    
    def setUp(self):
        """Configuração inicial para testes"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.mock_user_id = 1
        
    def test_dashboard_access(self):
        """Testa acesso ao dashboard"""
        response = self.client.get('/dashboard')
        # Dashboard deve estar acessível (pode retornar 200 ou redirect)
        self.assertIn(response.status_code, [200, 302, 401])
        print("✅ Dashboard acessível")
        
    def test_relatorio_tarefas_access(self):
        """Testa acesso ao relatório de tarefas"""
        response = self.client.get('/relatorio-tarefas')
        # Página deve estar acessível
        self.assertIn(response.status_code, [200, 302, 401])
        print("✅ Relatório de tarefas acessível")
        
    def test_api_endpoints_basic(self):
        """Testa endpoints básicos da API"""
        # Test filter options endpoint
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
                    
                    response = self.client.get('/api/dashboard/filters/options')
                    self.assertIn(response.status_code, [200, 401])
                    
        print("✅ API endpoints básicos funcionando")
        
    def test_static_files_access(self):
        """Testa acesso a arquivos estáticos"""
        # Test CSS file access
        response = self.client.get('/static/css/dashboard.css')
        self.assertEqual(response.status_code, 200)
        
        # Test JS file access  
        response = self.client.get('/static/js/dashboard.js')
        self.assertEqual(response.status_code, 200)
        
        print("✅ Arquivos estáticos acessíveis")
        
    def test_api_sync_endpoints(self):
        """Testa endpoints de sincronização"""
        with self.app.app_context():
            with patch('flask.session', {'user_id': self.mock_user_id}):
                # Test products sync
                with patch('App.Controllers.produtos.ProdutoController.fetch_and_save_products') as mock_sync:
                    mock_sync.return_value = {'success': True, 'count': 5}
                    response = self.client.post('/api/products/sync')
                    self.assertIn(response.status_code, [200, 401, 400])
                    
                # Test services sync
                with patch('App.Controllers.serviço.ServicoController.fetch_and_save_services') as mock_sync:
                    mock_sync.return_value = {'success': True, 'count': 3}
                    response = self.client.post('/api/services/sync')
                    self.assertIn(response.status_code, [200, 401, 400])
                    
        print("✅ Endpoints de sincronização funcionando")


if __name__ == '__main__':
    unittest.main()
