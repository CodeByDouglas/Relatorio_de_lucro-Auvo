from flask import Blueprint, render_template, jsonify, request, session
from datetime import datetime, timedelta
from ..Controllers.tarefas import TarefaController
from ..Models import (
    FaturamentoTotal, FaturamentoProduto, FaturamentoServico,
    LucroTotal, LucroProduto, LucroServico, Produto, Servico,
    TipoTarefa, Colaborador
)

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
    
      #Verifica se o usuário está autenticado
    user_id = session.get('user_id')
    if not user_id:
         return jsonify({
             'error': 'Usuário não autenticado'
        }), 401
    
    # Para teste, vamos usar um user_id fixo
    user_id = 1
    
    # Captura os filtros enviados via query parameters
    filters = {
        'data_inicial': request.args.get('data_inicial'),
        'data_final': request.args.get('data_final'),
        'produto': request.args.get('produto'),
        'servico': request.args.get('servico'),
        'tipo_tarefa': request.args.get('tipo_tarefa'),
        'colaborador': request.args.get('colaborador')
    }
    
    # Define datas padrão se não fornecidas
    from datetime import datetime, timedelta
    if not filters['data_inicial']:
        filters['data_inicial'] = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    if not filters['data_final']:
        filters['data_final'] = datetime.now().strftime('%Y-%m-%d')
    
    # Busca resumo financeiro do período
    financial_summary = TarefaController.get_financial_summary(
        user_id, 
        filters['data_inicial'], 
        filters['data_final']
    )
    
    # Se não há dados, retorna valores zerados
    if not financial_summary:
        financial_summary = {
            'faturamento': {
                'total': 0,
                'produto': 0,
                'servico': 0,
                'porcentagem_produto': 0,
                'porcentagem_servico': 0
            },
            'lucro': {
                'total': 0,
                'produto': 0,
                'servico': 0,
                'porcentagem_produto': 0,
                'porcentagem_servico': 0,
                'margem_lucro': 0
            }
        }
    
    # Formata os dados para o frontend
    data = {
        'faturamento_total': financial_summary['faturamento']['total'],
        'faturamento_produto': financial_summary['faturamento']['produto'],
        'faturamento_servico': financial_summary['faturamento']['servico'],
        'lucro_total': financial_summary['lucro']['total'],
        'lucro_produto': financial_summary['lucro']['produto'],
        'lucro_servico': financial_summary['lucro']['servico'],
        'percentuais': {
            'faturamento_produto': financial_summary['faturamento']['porcentagem_produto'],
            'faturamento_servico': financial_summary['faturamento']['porcentagem_servico'],
            'lucro_produto': financial_summary['lucro']['porcentagem_produto'],
            'lucro_servico': financial_summary['lucro']['porcentagem_servico'],
            'margem_lucro': financial_summary['lucro']['margem_lucro']
        },
        'periodo': financial_summary.get('periodo', {
            'inicio': filters['data_inicial'],
            'fim': filters['data_final']
        }),
        'filtros_aplicados': filters
    }
    
    return jsonify(data)

@dashboard_bp.route('/api/dashboard/detailed-data')
def detailed_data():
    """API para retornar dados detalhados da tabela"""
    
    # Verifica se o usuário está autenticado
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({
            'error': 'Usuário não autenticado'
        }), 401
    
    # Captura os filtros enviados via query parameters
    filters = {
        'data_inicial': request.args.get('data_inicial'),
        'data_final': request.args.get('data_final'),
        'produto': request.args.get('produto'),
        'servico': request.args.get('servico'),
        'tipo_tarefa': request.args.get('tipo_tarefa'),
        'colaborador': request.args.get('colaborador')
    }
    
    try:
        from ..Models import Tarefa
        from datetime import datetime
        
        # Define datas padrão se não fornecidas
        if not filters['data_inicial']:
            filters['data_inicial'] = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        if not filters['data_final']:
            filters['data_final'] = datetime.now().strftime('%Y-%m-%d')
        
        # Converte datas para datetime
        data_inicial = datetime.strptime(filters['data_inicial'], '%Y-%m-%d')
        data_final = datetime.strptime(filters['data_final'], '%Y-%m-%d')
        
        # Busca tarefas do usuário no período
        query = Tarefa.query.filter_by(usuario_id=user_id).filter(
            Tarefa.data >= data_inicial,
            Tarefa.data <= data_final
        )
        
        # Aplica filtros adicionais se fornecidos
        if filters['tipo_tarefa']:
            query = query.filter(Tarefa.tipo_tarefa_id == int(filters['tipo_tarefa']))
        
        if filters['colaborador']:
            query = query.filter(Tarefa.colaborador_id == int(filters['colaborador']))
        
        tarefas = query.all()
        
        # Formata dados para o frontend
        data = []
        for tarefa in tarefas:
            # Busca nomes relacionados
            tipo_tarefa_nome = tarefa.tipo_tarefa.descricao if tarefa.tipo_tarefa else 'N/A'
            colaborador_nome = tarefa.colaborador.nome if tarefa.colaborador else 'N/A'
            
            # Extrai produtos e serviços do JSON de detalhes
            detalhes = tarefa.detalhes_json or {}
            task_original = detalhes.get('task_original', {})
            produtos = task_original.get('products', [])
            servicos = task_original.get('services', [])
            
            # Monta string de produtos/serviços
            itens_str = ""
            if produtos:
                produto_nomes = [p.get('nome', f"Produto {p.get('productId', 'N/A')}") for p in produtos]
                itens_str += "Produtos: " + ", ".join(produto_nomes)
            
            if servicos:
                servico_nomes = [s.get('nome', f"Serviço {s.get('id', 'N/A')}") for s in servicos]
                if itens_str:
                    itens_str += " | "
                itens_str += "Serviços: " + ", ".join(servico_nomes)
            
            if not itens_str:
                itens_str = "N/A"
            
            data.append({
                'id': tarefa.id,
                'cliente': tarefa.cliente or 'N/A',
                'tipo_tarefa': tipo_tarefa_nome,
                'colaborador': colaborador_nome,
                'data': tarefa.data.strftime('%d/%m/%Y') if tarefa.data else 'N/A',
                'itens': itens_str,
                'valor_total': f"{tarefa.valor_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                'custo_total': f"{tarefa.custo_total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
                'lucro_bruto': f"{tarefa.lucro_bruto:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            })
        
        return jsonify(data)
        
    except Exception as e:
        return jsonify({
            'error': f'Erro ao buscar dados detalhados: {str(e)}'
        }), 500

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
    from ..Controllers.tipo_de_tarefas import TipoTarefaController
    
    # Verifica se o usuário está autenticado
    # user_id = session.get('user_id')
    # if not user_id:
    #     return jsonify({
    #         'error': 'Usuário não autenticado'
    #     }), 401
    
    # Para teste, vamos usar um user_id fixo
    user_id = 1
    
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
    
    # Busca tipos de tarefa reais do banco
    tipos_tarefa_list = TipoTarefaController.get_task_types_for_user(user_id)
    tipos_tarefa_formatted = [
        {'id': tipo['id'], 'nome': tipo['descricao']} 
        for tipo in tipos_tarefa_list
    ]
    
    # Dados dos filtros
    filters_data = {
        'produtos': produtos_list,
        'servicos': servicos_list,
        'tipos_tarefa': tipos_tarefa_formatted,
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
    # if not session.get('authenticated') or not session.get('user_id'):
    #     return jsonify({
    #         'success': False,
    #         'message': 'Usuário não autenticado'
    #     }), 401
    
    # Para teste, vamos usar um user_id fixo
    user_id = 1
    
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
    # if not session.get('authenticated') or not session.get('user_id'):
    #     return jsonify({
    #         'success': False,
    #         'message': 'Usuário não autenticado'
    #     }), 401
    
    # Para teste, vamos usar um user_id fixo
    user_id = 1
    
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
    # if not session.get('authenticated') or not session.get('user_id'):
    #     return jsonify({
    #         'success': False,
    #         'message': 'Usuário não autenticado'
    #     }), 401
    
    # Para teste, vamos usar um user_id fixo
    user_id = 1
    
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

@dashboard_bp.route('/api/tasks/sync', methods=['POST'])
def sync_tasks():
    """Endpoint para sincronização manual de tarefas"""
    
    # Verifica se o usuário está autenticado
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({
            'success': False,
            'message': 'Usuário não autenticado'
        }), 401
    
    try:
        # Pega parâmetros opcionais da requisição
        data = request.get_json() if request.is_json else {}
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        # Executa sincronização de tarefas
        result = TarefaController.fetch_and_process_tasks(user_id, start_date, end_date)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500

@dashboard_bp.route('/api/dashboard/filters/options')
def get_filter_options():
    """Retorna as opções dinâmicas para os filtros baseadas no usuário logado"""
    
    print("DEBUG: Executando endpoint filters/options")
    
    # Verifica se o usuário está autenticado
    # user_id = session.get('user_id')
    # if not user_id:
    #     return jsonify({
    #         'error': 'Usuário não autenticado'
    #     }), 401
    
    # Para teste, vamos usar um user_id fixo
    user_id = 1
    
    try:
        # Busca produtos do usuário
        produtos = Produto.query.filter_by(usuario_id=user_id).all()
        produtos_list = [
            {'id': produto.id, 'nome': produto.nome} 
            for produto in produtos
        ]
        
        # Busca serviços do usuário
        servicos = Servico.query.filter_by(usuario_id=user_id).all()
        servicos_list = [
            {'id': servico.id, 'nome': servico.nome} 
            for servico in servicos
        ]
        
        # Busca tipos de tarefa do usuário
        tipos_tarefa = TipoTarefa.query.filter_by(usuario_id=user_id).all()
        tipos_tarefa_list = [
            {'id': tipo.id, 'nome': tipo.descricao} 
            for tipo in tipos_tarefa
        ]
        
        # Busca colaboradores do usuário
        colaboradores = Colaborador.query.filter_by(usuario_id=user_id).all()
        colaboradores_list = [
            {'id': colaborador.id, 'nome': colaborador.nome} 
            for colaborador in colaboradores
        ]
        
        filters_data = {
            'produtos': produtos_list,
            'servicos': servicos_list,
            'tipos_tarefa': tipos_tarefa_list,
            'colaboradores': colaboradores_list
        }
        
        return jsonify(filters_data)
        
    except Exception as e:
        return jsonify({
            'error': f'Erro ao buscar opções de filtro: {str(e)}'
        }), 500