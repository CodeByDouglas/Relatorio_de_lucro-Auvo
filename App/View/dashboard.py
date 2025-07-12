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
    # Dados mockados - substitua pela consulta real ao banco
    filters_data = {
        'produtos': [
            {'id': 1, 'nome': 'Produto A'},
            {'id': 2, 'nome': 'Produto B'},
            {'id': 3, 'nome': 'Produto C'}
        ],
        'servicos': [
            {'id': 1, 'nome': 'Serviço A'},
            {'id': 2, 'nome': 'Serviço B'},
            {'id': 3, 'nome': 'Serviço C'}
        ],
        'tipos_tarefa': [
            {'id': 1, 'nome': 'Desenvolvimento'},
            {'id': 2, 'nome': 'Consultoria'},
            {'id': 3, 'nome': 'Suporte'}
        ],
        'colaboradores': [
            {'id': 1, 'nome': 'João Silva'},
            {'id': 2, 'nome': 'Maria Santos'},
            {'id': 3, 'nome': 'Pedro Costa'}
        ]
    }
    
    return jsonify(filters_data)