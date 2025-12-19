"""Servico de gestao de posicoes de entidades em mapas tacticos.

Gere posicionamento de jogadores, NPCs e monstros em grelhas de combate.
"""

from app import db
from app.models.position import EntityPosition, MapConfiguration
from app.models.session import SessionPlayer


class PositionService:
    """Servico de gestao de posicoes no mapa."""

    # Cores padrao para tipos de entidades
    DEFAULT_COLORS = {
        'jogador': '#00ff00',  # Verde
        'npc': '#00ccff',      # Azul claro
        'monstro': '#ff0000'   # Vermelho
    }

    # Icones padrao (Bootstrap Icons)
    DEFAULT_ICONS = {
        'jogador': 'person-fill',
        'npc': 'person',
        'monstro': 'bug-fill'
    }

    def initialize_step_map(self, session_id: int, quest_step_id: int, map_config: dict):
        """Criar ou actualizar configuracao de mapa para um passo.

        Args:
            session_id: ID da sessao de jogo
            quest_step_id: ID do passo da quest (None para mapa overview)
            map_config: Dicionario com configuracao do mapa

        Returns:
            Objeto MapConfiguration criado/actualizado
        """
        # Procurar configuracao existente
        map_conf = MapConfiguration.query.filter_by(
            session_id=session_id,
            quest_step_id=quest_step_id
        ).first()

        if not map_conf:
            map_conf = MapConfiguration(
                session_id=session_id,
                quest_step_id=quest_step_id
            )
            db.session.add(map_conf)

        # Actualizar configuracao
        map_conf.grid_width = map_config.get('grid_largura', 20)
        map_conf.grid_height = map_config.get('grid_altura', 20)
        map_conf.square_size_meters = map_config.get('metros_por_quadrado', 1.5)
        map_conf.background_image_url = map_config.get('imagem_fundo')

        db.session.commit()
        return map_conf

    def place_entities_initial(self, session_id: int, quest_step_id: int, initial_positions: dict):
        """Colocar entidades nas posicoes iniciais do mapa.

        Args:
            session_id: ID da sessao de jogo
            quest_step_id: ID do passo da quest
            initial_positions: Dicionario com posicoes iniciais
                {
                    'jogadores': [{'indice': 0, 'x': 2, 'y': 7}, ...],
                    'monstros': [{'id': 'goblin', 'instancia': 0, 'x': 12, 'y': 7}, ...],
                    'npcs': [{'id': 'bertoldo', 'x': 5, 'y': 5}, ...]
                }

        Returns:
            Lista de EntityPosition criados
        """
        # Limpar posicoes existentes para este passo
        EntityPosition.query.filter_by(
            session_id=session_id,
            quest_step_id=quest_step_id
        ).delete()

        positions_created = []

        # Colocar jogadores
        player_positions = initial_positions.get('jogadores', [])
        players = SessionPlayer.query.filter_by(session_id=session_id).order_by(SessionPlayer.id).all()

        for pos_data in player_positions:
            player_index = pos_data.get('indice', 0)
            if player_index < len(players):
                player = players[player_index]
                position = EntityPosition(
                    session_id=session_id,
                    quest_step_id=quest_step_id,
                    entity_type='jogador',
                    entity_id=f'player_{player.id}',
                    grid_x=pos_data['x'],
                    grid_y=pos_data['y'],
                    token_cor=self.DEFAULT_COLORS['jogador'],
                    token_icone=self.DEFAULT_ICONS['jogador'],
                    visivel=True
                )
                db.session.add(position)
                positions_created.append(position)

        # Colocar monstros
        monster_positions = initial_positions.get('monstros', [])
        for pos_data in monster_positions:
            monster_id = pos_data.get('id', 'unknown')
            instance = pos_data.get('instancia', 0)
            entity_id = f"monster_{monster_id}_{instance}"

            position = EntityPosition(
                session_id=session_id,
                quest_step_id=quest_step_id,
                entity_type='monstro',
                entity_id=entity_id,
                grid_x=pos_data['x'],
                grid_y=pos_data['y'],
                token_cor=self.DEFAULT_COLORS['monstro'],
                token_icone=self.DEFAULT_ICONS['monstro'],
                visivel=True
            )
            db.session.add(position)
            positions_created.append(position)

        # Colocar NPCs
        npc_positions = initial_positions.get('npcs', [])
        for pos_data in npc_positions:
            npc_id = pos_data.get('id', 'unknown')
            entity_id = f"npc_{npc_id}"

            position = EntityPosition(
                session_id=session_id,
                quest_step_id=quest_step_id,
                entity_type='npc',
                entity_id=entity_id,
                grid_x=pos_data['x'],
                grid_y=pos_data['y'],
                token_cor=self.DEFAULT_COLORS['npc'],
                token_icone=self.DEFAULT_ICONS['npc'],
                visivel=True
            )
            db.session.add(position)
            positions_created.append(position)

        db.session.commit()
        return positions_created

    def move_entity(self, session_id: int, quest_step_id: int, entity_id: str, new_x: int, new_y: int):
        """Mover entidade para nova posicao.

        Args:
            session_id: ID da sessao de jogo
            quest_step_id: ID do passo da quest
            entity_id: ID da entidade (ex: 'player_1', 'monster_goblin_0')
            new_x: Nova coordenada X
            new_y: Nova coordenada Y

        Returns:
            Dicionario com dados da posicao actualizada, ou None se nao encontrada
        """
        position = EntityPosition.query.filter_by(
            session_id=session_id,
            quest_step_id=quest_step_id,
            entity_id=entity_id
        ).first()

        if position:
            position.grid_x = new_x
            position.grid_y = new_y
            db.session.commit()
            return position.to_dict()

        return None

    def get_all_positions(self, session_id: int, quest_step_id: int):
        """Obter todas as posicoes de entidades para um passo.

        Args:
            session_id: ID da sessao de jogo
            quest_step_id: ID do passo da quest

        Returns:
            Lista de dicionarios com dados das posicoes
        """
        positions = EntityPosition.query.filter_by(
            session_id=session_id,
            quest_step_id=quest_step_id
        ).all()

        return [p.to_dict() for p in positions]

    def get_position_by_entity(self, session_id: int, quest_step_id: int, entity_id: str):
        """Obter posicao de uma entidade especifica.

        Args:
            session_id: ID da sessao de jogo
            quest_step_id: ID do passo da quest
            entity_id: ID da entidade

        Returns:
            Dicionario com dados da posicao, ou None se nao encontrada
        """
        position = EntityPosition.query.filter_by(
            session_id=session_id,
            quest_step_id=quest_step_id,
            entity_id=entity_id
        ).first()

        return position.to_dict() if position else None

    def toggle_entity_visibility(self, session_id: int, quest_step_id: int, entity_id: str):
        """Alternar visibilidade de entidade (mostrar/esconder).

        Args:
            session_id: ID da sessao de jogo
            quest_step_id: ID do passo da quest
            entity_id: ID da entidade

        Returns:
            Novo estado de visibilidade (True/False), ou None se nao encontrada
        """
        position = EntityPosition.query.filter_by(
            session_id=session_id,
            quest_step_id=quest_step_id,
            entity_id=entity_id
        ).first()

        if position:
            position.visivel = not position.visivel
            db.session.commit()
            return position.visivel

        return None

    def set_entity_visibility(self, session_id: int, quest_step_id: int, entity_id: str, visible: bool):
        """Definir visibilidade de entidade.

        Args:
            session_id: ID da sessao de jogo
            quest_step_id: ID do passo da quest
            entity_id: ID da entidade
            visible: True para visivel, False para escondida

        Returns:
            True se sucesso, False caso contrario
        """
        position = EntityPosition.query.filter_by(
            session_id=session_id,
            quest_step_id=quest_step_id,
            entity_id=entity_id
        ).first()

        if position:
            position.visivel = visible
            db.session.commit()
            return True

        return False

    def update_entity_appearance(self, session_id: int, quest_step_id: int, entity_id: str,
                                  token_cor: str = None, token_icone: str = None):
        """Actualizar aparencia da entidade (cor e icone).

        Args:
            session_id: ID da sessao de jogo
            quest_step_id: ID do passo da quest
            entity_id: ID da entidade
            token_cor: Nova cor (formato hex, ex: '#ff0000')
            token_icone: Novo icone (nome do icone Bootstrap)

        Returns:
            Dicionario com dados actualizados, ou None se nao encontrada
        """
        position = EntityPosition.query.filter_by(
            session_id=session_id,
            quest_step_id=quest_step_id,
            entity_id=entity_id
        ).first()

        if position:
            if token_cor:
                position.token_cor = token_cor
            if token_icone:
                position.token_icone = token_icone

            db.session.commit()
            return position.to_dict()

        return None

    def get_map_configuration(self, session_id: int, quest_step_id: int):
        """Obter configuracao do mapa para um passo.

        Args:
            session_id: ID da sessao de jogo
            quest_step_id: ID do passo da quest

        Returns:
            Dicionario com configuracao do mapa, ou None se nao existe
        """
        map_conf = MapConfiguration.query.filter_by(
            session_id=session_id,
            quest_step_id=quest_step_id
        ).first()

        return map_conf.to_dict() if map_conf else None

    def get_entities_at_position(self, session_id: int, quest_step_id: int, x: int, y: int):
        """Obter todas as entidades numa posicao especifica.

        Args:
            session_id: ID da sessao de jogo
            quest_step_id: ID do passo da quest
            x: Coordenada X
            y: Coordenada Y

        Returns:
            Lista de dicionarios com entidades na posicao
        """
        positions = EntityPosition.query.filter_by(
            session_id=session_id,
            quest_step_id=quest_step_id,
            grid_x=x,
            grid_y=y
        ).all()

        return [p.to_dict() for p in positions]

    def remove_entity(self, session_id: int, quest_step_id: int, entity_id: str):
        """Remover entidade do mapa (util quando monstro morre).

        Args:
            session_id: ID da sessao de jogo
            quest_step_id: ID do passo da quest
            entity_id: ID da entidade

        Returns:
            True se removida, False caso contrario
        """
        position = EntityPosition.query.filter_by(
            session_id=session_id,
            quest_step_id=quest_step_id,
            entity_id=entity_id
        ).first()

        if position:
            db.session.delete(position)
            db.session.commit()
            return True

        return False

    def clear_step_positions(self, session_id: int, quest_step_id: int):
        """Limpar todas as posicoes de um passo (util ao recomec ar passo).

        Args:
            session_id: ID da sessao de jogo
            quest_step_id: ID do passo da quest

        Returns:
            Numero de posicoes removidas
        """
        count = EntityPosition.query.filter_by(
            session_id=session_id,
            quest_step_id=quest_step_id
        ).delete()

        db.session.commit()
        return count
