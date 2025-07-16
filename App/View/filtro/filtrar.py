from flask import Blueprint, request, session, redirect, url_for, jsonify
from datetime import datetime, timedelta
from ...Controllers.auth_api import AuthController
from ...Controllers.produtos import ProdutoController
from ...Controllers.serviço import ServicoController
from ...Controllers.Colaborador import ColaboradorController
from ...Controllers.tipo_de_tarefas import TipoTarefaController
from ...Controllers.tarefas import TarefaController
from ...Models import (
    Usuario, Produto, Servico, TipoTarefa, Colaborador, Tarefa,
    FaturamentoTotal, FaturamentoProduto, FaturamentoServico,
    LucroTotal, LucroProduto, LucroServico
)
from ... import db

filtrar_bp = Blueprint('filtrar', __name__)

@filtrar_bp.route('/filtros/consulta', methods=['POST'])
def consulta_filtros():
    """
    Rota para processar consulta com filtros
    
    Fluxo:
    1. Extrai user_id do usuário logado
    2. Deleta todos os dados do banco vinculados ao usuário (exceto tabela user)
    3. Captura filtros (data_inicial, data_final, etc.) do request
    4. Valida token_bearer do usuário
    5. Se válido: usa token atual para sincronizações
    6. Se inválido: re-autentica com api_key e token_api
    7. Realiza todas as sincronizações (produtos, serviços, colaboradores, tipos_tarefa, tarefas)
       - Para tarefas: passa data_inicial e data_final dos filtros
    8. Redireciona para /dashboard/refresh com filtros aplicados
    """
    
    # ========== ETAPA 1: EXTRAIR USER_ID DO USUÁRIO LOGADO ==========
    user_id = session.get('user_id')
    
    if not user_id or not session.get('authenticated'):
        return jsonify({
            'success': False,
            'message': 'Usuário não autenticado'
        }), 401
    
    # ========== ETAPA 2: BUSCAR DADOS DO USUÁRIO ==========
    usuario = Usuario.query.get(user_id)
    if not usuario:
        return jsonify({
            'success': False,
            'message': 'Usuário não encontrado'
        }), 404
    
    # ========== ETAPA 3: DELETAR DADOS DO BANCO (EXCETO TABELA USER) ==========
    try:
        # Deletar dados financeiros
        FaturamentoTotal.query.filter_by(usuario_id=user_id).delete()
        FaturamentoProduto.query.filter_by(usuario_id=user_id).delete()
        FaturamentoServico.query.filter_by(usuario_id=user_id).delete()
        LucroTotal.query.filter_by(usuario_id=user_id).delete()
        LucroProduto.query.filter_by(usuario_id=user_id).delete()
        LucroServico.query.filter_by(usuario_id=user_id).delete()
        
        # Deletar dados operacionais
        Tarefa.query.filter_by(usuario_id=user_id).delete()
        Produto.query.filter_by(usuario_id=user_id).delete()
        Servico.query.filter_by(usuario_id=user_id).delete()
        TipoTarefa.query.filter_by(usuario_id=user_id).delete()
        Colaborador.query.filter_by(usuario_id=user_id).delete()
        
        # Commit das exclusões
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Erro ao limpar dados do banco: {str(e)}'
        }), 500
    
    # ========== ETAPA 4: VALIDAR TOKEN_BEARER ==========
    token_validation = AuthController.validate_token(usuario.chave_app)
    token_valido = token_validation.get('valid', False)
    
    # ========== ETAPA 5: ESTRUTURA DE DECISÃO PARA AUTENTICAÇÃO ==========
    if token_valido:
        # Token ainda válido - usar token atual
        print(f"✅ Token válido para usuário {user_id}")
        
    else:
        # Token inválido - re-autenticar
        print(f"❌ Token inválido para usuário {user_id} - Re-autenticando...")
        
        # Obter api_key e token_api do usuário
        api_key = usuario.chave_app
        token_api = usuario.token_api
        
        if not api_key or not token_api:
            return jsonify({
                'success': False,
                'message': 'Credenciais de API não encontradas para re-autenticação'
            }), 400
        
        # Re-autenticar com a API da Auvo
        auth_result = AuthController.authenticate_auvo(api_key, token_api)
        
        if not auth_result.get('success'):
            return jsonify({
                'success': False,
                'message': f'Erro na re-autenticação: {auth_result.get("message", "Erro desconhecido")}'
            }), 401
        
        print(f"✅ Re-autenticação bem-sucedida para usuário {user_id}")
    
    # ========== ETAPA 6: CAPTURAR FILTROS PARA SINCRONIZAÇÃO ==========
    data = request.get_json() or {}
    filters = {
        'data_inicial': data.get('data_inicial'),
        'data_final': data.get('data_final'),
        'produto': data.get('produto'),
        'servico': data.get('servico'),
        'tipo_tarefa': data.get('tipo_tarefa'),
        'colaborador': data.get('colaborador')
    }
    
    # ========== ETAPA 7: REALIZAR TODAS AS SINCRONIZAÇÕES ==========
    sync_results = {}
    
    try:
        # Sincronizar produtos
        print("🔄 Sincronizando produtos...")
        produtos_result = ProdutoController.fetch_and_save_products(user_id)
        sync_results['produtos'] = produtos_result
        
        # Sincronizar serviços
        print("🔄 Sincronizando serviços...")
        servicos_result = ServicoController.fetch_and_save_services(user_id)
        sync_results['servicos'] = servicos_result
        
        # Sincronizar colaboradores
        print("🔄 Sincronizando colaboradores...")
        colaboradores_result = ColaboradorController.fetch_and_save_collaborators(user_id)
        sync_results['colaboradores'] = colaboradores_result
        
        # Sincronizar tipos de tarefa
        print("🔄 Sincronizando tipos de tarefa...")
        tipos_result = TipoTarefaController.fetch_and_save_task_types(user_id)
        sync_results['tipos_tarefa'] = tipos_result
        
        # Sincronizar tarefas
        print("🔄 Sincronizando tarefas...")
        # Passar data_inicial e data_final dos filtros para a sincronização
        tarefas_result = TarefaController.fetch_and_process_tasks(
            user_id, 
            start_date=filters.get('data_inicial'),
            end_date=filters.get('data_final')
        )
        sync_results['tarefas'] = tarefas_result
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro durante sincronização: {str(e)}',
            'sync_results': sync_results
        }), 500
    
    # ========== ETAPA 8: CAPTURAR FILTROS PARA REDIRECIONAMENTO ==========
    # Remover filtros vazios
    filters_clean = {k: v for k, v in filters.items() if v}
    
    # ========== ETAPA 9: RETORNAR SUCESSO E DADOS PARA REDIRECIONAMENTO ==========
    return jsonify({
        'success': True,
        'message': 'Sincronização completa realizada com sucesso',
        'sync_results': {
            'produtos': sync_results.get('produtos', {}).get('message', 'Erro'),
            'servicos': sync_results.get('servicos', {}).get('message', 'Erro'),
            'colaboradores': sync_results.get('colaboradores', {}).get('message', 'Erro'),
            'tipos_tarefa': sync_results.get('tipos_tarefa', {}).get('message', 'Erro'),
            'tarefas': sync_results.get('tarefas', {}).get('message', 'Erro')
        },
        'redirect_url': url_for('renderizar_pagina.dashboard', **filters_clean) if filters_clean else url_for('renderizar_pagina.dashboard'),
        'token_was_renewed': not token_valido
    })


@filtrar_bp.route('/filtros/status', methods=['GET'])
def status_filtros():
    """
    Rota auxiliar para verificar status dos filtros e autenticação
    """
    
    user_id = session.get('user_id')
    
    if not user_id or not session.get('authenticated'):
        return jsonify({
            'success': False,
            'message': 'Usuário não autenticado'
        }), 401
    
    usuario = Usuario.query.get(user_id)
    if not usuario:
        return jsonify({
            'success': False,
            'message': 'Usuário não encontrado'
        }), 404
    
    # Verificar status do token
    token_validation = AuthController.validate_token(usuario.chave_app)
    
    return jsonify({
        'success': True,
        'user_id': user_id,
        'token_valid': token_validation.get('valid', False),
        'last_sync': getattr(usuario, 'last_sync', None),
        'api_key_present': bool(usuario.chave_app),
        'token_api_present': bool(usuario.token_api)
    })
