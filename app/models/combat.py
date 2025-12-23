"""Modelos para sessões de combate."""

from app import db
from datetime import datetime


class CombatSession(db.Model):
    """Sessão de combate guardada na base de dados."""
    __tablename__ = 'combat_sessions'

    id = db.Column(db.Integer, primary_key=True)
    quest_id = db.Column(db.String(100), nullable=True)
    nome = db.Column(db.String(200), default='Combate')
    ronda_atual = db.Column(db.Integer, default=1)
    turno_atual = db.Column(db.Integer, default=0)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Participantes guardados como JSON
    participantes_json = db.Column(db.Text, default='[]')

    def __repr__(self):
        return f'<CombatSession {self.nome}>'


# Condições do D&D 5e em português
CONDICOES_5E = {
    'agarrado': {
        'nome': 'Agarrado',
        'descricao': 'Velocidade 0, não pode beneficiar de bónus à velocidade.',
        'icone': 'bi-hand-index',
        'imagem': '/static/img/conditions/agarrado.webp'
    },
    'amedrontado': {
        'nome': 'Amedrontado',
        'descricao': 'Desvantagem em testes de habilidade e ataques enquanto vê a fonte do medo.',
        'icone': 'bi-emoji-frown',
        'imagem': '/static/img/conditions/assustado.webp'
    },
    'atordoado': {
        'nome': 'Atordoado',
        'descricao': 'Incapacitado, não pode mover-se, falha automaticamente saves de FOR e DES.',
        'icone': 'bi-stars',
        'imagem': '/static/img/conditions/atordoado.webp'
    },
    'cego': {
        'nome': 'Cego',
        'descricao': 'Falha automaticamente testes que requerem visão. Desvantagem em ataques.',
        'icone': 'bi-eye-slash',
        'imagem': '/static/img/conditions/cego.webp'
    },
    'enfeiticado': {
        'nome': 'Enfeitiçado',
        'descricao': 'Não pode atacar quem o enfeitiçou. Quem enfeitiçou tem vantagem em interações sociais.',
        'icone': 'bi-heart',
        'imagem': '/static/img/conditions/encantado.webp'
    },
    'envenenado': {
        'nome': 'Envenenado',
        'descricao': 'Desvantagem em ataques e testes de habilidade.',
        'icone': 'bi-droplet-fill',
        'imagem': '/static/img/conditions/envenenado.webp'
    },
    'exausto': {
        'nome': 'Exausto',
        'descricao': 'Níveis de exaustão acumulam penalidades progressivas.',
        'icone': 'bi-battery-half'
    },
    'incapacitado': {
        'nome': 'Incapacitado',
        'descricao': 'Não pode realizar ações ou reações.',
        'icone': 'bi-x-circle',
        'imagem': '/static/img/conditions/incapacitado.webp'
    },
    'inconsciente': {
        'nome': 'Inconsciente',
        'descricao': 'Incapacitado, não pode mover-se ou falar, larga o que segura.',
        'icone': 'bi-moon-stars',
        'imagem': '/static/img/conditions/inconsciente.webp'
    },
    'invisivel': {
        'nome': 'Invisível',
        'descricao': 'Impossível de ver sem magia. Vantagem em ataques, ataques contra têm desvantagem.',
        'icone': 'bi-eye',
        'imagem': '/static/img/conditions/invisivel.webp'
    },
    'paralisado': {
        'nome': 'Paralisado',
        'descricao': 'Incapacitado, não pode mover-se ou falar. Falha saves de FOR e DES.',
        'icone': 'bi-lightning',
        'imagem': '/static/img/conditions/paralisado.webp'
    },
    'petrificado': {
        'nome': 'Petrificado',
        'descricao': 'Transformado em pedra. Peso x10, não envelhece.',
        'icone': 'bi-gem',
        'imagem': '/static/img/conditions/petrificado.webp'
    },
    'propenso': {
        'nome': 'Caído/Propenso',
        'descricao': 'Só pode rastejar. Desvantagem em ataques. Ataques a 1.5m têm vantagem.',
        'icone': 'bi-person-down',
        'imagem': '/static/img/conditions/caido.webp'
    },
    'restringido': {
        'nome': 'Restringido',
        'descricao': 'Velocidade 0. Desvantagem em ataques e saves de DES.',
        'icone': 'bi-lock',
        'imagem': '/static/img/conditions/impedido.webp'
    },
    'surdo': {
        'nome': 'Surdo',
        'descricao': 'Falha automaticamente testes que requerem audição.',
        'icone': 'bi-ear',
        'imagem': '/static/img/conditions/surdo.webp'
    },
    'concentrando': {
        'nome': 'Concentrando',
        'descricao': 'A manter concentração numa magia.',
        'icone': 'bi-bullseye'
    }
}
