"""
Configuração base para testes unitários
"""
import sys
import os
import pytest
from unittest.mock import Mock, patch
from flask import Flask

# Adiciona o diretório raiz ao path para importar módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from App import create_app, db
from App.Models import Usuario, Produto, Servico, Colaborador, TipoTarefa, Tarefa


@pytest.fixture
def app():
    """Cria uma instância da aplicação para testes"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Cliente de teste Flask"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Runner de comandos CLI para testes"""
    return app.test_cli_runner()


@pytest.fixture
def mock_usuario():
    """Mock de usuário para testes"""
    return Mock(
        id=1,
        chave_app='test_app_key',
        token_bearer='test_bearer_token',
        nome='Usuário Teste'
    )


@pytest.fixture
def mock_produto():
    """Mock de produto para testes"""
    return Mock(
        id='prod-123',
        usuario_id=1,
        nome='Produto Teste',
        custo_unitario=10.50,
        preco_unitario=25.00
    )


@pytest.fixture
def mock_servico():
    """Mock de serviço para testes"""
    return Mock(
        id='serv-456',
        usuario_id=1,
        nome='Serviço Teste',
        custo_unitario=50.00
    )


@pytest.fixture
def mock_colaborador():
    """Mock de colaborador para testes"""
    return Mock(
        id=123,
        usuario_id=1,
        nome='João Silva'
    )


@pytest.fixture
def mock_tipo_tarefa():
    """Mock de tipo de tarefa para testes"""
    return Mock(
        id=1,
        usuario_id=1,
        descricao='Desenvolvimento'
    )


@pytest.fixture
def mock_api_response_success():
    """Mock de resposta de sucesso da API"""
    return {
        'result': {
            'entityList': [
                {
                    'id': 'test-id',
                    'name': 'Test Item',
                    'description': 'Test Description'
                }
            ],
            'pagedSearchReturnData': {
                'totalItems': 1,
                'page': 1
            }
        }
    }


@pytest.fixture
def mock_api_response_error():
    """Mock de resposta de erro da API"""
    return {
        'error': 'Unauthorized',
        'message': 'Token inválido'
    }
