"""Rotas do sistema de combate - SESSION-BASED ONLY."""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app.models.combat import CONDICOES_5E
from app.services.session_service import SessionService
from app import db

combat_bp = Blueprint('combat', __name__)
session_service = SessionService()


@combat_bp.route('/sessao/<int:session_id>')
def session_tracker(session_id):
    """Rastreador de combate para uma sessao especifica."""
    from app.services.quest_loader import QuestLoader

    game_session = session_service.get_session(session_id)
    if not game_session:
        return redirect(url_for('combat.tracker'))

    combat = session_service.get_session_combat(session_id)
    participants = combat.get_participantes() if combat and combat.activo else []

    # Carregar quest e step atual para o mapa tatico
    quest = None
    current_step = None
    if game_session.quest_id:
        quest_loader = QuestLoader()
        quest = quest_loader.get_quest(game_session.quest_id)
        if quest and combat and combat.quest_step_id:
            current_step = quest.get_step(combat.quest_step_id)

    return render_template(
        'combat/tracker.html',
        conditions=CONDICOES_5E,
        game_session=game_session,
        session_combat=combat,
        initial_participants=participants,
        quest=quest,
        current_step=current_step
    )


@combat_bp.route('/sessao/<int:session_id>/atualizar', methods=['POST'])
def update_session_combat(session_id):
    """Atualizar estado de combate de uma sessao."""
    game_session = session_service.get_session(session_id)
    if not game_session:
        return jsonify({'erro': 'Sessao nao encontrada'}), 404

    data = request.get_json()
    combat = session_service.get_session_combat(session_id)

    if combat:
        participants = data.get('participants', [])
        combat.set_participantes(participants)
        combat.ronda_atual = data.get('ronda', combat.ronda_atual)
        combat.turno_atual = data.get('turno', combat.turno_atual)
        db.session.commit()

    return jsonify({'success': True})


@combat_bp.route('/sessao/<int:session_id>/terminar', methods=['POST'])
def end_session_combat(session_id):
    """Terminar combate e sincronizar estado dos jogadores."""
    game_session = session_service.get_session(session_id)
    if not game_session:
        return jsonify({'erro': 'Sessao nao encontrada'}), 404

    combat = session_service.end_combat(session_id)

    return redirect(url_for('session.dashboard', session_id=session_id))
