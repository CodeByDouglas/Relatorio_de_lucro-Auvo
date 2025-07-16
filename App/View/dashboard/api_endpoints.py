from flask import Blueprint, render_template, jsonify, request, session
from datetime import datetime, timedelta
from ...Controllers.tarefas import TarefaController
from ...Controllers.produtos import ProdutoController
from ...Controllers.serviço import ServicoController
from ...Controllers.Colaborador import ColaboradorController
from ...Controllers.tipo_de_tarefas import TipoTarefaController
from ...Controllers.auth_api import AuthController
from ...Models import (
    FaturamentoTotal, FaturamentoProduto, FaturamentoServico,
    LucroTotal, LucroProduto, LucroServico, Produto, Servico,
    TipoTarefa, Colaborador
)

dashboard_bp = Blueprint('dashboard', __name__)

# =============================================================================
# NOTA: As APIs abaixo foram desabilitadas porque o dashboard agora carrega
# todas as informações diretamente no servidor via renderizar_pagina.py
# =============================================================================

# @dashboard_bp.route('/api/dashboard/data')
# def dashboard_data():
#     """API para retornar dados do dashboard com filtros"""
#     # REMOVIDA: O dashboard agora carrega dados diretamente no servidor
#     pass

# @dashboard_bp.route('/api/dashboard/sync', methods=['POST'])
# def sync_dashboard_data():
#     """API para sincronizar dados do dashboard"""
#     # REMOVIDA: Sincronização agora é feita via /filtros/consulta
#     pass

# =============================================================================
# APIs mantidas para funcionalidades específicas que podem ser úteis
# =============================================================================