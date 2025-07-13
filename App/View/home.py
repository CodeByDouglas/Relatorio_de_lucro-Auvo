from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from ..Controllers.auth_api import AuthController
from ..Controllers.produtos import ProdutoController
from ..Controllers.serviço import ServicoController
from ..Controllers.Colaborador import ColaboradorController
from ..Controllers.tipo_de_tarefas import TipoTarefaController
from ..Controllers.tarefas import TarefaController

home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def index():
    return render_template('login_credencial.html')

@home_bp.route('/login', methods=['POST'])
def login():
    """Processa o login com as credenciais da API Auvo"""
    try:
        # Captura os dados do formulário
        data = request.get_json() if request.is_json else request.form
        
        api_key = data.get('appkey') or data.get('api_key')
        api_token = data.get('token') or data.get('api_token')
        
        if not api_key or not api_token:
            return jsonify({
                'success': False,
                'message': 'API Key e Token são obrigatórios'
            }), 400
        
        # Chama o controller de autenticação
        result = AuthController.authenticate_auvo(api_key, api_token)
        
        if result['success']:
            # Salva dados na sessão
            session['user_id'] = result['data']['user_id']
            session['api_key'] = api_key
            session['authenticated'] = True
            session['access_token'] = result['data']['access_token']
            
            # Sincroniza produtos automaticamente após login bem-sucedido
            user_id = result['data']['user_id']
            produtos_result = ProdutoController.fetch_and_save_products(user_id)
            
            # Sincroniza serviços automaticamente após login bem-sucedido
            servicos_result = ServicoController.fetch_and_save_services(user_id)
            
            # Sincroniza colaboradores automaticamente após login bem-sucedido
            colaboradores_result = ColaboradorController.fetch_and_save_collaborators(user_id)
            
            # Sincroniza tipos de tarefa automaticamente após login bem-sucedido
            tipos_tarefa_result = TipoTarefaController.fetch_and_save_task_types(user_id)
            
            # Sincroniza tarefas e calcula dados financeiros automaticamente após login bem-sucedido
            tarefas_result = TarefaController.fetch_and_process_tasks(user_id)
            
            # Adiciona informações sobre a sincronização na resposta
            response_message = result['message']
            if produtos_result['success']:
                response_message += f" Produtos sincronizados: {produtos_result['data']['saved']} novos, {produtos_result['data']['updated']} atualizados."
            else:
                response_message += f" Aviso: Erro ao sincronizar produtos - {produtos_result['message']}"
            
            if servicos_result['success']:
                response_message += f" Serviços sincronizados: {servicos_result['data']['saved']} novos, {servicos_result['data']['updated']} atualizados."
            else:
                response_message += f" Aviso: Erro ao sincronizar serviços - {servicos_result['message']}"
            
            if colaboradores_result['success']:
                response_message += f" Colaboradores sincronizados: {colaboradores_result['data']['saved']} novos, {colaboradores_result['data']['updated']} atualizados."
            else:
                response_message += f" Aviso: Erro ao sincronizar colaboradores - {colaboradores_result['message']}"
            
            if tipos_tarefa_result['success']:
                response_message += f" Tipos de tarefa sincronizados: {tipos_tarefa_result['data']['saved']} novos, {tipos_tarefa_result['data']['updated']} atualizados."
            else:
                response_message += f" Aviso: Erro ao sincronizar tipos de tarefa - {tipos_tarefa_result['message']}"
            
            if tarefas_result['success']:
                response_message += f" Tarefas processadas: {tarefas_result['data']['tasks_processed']}, dados financeiros calculados."
            else:
                response_message += f" Aviso: Erro ao processar tarefas - {tarefas_result['message']}"
            
            return jsonify({
                'success': True,
                'message': response_message,
                'redirect_url': url_for('dashboard.dashboard'),
                'produtos_sync': produtos_result,
                'servicos_sync': servicos_result,
                'colaboradores_sync': colaboradores_result,
                'tipos_tarefa_sync': tipos_tarefa_result,
                'tarefas_sync': tarefas_result
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Erro interno do servidor'
        }), 500

@home_bp.route('/logout')
def logout():
    """Faz logout do usuário"""
    session.clear()
    return redirect(url_for('home.index'))