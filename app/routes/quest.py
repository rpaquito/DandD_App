"""Rotas de gestão de aventuras."""

from flask import Blueprint, render_template, abort, session, redirect, url_for
from app.services.quest_loader import QuestLoader

quest_bp = Blueprint('quest', __name__)


@quest_bp.route('/<quest_id>')
def overview(quest_id):
    """Visão geral de uma aventura."""
    loader = QuestLoader()
    quest = loader.get_quest(quest_id)
    if not quest:
        abort(404)
    return render_template('quest/overview.html', quest=quest)


@quest_bp.route('/<quest_id>/passo/<int:step_id>')
def step(quest_id, step_id):
    """Visualizar um passo específico da aventura."""
    loader = QuestLoader()
    quest = loader.get_quest(quest_id)
    if not quest:
        abort(404)

    current_step = quest.get_step(step_id)
    if not current_step:
        abort(404)

    # Guardar progresso na sessão
    session[f'quest_{quest_id}_step'] = step_id

    return render_template(
        'quest/step.html',
        quest=quest,
        step=current_step,
        step_id=step_id
    )


@quest_bp.route('/<quest_id>/npcs')
def npcs(quest_id):
    """Lista de NPCs da aventura."""
    loader = QuestLoader()
    quest = loader.get_quest(quest_id)
    if not quest:
        abort(404)
    return render_template('quest/npcs.html', quest=quest)


@quest_bp.route('/<quest_id>/monstros')
def monsters(quest_id):
    """Lista de monstros da aventura."""
    loader = QuestLoader()
    quest = loader.get_quest(quest_id)
    if not quest:
        abort(404)
    return render_template('quest/monsters.html', quest=quest)
