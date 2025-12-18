"""Rotas do sistema de combate."""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from app.models.combat import CONDICOES_5E
from app.services.session_service import SessionService

combat_bp = Blueprint('combat', __name__)
session_service = SessionService()


@combat_bp.route('/')
def tracker():
    """Rastreador de combate principal."""
    return render_template('combat/tracker.html', conditions=CONDICOES_5E)


@combat_bp.route('/iniciativa', methods=['POST'])
def add_to_initiative():
    """Adicionar participante à iniciativa."""
    data = request.get_json()

    if 'combat_initiative' not in session:
        session['combat_initiative'] = []

    participant = {
        'id': len(session['combat_initiative']) + 1,
        'nome': data.get('nome', 'Desconhecido'),
        'iniciativa': data.get('iniciativa', 0),
        'hp_atual': data.get('hp_max', 10),
        'hp_max': data.get('hp_max', 10),
        'ac': data.get('ac', 10),
        'tipo': data.get('tipo', 'monstro'),  # jogador, monstro, npc
        'condicoes': []
    }

    initiative = session['combat_initiative']
    initiative.append(participant)
    # Ordenar por iniciativa (maior primeiro)
    initiative.sort(key=lambda x: x['iniciativa'], reverse=True)
    session['combat_initiative'] = initiative
    session.modified = True

    return jsonify({'success': True, 'participants': initiative})


@combat_bp.route('/iniciativa', methods=['GET'])
def get_initiative():
    """Obter lista de iniciativa atual."""
    initiative = session.get('combat_initiative', [])
    return jsonify({'participants': initiative})


@combat_bp.route('/iniciativa/limpar', methods=['POST'])
def clear_initiative():
    """Limpar a lista de iniciativa."""
    session['combat_initiative'] = []
    session.modified = True
    return jsonify({'success': True})


@combat_bp.route('/dano', methods=['POST'])
def apply_damage():
    """Aplicar dano ou cura a um participante."""
    data = request.get_json()
    participant_id = data.get('id')
    amount = data.get('amount', 0)
    is_healing = data.get('healing', False)

    initiative = session.get('combat_initiative', [])

    for p in initiative:
        if p['id'] == participant_id:
            if is_healing:
                p['hp_atual'] = min(p['hp_atual'] + amount, p['hp_max'])
            else:
                p['hp_atual'] = max(p['hp_atual'] - amount, 0)
            break

    session['combat_initiative'] = initiative
    session.modified = True

    return jsonify({'success': True, 'participants': initiative})


@combat_bp.route('/condicao', methods=['POST'])
def toggle_condition():
    """Adicionar ou remover condição de um participante."""
    data = request.get_json()
    participant_id = data.get('id')
    condition = data.get('condition')

    initiative = session.get('combat_initiative', [])

    for p in initiative:
        if p['id'] == participant_id:
            if condition in p['condicoes']:
                p['condicoes'].remove(condition)
            else:
                p['condicoes'].append(condition)
            break

    session['combat_initiative'] = initiative
    session.modified = True

    return jsonify({'success': True, 'participants': initiative})


@combat_bp.route('/remover', methods=['POST'])
def remove_participant():
    """Remover participante do combate."""
    data = request.get_json()
    participant_id = data.get('id')

    initiative = session.get('combat_initiative', [])
    initiative = [p for p in initiative if p['id'] != participant_id]
    session['combat_initiative'] = initiative
    session.modified = True

    return jsonify({'success': True, 'participants': initiative})


@combat_bp.route('/sessao/<int:session_id>')
def session_tracker(session_id):
    """Rastreador de combate para uma sessao especifica."""
    game_session = session_service.get_session(session_id)
    if not game_session:
        return redirect(url_for('combat.tracker'))

    combat = session_service.get_session_combat(session_id)
    participants = combat.get_participantes() if combat and combat.activo else []

    return render_template(
        'combat/tracker.html',
        conditions=CONDICOES_5E,
        game_session=game_session,
        session_combat=combat,
        initial_participants=participants
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
        from app import db
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
