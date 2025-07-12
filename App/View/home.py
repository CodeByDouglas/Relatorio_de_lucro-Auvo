from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from ..Controllers.auth_api import AuthController

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
            
            return jsonify({
                'success': True,
                'message': result['message'],
                'redirect_url': url_for('dashboard.dashboard')
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