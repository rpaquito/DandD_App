"""
Serviço de Combat Log

Gere o histórico de ações de combate.
"""

from app import db
from app.models.combat_log import CombatLog
from typing import List, Dict, Optional
from datetime import datetime


class CombatLogService:
    """Serviço para gestão de combat logs."""

    @staticmethod
    def log_attack(
        session_id: int,
        actor_id: str,
        actor_nome: str,
        target_id: str,
        target_nome: str,
        attack_result: Dict,
        ronda: int = 1,
        turno: int = 1,
        combat_id: Optional[int] = None
    ) -> CombatLog:
        """
        Registra um attack roll.

        Args:
            session_id: ID da sessão
            actor_id: ID do atacante
            actor_nome: Nome do atacante
            target_id: ID do alvo
            target_nome: Nome do alvo
            attack_result: Resultado do roll_attack()
            ronda: Ronda atual
            turno: Turno atual
            combat_id: ID do combate (opcional)

        Returns:
            CombatLog criado
        """
        # Formatar mensagem
        if attack_result['crit']:
            message = f"🎯 {actor_nome} **CRÍTICO!** contra {target_nome}! (d20: {attack_result['d20_result']}+{attack_result['bonus']} = {attack_result['total']} vs AC {attack_result['target_ac']})"
        elif attack_result['crit_fail']:
            message = f"💥 {actor_nome} **FALHA CRÍTICA!** ao atacar {target_nome}! (d20: 1)"
        elif attack_result['hit']:
            message = f"⚔️ {actor_nome} acerta {target_nome}! (d20: {attack_result['d20_result']}+{attack_result['bonus']} = {attack_result['total']} vs AC {attack_result['target_ac']})"
        else:
            message = f"❌ {actor_nome} erra {target_nome}. (d20: {attack_result['d20_result']}+{attack_result['bonus']} = {attack_result['total']} vs AC {attack_result['target_ac']})"

        log = CombatLog(
            session_id=session_id,
            combat_id=combat_id,
            ronda=ronda,
            turno=turno,
            actor_id=actor_id,
            actor_nome=actor_nome,
            target_id=target_id,
            target_nome=target_nome,
            action_type='attack',
            message=message
        )
        log.set_details(attack_result)

        db.session.add(log)
        db.session.commit()

        return log

    @staticmethod
    def log_damage(
        session_id: int,
        actor_id: str,
        actor_nome: str,
        target_id: str,
        target_nome: str,
        damage_result: Dict,
        ronda: int = 1,
        turno: int = 1,
        combat_id: Optional[int] = None
    ) -> CombatLog:
        """
        Registra dano aplicado.

        Args:
            session_id: ID da sessão
            actor_id: ID do atacante
            actor_nome: Nome do atacante
            target_id: ID do alvo
            target_nome: Nome do alvo
            damage_result: Resultado do roll_damage()
            ronda: Ronda atual
            turno: Turno atual
            combat_id: ID do combate (opcional)

        Returns:
            CombatLog criado
        """
        # Formatar mensagem
        damage = damage_result['final_damage']
        dtype = damage_result['damage_type']

        modifiers = []
        if damage_result['immunity']:
            modifiers.append("IMUNE")
        elif damage_result['resistance']:
            modifiers.append("resistente")
        elif damage_result['vulnerability']:
            modifiers.append("vulnerável")

        mod_text = f" ({', '.join(modifiers)})" if modifiers else ""

        if damage_result['crit']:
            message = f"💥 {actor_nome} causa **{damage} de dano {dtype} CRÍTICO** em {target_nome}!{mod_text}"
        else:
            message = f"⚔️ {actor_nome} causa {damage} de dano {dtype} em {target_nome}.{mod_text}"

        log = CombatLog(
            session_id=session_id,
            combat_id=combat_id,
            ronda=ronda,
            turno=turno,
            actor_id=actor_id,
            actor_nome=actor_nome,
            target_id=target_id,
            target_nome=target_nome,
            action_type='damage',
            message=message
        )
        log.set_details(damage_result)

        db.session.add(log)
        db.session.commit()

        return log

    @staticmethod
    def log_heal(
        session_id: int,
        actor_id: str,
        actor_nome: str,
        target_id: str,
        target_nome: str,
        amount: int,
        ronda: int = 1,
        turno: int = 1,
        combat_id: Optional[int] = None
    ) -> CombatLog:
        """Registra cura."""
        message = f"💚 {actor_nome} cura {amount} HP em {target_nome}."

        log = CombatLog(
            session_id=session_id,
            combat_id=combat_id,
            ronda=ronda,
            turno=turno,
            actor_id=actor_id,
            actor_nome=actor_nome,
            target_id=target_id,
            target_nome=target_nome,
            action_type='heal',
            message=message
        )
        log.set_details({'amount': amount})

        db.session.add(log)
        db.session.commit()

        return log

    @staticmethod
    def log_condition(
        session_id: int,
        actor_id: str,
        actor_nome: str,
        condition: str,
        added: bool = True,
        ronda: int = 1,
        turno: int = 1,
        combat_id: Optional[int] = None
    ) -> CombatLog:
        """Registra adição/remoção de condição."""
        if added:
            message = f"🔴 {actor_nome} ganhou condição: {condition}"
        else:
            message = f"🟢 {actor_nome} perdeu condição: {condition}"

        log = CombatLog(
            session_id=session_id,
            combat_id=combat_id,
            ronda=ronda,
            turno=turno,
            actor_id=actor_id,
            actor_nome=actor_nome,
            action_type='condition',
            message=message
        )
        log.set_details({'condition': condition, 'added': added})

        db.session.add(log)
        db.session.commit()

        return log

    @staticmethod
    def log_spell(
        session_id: int,
        actor_id: str,
        actor_nome: str,
        spell_name: str,
        spell_level: int,
        target_id: Optional[str] = None,
        target_nome: Optional[str] = None,
        ronda: int = 1,
        turno: int = 1,
        combat_id: Optional[int] = None
    ) -> CombatLog:
        """Registra lançamento de magia."""
        target_text = f" em {target_nome}" if target_nome else ""
        level_text = f"nível {spell_level}" if spell_level > 0 else "truque"

        message = f"✨ {actor_nome} lança {spell_name} ({level_text}){target_text}."

        log = CombatLog(
            session_id=session_id,
            combat_id=combat_id,
            ronda=ronda,
            turno=turno,
            actor_id=actor_id,
            actor_nome=actor_nome,
            target_id=target_id,
            target_nome=target_nome,
            action_type='spell',
            message=message
        )
        log.set_details({
            'spell_name': spell_name,
            'spell_level': spell_level
        })

        db.session.add(log)
        db.session.commit()

        return log

    @staticmethod
    def log_death(
        session_id: int,
        actor_id: str,
        actor_nome: str,
        ronda: int = 1,
        turno: int = 1,
        combat_id: Optional[int] = None
    ) -> CombatLog:
        """Registra morte de participante."""
        message = f"💀 {actor_nome} foi derrotado!"

        log = CombatLog(
            session_id=session_id,
            combat_id=combat_id,
            ronda=ronda,
            turno=turno,
            actor_id=actor_id,
            actor_nome=actor_nome,
            action_type='death',
            message=message
        )

        db.session.add(log)
        db.session.commit()

        return log

    @staticmethod
    def log_custom(
        session_id: int,
        actor_id: str,
        actor_nome: str,
        message: str,
        ronda: int = 1,
        turno: int = 1,
        combat_id: Optional[int] = None,
        details: Optional[Dict] = None
    ) -> CombatLog:
        """Registra ação personalizada."""
        log = CombatLog(
            session_id=session_id,
            combat_id=combat_id,
            ronda=ronda,
            turno=turno,
            actor_id=actor_id,
            actor_nome=actor_nome,
            action_type='other',
            message=message
        )
        if details:
            log.set_details(details)

        db.session.add(log)
        db.session.commit()

        return log

    @staticmethod
    def get_combat_logs(
        session_id: int,
        limit: int = 50,
        combat_id: Optional[int] = None
    ) -> List[CombatLog]:
        """
        Obtém logs de combate.

        Args:
            session_id: ID da sessão
            limit: Número máximo de logs a retornar
            combat_id: Filtrar por combat_id específico (opcional)

        Returns:
            Lista de CombatLog ordenados por timestamp (mais recente primeiro)
        """
        query = CombatLog.query.filter_by(session_id=session_id)

        if combat_id is not None:
            query = query.filter_by(combat_id=combat_id)

        logs = query.order_by(CombatLog.timestamp.desc()).limit(limit).all()

        return logs

    @staticmethod
    def clear_combat_logs(session_id: int, combat_id: Optional[int] = None) -> int:
        """
        Limpa logs de combate.

        Args:
            session_id: ID da sessão
            combat_id: Limpar apenas logs de um combate específico (opcional)

        Returns:
            Número de logs apagados
        """
        query = CombatLog.query.filter_by(session_id=session_id)

        if combat_id is not None:
            query = query.filter_by(combat_id=combat_id)

        count = query.count()
        query.delete()
        db.session.commit()

        return count
