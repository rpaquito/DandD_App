"""Rotas para gestão de jogadores."""

import json
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session

players_bp = Blueprint('players', __name__, url_prefix='/jogadores')

PLAYERS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'players.json')
CHARACTERS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'characters.json')


def load_players():
    """Carrega os jogadores do ficheiro JSON."""
    if os.path.exists(PLAYERS_FILE):
        with open(PLAYERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f).get('jogadores', [])
    return []


def save_players(players):
    """Guarda os jogadores no ficheiro JSON."""
    with open(PLAYERS_FILE, 'w', encoding='utf-8') as f:
        json.dump({'jogadores': players}, f, ensure_ascii=False, indent=2)


def load_templates():
    """Carrega os personagens template."""
    if os.path.exists(CHARACTERS_FILE):
        with open(CHARACTERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f).get('personagens', [])
    return []


def calculate_modifier(score):
    """Calcula o modificador de atributo."""
    return (score - 10) // 2


@players_bp.route('/')
def list_players():
    """Lista todos os jogadores da sessão atual."""
    players = load_players()
    templates = load_templates()
    return render_template('players/list.html', players=players, templates=templates)


@players_bp.route('/adicionar', methods=['GET', 'POST'])
def add_player():
    """Adiciona um novo jogador."""
    templates = load_templates()

    if request.method == 'POST':
        players = load_players()

        template_id = request.form.get('template_id')

        if template_id:
            # Usar personagem template
            template = next((t for t in templates if t['id'] == template_id), None)
            if template:
                new_player = template.copy()
                new_player['player_id'] = len(players) + 1
                new_player['nome_jogador'] = request.form.get('nome_jogador', 'Jogador')
                new_player['hp_atual'] = new_player['hp_max']
                new_player['condicoes'] = []
                players.append(new_player)
                save_players(players)
                flash(f'Jogador {new_player["nome_jogador"]} adicionado com {new_player["nome"]}!', 'success')
                return redirect(url_for('players.list_players'))
        else:
            # Criar personagem personalizado
            new_player = {
                'player_id': len(players) + 1,
                'nome_jogador': request.form.get('nome_jogador', 'Jogador'),
                'nome': request.form.get('nome', 'Personagem'),
                'classe': request.form.get('classe', 'Guerreiro'),
                'nivel': int(request.form.get('nivel', 1)),
                'raca': request.form.get('raca', 'Humano'),
                'forca': int(request.form.get('forca', 10)),
                'destreza': int(request.form.get('destreza', 10)),
                'constituicao': int(request.form.get('constituicao', 10)),
                'inteligencia': int(request.form.get('inteligencia', 10)),
                'sabedoria': int(request.form.get('sabedoria', 10)),
                'carisma': int(request.form.get('carisma', 10)),
                'hp_max': int(request.form.get('hp_max', 10)),
                'hp_atual': int(request.form.get('hp_max', 10)),
                'ac': int(request.form.get('ac', 10)),
                'velocidade': request.form.get('velocidade', '9m'),
                'condicoes': []
            }
            players.append(new_player)
            save_players(players)
            flash(f'Jogador {new_player["nome_jogador"]} adicionado!', 'success')
            return redirect(url_for('players.list_players'))

    return render_template('players/add.html', templates=templates)


@players_bp.route('/escolher/<template_id>')
def choose_template(template_id):
    """Escolhe um template de personagem."""
    templates = load_templates()
    template = next((t for t in templates if t['id'] == template_id), None)

    if template:
        return render_template('players/confirm.html', template=template)

    flash('Personagem template não encontrado.', 'danger')
    return redirect(url_for('players.list_players'))


@players_bp.route('/confirmar/<template_id>', methods=['POST'])
def confirm_template(template_id):
    """Confirma a escolha do template e adiciona o jogador."""
    templates = load_templates()
    template = next((t for t in templates if t['id'] == template_id), None)

    if template:
        players = load_players()
        new_player = template.copy()
        new_player['player_id'] = len(players) + 1
        new_player['nome_jogador'] = request.form.get('nome_jogador', 'Jogador')
        new_player['hp_atual'] = new_player['hp_max']
        new_player['condicoes'] = []
        players.append(new_player)
        save_players(players)
        flash(f'{new_player["nome_jogador"]} junta-se à aventura com {new_player["nome"]}!', 'success')

    return redirect(url_for('players.list_players'))


@players_bp.route('/editar/<int:player_id>', methods=['GET', 'POST'])
def edit_player(player_id):
    """Edita um jogador existente."""
    players = load_players()
    player = next((p for p in players if p['player_id'] == player_id), None)

    if not player:
        flash('Jogador não encontrado.', 'danger')
        return redirect(url_for('players.list_players'))

    if request.method == 'POST':
        player['nome_jogador'] = request.form.get('nome_jogador', player['nome_jogador'])
        player['nome'] = request.form.get('nome', player['nome'])
        player['hp_atual'] = int(request.form.get('hp_atual', player['hp_atual']))
        player['hp_max'] = int(request.form.get('hp_max', player['hp_max']))
        player['ac'] = int(request.form.get('ac', player['ac']))
        save_players(players)
        flash('Jogador atualizado!', 'success')
        return redirect(url_for('players.list_players'))

    return render_template('players/edit.html', player=player)


@players_bp.route('/remover/<int:player_id>', methods=['POST'])
def remove_player(player_id):
    """Remove um jogador."""
    players = load_players()
    players = [p for p in players if p['player_id'] != player_id]
    save_players(players)
    flash('Jogador removido.', 'info')
    return redirect(url_for('players.list_players'))


@players_bp.route('/hp/<int:player_id>', methods=['POST'])
def update_hp(player_id):
    """Atualiza HP de um jogador via AJAX."""
    players = load_players()
    player = next((p for p in players if p['player_id'] == player_id), None)

    if player:
        action = request.form.get('action')
        amount = int(request.form.get('amount', 1))

        if action == 'damage':
            player['hp_atual'] = max(0, player['hp_atual'] - amount)
        elif action == 'heal':
            player['hp_atual'] = min(player['hp_max'], player['hp_atual'] + amount)

        save_players(players)

    return redirect(request.referrer or url_for('players.list_players'))


@players_bp.route('/condicao/<int:player_id>', methods=['POST'])
def toggle_condition(player_id):
    """Adiciona ou remove uma condição de um jogador."""
    players = load_players()
    player = next((p for p in players if p['player_id'] == player_id), None)

    if player:
        condition = request.form.get('condition')
        if 'condicoes' not in player:
            player['condicoes'] = []

        if condition in player['condicoes']:
            player['condicoes'].remove(condition)
        else:
            player['condicoes'].append(condition)

        save_players(players)

    return redirect(request.referrer or url_for('players.list_players'))


@players_bp.route('/limpar', methods=['POST'])
def clear_players():
    """Remove todos os jogadores."""
    save_players([])
    flash('Todos os jogadores foram removidos.', 'info')
    return redirect(url_for('players.list_players'))


@players_bp.route('/imprimir/<int:player_id>')
def print_sheet(player_id):
    """Ficha de personagem para impressão."""
    players = load_players()
    player = next((p for p in players if p['player_id'] == player_id), None)

    if not player:
        flash('Jogador não encontrado.', 'danger')
        return redirect(url_for('players.list_players'))

    return render_template('players/sheet.html', player=player)


@players_bp.route('/imprimir-todos')
def print_all_sheets():
    """Todas as fichas de personagem para impressão."""
    players = load_players()
    return render_template('players/sheets_all.html', players=players)
