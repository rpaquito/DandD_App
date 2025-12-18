"""Rotas de gestao de aventuras."""

from flask import Blueprint, render_template, abort, session, redirect, url_for, request, jsonify, flash
from app.services.quest_loader import QuestLoader
from app.services.session_service import SessionService, load_character_templates, get_saved_characters

quest_bp = Blueprint('quest', __name__)
session_service = SessionService()


@quest_bp.route('/')
def list_quests():
    """Lista todas as aventuras disponiveis com informacao de sessoes."""
    loader = QuestLoader()
    quests = loader.get_all_quests()

    # Adicionar informacao de sessoes a cada aventura
    quests_data = []
    for quest in quests:
        quest_info = {
            'quest': quest,
            'sessions': session_service.get_sessions_for_quest(quest.id),
            'session_count': session_service.count_sessions_for_quest(quest.id),
            'can_create': session_service.can_create_session_for_quest(quest.id)
        }
        quests_data.append(quest_info)

    return render_template('quest/list.html', quests_data=quests_data)


@quest_bp.route('/<quest_id>/iniciar')
def start_quest(quest_id):
    """Pagina para iniciar ou continuar uma aventura."""
    loader = QuestLoader()
    quest = loader.get_quest(quest_id)
    if not quest:
        abort(404)

    sessions = session_service.get_sessions_for_quest(quest_id)
    can_create = session_service.can_create_session_for_quest(quest_id)

    return render_template('quest/start.html',
                           quest=quest,
                           sessions=sessions,
                           can_create=can_create)


@quest_bp.route('/<quest_id>/nova-sessao', methods=['POST'])
def create_quest_session(quest_id):
    """Criar nova sessao para uma aventura."""
    loader = QuestLoader()
    quest = loader.get_quest(quest_id)
    if not quest:
        flash('Aventura nao encontrada.', 'danger')
        return redirect(url_for('quest.list_quests'))

    if not session_service.can_create_session_for_quest(quest_id):
        flash('Ja existem 3 sessoes para esta aventura. Apaga uma para criar outra.', 'warning')
        return redirect(url_for('quest.start_quest', quest_id=quest_id))

    new_session = session_service.create_quest_session(quest_id, quest.titulo)
    if new_session:
        flash(f'Sessao criada! Agora escolhe os personagens.', 'success')
        return redirect(url_for('quest.select_characters',
                                quest_id=quest_id,
                                session_id=new_session.id))

    flash('Erro ao criar sessao.', 'danger')
    return redirect(url_for('quest.start_quest', quest_id=quest_id))


@quest_bp.route('/<quest_id>/sessao/<int:session_id>/apagar', methods=['POST'])
def delete_quest_session(quest_id, session_id):
    """Apagar uma sessao de aventura."""
    if session_service.delete_session(session_id):
        flash('Sessao apagada.', 'info')
    else:
        flash('Erro ao apagar sessao.', 'danger')

    return redirect(url_for('quest.start_quest', quest_id=quest_id))


@quest_bp.route('/<quest_id>/sessao/<int:session_id>/escolher')
def select_characters(quest_id, session_id):
    """Pagina para escolher personagens para a sessao."""
    loader = QuestLoader()
    quest = loader.get_quest(quest_id)
    if not quest:
        abort(404)

    game_session = session_service.get_session(session_id)
    if not game_session:
        flash('Sessao nao encontrada.', 'danger')
        return redirect(url_for('quest.start_quest', quest_id=quest_id))

    players = session_service.get_session_players(session_id)
    templates = load_character_templates()
    saved_characters = get_saved_characters()

    return render_template('quest/select_characters.html',
                           quest=quest,
                           game_session=game_session,
                           players=players,
                           templates=templates,
                           saved_characters=saved_characters)


@quest_bp.route('/<quest_id>/sessao/<int:session_id>/adicionar-jogador', methods=['POST'])
def add_session_player(quest_id, session_id):
    """Adicionar jogador a sessao."""
    nome_jogador = request.form.get('nome_jogador', 'Jogador')
    template_id = request.form.get('template_id')
    saved_id = request.form.get('saved_id')

    if template_id:
        templates = load_character_templates()
        template = next((t for t in templates if t['id'] == template_id), None)
        if template:
            session_service.add_player_from_template(session_id, template, nome_jogador)
    elif saved_id:
        try:
            session_service.add_player_from_saved(session_id, int(saved_id), nome_jogador)
        except ValueError:
            pass

    return redirect(url_for('quest.select_characters',
                            quest_id=quest_id,
                            session_id=session_id))


@quest_bp.route('/<quest_id>/sessao/<int:session_id>/remover-jogador/<int:player_id>', methods=['POST'])
def remove_session_player(quest_id, session_id, player_id):
    """Remover jogador da sessao."""
    session_service.remove_player(player_id)
    return redirect(url_for('quest.select_characters',
                            quest_id=quest_id,
                            session_id=session_id))


@quest_bp.route('/<quest_id>/sessao/<int:session_id>/confirmar', methods=['POST'])
def confirm_and_start(quest_id, session_id):
    """Confirmar party e iniciar a aventura."""
    game_session = session_service.get_session(session_id)
    if not game_session:
        flash('Sessao nao encontrada.', 'danger')
        return redirect(url_for('quest.list_quests'))

    players = session_service.get_session_players(session_id)
    if not players:
        flash('Adiciona pelo menos um jogador antes de comecar!', 'warning')
        return redirect(url_for('quest.select_characters',
                                quest_id=quest_id,
                                session_id=session_id))

    # Guardar sessao activa
    session['active_session_id'] = session_id

    # Ir para o passo atual da aventura
    return redirect(url_for('quest.step',
                            quest_id=quest_id,
                            step_id=game_session.passo_atual,
                            session_id=session_id))


@quest_bp.route('/<quest_id>')
def overview(quest_id):
    """Visão geral de uma aventura."""
    loader = QuestLoader()
    quest = loader.get_quest(quest_id)
    if not quest:
        abort(404)

    # Verificar se ha uma sessao activa
    game_session = None
    players = []
    session_id = request.args.get('session_id', type=int)
    if session_id:
        game_session = session_service.get_session(session_id)
        if game_session:
            players = session_service.get_session_players(session_id)

    return render_template('quest/overview.html',
                           quest=quest,
                           game_session=game_session,
                           players=players)


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

    # Verificar sessao activa
    game_session = None
    players = []
    session_id = request.args.get('session_id', type=int)

    if session_id:
        game_session = session_service.get_session(session_id)
        if game_session:
            players = session_service.get_session_players(session_id)
            # Guardar progresso na base de dados
            session_service.update_progress(session_id, step_id)

    # Guardar progresso na sessao Flask (fallback)
    session[f'quest_{quest_id}_step'] = step_id

    return render_template(
        'quest/step.html',
        quest=quest,
        step=current_step,
        step_id=step_id,
        game_session=game_session,
        players=players
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


@quest_bp.route('/<quest_id>/passo/<int:step_id>/iniciar-combate', methods=['POST'])
def start_step_combat(quest_id, step_id):
    """Preparar combate - redirecionar para pagina de iniciativa."""
    session_id = request.form.get('session_id', type=int)
    if not session_id:
        flash('Sessao nao especificada.', 'danger')
        return redirect(url_for('quest.step', quest_id=quest_id, step_id=step_id))

    # Redirecionar para pagina de iniciativa
    return redirect(url_for('quest.setup_initiative',
                            quest_id=quest_id,
                            step_id=step_id,
                            session_id=session_id))


@quest_bp.route('/<quest_id>/passo/<int:step_id>/iniciativa')
def setup_initiative(quest_id, step_id):
    """Pagina para definir iniciativa antes de comecar combate."""
    session_id = request.args.get('session_id', type=int)
    if not session_id:
        flash('Sessao nao especificada.', 'danger')
        return redirect(url_for('quest.step', quest_id=quest_id, step_id=step_id))

    game_session = session_service.get_session(session_id)
    if not game_session:
        flash('Sessao nao encontrada.', 'danger')
        return redirect(url_for('quest.list_quests'))

    loader = QuestLoader()
    quest = loader.get_quest(quest_id)
    if not quest:
        flash('Aventura nao encontrada.', 'danger')
        return redirect(url_for('quest.list_quests'))

    current_step = quest.get_step(step_id)
    if not current_step:
        flash('Passo nao encontrado.', 'danger')
        return redirect(url_for('quest.step', quest_id=quest_id, step_id=step_id))

    # Construir lista de participantes
    participants = []

    # Adicionar jogadores da sessao
    players = session_service.get_session_players(session_id)
    for player in players:
        char_data = player.get_character_data()
        participants.append({
            'id': f'player_{player.id}',
            'nome': char_data.get('nome', player.nome_jogador),
            'tipo': 'jogador',
            'hp_max': player.hp_max,
            'hp_atual': player.hp_atual,
            'ac': char_data.get('ac', 10),
            'destreza_mod': char_data.get('destreza_mod', 0)
        })

    # Adicionar monstros do passo
    monstros = quest.get_monsters_for_step(current_step)
    for i, monster in enumerate(monstros):
        participants.append({
            'id': f'monster_{monster.id}_{i}',
            'nome': monster.nome,
            'tipo': 'monstro',
            'hp_max': monster.hp_max,
            'hp_atual': monster.hp_max,
            'ac': monster.ac,
            'destreza_mod': getattr(monster, 'destreza_mod', 0)
        })

    return render_template('quest/initiative.html',
                           quest=quest,
                           step=current_step,
                           game_session=game_session,
                           participants=participants)


@quest_bp.route('/<quest_id>/passo/<int:step_id>/confirmar-combate', methods=['POST'])
def confirm_combat(quest_id, step_id):
    """Iniciar combate com valores de iniciativa definidos."""
    session_id = request.form.get('session_id', type=int)
    if not session_id:
        flash('Sessao nao especificada.', 'danger')
        return redirect(url_for('quest.step', quest_id=quest_id, step_id=step_id))

    # Recolher iniciativas do formulario
    participants = []
    i = 0
    while f'participant_{i}_id' in request.form:
        participant = {
            'id': request.form.get(f'participant_{i}_id'),
            'nome': request.form.get(f'participant_{i}_nome'),
            'tipo': request.form.get(f'participant_{i}_tipo'),
            'hp_max': int(request.form.get(f'participant_{i}_hp_max', 10)),
            'hp_atual': int(request.form.get(f'participant_{i}_hp_atual', 10)),
            'ac': int(request.form.get(f'participant_{i}_ac', 10)),
            'iniciativa': int(request.form.get(f'participant_{i}_iniciativa', 0)),
            'condicoes': []
        }
        participants.append(participant)
        i += 1

    # Iniciar combate na sessao
    combat = session_service.start_combat(session_id, participants, quest_step_id=step_id)

    flash('Combate iniciado!', 'success')
    return redirect(url_for('combat.session_tracker', session_id=session_id))
