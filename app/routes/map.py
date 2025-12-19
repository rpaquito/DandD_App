"""Rotas para gestao de mapas tacticos e posicionamento de entidades."""

from flask import Blueprint, request, jsonify
from app.services.position_service import PositionService

map_bp = Blueprint('map', __name__, url_prefix='/mapa')
position_service = PositionService()


@map_bp.route('/sessao/<int:session_id>/passo/<int:step_id>/posicoes')
def get_positions(session_id, step_id):
    """Obter todas as posicoes de entidades para um passo.

    Returns:
        JSON com lista de posicoes e configuracao do mapa
    """
    positions = position_service.get_all_positions(session_id, step_id)
    map_config = position_service.get_map_configuration(session_id, step_id)

    return jsonify({
        'positions': positions,
        'map_config': map_config
    })


@map_bp.route('/sessao/<int:session_id>/passo/<int:step_id>/mover', methods=['POST'])
def move_entity(session_id, step_id):
    """Mover entidade para nova posicao.

    Expects JSON:
        {
            "entity_id": "player_1",
            "x": 5,
            "y": 7
        }

    Returns:
        JSON com dados da posicao actualizada
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados nao fornecidos'}), 400

    entity_id = data.get('entity_id')
    new_x = data.get('x')
    new_y = data.get('y')

    if entity_id is None or new_x is None or new_y is None:
        return jsonify({'error': 'Campos obrigatorios: entity_id, x, y'}), 400

    result = position_service.move_entity(session_id, step_id, entity_id, new_x, new_y)

    if result:
        return jsonify(result)

    return jsonify({'error': 'Entidade nao encontrada'}), 404


@map_bp.route('/sessao/<int:session_id>/passo/<int:step_id>/visibilidade', methods=['POST'])
def toggle_visibility(session_id, step_id):
    """Alternar visibilidade de uma entidade.

    Expects JSON:
        {
            "entity_id": "monster_goblin_0"
        }

    Returns:
        JSON com novo estado de visibilidade
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados nao fornecidos'}), 400

    entity_id = data.get('entity_id')
    if not entity_id:
        return jsonify({'error': 'Campo obrigatorio: entity_id'}), 400

    visible = position_service.toggle_entity_visibility(session_id, step_id, entity_id)

    if visible is not None:
        return jsonify({
            'entity_id': entity_id,
            'visivel': visible
        })

    return jsonify({'error': 'Entidade nao encontrada'}), 404


@map_bp.route('/sessao/<int:session_id>/passo/<int:step_id>/visibilidade/definir', methods=['POST'])
def set_visibility(session_id, step_id):
    """Definir visibilidade de uma entidade.

    Expects JSON:
        {
            "entity_id": "monster_goblin_0",
            "visible": true
        }

    Returns:
        JSON com confirmacao
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados nao fornecidos'}), 400

    entity_id = data.get('entity_id')
    visible = data.get('visible')

    if entity_id is None or visible is None:
        return jsonify({'error': 'Campos obrigatorios: entity_id, visible'}), 400

    success = position_service.set_entity_visibility(session_id, step_id, entity_id, visible)

    if success:
        return jsonify({
            'entity_id': entity_id,
            'visivel': visible
        })

    return jsonify({'error': 'Entidade nao encontrada'}), 404


@map_bp.route('/sessao/<int:session_id>/passo/<int:step_id>/config')
def get_map_config(session_id, step_id):
    """Obter configuracao do mapa para um passo.

    Returns:
        JSON com configuracao do mapa (dimensoes, tamanho de quadrados, imagem de fundo)
    """
    map_config = position_service.get_map_configuration(session_id, step_id)

    if map_config:
        return jsonify(map_config)

    return jsonify({'error': 'Configuracao de mapa nao encontrada'}), 404


@map_bp.route('/sessao/<int:session_id>/passo/<int:step_id>/entidade/<entity_id>')
def get_entity_position(session_id, step_id, entity_id):
    """Obter posicao de uma entidade especifica.

    Returns:
        JSON com dados da posicao
    """
    position = position_service.get_position_by_entity(session_id, step_id, entity_id)

    if position:
        return jsonify(position)

    return jsonify({'error': 'Entidade nao encontrada'}), 404


@map_bp.route('/sessao/<int:session_id>/passo/<int:step_id>/entidade/<entity_id>/aparencia', methods=['POST'])
def update_entity_appearance(session_id, step_id, entity_id):
    """Actualizar aparencia de uma entidade (cor e icone).

    Expects JSON:
        {
            "token_cor": "#ff0000",
            "token_icone": "bug-fill"
        }

    Returns:
        JSON com dados actualizados da entidade
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados nao fornecidos'}), 400

    token_cor = data.get('token_cor')
    token_icone = data.get('token_icone')

    result = position_service.update_entity_appearance(
        session_id, step_id, entity_id,
        token_cor=token_cor,
        token_icone=token_icone
    )

    if result:
        return jsonify(result)

    return jsonify({'error': 'Entidade nao encontrada'}), 404


@map_bp.route('/sessao/<int:session_id>/passo/<int:step_id>/entidade/<entity_id>/remover', methods=['POST'])
def remove_entity(session_id, step_id, entity_id):
    """Remover entidade do mapa (util quando monstro morre).

    Returns:
        JSON com confirmacao
    """
    success = position_service.remove_entity(session_id, step_id, entity_id)

    if success:
        return jsonify({
            'success': True,
            'entity_id': entity_id,
            'message': 'Entidade removida do mapa'
        })

    return jsonify({'error': 'Entidade nao encontrada'}), 404


@map_bp.route('/sessao/<int:session_id>/passo/<int:step_id>/posicao/<int:x>/<int:y>')
def get_entities_at_position(session_id, step_id, x, y):
    """Obter todas as entidades numa posicao especifica.

    Args:
        x: Coordenada X da grelha
        y: Coordenada Y da grelha

    Returns:
        JSON com lista de entidades na posicao
    """
    entities = position_service.get_entities_at_position(session_id, step_id, x, y)

    return jsonify({
        'x': x,
        'y': y,
        'entities': entities,
        'count': len(entities)
    })


@map_bp.route('/sessao/<int:session_id>/passo/<int:step_id>/inicializar', methods=['POST'])
def initialize_map(session_id, step_id):
    """Inicializar mapa com configuracao e posicoes iniciais.

    Expects JSON:
        {
            "map_config": {
                "grid_largura": 20,
                "grid_altura": 20,
                "metros_por_quadrado": 1.5,
                "imagem_fundo": "/static/maps/step-1.png"
            },
            "initial_positions": {
                "jogadores": [{"indice": 0, "x": 2, "y": 7}],
                "monstros": [{"id": "goblin", "instancia": 0, "x": 12, "y": 7}],
                "npcs": []
            }
        }

    Returns:
        JSON com confirmacao e dados criados
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados nao fornecidos'}), 400

    map_config = data.get('map_config', {})
    initial_positions = data.get('initial_positions', {})

    # Criar/actualizar configuracao do mapa
    map_conf = position_service.initialize_step_map(session_id, step_id, map_config)

    # Colocar entidades nas posicoes iniciais
    positions_created = position_service.place_entities_initial(
        session_id, step_id, initial_positions
    )

    return jsonify({
        'success': True,
        'map_config': map_conf.to_dict(),
        'positions_created': len(positions_created),
        'positions': [p.to_dict() for p in positions_created]
    })


@map_bp.route('/sessao/<int:session_id>/passo/<int:step_id>/limpar', methods=['POST'])
def clear_positions(session_id, step_id):
    """Limpar todas as posicoes de um passo (util ao recomecar passo).

    Returns:
        JSON com numero de posicoes removidas
    """
    count = position_service.clear_step_positions(session_id, step_id)

    return jsonify({
        'success': True,
        'positions_removed': count,
        'message': f'{count} posicoes removidas'
    })
