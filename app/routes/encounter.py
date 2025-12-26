"""
Rotas para o Gerador de Encontros
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, session
from app.services.encounter_generator import EncounterGeneratorService
from app.services.quest_loader import QuestLoader
from app.services.session_service import SessionService
from app.models.session import GameSession

encounter_bp = Blueprint('encounter', __name__, url_prefix='/gerador-encontros')

# Serviços
encounter_service = EncounterGeneratorService()
quest_loader = QuestLoader()
session_service = SessionService()


@encounter_bp.route('/')
def generator_page():
    """Página do gerador de encontros."""
    # Carregar todas as quests para obter pool de monstros
    quests = quest_loader.get_all_quests()

    # Obter sessão activa se existir
    active_session_id = session.get('active_session_id')
    game_session = None
    if active_session_id:
        game_session = session_service.get_session(active_session_id)

    return render_template(
        'encounter/generator.html',
        quests=quests,
        game_session=game_session
    )


@encounter_bp.route('/gerar', methods=['POST'])
def generate_encounter():
    """Gera um encontro balanceado."""
    try:
        data = request.get_json()

        # Validar dados de entrada
        party_size = data.get('party_size', 4)
        party_levels = data.get('party_levels', [1] * party_size)
        difficulty = data.get('difficulty', 'medium')
        quest_id = data.get('quest_id')  # Opcional
        max_monsters = data.get('max_monsters', 10)
        min_monsters = data.get('min_monsters', 1)

        # Validações
        if not isinstance(party_levels, list) or not party_levels:
            return jsonify({'error': 'Níveis do grupo inválidos'}), 400

        if difficulty not in ['easy', 'medium', 'hard', 'deadly']:
            return jsonify({'error': 'Dificuldade inválida'}), 400

        # Obter pool de monstros
        monster_pool = []

        if quest_id and quest_id != 'all':
            # Monstros de uma quest específica
            quest = quest_loader.get_quest(quest_id)
            if quest and hasattr(quest, 'monstros') and quest.monstros:
                # monstros é um dict {id: Monster}, pegar os valores
                monster_pool = [m.__dict__ if hasattr(m, '__dict__') else m for m in quest.monstros.values()]
        else:
            # Todos os monstros de todas as quests
            quests = quest_loader.get_all_quests()
            seen_ids = set()
            for q in quests:
                if hasattr(q, 'monstros') and q.monstros:
                    # monstros é um dict {id: Monster}
                    for monster_id, monster in q.monstros.items():
                        # Evitar duplicados
                        if monster_id not in seen_ids:
                            # Converter Monster object para dict
                            monster_dict = monster.__dict__ if hasattr(monster, '__dict__') else monster
                            monster_pool.append(monster_dict)
                            seen_ids.add(monster_id)

        if not monster_pool:
            return jsonify({'error': 'Nenhum monstro disponível no pool selecionado'}), 400

        # Gerar encontro
        encounter = encounter_service.generate_encounter(
            party_levels=party_levels,
            difficulty=difficulty,
            monster_pool=monster_pool,
            max_monsters=max_monsters,
            min_monsters=min_monsters
        )

        # Adicionar dificuldade real calculada
        encounter['actual_difficulty'] = encounter_service.get_difficulty_from_xp(
            party_levels,
            encounter['adjusted_xp']
        )

        return jsonify(encounter)

    except Exception as e:
        return jsonify({'error': f'Erro ao gerar encontro: {str(e)}'}), 500


@encounter_bp.route('/adicionar-combate', methods=['POST'])
def add_to_combat():
    """Adiciona o encontro gerado ao combat tracker de uma sessão."""
    try:
        data = request.get_json()

        session_id = data.get('session_id')
        monsters = data.get('monsters', [])

        if not session_id:
            return jsonify({'error': 'Session ID não fornecido'}), 400

        if not monsters:
            return jsonify({'error': 'Nenhum monstro para adicionar'}), 400

        # Verificar se sessão existe
        game_session = session_service.get_session(session_id)
        if not game_session:
            return jsonify({'error': 'Sessão não encontrada'}), 404

        # Obter ou criar combate
        combat = game_session.combate
        if not combat:
            from app.models.session import SessionCombat
            from app import db
            combat = SessionCombat(session_id=session_id)
            db.session.add(combat)
            db.session.commit()

        # Adicionar monstros ao combate
        participantes = combat.get_participantes()

        for monster_data in monsters:
            quantity = monster_data.get('quantity', 1)
            for i in range(quantity):
                # Gerar ID único para cada instância
                base_id = monster_data.get('id', 'monster')
                unique_id = f"{base_id}_{len(participantes) + 1}"

                participante = {
                    'id': unique_id,
                    'nome': f"{monster_data.get('nome', 'Monstro')} {i + 1}" if quantity > 1 else monster_data.get('nome', 'Monstro'),
                    'tipo': 'monstro',
                    'hp_atual': monster_data.get('hp_max', 10),
                    'hp_max': monster_data.get('hp_max', 10),
                    'ac': monster_data.get('ac', 10),
                    'iniciativa': 10,  # Placeholder
                    'xp': monster_data.get('xp', 0)
                }
                participantes.append(participante)

        combat.set_participantes(participantes)
        combat.activo = True

        from app import db
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'{sum(m.get("quantity", 1) for m in monsters)} monstro(s) adicionado(s) ao combate!',
            'num_added': sum(m.get('quantity', 1) for m in monsters)
        })

    except Exception as e:
        return jsonify({'error': f'Erro ao adicionar ao combate: {str(e)}'}), 500


@encounter_bp.route('/calcular-budget', methods=['POST'])
def calculate_budget():
    """Calcula o XP budget para um grupo e dificuldade."""
    try:
        data = request.get_json()

        party_levels = data.get('party_levels', [1])
        difficulty = data.get('difficulty', 'medium')

        xp_budget = encounter_service.calculate_xp_budget(party_levels, difficulty)

        return jsonify({
            'xp_budget': xp_budget,
            'party_size': len(party_levels),
            'difficulty': difficulty
        })

    except Exception as e:
        return jsonify({'error': f'Erro ao calcular budget: {str(e)}'}), 500
