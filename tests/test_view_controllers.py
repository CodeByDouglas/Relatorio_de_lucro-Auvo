"""
Testes unitários para os controllers da View (dashboard.py e login/)
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from App import create_app


class TestDashboardController(unittest.TestCase):
    """Testes para os endpoints do dashboard"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Mock do usuário autenticado
        self.user_id = 1
        self.mock_usuario = Mock()
        self.mock_usuario.id = self.user_id
        self.mock_usuario.nome = 'Test User'
        self.mock_usuario.chave_app = 'test_app_key'
        self.mock_usuario.token_bearer = 'test_bearer_token'
    
    @patch('App.View.dashboard.session')
    @patch('App.View.dashboard.Usuario')
    def test_dashboard_route_authenticated(self, mock_usuario_model, mock_session):
        """Testa acesso ao dashboard com usuário autenticado"""
        mock_session.get.return_value = self.user_id
        mock_usuario_model.query.get.return_value = self.mock_usuario
        
        response = self.client.get('/dashboard')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'dashboard', response.data)
    
    @patch('App.View.dashboard.session')
    def test_dashboard_route_not_authenticated(self, mock_session):
        """Testa redirecionamento quando não autenticado"""
        mock_session.get.return_value = None
        
        response = self.client.get('/dashboard')
        
        # Deve redirecionar para login
        self.assertEqual(response.status_code, 302)
    
    @patch('App.View.dashboard.session')
    @patch('App.View.dashboard.CalculosService')
    def test_calcular_faturamento_total_success(self, mock_calculos, mock_session):
        """Testa cálculo de faturamento total com sucesso"""
        mock_session.get.return_value = self.user_id
        mock_calculos.calcular_faturamento_total.return_value = 50000.0
        
        response = self.client.post('/calcular_faturamento_total')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['faturamento_total'], 50000.0)
    
    @patch('App.View.dashboard.session')
    def test_calcular_faturamento_total_not_authenticated(self, mock_session):
        """Testa cálculo de faturamento sem autenticação"""
        mock_session.get.return_value = None
        
        response = self.client.post('/calcular_faturamento_total')
        
        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Usuário não autenticado')
    
    @patch('App.View.dashboard.session')
    @patch('App.View.dashboard.CalculosService')
    def test_calcular_lucro_total_success(self, mock_calculos, mock_session):
        """Testa cálculo de lucro total com sucesso"""
        mock_session.get.return_value = self.user_id
        mock_calculos.calcular_lucro_total.return_value = 25000.0
        
        response = self.client.post('/calcular_lucro_total')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['lucro_total'], 25000.0)
    
    @patch('App.View.dashboard.session')
    @patch('App.View.dashboard.CalculosService')
    def test_calcular_porcentagem_lucro_faturamento_success(self, mock_calculos, mock_session):
        """Testa cálculo de porcentagem de lucro/faturamento com sucesso"""
        mock_session.get.return_value = self.user_id
        mock_calculos.calcular_porcentagem_lucro_faturamento.return_value = 50.0
        
        response = self.client.post('/calcular_porcentagem_lucro_faturamento')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['porcentagem'], 50.0)
    
    @patch('App.View.dashboard.session')
    @patch('App.View.dashboard.ProdutoController')
    def test_sync_produtos_success(self, mock_produto_controller, mock_session):
        """Testa sincronização de produtos com sucesso"""
        mock_session.get.return_value = self.user_id
        mock_produto_controller.fetch_and_save_products.return_value = {
            'success': True,
            'message': 'Produtos sincronizados com sucesso',
            'data': {'saved': 10, 'updated': 5}
        }
        
        response = self.client.post('/sync_produtos')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('Produtos sincronizados', data['message'])
    
    @patch('App.View.dashboard.session')
    @patch('App.View.dashboard.ServicoController')
    def test_sync_servicos_success(self, mock_servico_controller, mock_session):
        """Testa sincronização de serviços com sucesso"""
        mock_session.get.return_value = self.user_id
        mock_servico_controller.fetch_and_save_services.return_value = {
            'success': True,
            'message': 'Serviços sincronizados com sucesso',
            'data': {'saved': 8, 'updated': 3}
        }
        
        response = self.client.post('/sync_servicos')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('Serviços sincronizados', data['message'])
    
    @patch('App.View.dashboard.session')
    @patch('App.View.dashboard.ColaboradorController')
    def test_sync_colaboradores_success(self, mock_colaborador_controller, mock_session):
        """Testa sincronização de colaboradores com sucesso"""
        mock_session.get.return_value = self.user_id
        mock_colaborador_controller.fetch_and_save_collaborators.return_value = {
            'success': True,
            'message': 'Colaboradores sincronizados com sucesso',
            'data': {'saved': 15, 'updated': 2}
        }
        
        response = self.client.post('/sync_colaboradores')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('Colaboradores sincronizados', data['message'])
    
    @patch('App.View.dashboard.session')
    @patch('App.View.dashboard.TipoTarefaController')
    def test_sync_tipos_tarefa_success(self, mock_tipo_tarefa_controller, mock_session):
        """Testa sincronização de tipos de tarefa com sucesso"""
        mock_session.get.return_value = self.user_id
        mock_tipo_tarefa_controller.fetch_and_save_task_types.return_value = {
            'success': True,
            'message': 'Tipos de tarefa sincronizados com sucesso',
            'data': {'saved': 6, 'updated': 1}
        }
        
        response = self.client.post('/sync_tipos_tarefa')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('Tipos de tarefa sincronizados', data['message'])
    
    @patch('App.View.dashboard.session')
    @patch('App.View.dashboard.TarefaController')
    def test_sync_tarefas_success(self, mock_tarefa_controller, mock_session):
        """Testa sincronização de tarefas com sucesso"""
        mock_session.get.return_value = self.user_id
        mock_tarefa_controller.fetch_and_save_tasks.return_value = {
            'success': True,
            'message': 'Tarefas sincronizadas com sucesso',
            'data': {'saved': 50, 'updated': 10}
        }
        
        response = self.client.post('/sync_tarefas')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('Tarefas sincronizadas', data['message'])
    
    @patch('App.View.dashboard.session')
    @patch('App.View.dashboard.TipoTarefaController')
    def test_get_tipos_tarefa_success(self, mock_tipo_tarefa_controller, mock_session):
        """Testa busca de tipos de tarefa com sucesso"""
        mock_session.get.return_value = self.user_id
        mock_tipos = [
            {'id': 1, 'descricao': 'Desenvolvimento'},
            {'id': 2, 'descricao': 'Consultoria'}
        ]
        mock_tipo_tarefa_controller.get_task_types_for_user.return_value = mock_tipos
        
        response = self.client.get('/get_tipos_tarefa')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(len(data['tipos_tarefa']), 2)
        self.assertEqual(data['tipos_tarefa'][0]['descricao'], 'Desenvolvimento')
    
    @patch('App.View.dashboard.session')
    @patch('App.View.dashboard.CalculosService')
    def test_calcular_faturamento_total_error(self, mock_calculos, mock_session):
        """Testa erro no cálculo de faturamento total"""
        mock_session.get.return_value = self.user_id
        mock_calculos.calcular_faturamento_total.side_effect = Exception('Erro de cálculo')
        
        response = self.client.post('/calcular_faturamento_total')
        
        self.assertEqual(response.status_code, 500)
        data = response.get_json()
        self.assertFalse(data['success'])
        self.assertIn('Erro interno', data['message'])
    
    @patch('App.View.dashboard.session')
    @patch('App.View.dashboard.CalculosService')
    def test_calcular_lucro_produto_success(self, mock_calculos, mock_session):
        """Testa cálculo de lucro por produto com sucesso"""
        mock_session.get.return_value = self.user_id
        mock_calculos.calcular_lucro_produto.return_value = {
            'Produto A': 15000.0,
            'Produto B': 10000.0
        }
        
        response = self.client.post('/calcular_lucro_produto')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('Produto A', data['lucro_por_produto'])
        self.assertEqual(data['lucro_por_produto']['Produto A'], 15000.0)
    
    @patch('App.View.dashboard.session')
    @patch('App.View.dashboard.CalculosService')
    def test_calcular_porcentagem_faturamento_produto_success(self, mock_calculos, mock_session):
        """Testa cálculo de porcentagem de faturamento por produto"""
        mock_session.get.return_value = self.user_id
        mock_calculos.calcular_porcentagem_faturamento_produto.return_value = {
            'Produto A': 60.0,
            'Produto B': 40.0
        }
        
        response = self.client.post('/calcular_porcentagem_faturamento_produto')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['porcentagem_por_produto']['Produto A'], 60.0)


class TestHomeController(unittest.TestCase):
    """Testes para os endpoints do home"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_home_route(self):
        """Testa acesso à página inicial"""
        response = self.client.get('/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'login', response.data.lower())
    
    @patch('App.View.login.logar_user.AuthController')
    def test_login_success(self, mock_auth_controller):
        """Testa login com sucesso"""
        mock_auth_controller.authenticate.return_value = {
            'success': True,
            'user_id': 1,
            'message': 'Login realizado com sucesso'
        }
        
        response = self.client.post('/login', data={
            'chave_app': 'test_app_key',
            'email': 'test@test.com',
            'senha': 'test_password'
        })
        
        # Deve redirecionar para dashboard
        self.assertEqual(response.status_code, 302)
    
    @patch('App.View.login.logar_user.AuthController')
    def test_login_failure(self, mock_auth_controller):
        """Testa login com falha"""
        mock_auth_controller.authenticate.return_value = {
            'success': False,
            'message': 'Credenciais inválidas'
        }
        
        response = self.client.post('/login', data={
            'chave_app': 'invalid_key',
            'email': 'test@test.com',
            'senha': 'wrong_password'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Credenciais invalidas', response.data)
    
    @patch('App.View.login.logar_user.session')
    def test_logout(self, mock_session):
        """Testa logout"""
        response = self.client.get('/logout')
        
        # Deve limpar a sessão e redirecionar
        mock_session.clear.assert_called_once()
        self.assertEqual(response.status_code, 302)
    
    def test_login_get_method(self):
        """Testa acesso GET à página de login"""
        response = self.client.get('/login')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'login', response.data.lower())
    
    def test_login_missing_fields(self):
        """Testa login com campos obrigatórios faltando"""
        response = self.client.post('/login', data={
            'chave_app': 'test_app_key'
            # Faltam email e senha
        })
        
        self.assertEqual(response.status_code, 400)
    
    @patch('App.View.login.logar_user.AuthController')
    def test_login_server_error(self, mock_auth_controller):
        """Testa erro de servidor durante login"""
        mock_auth_controller.authenticate.side_effect = Exception('Erro de servidor')
        
        response = self.client.post('/login', data={
            'chave_app': 'test_app_key',
            'email': 'test@test.com',
            'senha': 'test_password'
        })
        
        self.assertEqual(response.status_code, 500)


class TestViewIntegration(unittest.TestCase):
    """Testes de integração entre os controllers de view"""
    
    def setUp(self):
        """Configuração inicial para testes de integração"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    @patch('App.View.login.logar_user.AuthController')
    @patch('App.View.dashboard.session')
    def test_login_to_dashboard_flow(self, mock_dashboard_session, mock_auth_controller):
        """Testa fluxo completo de login para dashboard"""
        # Mock do login bem-sucedido
        mock_auth_controller.authenticate.return_value = {
            'success': True,
            'user_id': 1,
            'message': 'Login realizado com sucesso'
        }
        
        # Realiza login
        login_response = self.client.post('/login', data={
            'chave_app': 'test_app_key',
            'email': 'test@test.com',
            'senha': 'test_password'
        })
        
        self.assertEqual(login_response.status_code, 302)
        
        # Simula sessão autenticada no dashboard
        mock_dashboard_session.get.return_value = 1
        
        # Acessa dashboard
        with patch('App.View.dashboard.Usuario') as mock_usuario:
            mock_user = Mock()
            mock_user.nome = 'Test User'
            mock_usuario.query.get.return_value = mock_user
            
            dashboard_response = self.client.get('/dashboard')
            self.assertEqual(dashboard_response.status_code, 200)
    
    def test_unauthorized_dashboard_access(self):
        """Testa acesso não autorizado ao dashboard"""
        with patch('App.View.dashboard.session') as mock_session:
            mock_session.get.return_value = None
            
            response = self.client.get('/dashboard')
            self.assertEqual(response.status_code, 302)  # Redirecionamento
    
    @patch('App.View.dashboard.session')
    def test_session_timeout_handling(self, mock_session):
        """Testa tratamento de timeout de sessão"""
        # Simula sessão expirada
        mock_session.get.return_value = None
        
        response = self.client.post('/calcular_faturamento_total')
        
        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Usuário não autenticado')


if __name__ == '__main__':
    unittest.main()
