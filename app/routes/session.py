"""Rotas para gestao de sessoes de jogo."""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app import db
from app.services.session_service import SessionService, load_character_templates, get_saved_characters
from app.services.quest_loader import QuestLoader
from app.services.time_service import TimeTrackingService

session_bp = Blueprint('session', __name__, url_prefix='/sessao')
session_service = SessionService()
quest_loader = QuestLoader()
time_service = TimeTrackingService()


@session_bp.route('/')
def list_sessions():
    """Lista todas as sessoes."""
    sessions = session_service.get_all_sessions()

    # Adicionar informacao da quest a cada sessao
    sessions_data = []
    for s in sessions:
        session_dict = s.to_dict()
        if s.quest_id:
            quest = quest_loader.get_quest(s.quest_id)
            session_dict['quest'] = quest
        else:
            session_dict['quest'] = None
        sessions_data.append(session_dict)

    return render_template('session/list.html', sessions=sessions_data)


@session_bp.route('/nova', methods=['GET', 'POST'])
def create_session():
    """Criar uma nova sessao."""
    quests = quest_loader.get_all_quests()

    if request.method == 'POST':
        nome = request.form.get('nome', 'Nova Sessao')
        quest_id = request.form.get('quest_id')

        if not nome.strip():
            flash('O nome da sessao e obrigatorio.', 'danger')
            return render_template('session/create.html', quests=quests)

        new_session = session_service.create_session(
            nome=nome.strip(),
            quest_id=quest_id if quest_id else None
        )

        # Guardar sessao activa na sessao Flask
        session['active_session_id'] = new_session.id

        flash(f'Sessao "{nome}" criada com sucesso!', 'success')
        return redirect(url_for('session.dashboard', session_id=new_session.id))

    return render_template('session/create.html', quests=quests)


@session_bp.route('/<int:session_id>')
def dashboard(session_id):
    """Pagina principal da sessao (dashboard)."""
    game_session = session_service.get_session(session_id)
    if not game_session:
        flash('Sessao nao encontrada.', 'danger')
        return redirect(url_for('session.list_sessions'))

    # Marcar como sessao activa
    session['active_session_id'] = session_id

    # Carregar dados relacionados
    quest = None
    current_step = None
    if game_session.quest_id:
        quest = quest_loader.get_quest(game_session.quest_id)
        if quest:
            current_step = quest.get_step(game_session.passo_atual)

    players = session_service.get_session_players(session_id)
    combat = session_service.get_session_combat(session_id)

    # Templates para adicionar jogadores
    templates = load_character_templates()
    saved_characters = get_saved_characters()

    return render_template(
        'session/dashboard.html',
        game_session=game_session,
        quest=quest,
        current_step=current_step,
        players=players,
        combat=combat,
        templates=templates,
        saved_characters=saved_characters
    )


@session_bp.route('/<int:session_id>/aventura', methods=['POST'])
def set_quest(session_id):
    """Definir a aventura de uma sessao."""
    game_session = session_service.get_session(session_id)
    if not game_session:
        flash('Sessao nao encontrada.', 'danger')
        return redirect(url_for('session.list_sessions'))

    quest_id = request.form.get('quest_id')
    if quest_id:
        quest = quest_loader.get_quest(quest_id)
        if quest:
            session_service.set_quest(session_id, quest_id)
            flash(f'Aventura "{quest.titulo}" selecionada!', 'success')
        else:
            flash('Aventura nao encontrada.', 'danger')

    return redirect(url_for('session.dashboard', session_id=session_id))


@session_bp.route('/<int:session_id>/jogador', methods=['POST'])
def add_player(session_id):
    """Adicionar jogador a uma sessao."""
    game_session = session_service.get_session(session_id)
    if not game_session:
        flash('Sessao nao encontrada.', 'danger')
        return redirect(url_for('session.list_sessions'))

    nome_jogador = request.form.get('nome_jogador', 'Jogador')
    template_id = request.form.get('template_id')
    saved_id = request.form.get('saved_id')

    if template_id:
        # Adicionar a partir de template
        templates = load_character_templates()
        template = next((t for t in templates if t['id'] == template_id), None)
        if template:
            player = session_service.add_player_from_template(
                session_id, template, nome_jogador
            )
            if player:
                char_data = player.get_character_data()
                flash(f'{nome_jogador} junta-se com {char_data.get("nome", "personagem")}!', 'success')
    elif saved_id:
        # Adicionar a partir de personagem guardado
        try:
            player = session_service.add_player_from_saved(
                session_id, int(saved_id), nome_jogador
            )
            if player:
                char_data = player.get_character_data()
                flash(f'{nome_jogador} junta-se com {char_data.get("nome", "personagem")}!', 'success')
        except ValueError:
            flash('Personagem guardado invalido.', 'danger')
    else:
        # Criar personagem basico (para ser expandido com o character builder)
        character_data = {
            'nome': request.form.get('nome_personagem', 'Aventureiro'),
            'classe': request.form.get('classe', 'Guerreiro'),
            'nivel': int(request.form.get('nivel', 1)),
            'raca': request.form.get('raca', 'Humano'),
            'hp_max': int(request.form.get('hp_max', 10)),
            'ac': int(request.form.get('ac', 10)),
            'forca': 10,
            'destreza': 10,
            'constituicao': 10,
            'inteligencia': 10,
            'sabedoria': 10,
            'carisma': 10
        }
        player = session_service.add_custom_player(
            session_id, nome_jogador, character_data
        )
        if player:
            flash(f'{nome_jogador} junta-se a aventura!', 'success')

    return redirect(url_for('session.dashboard', session_id=session_id))


@session_bp.route('/<int:session_id>/jogador/<int:player_id>/remover', methods=['POST'])
def remove_player(session_id, player_id):
    """Remover jogador de uma sessao."""
    if session_service.remove_player(player_id):
        flash('Jogador removido da sessao.', 'info')
    else:
        flash('Erro ao remover jogador.', 'danger')

    return redirect(url_for('session.dashboard', session_id=session_id))


@session_bp.route('/<int:session_id>/jogador/<int:player_id>/hp', methods=['POST'])
def update_player_hp(session_id, player_id):
    """Atualizar HP de um jogador."""
    action = request.form.get('action')
    amount = int(request.form.get('amount', 1))

    if action == 'damage':
        session_service.update_player_hp(player_id, amount, is_damage=True)
    elif action == 'heal':
        session_service.update_player_hp(player_id, amount, is_damage=False)

    # Se for AJAX, retornar JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        player = session_service.get_player(player_id)
        if player:
            return jsonify(player.to_dict())
        return jsonify({'error': 'Jogador nao encontrado'}), 404

    return redirect(url_for('session.dashboard', session_id=session_id))


@session_bp.route('/<int:session_id>/jogador/<int:player_id>/condicao', methods=['POST'])
def toggle_player_condition(session_id, player_id):
    """Adicionar ou remover condicao de um jogador."""
    condition = request.form.get('condition')

    if condition:
        session_service.toggle_player_condition(player_id, condition)

    # Se for AJAX, retornar JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        player = session_service.get_player(player_id)
        if player:
            return jsonify(player.to_dict())
        return jsonify({'error': 'Jogador nao encontrado'}), 404

    return redirect(url_for('session.dashboard', session_id=session_id))


@session_bp.route('/<int:session_id>/retomar')
def resume_session(session_id):
    """Retomar uma sessao (redireciona para o passo atual)."""
    game_session = session_service.get_session(session_id)
    if not game_session:
        flash('Sessao nao encontrada.', 'danger')
        return redirect(url_for('session.list_sessions'))

    # Marcar como sessao activa
    session['active_session_id'] = session_id

    # Se tiver aventura, ir para o passo atual com session_id
    if game_session.quest_id:
        return redirect(url_for(
            'quest.step',
            quest_id=game_session.quest_id,
            step_id=game_session.passo_atual,
            session_id=session_id
        ))

    # Caso contrario, ir para o dashboard
    return redirect(url_for('session.dashboard', session_id=session_id))


@session_bp.route('/<int:session_id>/apagar', methods=['POST'])
def delete_session(session_id):
    """Apagar uma sessao (via formulario)."""
    game_session = session_service.get_session(session_id)
    if not game_session:
        flash('Sessao nao encontrada.', 'danger')
        return redirect(url_for('session.list_sessions'))

    nome = game_session.nome
    if session_service.delete_session(session_id):
        # Limpar sessao activa se for esta
        if session.get('active_session_id') == session_id:
            session.pop('active_session_id', None)
        flash(f'Sessao "{nome}" apagada.', 'info')
    else:
        flash('Erro ao apagar sessao.', 'danger')

    return redirect(url_for('session.list_sessions'))


@session_bp.route('/<int:session_id>', methods=['DELETE'])
def delete_session_api(session_id):
    """Apagar uma sessao (via API)."""
    if session_service.delete_session(session_id):
        # Limpar sessao activa se for esta
        if session.get('active_session_id') == session_id:
            session.pop('active_session_id', None)
        return jsonify({'success': True})

    return jsonify({'error': 'Sessao nao encontrada'}), 404


@session_bp.route('/<int:session_id>/notas', methods=['POST'])
def update_notes(session_id):
    """Atualizar notas da sessao."""
    notas = request.form.get('notas', '')
    session_service.update_session(session_id, notas=notas)

    # Se for AJAX, retornar JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True})

    flash('Notas atualizadas.', 'success')
    return redirect(url_for('session.dashboard', session_id=session_id))


@session_bp.route('/<int:session_id>/estado', methods=['POST'])
def update_state(session_id):
    """Atualizar estado da sessao (activa, pausada, terminada)."""
    estado = request.form.get('estado', 'activa')
    if estado in ['activa', 'pausada', 'terminada']:
        session_service.update_session(session_id, estado=estado)
        flash(f'Estado da sessao atualizado para: {estado}', 'success')

    return redirect(url_for('session.dashboard', session_id=session_id))


# ===== RASTREAMENTO DE TEMPO (API) =====

@session_bp.route('/<int:session_id>/tempo/iniciar', methods=['POST'])
def start_timer(session_id):
    """Iniciar cronometro da sessao."""
    if time_service.start_session_timer(session_id):
        return jsonify({'success': True})
    return jsonify({'error': 'Sessao nao encontrada'}), 404


@session_bp.route('/<int:session_id>/tempo/pausar', methods=['POST'])
def pause_timer(session_id):
    """Pausar cronometro da sessao."""
    total = time_service.pause_session_timer(session_id)
    if total >= 0:
        return jsonify({'success': True, 'total_seconds': total})
    return jsonify({'error': 'Sessao nao encontrada'}), 404


@session_bp.route('/<int:session_id>/tempo/status')
def get_time_status(session_id):
    """Obter estado completo de todos os sistemas de tempo."""
    status = time_service.get_all_time_status(session_id)
    return jsonify(status)


@session_bp.route('/<int:session_id>/tempo/avancar', methods=['POST'])
def advance_time(session_id):
    """Avancar tempo no jogo."""
    data = request.get_json() or {}
    minutes = data.get('minutes', 0)
    hours = data.get('hours', 0)
    days = data.get('days', 0)

    result = time_service.advance_game_time(session_id, minutes=minutes, hours=hours, days=days)
    if result:
        return jsonify(result)

    return jsonify({'error': 'Sessao nao encontrada'}), 404


@session_bp.route('/<int:session_id>/tempo/definir', methods=['POST'])
def set_time(session_id):
    """Definir tempo no jogo manualmente."""
    data = request.get_json() or {}
    dia = data.get('dia', 1)
    hora = data.get('hora', '08:00')

    if time_service.set_game_time(session_id, dia, hora):
        return jsonify(time_service.get_game_time(session_id))

    return jsonify({'error': 'Formato de hora invalido ou sessao nao encontrada'}), 400


@session_bp.route('/<int:session_id>/tempo/descanso', methods=['POST'])
def register_rest(session_id):
    """Registar descanso (curto ou longo)."""
    data = request.get_json() or {}
    rest_type = data.get('tipo', 'curto')  # 'curto' ou 'longo'

    result = time_service.register_rest(session_id, rest_type)
    if result:
        return jsonify(result)

    return jsonify({'error': 'Tipo de descanso invalido ou sessao nao encontrada'}), 400


@session_bp.route('/<int:session_id>/tempo/exploracao/avancar', methods=['POST'])
def advance_exploration(session_id):
    """Avancar turnos de exploracao (10 minutos cada)."""
    data = request.get_json() or {}
    turns = data.get('turnos', 1)

    total = time_service.advance_exploration_turn(session_id, turns)
    return jsonify({
        'turnos_total': total,
        'tempo_jogo': time_service.get_game_time(session_id)
    })


@session_bp.route('/<int:session_id>/tempo/combate/avancar', methods=['POST'])
def advance_combat_round(session_id):
    """Avancar tempo de combate (6 segundos no jogo)."""
    from app.models.session import SessionCombat

    combat = SessionCombat.query.filter_by(session_id=session_id).first()
    if not combat or not combat.activo:
        return jsonify({'error': 'Nao ha combate activo'}), 400

    # Avancar tempo no jogo (6 segundos = 1 ronda D&D)
    time_service.advance_game_time(session_id, seconds=6)

    # Retornar estado atualizado
    return jsonify({
        'ronda_atual': combat.ronda_atual,
        'combat_time': time_service.get_combat_time(session_id),
        'tempo_jogo': time_service.get_game_time(session_id)
    })
