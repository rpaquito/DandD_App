"""Rotas para versões imprimíveis."""

import json
import os
from flask import Blueprint, render_template, abort
from app.services.quest_loader import QuestLoader

print_bp = Blueprint('print', __name__)

CHARACTERS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'characters.json')


def load_characters():
    """Carrega os personagens pré-criados."""
    if os.path.exists(CHARACTERS_FILE):
        with open(CHARACTERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f).get('personagens', [])
    return []


@print_bp.route('/mapa/<quest_id>')
def map_view(quest_id):
    """Mapa imprimível da aventura."""
    loader = QuestLoader()
    quest = loader.get_quest(quest_id)
    if not quest:
        abort(404)
    return render_template('print/map.html', quest=quest)


@print_bp.route('/fichas')
def character_sheets():
    """Fichas de personagens em branco para impressão."""
    return render_template('print/sheets.html')


@print_bp.route('/aventura/<quest_id>')
def quest_summary(quest_id):
    """Resumo imprimível da aventura."""
    loader = QuestLoader()
    quest = loader.get_quest(quest_id)
    if not quest:
        abort(404)
    return render_template('print/quest_summary.html', quest=quest)


@print_bp.route('/monstros/<quest_id>')
def monster_cards(quest_id):
    """Fichas de monstros imprimíveis."""
    loader = QuestLoader()
    quest = loader.get_quest(quest_id)
    if not quest:
        abort(404)
    return render_template('print/monster_cards.html', quest=quest)


@print_bp.route('/personagens-prontos')
def premade_sheets():
    """Todas as fichas de personagens pré-criados para impressão."""
    characters = load_characters()
    return render_template('print/premade_sheets.html', characters=characters)


@print_bp.route('/personagem/<char_id>')
def premade_sheet(char_id):
    """Ficha de um personagem pré-criado para impressão."""
    characters = load_characters()
    character = next((c for c in characters if c['id'] == char_id), None)
    if not character:
        abort(404)
    return render_template('print/premade_sheet.html', character=character)
