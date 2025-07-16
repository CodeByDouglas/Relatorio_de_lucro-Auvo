from flask import Blueprint, render_template, jsonify, request, session
from datetime import datetime, timedelta
from ..Controllers.tarefas import TarefaController
from ..Models import Tarefa, Produto, Servico, TipoTarefa, Colaborador

relatorio_tarefas_bp = Blueprint('relatorio_tarefas', __name__)

@relatorio_tarefas_bp.route('/relatorio-tarefas')
def relatorio_tarefas():
    """Renderiza a página de relatório detalhado de tarefas"""
    return render_template('relatorio_tarefas.html')

@relatorio_tarefas_bp.route('/api/relatorio/detailed-data')
def detailed_data():
    """API para retornar dados detalhados da tabela de tarefas"""
    
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

@relatorio_tarefas_bp.route('/api/relatorio/export')
def export_excel():
    """Exporta os dados do relatório de tarefas para Excel"""
    # Aqui você implementaria a lógica de exportação específica para tarefas
    # Por enquanto, retorna uma resposta JSON
    return jsonify({
        'status': 'success',
        'message': 'Exportação de relatório de tarefas em desenvolvimento',
        'filename': f'relatorio_tarefas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    })

@relatorio_tarefas_bp.route('/api/tasks/sync', methods=['POST'])
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
