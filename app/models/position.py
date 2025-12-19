"""Modelos para gestao de posicoes e mapas tacticos."""

from app import db
from datetime import datetime


class EntityPosition(db.Model):
    """Rastreia posicoes de entidades (jogadores, NPCs, monstros) em mapas tacticos."""
    __tablename__ = 'entity_positions'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('game_sessions.id'), nullable=False)
    quest_step_id = db.Column(db.Integer, nullable=True)  # null = mapa overview da quest

    # Identificacao da entidade
    entity_type = db.Column(db.String(20), nullable=False)  # 'jogador', 'npc', 'monstro'
    entity_id = db.Column(db.String(100), nullable=False)  # 'player_1', 'npc_bertoldo', 'monster_goblin_1'

    # Posicao na grelha
    grid_x = db.Column(db.Integer, default=0)
    grid_y = db.Column(db.Integer, default=0)

    # Visibilidade e aparencia
    visivel = db.Column(db.Boolean, default=True)
    token_cor = db.Column(db.String(20), default='#ffffff')
    token_icone = db.Column(db.String(50), default='person')  # Nome do icone Bootstrap

    # Metadata
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Constraint: uma posicao por entidade por passo
    __table_args__ = (
        db.UniqueConstraint('session_id', 'quest_step_id', 'entity_id', name='uix_entity_step_position'),
    )

    def __repr__(self):
        return f'<EntityPosition {self.entity_type}:{self.entity_id} ({self.grid_x},{self.grid_y})>'

    def to_dict(self):
        """Converte a posicao para dicionario."""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'quest_step_id': self.quest_step_id,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'grid_x': self.grid_x,
            'grid_y': self.grid_y,
            'visivel': self.visivel,
            'token_cor': self.token_cor,
            'token_icone': self.token_icone,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None
        }


class MapConfiguration(db.Model):
    """Configuracao de mapa tactico para um passo especifico."""
    __tablename__ = 'map_configurations'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('game_sessions.id'), nullable=False)
    quest_step_id = db.Column(db.Integer, nullable=True)  # null = mapa overview

    # Configuracao da grelha
    grid_width = db.Column(db.Integer, default=20)  # Numero de quadrados horizontal
    grid_height = db.Column(db.Integer, default=20)  # Numero de quadrados vertical
    square_size_meters = db.Column(db.Float, default=1.5)  # Tamanho em metros (1.5m = 5 pes D&D)

    # Imagem de fundo (opcional)
    background_image_url = db.Column(db.String(500), nullable=True)

    # Metadata
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    # Constraint: um mapa por sessao por passo
    __table_args__ = (
        db.UniqueConstraint('session_id', 'quest_step_id', name='uix_session_step_map'),
    )

    def __repr__(self):
        return f'<MapConfiguration sessao={self.session_id} passo={self.quest_step_id} {self.grid_width}x{self.grid_height}>'

    def to_dict(self):
        """Converte a configuracao para dicionario."""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'quest_step_id': self.quest_step_id,
            'grid_width': self.grid_width,
            'grid_height': self.grid_height,
            'square_size_meters': self.square_size_meters,
            'background_image_url': self.background_image_url,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None
        }
