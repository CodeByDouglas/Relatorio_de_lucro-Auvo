"""
Testes unitários para o TarefaController
"""
import unittest
from unittest.mock import Mock, patch
import sys
import os
from datetime import datetime, date

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from App.Controllers.tarefas import TarefaController


class TestTarefaController(unittest.TestCase):
    """Testes para o controller de tarefas"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.user_id = 1
        self.mock_usuario = Mock()
        self.mock_usuario.id = self.user_id
        self.mock_usuario.chave_app = 'test_app_key'
        self.mock_usuario.token_bearer = 'test_bearer_token'
        
        # Mock das tarefas da API
        self.mock_api_tasks = [
            {
                'id': 1,
                'description': 'Desenvolvimento de funcionalidade',
                'observation': 'Observação da tarefa',
                'dateTimeStart': '2024-01-15T08:00:00',
                'dateTimeEnd': '2024-01-15T17:00:00',
                'billable': True,
                'collaborator': {'id': 101, 'name': 'João Silva'},
                'taskType': {'id': 201, 'description': 'Desenvolvimento'},
                'product': {'id': 301, 'description': 'Sistema ERP'},
                'service': {'id': 401, 'description': 'Consultoria'}
            },
            {
                'id': 2,
                'description': 'Reunião de alinhamento',
                'observation': '',
                'dateTimeStart': '2024-01-16T09:00:00',
                'dateTimeEnd': '2024-01-16T10:00:00',
                'billable': False,
                'collaborator': {'id': 102, 'name': 'Maria Santos'},
                'taskType': {'id': 202, 'description': 'Reunião'},
                'product': None,  # Sem produto
                'service': None   # Sem serviço
            }
        ]
        
        # Mock da resposta da API
        self.mock_api_response = {
            'result': {
                'entityList': self.mock_api_tasks,
                'pagedSearchReturnData': {
                    'totalItems': 2,
                    'page': 1
                }
            }
        }
    
    @patch('App.Controllers.tarefas.Usuario')
    @patch('App.Controllers.tarefas.AuthController')
    @patch('App.Controllers.tarefas.requests')
    @patch('App.Controllers.tarefas.db')
    def test_fetch_and_save_tasks_success(self, mock_db, mock_requests, mock_auth, mock_usuario_model):
        """Testa a sincronização bem-sucedida de tarefas"""
        # Configuração dos mocks
        mock_usuario_model.query.get.return_value = self.mock_usuario
        mock_auth.validate_token.return_value = {'valid': True}
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.mock_api_response
        mock_requests.get.return_value = mock_response
        
        # Mock do método _save_tasks_to_database
        with patch.object(TarefaController, '_save_tasks_to_database') as mock_save:
            mock_save.return_value = {
                'saved': 2,
                'updated': 0,
                'errors': 0,
                'error_details': []
            }
            
            # Executa o método
            resultado = TarefaController.fetch_and_save_tasks(self.user_id)
            
            # Verificações
            self.assertTrue(resultado['success'])
            self.assertIn('Tarefas sincronizadas com sucesso', resultado['message'])
            self.assertEqual(resultado['data']['total_tasks'], 2)
            self.assertEqual(resultado['data']['saved'], 2)
    
    def test_fetch_and_save_tasks_with_date_filter(self):
        """Testa sincronização com filtro de data"""
        start_date = '2024-01-01'
        end_date = '2024-01-31'
        
        with patch('App.Controllers.tarefas.Usuario') as mock_usuario_model, \
             patch('App.Controllers.tarefas.AuthController') as mock_auth, \
             patch('App.Controllers.tarefas.requests') as mock_requests:
            
            mock_usuario_model.query.get.return_value = self.mock_usuario
            mock_auth.validate_token.return_value = {'valid': True}
            
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = self.mock_api_response
            mock_requests.get.return_value = mock_response
            
            with patch.object(TarefaController, '_save_tasks_to_database') as mock_save:
                mock_save.return_value = {'saved': 2, 'updated': 0, 'errors': 0}
                
                resultado = TarefaController.fetch_and_save_tasks(
                    self.user_id, 
                    start_date=start_date, 
                    end_date=end_date
                )
                
                # Verifica se a URL foi construída com os parâmetros de data
                mock_requests.get.assert_called_once()
                call_args = mock_requests.get.call_args
                self.assertIn('dateStart', call_args[1]['params'])
                self.assertIn('dateEnd', call_args[1]['params'])
    
    @patch('App.Controllers.tarefas.Usuario')
    def test_fetch_and_save_tasks_user_not_found(self, mock_usuario_model):
        """Testa erro quando usuário não é encontrado"""
        mock_usuario_model.query.get.return_value = None
        
        resultado = TarefaController.fetch_and_save_tasks(self.user_id)
        
        self.assertFalse(resultado['success'])
        self.assertEqual(resultado['message'], 'Usuário não encontrado')
    
    @patch('App.Controllers.tarefas.Usuario')
    @patch('App.Controllers.tarefas.AuthController')
    def test_fetch_and_save_tasks_invalid_token(self, mock_auth, mock_usuario_model):
        """Testa erro quando token é inválido"""
        mock_usuario_model.query.get.return_value = self.mock_usuario
        mock_auth.validate_token.return_value = {'valid': False}
        
        resultado = TarefaController.fetch_and_save_tasks(self.user_id)
        
        self.assertFalse(resultado['success'])
        self.assertEqual(resultado['message'], 'Token expirado. Faça login novamente.')
    
    @patch('App.Controllers.tarefas.Usuario')
    @patch('App.Controllers.tarefas.AuthController')
    @patch('App.Controllers.tarefas.requests')
    def test_fetch_and_save_tasks_api_error(self, mock_requests, mock_auth, mock_usuario_model):
        """Testa erro da API"""
        mock_usuario_model.query.get.return_value = self.mock_usuario
        mock_auth.validate_token.return_value = {'valid': True}
        
        mock_response = Mock()
        mock_response.status_code = 404
        mock_requests.get.return_value = mock_response
        
        resultado = TarefaController.fetch_and_save_tasks(self.user_id)
        
        self.assertFalse(resultado['success'])
        self.assertIn('Erro na API', resultado['message'])
    
    @patch('App.Controllers.tarefas.Tarefa')
    @patch('App.Controllers.tarefas.db')
    def test_save_tasks_to_database(self, mock_db, mock_tarefa_model):
        """Testa o salvamento de tarefas no banco"""
        # Mock de tarefa existente
        mock_tarefa_existente = Mock()
        mock_tarefa_model.query.filter_by.return_value.first.return_value = None
        
        resultado = TarefaController._save_tasks_to_database(
            self.mock_api_tasks, 
            self.user_id
        )
        
        # Verifica se retorna estatísticas
        self.assertIn('saved', resultado)
        self.assertIn('updated', resultado)
        self.assertIn('errors', resultado)
    
    def test_parse_datetime_valid_formats(self):
        """Testa a conversão de datas/horas em diferentes formatos"""
        # Formato ISO 8601
        datetime_str = '2024-01-15T08:00:00'
        result = TarefaController._parse_datetime(datetime_str)
        self.assertIsInstance(result, datetime)
        self.assertEqual(result.year, 2024)
        self.assertEqual(result.month, 1)
        self.assertEqual(result.day, 15)
        self.assertEqual(result.hour, 8)
        
        # Formato com timezone
        datetime_str_tz = '2024-01-15T08:00:00Z'
        result_tz = TarefaController._parse_datetime(datetime_str_tz)
        self.assertIsInstance(result_tz, datetime)
    
    def test_parse_datetime_invalid_formats(self):
        """Testa a conversão de datas/horas em formatos inválidos"""
        # Valores inválidos
        self.assertIsNone(TarefaController._parse_datetime(None))
        self.assertIsNone(TarefaController._parse_datetime(''))
        self.assertIsNone(TarefaController._parse_datetime('data_inválida'))
        self.assertIsNone(TarefaController._parse_datetime('2024-13-40'))
    
    def test_calculate_task_duration(self):
        """Testa o cálculo de duração da tarefa"""
        start_datetime = datetime(2024, 1, 15, 8, 0, 0)
        end_datetime = datetime(2024, 1, 15, 17, 0, 0)
        
        duration = TarefaController._calculate_task_duration(start_datetime, end_datetime)
        
        # 9 horas = 540 minutos
        self.assertEqual(duration, 540)
    
    def test_calculate_task_duration_invalid_dates(self):
        """Testa cálculo de duração com datas inválidas"""
        start_datetime = datetime(2024, 1, 15, 17, 0, 0)
        end_datetime = datetime(2024, 1, 15, 8, 0, 0)  # Hora fim antes do início
        
        duration = TarefaController._calculate_task_duration(start_datetime, end_datetime)
        
        # Deve retornar 0 para durações inválidas
        self.assertEqual(duration, 0)
    
    def test_calculate_task_duration_none_values(self):
        """Testa cálculo de duração com valores None"""
        duration1 = TarefaController._calculate_task_duration(None, datetime.now())
        duration2 = TarefaController._calculate_task_duration(datetime.now(), None)
        duration3 = TarefaController._calculate_task_duration(None, None)
        
        self.assertEqual(duration1, 0)
        self.assertEqual(duration2, 0)
        self.assertEqual(duration3, 0)
    
    @patch('App.Controllers.tarefas.Tarefa')
    def test_get_tasks_for_user(self, mock_tarefa_model):
        """Testa a busca de tarefas do usuário"""
        # Mock das tarefas do banco
        mock_tarefas = [
            Mock(
                id=1, 
                descricao='Tarefa 1', 
                data_inicio=date(2024, 1, 15),
                duracao_minutos=480,
                faturavel=True,
                usuario_id=1
            ),
            Mock(
                id=2, 
                descricao='Tarefa 2', 
                data_inicio=date(2024, 1, 16),
                duracao_minutos=120,
                faturavel=False,
                usuario_id=1
            )
        ]
        mock_tarefa_model.query.filter_by.return_value.all.return_value = mock_tarefas
        
        resultado = TarefaController.get_tasks_for_user(self.user_id)
        
        self.assertEqual(len(resultado), 2)
        self.assertEqual(resultado[0]['id'], 1)
        self.assertEqual(resultado[0]['descricao'], 'Tarefa 1')
        self.assertTrue(resultado[0]['faturavel'])
    
    @patch('App.Controllers.tarefas.Tarefa')
    def test_get_tasks_for_user_with_filters(self, mock_tarefa_model):
        """Testa a busca de tarefas com filtros"""
        mock_query = Mock()
        mock_tarefa_model.query.filter_by.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = []
        
        # Testa filtro por data
        resultado = TarefaController.get_tasks_for_user(
            self.user_id,
            start_date='2024-01-01',
            end_date='2024-01-31'
        )
        
        # Verifica se os filtros foram aplicados
        mock_query.filter.assert_called()
        self.assertEqual(resultado, [])
    
    @patch('App.Controllers.tarefas.session')
    def test_sync_tasks_endpoint_success(self, mock_session):
        """Testa o endpoint de sincronização com usuário autenticado"""
        mock_session.get.return_value = self.user_id
        
        with patch.object(TarefaController, 'fetch_and_save_tasks') as mock_fetch:
            mock_fetch.return_value = {
                'success': True,
                'message': 'Tarefas sincronizadas com sucesso',
                'data': {'saved': 15, 'updated': 3}
            }
            
            resultado = TarefaController.sync_tasks_endpoint()
            
            self.assertTrue(resultado['success'])
            self.assertIn('Tarefas sincronizadas com sucesso', resultado['message'])
    
    @patch('App.Controllers.tarefas.session')
    def test_sync_tasks_endpoint_no_auth(self, mock_session):
        """Testa o endpoint de sincronização sem autenticação"""
        mock_session.get.return_value = None
        
        resultado = TarefaController.sync_tasks_endpoint()
        
        self.assertFalse(resultado['success'])
        self.assertEqual(resultado['message'], 'Usuário não autenticado')
    
    def test_extract_related_entity_id_valid(self):
        """Testa extração de ID de entidades relacionadas válidas"""
        collaborator = {'id': 123, 'name': 'João'}
        task_type = {'id': 456, 'description': 'Desenvolvimento'}
        
        collab_id = TarefaController._extract_related_entity_id(collaborator)
        task_type_id = TarefaController._extract_related_entity_id(task_type)
        
        self.assertEqual(collab_id, 123)
        self.assertEqual(task_type_id, 456)
    
    def test_extract_related_entity_id_invalid(self):
        """Testa extração de ID de entidades relacionadas inválidas"""
        # Entidade None
        self.assertIsNone(TarefaController._extract_related_entity_id(None))
        
        # Entidade sem ID
        self.assertIsNone(TarefaController._extract_related_entity_id({}))
        
        # Entidade com ID None
        self.assertIsNone(TarefaController._extract_related_entity_id({'id': None}))
    
    def test_save_tasks_handles_missing_data(self):
        """Testa o tratamento de dados faltantes nas tarefas"""
        tasks_with_missing_data = [
            {
                'id': 1,
                'description': 'Tarefa sem datas',
                'billable': True
                # Faltam dateTimeStart, dateTimeEnd, etc.
            },
            {
                'id': 2,
                # Falta description
                'dateTimeStart': '2024-01-15T08:00:00',
                'dateTimeEnd': '2024-01-15T17:00:00',
                'billable': False
            }
        ]
        
        with patch('App.Controllers.tarefas.Tarefa') as mock_tarefa, \
             patch('App.Controllers.tarefas.db') as mock_db:
            
            mock_tarefa.query.filter_by.return_value.first.return_value = None
            
            resultado = TarefaController._save_tasks_to_database(
                tasks_with_missing_data, 
                self.user_id
            )
            
            # Verifica que processou as tarefas mesmo com dados faltantes
            self.assertEqual(resultado['saved'], 2)
            self.assertEqual(resultado['errors'], 0)
    
    @patch('App.Controllers.tarefas.Tarefa')
    @patch('App.Controllers.tarefas.db')
    def test_database_transaction_rollback(self, mock_db, mock_tarefa_model):
        """Testa rollback da transação em caso de erro"""
        # Simula erro durante commit
        mock_db.session.commit.side_effect = Exception('Database error')
        
        resultado = TarefaController._save_tasks_to_database(
            self.mock_api_tasks, 
            self.user_id
        )
        
        # Verifica que houve rollback
        mock_db.session.rollback.assert_called_once()
        
        # Verifica resposta de erro
        self.assertEqual(resultado['saved'], 0)
        self.assertEqual(resultado['updated'], 0)
        self.assertEqual(resultado['errors'], len(self.mock_api_tasks))
    
    def test_update_existing_task(self):
        """Testa atualização de tarefa existente"""
        with patch('App.Controllers.tarefas.Tarefa') as mock_tarefa, \
             patch('App.Controllers.tarefas.db') as mock_db:
            
            # Mock de tarefa existente
            mock_existing_task = Mock()
            mock_existing_task.descricao = 'Descrição Antiga'
            mock_existing_task.observacao = 'Observação Antiga'
            mock_existing_task.faturavel = False
            
            mock_tarefa.query.filter_by.return_value.first.return_value = mock_existing_task
            
            # Dados atualizados
            updated_task = {
                'id': 1,
                'description': 'Descrição Nova',
                'observation': 'Observação Nova',
                'billable': True,
                'dateTimeStart': '2024-01-15T08:00:00',
                'dateTimeEnd': '2024-01-15T17:00:00'
            }
            
            resultado = TarefaController._save_tasks_to_database([updated_task], self.user_id)
            
            # Verifica se a tarefa foi atualizada
            self.assertEqual(mock_existing_task.descricao, 'Descrição Nova')
            self.assertEqual(mock_existing_task.observacao, 'Observação Nova')
            self.assertTrue(mock_existing_task.faturavel)
            self.assertEqual(resultado['updated'], 1)


if __name__ == '__main__':
    unittest.main()
