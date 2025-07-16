from flask import Blueprint, render_template

renderizar_página_bp = Blueprint('renderizar_página', __name__)

@renderizar_página_bp.route('/')
def index():
    return render_template('login_credencial.html')
