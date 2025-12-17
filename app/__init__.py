"""Inicialização da aplicação Flask - Companheiro de Mestre de Dungeon."""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()


def create_app():
    """Factory function para criar a aplicação Flask."""
    app = Flask(__name__)

    # Carregar configuração
    app.config.from_object('config.Config')

    # Garantir que as pastas necessárias existem
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config['QUESTS_FOLDER'], exist_ok=True)

    # Inicializar extensões
    db.init_app(app)

    # Registar blueprints
    from app.routes.main import main_bp
    from app.routes.quest import quest_bp
    from app.routes.combat import combat_bp
    from app.routes.print import print_bp
    from app.routes.players import players_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(quest_bp, url_prefix='/aventura')
    app.register_blueprint(combat_bp, url_prefix='/combate')
    app.register_blueprint(print_bp, url_prefix='/imprimir')
    app.register_blueprint(players_bp)

    # Criar tabelas da base de dados
    with app.app_context():
        db.create_all()

    return app
