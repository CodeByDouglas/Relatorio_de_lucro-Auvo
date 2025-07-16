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

    from .View.login.renderizar_pagina import renderizar_página_bp
    from .View.login.logar_user import logar_user_bp
    # REMOVIDO: from .View.dashboard.api_endpoints import dashboard_bp
    from .View.dashboard.renderizar_pagina import renderizar_pagina_bp
    from .View.relatorio_tarefas import relatorio_tarefas_bp
    from .View.filtro.filtrar import filtrar_bp
    
    app.register_blueprint(renderizar_página_bp)
    app.register_blueprint(logar_user_bp)
    # REMOVIDO: app.register_blueprint(dashboard_bp)
    app.register_blueprint(renderizar_pagina_bp)
    app.register_blueprint(relatorio_tarefas_bp)
    app.register_blueprint(filtrar_bp)

    # Importar os modelos para que o SQLAlchemy os reconheça
    from .Models import (
        Usuario, TipoTarefa, Colaborador, Produto, Servico, Tarefa,
        FaturamentoTotal, FaturamentoProduto, FaturamentoServico,
        LucroTotal, LucroProduto, LucroServico
    )

    with app.app_context():
        db.create_all()

    return app