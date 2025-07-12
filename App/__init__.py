from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    # Caminho absoluto para a pasta templates na raiz do projeto
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../templates'))
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../static'))
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    
    # Configurações da aplicação
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'sua-chave-secreta-aqui'  # Mude para uma chave segura
    
    db.init_app(app)

    from .View.home import home_bp
    from .View.dashboard import dashboard_bp
    
    app.register_blueprint(home_bp)
    app.register_blueprint(dashboard_bp)

    # Importar os modelos para que o SQLAlchemy os reconheça
    from .Models import (
        Usuario, TipoTarefa, Colaborador, Produto, Servico, Tarefa,
        FaturamentoTotal, FaturamentoProduto, FaturamentoServico,
        LucroTotal, LucroProduto, LucroServico
    )

    with app.app_context():
        db.create_all()

    return app