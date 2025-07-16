from flask import Blueprint, request, jsonify, redirect, url_for, session
from ...Controllers.auth_api import AuthController
from ...Controllers.produtos import ProdutoController
from ...Controllers.serviço import ServicoController
from ...Controllers.Colaborador import ColaboradorController
from ...Controllers.tipo_de_tarefas import TipoTarefaController
from ...Controllers.tarefas import TarefaController

logar_user_bp = Blueprint('logar_user', __name__)

@logar_user_bp.route('/login', methods=['POST'])
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
            
            user_id = result['data']['user_id']
            response_message = result['message']
            
            try:
                # Sincroniza produtos automaticamente após login bem-sucedido
                produtos_result = ProdutoController.fetch_and_save_products(user_id)
                
                # Sincroniza serviços automaticamente após login bem-sucedido
                servicos_result = ServicoController.fetch_and_save_services(user_id)
                
                # Sincroniza colaboradores automaticamente após login bem-sucedido
                colaboradores_result = ColaboradorController.fetch_and_save_collaborators(user_id)
                
                # Sincroniza tipos de tarefa automaticamente após login bem-sucedido
                tipos_tarefa_result = TipoTarefaController.fetch_and_save_task_types(user_id)
                
                # Sincroniza tarefas e calcula dados financeiros automaticamente após login bem-sucedido
                tarefas_result = TarefaController.fetch_and_process_tasks(user_id)
                
            except Exception as sync_error:
                print(f"Erro durante sincronização: {str(sync_error)}")
                # Em caso de erro na sincronização, continua com login mas sem sincronizar
                return jsonify({
                    'success': True,
                    'message': result['message'] + " (Aviso: Erro na sincronização automática)",
                    'redirect_url': url_for('renderizar_pagina.dashboard'),
                    'sync_error': str(sync_error)
                }), 200
            
            # Adiciona informações sobre a sincronização na resposta
            try:
                if produtos_result.get('success'):
                    response_message += f" Produtos: {produtos_result['data']['saved']} novos, {produtos_result['data']['updated']} atualizados."
                else:
                    response_message += f" Produtos: erro - {produtos_result.get('message', 'Erro desconhecido')}"
                
                if servicos_result.get('success'):
                    response_message += f" Serviços: {servicos_result['data']['saved']} novos, {servicos_result['data']['updated']} atualizados."
                else:
                    response_message += f" Serviços: erro - {servicos_result.get('message', 'Erro desconhecido')}"
                
                if colaboradores_result.get('success'):
                    response_message += f" Colaboradores: {colaboradores_result['data']['saved']} novos, {colaboradores_result['data']['updated']} atualizados."
                else:
                    response_message += f" Colaboradores: erro - {colaboradores_result.get('message', 'Erro desconhecido')}"
                
                if tipos_tarefa_result.get('success'):
                    response_message += f" Tipos de tarefa: {tipos_tarefa_result['data']['saved']} novos, {tipos_tarefa_result['data']['updated']} atualizados."
                else:
                    response_message += f" Tipos de tarefa: erro - {tipos_tarefa_result.get('message', 'Erro desconhecido')}"
                
                if tarefas_result.get('success'):
                    tasks_processed = tarefas_result.get('data', {}).get('tasks_processed', 0)
                    response_message += f" Tarefas processadas: {tasks_processed}, dados financeiros calculados."
                else:
                    response_message += f" Tarefas: erro - {tarefas_result.get('message', 'Erro desconhecido')}"
                    
            except Exception as msg_error:
                response_message += f" (Erro ao formatar mensagem: {str(msg_error)})"
            
            return jsonify({
                'success': True,
                'message': response_message,
                'redirect_url': url_for('renderizar_pagina.dashboard'),
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

@logar_user_bp.route('/logout')
def logout():
    """Faz logout do usuário"""
    session.clear()
    return redirect(url_for('renderizar_página.index'))
