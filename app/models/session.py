"""Modelos para gestao de sessoes de jogo."""

from app import db
from datetime import datetime
import json


class GameSession(db.Model):
    """Uma sessao de jogo completa que liga uma aventura aos jogadores."""
    __tablename__ = 'game_sessions'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    quest_id = db.Column(db.String(100), nullable=True)  # Referencia ao JSON da aventura
    passo_atual = db.Column(db.Integer, default=1)
    estado = db.Column(db.String(50), default='activa')  # activa, pausada, terminada
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notas = db.Column(db.Text, default='')

    # Rastreamento de tempo (4 sistemas)
    # 1. Tempo de sessao (real-world)
    sessao_iniciada_em = db.Column(db.DateTime, nullable=True)
    sessao_pausada_em = db.Column(db.DateTime, nullable=True)
    tempo_total_segundos = db.Column(db.Integer, default=0)  # Tempo acumulado de jogo

    # 2. Tempo no jogo (in-game)
    tempo_jogo_inicio = db.Column(db.String(50), default="08:00")  # HH:MM formato
    tempo_jogo_atual = db.Column(db.String(50), default="08:00")
    dia_jogo_atual = db.Column(db.Integer, default=1)

    # 3. Exploracao
    turnos_exploracao_total = db.Column(db.Integer, default=0)  # Turnos de 10 minutos

    # 4. Descansos
    ultimo_descanso_curto = db.Column(db.DateTime, nullable=True)  # 1 hora
    ultimo_descanso_longo = db.Column(db.DateTime, nullable=True)  # 8 horas

    # Relacoes
    jogadores = db.relationship(
        'SessionPlayer',
        backref='sessao',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    combate = db.relationship(
        'SessionCombat',
        backref='sessao',
        uselist=False,
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<GameSession {self.nome}>'

    def to_dict(self):
        """Converte a sessao para dicionario."""
        return {
            'id': self.id,
            'nome': self.nome,
            'quest_id': self.quest_id,
            'passo_atual': self.passo_atual,
            'estado': self.estado,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None,
            'notas': self.notas,
            'num_jogadores': self.jogadores.count()
        }

    @classmethod
    def count_for_quest(cls, quest_id):
        """Conta sessoes activas/pausadas para uma aventura (max 2)."""
        return cls.query.filter_by(quest_id=quest_id).filter(
            cls.estado.in_(['activa', 'pausada'])
        ).count()

    @classmethod
    def get_for_quest(cls, quest_id):
        """Obtem todas as sessoes de uma aventura, ordenadas por data."""
        return cls.query.filter_by(quest_id=quest_id).order_by(
            cls.atualizado_em.desc()
        ).all()

    @classmethod
    def can_create_for_quest(cls, quest_id):
        """Verifica se pode criar nova sessao (max 3 por aventura)."""
        return cls.count_for_quest(quest_id) < 3


class SessionPlayer(db.Model):
    """Um jogador numa sessao especifica com estado atual."""
    __tablename__ = 'session_players'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('game_sessions.id'), nullable=False)
    nome_jogador = db.Column(db.String(100), nullable=False)  # Nome real do jogador
    character_data = db.Column(db.Text, nullable=False)  # JSON com dados do personagem
    hp_atual = db.Column(db.Integer, nullable=False)
    hp_max = db.Column(db.Integer, nullable=False)
    condicoes = db.Column(db.Text, default='[]')  # Array JSON de condicoes
    ordem_combate = db.Column(db.Integer, nullable=True)  # Ordem no combate
    iniciativa = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return f'<SessionPlayer {self.nome_jogador}>'

    def get_character_data(self):
        """Retorna os dados do personagem como dicionario."""
        try:
            return json.loads(self.character_data)
        except (json.JSONDecodeError, TypeError):
            return {}

    def set_character_data(self, data):
        """Define os dados do personagem a partir de um dicionario."""
        self.character_data = json.dumps(data, ensure_ascii=False)

    def get_condicoes(self):
        """Retorna a lista de condicoes."""
        try:
            return json.loads(self.condicoes)
        except (json.JSONDecodeError, TypeError):
            return []

    def set_condicoes(self, condicoes_list):
        """Define a lista de condicoes."""
        self.condicoes = json.dumps(condicoes_list, ensure_ascii=False)

    def add_condicao(self, condicao):
        """Adiciona uma condicao."""
        condicoes = self.get_condicoes()
        if condicao not in condicoes:
            condicoes.append(condicao)
            self.set_condicoes(condicoes)

    def remove_condicao(self, condicao):
        """Remove uma condicao."""
        condicoes = self.get_condicoes()
        if condicao in condicoes:
            condicoes.remove(condicao)
            self.set_condicoes(condicoes)

    def to_dict(self):
        """Converte o jogador para dicionario."""
        char_data = self.get_character_data()
        return {
            'id': self.id,
            'session_id': self.session_id,
            'nome_jogador': self.nome_jogador,
            'nome_personagem': char_data.get('nome', 'Desconhecido'),
            'classe': char_data.get('classe', ''),
            'nivel': char_data.get('nivel', 1),
            'hp_atual': self.hp_atual,
            'hp_max': self.hp_max,
            'ac': char_data.get('ac', 10),
            'condicoes': self.get_condicoes(),
            'iniciativa': self.iniciativa
        }


class SessionCombat(db.Model):
    """Estado de combate duma sessao."""
    __tablename__ = 'session_combats'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('game_sessions.id'), nullable=False, unique=True)
    activo = db.Column(db.Boolean, default=False)
    ronda_atual = db.Column(db.Integer, default=1)
    turno_atual = db.Column(db.Integer, default=0)
    participantes_json = db.Column(db.Text, default='[]')  # Monstros + estado
    quest_step_id = db.Column(db.Integer, nullable=True)  # Passo da aventura de onde veio o combate

    # Rastreamento de tempo de combate
    tempo_inicio_combate = db.Column(db.DateTime, nullable=True)  # Quando o combate comecou
    tempo_ronda_inicio = db.Column(db.DateTime, nullable=True)  # Quando a ronda atual comecou
    duracao_total_segundos = db.Column(db.Integer, default=0)  # Duracao real-world do combate

    def __repr__(self):
        return f'<SessionCombat sessao={self.session_id} activo={self.activo}>'

    def get_participantes(self):
        """Retorna a lista de participantes."""
        try:
            return json.loads(self.participantes_json)
        except (json.JSONDecodeError, TypeError):
            return []

    def set_participantes(self, participantes):
        """Define a lista de participantes."""
        self.participantes_json = json.dumps(participantes, ensure_ascii=False)

    def add_participante(self, participante):
        """Adiciona um participante ao combate."""
        participantes = self.get_participantes()
        participantes.append(participante)
        self.set_participantes(participantes)

    def remove_participante(self, participante_id):
        """Remove um participante pelo ID."""
        participantes = self.get_participantes()
        participantes = [p for p in participantes if p.get('id') != participante_id]
        self.set_participantes(participantes)

    def ordenar_por_iniciativa(self):
        """Ordena participantes por iniciativa (maior primeiro)."""
        participantes = self.get_participantes()
        participantes.sort(key=lambda p: p.get('iniciativa', 0), reverse=True)
        self.set_participantes(participantes)

    def to_dict(self):
        """Converte o combate para dicionario."""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'activo': self.activo,
            'ronda_atual': self.ronda_atual,
            'turno_atual': self.turno_atual,
            'participantes': self.get_participantes(),
            'quest_step_id': self.quest_step_id
        }


class SavedCharacter(db.Model):
    """Personagem personalizado guardado pelo utilizador."""
    __tablename__ = 'saved_characters'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    classe = db.Column(db.String(50), nullable=False)
    raca = db.Column(db.String(50), nullable=False)
    nivel = db.Column(db.Integer, default=1)
    character_data = db.Column(db.Text, nullable=False)  # JSON completo do personagem
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<SavedCharacter {self.nome} ({self.classe})>'

    def get_character_data(self):
        """Retorna os dados do personagem como dicionario."""
        try:
            return json.loads(self.character_data)
        except (json.JSONDecodeError, TypeError):
            return {}

    def set_character_data(self, data):
        """Define os dados do personagem a partir de um dicionario."""
        self.character_data = json.dumps(data, ensure_ascii=False)

    def to_dict(self):
        """Converte o personagem para dicionario."""
        char_data = self.get_character_data()
        return {
            'id': self.id,
            'nome': self.nome,
            'classe': self.classe,
            'raca': self.raca,
            'nivel': self.nivel,
            'hp_max': char_data.get('hp_max', 10),
            'ac': char_data.get('ac', 10),
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'character_data': char_data
        }
