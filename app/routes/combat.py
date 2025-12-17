"""Rotas do sistema de combate."""

from flask import Blueprint, render_template, request, jsonify, session
from app.models.combat import CONDICOES_5E

combat_bp = Blueprint('combat', __name__)


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
