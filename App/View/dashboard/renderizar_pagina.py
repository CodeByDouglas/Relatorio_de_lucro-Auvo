from flask import Blueprint, render_template, session, redirect, url_for, request
from datetime import datetime, timedelta
from ...Controllers.tarefas import TarefaController
from ...Controllers.produtos import ProdutoController
from ...Controllers.serviço import ServicoController
from ...Controllers.Colaborador import ColaboradorController
from ...Controllers.tipo_de_tarefas import TipoTarefaController
from ...Models import (
    Usuario, Produto, Servico, TipoTarefa, Colaborador,
    FaturamentoTotal, FaturamentoProduto, FaturamentoServico,
    LucroTotal, LucroProduto, LucroServico
)

renderizar_pagina_bp = Blueprint('renderizar_pagina', __name__)

@renderizar_pagina_bp.route('/dashboard')
def dashboard():
    """
    Rota responsável por renderizar a página HTML do dashboard
    carregada com as informações do banco de dados
    """
    
    # Verificar se o usuário está autenticado
    if not session.get('authenticated') or not session.get('user_id'):
        return redirect(url_for('renderizar_página.index'))
    
    user_id = session.get('user_id')
    
    # Buscar usuário no banco
    usuario = Usuario.query.get(user_id)
    if not usuario:
        return redirect(url_for('renderizar_página.index'))
    
    # Definir período padrão (ontem até hoje)
    data_inicial = request.args.get('data_inicial')
    data_final = request.args.get('data_final')
    
    if not data_inicial:
        data_inicial = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    if not data_final:
        data_final = datetime.now().strftime('%Y-%m-%d')
    
    # Buscar dados financeiros do período
    try:
        financial_summary = TarefaController.get_financial_summary(
            user_id, 
            data_inicial, 
            data_final
        )
    except Exception as e:
        # Se houver erro, usar dados zerados
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
    
    # Buscar dados para os filtros
    try:
        # Produtos
        produtos_result = ProdutoController.get_products_from_database()
        produtos = produtos_result.get('data', []) if produtos_result.get('success') else []
        
        # Serviços
        servicos_result = ServicoController.get_services_from_database()
        servicos = servicos_result.get('data', []) if servicos_result.get('success') else []
        
        # Colaboradores
        colaboradores_result = ColaboradorController.get_collaborators_from_database()
        colaboradores = colaboradores_result.get('data', []) if colaboradores_result.get('success') else []
        
        # Tipos de tarefa
        tipos_tarefa_result = TipoTarefaController.get_task_types_from_database()
        tipos_tarefa = tipos_tarefa_result.get('data', []) if tipos_tarefa_result.get('success') else []
        
    except Exception as e:
        # Se houver erro, usar listas vazias
        produtos = []
        servicos = []
        colaboradores = []
        tipos_tarefa = []
    
    # Preparar dados para o template
    dashboard_data = {
        # Dados financeiros
        'faturamento_total': financial_summary['faturamento']['total'],
        'faturamento_produto': financial_summary['faturamento']['produto'],
        'faturamento_servico': financial_summary['faturamento']['servico'],
        'lucro_total': financial_summary['lucro']['total'],
        'lucro_produto': financial_summary['lucro']['produto'],
        'lucro_servico': financial_summary['lucro']['servico'],
        
        # Percentuais (estrutura para o template)
        'percentuais': {
            'faturamento_produto': financial_summary['faturamento']['porcentagem_produto'],
            'faturamento_servico': financial_summary['faturamento']['porcentagem_servico'],
            'lucro_produto': financial_summary['lucro']['porcentagem_produto'],
            'lucro_servico': financial_summary['lucro']['porcentagem_servico'],
            'margem_lucro': financial_summary['lucro']['margem_lucro']
        },
        
        # Período
        'data_inicial': data_inicial,
        'data_final': data_final,
        
        # Dados para filtros
        'produtos': produtos,
        'servicos': servicos,
        'colaboradores': colaboradores,
        'tipos_tarefa': tipos_tarefa,
        
        # Informações do usuário
        'usuario': {
            'id': usuario.id,
            'chave_app': usuario.chave_app,
            'nome': getattr(usuario, 'nome', 'Usuário')
        }
    }
    
    # Debug - imprimir dados antes de renderizar
    print("DEBUG - Financial summary keys:", list(financial_summary.keys()))
    print("DEBUG - Financial summary faturamento keys:", list(financial_summary.get('faturamento', {}).keys()))
    print("DEBUG - Financial summary lucro keys:", list(financial_summary.get('lucro', {}).keys()))
    print("DEBUG - Dashboard data keys:", list(dashboard_data.keys()))
    print("DEBUG - Percentuais:", dashboard_data.get('percentuais', 'NOT FOUND'))
    
    # Teste adicional - verificar se percentuais está no dashboard_data
    if 'percentuais' in dashboard_data:
        print("DEBUG - Percentuais encontrado no dashboard_data:", dashboard_data['percentuais'])
    else:
        print("DEBUG - Percentuais NÃO encontrado no dashboard_data")
    
    # Renderizar template com os dados
    try:
        return render_template('dashboard.html', **dashboard_data)
    except Exception as e:
        print(f"ERRO ao renderizar template: {e}")
        print(f"Tipo do erro: {type(e)}")
        print(f"Dashboard data keys: {list(dashboard_data.keys())}")
        raise


@renderizar_pagina_bp.route('/dashboard/refresh')
def refresh_dashboard():
    """
    Rota para atualizar os dados do dashboard mantendo os filtros aplicados
    """
    
    # Verificar autenticação
    if not session.get('authenticated') or not session.get('user_id'):
        return redirect(url_for('renderizar_página.index'))
    
    # Capturar parâmetros de filtro da URL
    filters = {
        'data_inicial': request.args.get('data_inicial'),
        'data_final': request.args.get('data_final'),
        'produto': request.args.get('produto'),
        'servico': request.args.get('servico'),
        'tipo_tarefa': request.args.get('tipo_tarefa'),
        'colaborador': request.args.get('colaborador')
    }
    
    # Redirecionar para a rota principal com os filtros
    return redirect(url_for('renderizar_pagina.dashboard', **{k: v for k, v in filters.items() if v}))


@renderizar_pagina_bp.route('/dashboard/export')
def export_dashboard():
    """
    Rota para exportar dados do dashboard
    """
    
    # Verificar autenticação
    if not session.get('authenticated') or not session.get('user_id'):
        return redirect(url_for('renderizar_página.index'))
    
    # Por enquanto, redireciona de volta para o dashboard
    # A funcionalidade de exportação será implementada posteriormente
    return redirect(url_for('renderizar_pagina.dashboard'))
