"""
Modelo para Combat Log - Histórico de ações de combate
"""

from app import db
from datetime import datetime
import json


class CombatLog(db.Model):
    """Registo de uma ação de combate."""
    __tablename__ = 'combat_logs'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('game_sessions.id'), nullable=False)
    combat_id = db.Column(db.Integer, nullable=True)  # ID do combate específico (opcional)

    # Timestamp e ordem
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ronda = db.Column(db.Integer, default=1)
    turno = db.Column(db.Integer, default=1)

    # Actor (quem executou a ação)
    actor_id = db.Column(db.String(100), nullable=False)
    actor_nome = db.Column(db.String(200), nullable=False)

    # Tipo de ação
    action_type = db.Column(db.String(50), nullable=False)
    # Tipos: 'attack', 'damage', 'heal', 'condition', 'spell', 'death', 'initiative', 'other'

    # Detalhes da ação (JSON)
    details_json = db.Column(db.Text, nullable=True)
    # Exemplos:
    # attack: {roll: 18, bonus: 5, target_ac: 15, hit: true, crit: false, advantage: false}
    # damage: {roll: "2d6+3", result: 11, type: "slashing", resistance: false}
    # spell: {name: "Mísseis Mágicos", level: 1, slot_used: true}

    # Alvo (opcional)
    target_id = db.Column(db.String(100), nullable=True)
    target_nome = db.Column(db.String(200), nullable=True)

    # Mensagem formatada para display
    message = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<CombatLog R{self.ronda}T{self.turno} {self.action_type}>'

    def get_details(self):
        """Retorna os detalhes como dicionário."""
        if not self.details_json:
            return {}
        try:
            return json.loads(self.details_json)
        except (json.JSONDecodeError, TypeError):
            return {}

    def set_details(self, details_dict):
        """Define os detalhes a partir de um dicionário."""
        if details_dict is None:
            self.details_json = None
        else:
            self.details_json = json.dumps(details_dict, ensure_ascii=False)

    def to_dict(self):
        """Converte o log para dicionário."""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'combat_id': self.combat_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'ronda': self.ronda,
            'turno': self.turno,
            'actor_id': self.actor_id,
            'actor_nome': self.actor_nome,
            'action_type': self.action_type,
            'details': self.get_details(),
            'target_id': self.target_id,
            'target_nome': self.target_nome,
            'message': self.message
        }
