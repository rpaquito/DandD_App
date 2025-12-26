"""Rotas do sistema de combate - SESSION-BASED ONLY."""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from app.models.combat import CONDICOES_5E
from app.services.session_service import SessionService
from app.services.combat_roll_service import CombatRollService
from app.services.combat_log_service import CombatLogService
from app import db

combat_bp = Blueprint('combat', __name__)
session_service = SessionService()
roll_service = CombatRollService()
log_service = CombatLogService()


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


@combat_bp.route('/sessao/<int:session_id>/atacar', methods=['POST'])
def roll_attack_route(session_id):
    """Realizar um attack roll e registar no log."""
    game_session = session_service.get_session(session_id)
    if not game_session:
        return jsonify({'erro': 'Sessao nao encontrada'}), 404

    data = request.get_json()
    combat = session_service.get_session_combat(session_id)

    # Roll attack
    attack_result = roll_service.roll_attack(
        bonus=data.get('bonus', 0),
        target_ac=data.get('target_ac', 10),
        advantage=data.get('advantage', False),
        disadvantage=data.get('disadvantage', False)
    )

    # Add metadata to result
    attack_result['actor_id'] = data.get('actor_id')
    attack_result['actor_nome'] = data.get('actor_nome')
    attack_result['target_id'] = data.get('target_id')
    attack_result['target_nome'] = data.get('target_nome')

    # Log the attack
    log_service.log_attack(
        session_id=session_id,
        actor_id=data.get('actor_id'),
        actor_nome=data.get('actor_nome'),
        target_id=data.get('target_id'),
        target_nome=data.get('target_nome'),
        attack_result=attack_result,
        ronda=combat.ronda_atual if combat else 1,
        turno=combat.turno_atual if combat else 1,
        combat_id=combat.id if combat else None
    )

    return jsonify(attack_result)


@combat_bp.route('/sessao/<int:session_id>/dano', methods=['POST'])
def roll_damage_route(session_id):
    """Realizar um damage roll, aplicar ao HP, e registar no log."""
    game_session = session_service.get_session(session_id)
    if not game_session:
        return jsonify({'erro': 'Sessao nao encontrada'}), 404

    data = request.get_json()
    combat = session_service.get_session_combat(session_id)

    # Roll damage
    damage_result = roll_service.roll_damage(
        dice_expression=data.get('dice_expression', '1d6'),
        damage_type=data.get('damage_type', 'slashing'),
        crit=data.get('crit', False),
        resistance=data.get('resistance', False),
        immunity=data.get('immunity', False),
        vulnerability=data.get('vulnerability', False)
    )

    # Apply damage to target HP
    target_id = data.get('target_id')
    if target_id and combat:
        participants = combat.get_participantes()
        for p in participants:
            if p.get('id') == target_id:
                p['hp_atual'] = max(0, p['hp_atual'] - damage_result['final_damage'])

                # Check for death
                if p['hp_atual'] == 0:
                    log_service.log_death(
                        session_id=session_id,
                        actor_id=target_id,
                        actor_nome=p.get('nome', 'Desconhecido'),
                        ronda=combat.ronda_atual,
                        turno=combat.turno_atual,
                        combat_id=combat.id
                    )
                break

        combat.set_participantes(participants)
        db.session.commit()

    # Log the damage
    log_service.log_damage(
        session_id=session_id,
        actor_id=data.get('actor_id'),
        actor_nome=data.get('actor_nome'),
        target_id=target_id,
        target_nome=data.get('target_nome'),
        damage_result=damage_result,
        ronda=combat.ronda_atual if combat else 1,
        turno=combat.turno_atual if combat else 1,
        combat_id=combat.id if combat else None
    )

    # Return updated participant info
    damage_result['target_hp_atual'] = next(
        (p['hp_atual'] for p in combat.get_participantes() if p.get('id') == target_id),
        None
    ) if combat else None

    return jsonify(damage_result)


@combat_bp.route('/sessao/<int:session_id>/magia', methods=['POST'])
def cast_spell_route(session_id):
    """Lancar magia, usar spell slot, e registar no log."""
    game_session = session_service.get_session(session_id)
    if not game_session:
        return jsonify({'erro': 'Sessao nao encontrada'}), 404

    data = request.get_json()
    combat = session_service.get_session_combat(session_id)

    if not combat:
        return jsonify({'erro': 'Combate nao encontrado'}), 404

    participant_id = data.get('participant_id')
    spell_level = data.get('spell_level', 0)

    # Use spell slot (if not cantrip)
    slot_used = True
    if spell_level > 0:
        slot_used = combat.use_spell_slot(participant_id, spell_level)
        if not slot_used:
            return jsonify({'erro': 'Nenhum spell slot disponivel'}), 400
        db.session.commit()

    # Log the spell
    log_service.log_spell(
        session_id=session_id,
        actor_id=data.get('actor_id'),
        actor_nome=data.get('actor_nome'),
        spell_name=data.get('spell_name', 'Magia'),
        spell_level=spell_level,
        target_id=data.get('target_id'),
        target_nome=data.get('target_nome'),
        ronda=combat.ronda_atual,
        turno=combat.turno_atual,
        combat_id=combat.id
    )

    return jsonify({
        'success': True,
        'spell_slots': combat.get_spell_slots().get(participant_id, {})
    })


@combat_bp.route('/sessao/<int:session_id>/log', methods=['GET'])
def get_combat_log_route(session_id):
    """Obter combat log."""
    game_session = session_service.get_session(session_id)
    if not game_session:
        return jsonify({'erro': 'Sessao nao encontrada'}), 404

    limit = request.args.get('limit', 50, type=int)
    combat_id = request.args.get('combat_id', type=int)

    logs = log_service.get_combat_logs(
        session_id=session_id,
        limit=limit,
        combat_id=combat_id
    )

    return jsonify({
        'logs': [
            {
                'id': log.id,
                'timestamp': log.timestamp.isoformat(),
                'ronda': log.ronda,
                'turno': log.turno,
                'actor_nome': log.actor_nome,
                'action_type': log.action_type,
                'message': log.message,
                'target_nome': log.target_nome
            }
            for log in logs
        ]
    })


@combat_bp.route('/sessao/<int:session_id>/log/limpar', methods=['POST'])
def clear_combat_log_route(session_id):
    """Limpar combat log."""
    game_session = session_service.get_session(session_id)
    if not game_session:
        return jsonify({'erro': 'Sessao nao encontrada'}), 404

    combat_id = request.get_json().get('combat_id') if request.is_json else None
    count = log_service.clear_combat_logs(session_id, combat_id)

    return jsonify({'success': True, 'deleted': count})


@combat_bp.route('/sessao/<int:session_id>/action-economy', methods=['POST'])
def use_action_route(session_id):
    """Marcar uma acao como usada."""
    game_session = session_service.get_session(session_id)
    if not game_session:
        return jsonify({'erro': 'Sessao nao encontrada'}), 404

    data = request.get_json()
    combat = session_service.get_session_combat(session_id)

    if not combat:
        return jsonify({'erro': 'Combate nao encontrado'}), 404

    participant_id = data.get('participant_id')
    action_type = data.get('action_type')  # 'action', 'bonus_action', 'reaction', 'movement'

    combat.use_action(participant_id, action_type)
    db.session.commit()

    return jsonify({
        'success': True,
        'action_economy': combat.get_action_economy().get(participant_id, {})
    })


@combat_bp.route('/sessao/<int:session_id>/action-economy/reset', methods=['POST'])
def reset_action_economy_route(session_id):
    """Resetar action economy para um participante."""
    game_session = session_service.get_session(session_id)
    if not game_session:
        return jsonify({'erro': 'Sessao nao encontrada'}), 404

    data = request.get_json()
    combat = session_service.get_session_combat(session_id)

    if not combat:
        return jsonify({'erro': 'Combate nao encontrado'}), 404

    participant_id = data.get('participant_id')
    combat.reset_action_economy_for_participant(participant_id)
    db.session.commit()

    return jsonify({
        'success': True,
        'action_economy': combat.get_action_economy().get(participant_id, {})
    })
