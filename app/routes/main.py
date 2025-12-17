"""Rotas principais da aplicação."""

import json
import os
from flask import Blueprint, render_template, current_app
from app.services.quest_loader import QuestLoader

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Página inicial - lista de aventuras disponíveis."""
    loader = QuestLoader()
    quests = loader.get_all_quests()
    return render_template('index.html', quests=quests)


@main_bp.route('/sobre')
def about():
    """Página sobre a aplicação."""
    return render_template('about.html')


@main_bp.route('/personagens')
def characters():
    """Personagens pré-criados para começar rapidamente."""
    characters_file = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'data', 'characters.json'
    )
    characters_data = []
    if os.path.exists(characters_file):
        with open(characters_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            characters_data = data.get('personagens', [])
    return render_template('characters.html', characters=characters_data)


@main_bp.route('/ajuda')
def help_page():
    """Página de ajuda - como usar o DM Companion."""
    return render_template('help.html')
