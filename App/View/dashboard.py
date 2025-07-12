from flask import Blueprint, render_template, jsonify, request
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    """Renderiza a página do dashboard"""
    return render_template('dashboard.html')

@dashboard_bp.route('/relatorio-tarefas')
def relatorio_tarefas():
    """Renderiza a página de relatório detalhado de tarefas"""
    return render_template('relatorio_tarefas.html')

@dashboard_bp.route('/api/dashboard/data')
def dashboard_data():
    """API para retornar dados do dashboard com filtros"""
    # Captura os filtros enviados via query parameters
    filters = {
        'data_inicial': request.args.get('data_inicial'),
        'data_final': request.args.get('data_final'),
        'produto': request.args.get('produto'),
        'servico': request.args.get('servico'),
        'tipo_tarefa': request.args.get('tipo_tarefa'),
        'colaborador': request.args.get('colaborador')
    }
    
    # Dados mockados para teste - substitua pela lógica real do banco
    data = {
        'faturamento_total': 999.99,
        'faturamento_produto': 999.99,
        'faturamento_servico': 999.99,
        'lucro_total': 999.99,
        'lucro_produto': 999.99,
        'lucro_servico': 999.99,
        'percentuais': {
            'faturamento_total': 100,
            'faturamento_produto': 99,
            'faturamento_servico': 99,
            'lucro_total': 100,
            'lucro_produto': 99,
            'lucro_servico': 99
        }
    }
    
    return jsonify(data)

@dashboard_bp.route('/api/dashboard/detailed-data')
def detailed_data():
    """API para retornar dados detalhados da tabela"""
    # Captura os filtros enviados via query parameters
    filters = {
        'data_inicial': request.args.get('data_inicial'),
        'data_final': request.args.get('data_final'),
        'produto': request.args.get('produto'),
        'servico': request.args.get('servico'),
        'tipo_tarefa': request.args.get('tipo_tarefa'),
        'colaborador': request.args.get('colaborador')
    }
    
    # Dados mockados para teste - substitua pela lógica real do banco
    data = [
        {
            'cliente': 'Cliente A',
            'tipo_tarefa': 'Desenvolvimento',
            'data': '11/07/2025',
            'produto': 'Produto A',
            'lucro': '999,99'
        },
        {
            'cliente': 'Cliente B',
            'tipo_tarefa': 'Consultoria',
            'data': '11/07/2025',
            'produto': 'Produto B',
            'lucro': '899,99'
        },
        {
            'cliente': 'Cliente C',
            'tipo_tarefa': 'Suporte',
            'data': '11/07/2025',
            'produto': 'Serviço A',
            'lucro': '799,99'
        }
    ]
    
    return jsonify(data)

@dashboard_bp.route('/api/dashboard/export')
def export_excel():
    """Exporta os dados do dashboard para Excel"""
    # Aqui você implementaria a lógica de exportação
    # Por enquanto, retorna uma resposta JSON
    return jsonify({
        'status': 'success',
        'message': 'Exportação em desenvolvimento',
        'filename': f'relatorio_lucro_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    })

@dashboard_bp.route('/api/dashboard/filters')
def get_filters():
    """Retorna as opções disponíveis para os filtros"""
    from ..Controllers.produtos import ProdutoController
    from ..Controllers.serviço import ServicoController
    from ..Controllers.Colaborador import ColaboradorController
    
    # Busca produtos reais do banco
    produtos_result = ProdutoController.get_products_from_database()
    produtos_list = []
    
    if produtos_result['success']:
        produtos_list = [
            {'id': produto['id'], 'nome': produto['nome']} 
            for produto in produtos_result['data']
        ]
    
    # Busca serviços reais do banco
    servicos_result = ServicoController.get_services_from_database()
    servicos_list = []
    
    if servicos_result['success']:
        servicos_list = [
            {'id': servico['id'], 'nome': servico['nome']} 
            for servico in servicos_result['data']
        ]
    
    # Busca colaboradores reais do banco
    colaboradores_result = ColaboradorController.get_collaborators_from_database()
    colaboradores_list = []
    
    if colaboradores_result['success']:
        colaboradores_list = [
            {'id': colaborador['id'], 'nome': colaborador['nome']} 
            for colaborador in colaboradores_result['data']
        ]
    
    # Dados mockados para outros filtros - substitua pela consulta real ao banco
    filters_data = {
        'produtos': produtos_list,
        'servicos': servicos_list,
        'tipos_tarefa': [
            {'id': 1, 'nome': 'Desenvolvimento'},
            {'id': 2, 'nome': 'Consultoria'},
            {'id': 3, 'nome': 'Suporte'}
        ],
        'colaboradores': colaboradores_list
    }
    
    return jsonify(filters_data)

@dashboard_bp.route('/api/auth/login', methods=['POST'])
def login():
    """API para autenticação com a API da Auvo"""
    from flask import request
    from ..Controllers.auth_api import AuthController
    
    # Captura os dados do corpo da requisição
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'message': 'Dados não fornecidos'
        }), 400
    
    api_key = data.get('api_key')
    api_token = data.get('api_token')
    
    if not api_key or not api_token:
        return jsonify({
            'success': False,
            'message': 'API Key e API Token são obrigatórios'
        }), 400
    
    # Faz a autenticação
    result = AuthController.authenticate_auvo(api_key, api_token)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 401


@dashboard_bp.route('/api/auth/validate', methods=['POST'])
def validate_token():
    """API para validar token de usuário"""
    from flask import request
    from ..Controllers.auth_api import AuthController
    
    data = request.get_json()
    
    if not data or not data.get('api_key'):
        return jsonify({
            'success': False,
            'message': 'API Key é obrigatória'
        }), 400
    
    api_key = data.get('api_key')
    
    # Valida o token
    result = AuthController.validate_token(api_key)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 401


@dashboard_bp.route('/api/products/sync', methods=['POST'])
def sync_products():
    """API para sincronizar produtos da API Auvo"""
    from flask import session
    from ..Controllers.produtos import ProdutoController
    
    # Verifica se o usuário está autenticado
    if not session.get('authenticated') or not session.get('user_id'):
        return jsonify({
            'success': False,
            'message': 'Usuário não autenticado'
        }), 401
    
    user_id = session.get('user_id')
    
    # Sincroniza os produtos
    result = ProdutoController.fetch_and_save_products(user_id)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 400


@dashboard_bp.route('/api/products', methods=['GET'])
def get_products():
    """API para obter produtos do banco de dados"""
    from flask import request
    from ..Controllers.produtos import ProdutoController
    
    # Parâmetro opcional para limitar resultados
    limit = request.args.get('limit', type=int)
    
    # Busca produtos no banco
    result = ProdutoController.get_products_from_database(limit)
    
    return jsonify(result), 200 if result['success'] else 400


@dashboard_bp.route('/api/products/<product_id>', methods=['GET'])
def get_product_by_id(product_id):
    """API para obter um produto específico por ID"""
    from ..Controllers.produtos import ProdutoController
    
    # Busca produto por ID
    result = ProdutoController.get_product_by_id(product_id)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 404


@dashboard_bp.route('/api/products/<product_id>/cost', methods=['PUT'])
def update_product_cost(product_id):
    """API para atualizar custos de um produto"""
    from flask import request
    from ..Controllers.produtos import ProdutoController
    
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'message': 'Dados não fornecidos'
        }), 400
    
    custo_unitario = data.get('custo_unitario')
    preco_unitario = data.get('preco_unitario')
    
    if custo_unitario is None:
        return jsonify({
            'success': False,
            'message': 'Custo unitário é obrigatório'
        }), 400
    
    # Atualiza o produto
    result = ProdutoController.update_product_cost(
        product_id, 
        custo_unitario, 
        preco_unitario
    )
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 400

# === ROTAS DA API PARA SERVIÇOS ===

@dashboard_bp.route('/api/services/sync', methods=['POST'])
def sync_services():
    """API para sincronizar serviços da API Auvo"""
    from flask import session
    from ..Controllers.serviço import ServicoController
    
    # Verifica se o usuário está autenticado
    if not session.get('authenticated') or not session.get('user_id'):
        return jsonify({
            'success': False,
            'message': 'Usuário não autenticado'
        }), 401
    
    user_id = session.get('user_id')
    
    # Sincroniza os serviços
    result = ServicoController.fetch_and_save_services(user_id)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 400


@dashboard_bp.route('/api/services', methods=['GET'])
def get_services():
    """API para obter serviços do banco de dados"""
    from flask import request
    from ..Controllers.serviço import ServicoController
    
    # Parâmetro opcional para limitar resultados
    limit = request.args.get('limit', type=int)
    
    # Busca serviços no banco
    result = ServicoController.get_services_from_database(limit)
    
    return jsonify(result), 200 if result['success'] else 400


@dashboard_bp.route('/api/services/<service_id>', methods=['GET'])
def get_service_by_id(service_id):
    """API para obter um serviço específico por ID"""
    from ..Controllers.serviço import ServicoController
    
    # Busca serviço por ID
    result = ServicoController.get_service_by_id(service_id)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 404


@dashboard_bp.route('/api/services/<service_id>/cost', methods=['PUT'])
def update_service_cost(service_id):
    """API para atualizar custo de um serviço"""
    from flask import request
    from ..Controllers.serviço import ServicoController
    
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'message': 'Dados não fornecidos'
        }), 400
    
    custo_unitario = data.get('custo_unitario')
    
    if custo_unitario is None:
        return jsonify({
            'success': False,
            'message': 'Custo unitário é obrigatório'
        }), 400
    
    # Atualiza o serviço
    result = ServicoController.update_service_cost(service_id, custo_unitario)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 400

# === ROTAS DA API PARA COLABORADORES ===

@dashboard_bp.route('/api/collaborators/sync', methods=['POST'])
def sync_collaborators():
    """API para sincronizar colaboradores da API Auvo"""
    from flask import session
    from ..Controllers.Colaborador import ColaboradorController
    
    # Verifica se o usuário está autenticado
    if not session.get('authenticated') or not session.get('user_id'):
        return jsonify({
            'success': False,
            'message': 'Usuário não autenticado'
        }), 401
    
    user_id = session.get('user_id')
    
    # Sincroniza os colaboradores
    result = ColaboradorController.fetch_and_save_collaborators(user_id)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 400


@dashboard_bp.route('/api/collaborators', methods=['GET'])
def get_collaborators():
    """API para obter colaboradores do banco de dados"""
    from flask import request
    from ..Controllers.Colaborador import ColaboradorController
    
    # Parâmetro opcional para limitar resultados
    limit = request.args.get('limit', type=int)
    
    # Busca colaboradores no banco
    result = ColaboradorController.get_collaborators_from_database(limit)
    
    return jsonify(result), 200 if result['success'] else 400


@dashboard_bp.route('/api/collaborators/<int:collaborator_id>', methods=['GET'])
def get_collaborator_by_id(collaborator_id):
    """API para obter um colaborador específico por ID"""
    from ..Controllers.Colaborador import ColaboradorController
    
    # Busca colaborador por ID
    result = ColaboradorController.get_collaborator_by_id(collaborator_id)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 404


@dashboard_bp.route('/api/collaborators/<int:collaborator_id>/name', methods=['PUT'])
def update_collaborator_name(collaborator_id):
    """API para atualizar nome de um colaborador"""
    from flask import request
    from ..Controllers.Colaborador import ColaboradorController
    
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'message': 'Dados não fornecidos'
        }), 400
    
    nome = data.get('nome')
    
    if not nome:
        return jsonify({
            'success': False,
            'message': 'Nome é obrigatório'
        }), 400
    
    # Atualiza o colaborador
    result = ColaboradorController.update_collaborator_name(collaborator_id, nome)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 400