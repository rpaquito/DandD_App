"""Rotas principais da aplicacao."""

import json
import os
from flask import Blueprint, render_template
from app.services.session_service import get_saved_characters

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Pagina inicial - menu principal."""
    return render_template('index.html')


@main_bp.route('/sobre')
def about():
    """Página sobre a aplicação."""
    return render_template('about.html')


@main_bp.route('/personagens')
def characters():
    """Pagina de gestao de personagens (pre-criados e guardados)."""
    # Carregar pre-criados
    characters_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'data', 'characters.json'
    )
    premade_characters = []
    if os.path.exists(characters_file):
        with open(characters_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            premade_characters = data.get('personagens', [])

    # Carregar personagens guardados
    saved_characters = get_saved_characters()

    return render_template('characters.html',
                           characters=premade_characters,
                           saved_characters=saved_characters)


@main_bp.route('/ajuda')
def help_page():
    """Pagina de ajuda - como usar o DM Companion."""
    from app.services.quest_loader import QuestLoader
    loader = QuestLoader()
    quests = loader.get_all_quests()
    return render_template('help.html', quests=quests)


@main_bp.route('/definicoes')
def settings():
    """Pagina de definicoes da aplicacao."""
    return render_template('settings.html')
