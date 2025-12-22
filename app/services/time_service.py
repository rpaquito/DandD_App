"""Servico centralizado de gestao de tempo para sessoes de D&D.

Gere 4 sistemas de tempo:
1. Tempo de Sessao (real-world): Cronometro da sessao de jogo
2. Rondas de Combate: 6 segundos por ronda (D&D 5e)
3. Turnos de Exploracao: 10 minutos por turno
4. Tempo no Jogo: Hora do dia, dias, descansos
"""

from datetime import datetime, timedelta
from app import db
from app.models.session import GameSession, SessionCombat


class TimeTrackingService:
    """Servico de gestao dos 4 sistemas de tempo."""

    # Constantes
    COMBAT_ROUND_SECONDS = 6  # Uma ronda de combate D&D = 6 segundos
    EXPLORATION_TURN_MINUTES = 10  # Um turno de exploracao = 10 minutos
    SHORT_REST_HOURS = 1  # Descanso curto = 1 hora
    LONG_REST_HOURS = 8  # Descanso longo = 8 horas

    # ===== 1. TEMPO DE SESSAO (REAL-WORLD) =====

    def start_session_timer(self, session_id: int):
        """Iniciar cronometro de sessao.

        Args:
            session_id: ID da sessao de jogo

        Returns:
            True se iniciado com sucesso, False caso contrario
        """
        session = GameSession.query.get(session_id)
        if not session:
            return False

        session.sessao_iniciada_em = datetime.utcnow()
        session.sessao_pausada_em = None
        db.session.commit()
        return True

    def pause_session_timer(self, session_id: int):
        """Pausar cronometro e acumular tempo.

        Args:
            session_id: ID da sessao de jogo

        Returns:
            Tempo total em segundos, ou 0 se falha
        """
        session = GameSession.query.get(session_id)
        if not session or not session.sessao_iniciada_em:
            return 0

        now = datetime.utcnow()
        elapsed = (now - session.sessao_iniciada_em).total_seconds()
        session.tempo_total_segundos += int(elapsed)
        session.sessao_pausada_em = now
        session.sessao_iniciada_em = None
        db.session.commit()

        return session.tempo_total_segundos

    def get_session_duration(self, session_id: int) -> dict:
        """Obter duracao total da sessao (incluindo tempo atual se activo).

        Args:
            session_id: ID da sessao de jogo

        Returns:
            Dicionario com tempo total em varios formatos
        """
        session = GameSession.query.get(session_id)
        if not session:
            return {"total_seconds": 0, "hours": 0, "minutes": 0, "formatted": "0h 0m"}

        total = session.tempo_total_segundos

        # Adicionar tempo activo se o cronometro estiver a correr
        if session.sessao_iniciada_em:
            elapsed = (datetime.utcnow() - session.sessao_iniciada_em).total_seconds()
            total += int(elapsed)

        hours = total // 3600
        minutes = (total % 3600) // 60

        return {
            "total_seconds": total,
            "hours": hours,
            "minutes": minutes,
            "formatted": f"{hours}h {minutes}m"
        }

    def is_session_timer_running(self, session_id: int) -> bool:
        """Verifica se o cronometro da sessao esta activo.

        Args:
            session_id: ID da sessao de jogo

        Returns:
            True se activo, False caso contrario
        """
        session = GameSession.query.get(session_id)
        return session and session.sessao_iniciada_em is not None

    # ===== 2. RONDAS DE COMBATE (6 SEGUNDOS) =====

    def start_combat_round_timer(self, session_id: int):
        """Iniciar timer da ronda de combate.

        Args:
            session_id: ID da sessao de jogo

        Returns:
            True se iniciado, False caso contrario
        """
        combat = SessionCombat.query.filter_by(session_id=session_id).first()
        if not combat:
            return False

        combat.tempo_ronda_inicio = datetime.utcnow()

        # Se e a primeira ronda, iniciar timer do combate
        if combat.ronda_atual == 1 and not combat.tempo_inicio_combate:
            combat.tempo_inicio_combate = datetime.utcnow()

        db.session.commit()
        return True

    def end_combat_round(self, session_id: int):
        """Finalizar ronda de combate e acumular tempo.

        Args:
            session_id: ID da sessao de jogo
        """
        combat = SessionCombat.query.filter_by(session_id=session_id).first()
        if combat and combat.tempo_ronda_inicio:
            elapsed = (datetime.utcnow() - combat.tempo_ronda_inicio).total_seconds()
            combat.duracao_total_segundos += int(elapsed)
            combat.tempo_ronda_inicio = None
            db.session.commit()

    def get_combat_time(self, session_id: int) -> dict:
        """Calcular tempo de combate (rounds e tempo real).

        Args:
            session_id: ID da sessao de jogo

        Returns:
            Dicionario com informacao de tempo de combate
        """
        combat = SessionCombat.query.filter_by(session_id=session_id).first()
        if not combat or not combat.activo:
            return {
                "rounds": 0,
                "game_seconds": 0,
                "game_formatted": "0s",
                "real_seconds": 0,
                "real_formatted": "0m 0s"
            }

        # Tempo no jogo (6 segundos por ronda)
        game_seconds = combat.ronda_atual * self.COMBAT_ROUND_SECONDS

        # Tempo real
        real_seconds = combat.duracao_total_segundos
        if combat.tempo_inicio_combate:
            current_elapsed = (datetime.utcnow() - combat.tempo_inicio_combate).total_seconds()
            real_seconds = int(current_elapsed)

        real_minutes = real_seconds // 60
        real_secs = real_seconds % 60

        return {
            "rounds": combat.ronda_atual,
            "game_seconds": game_seconds,
            "game_formatted": f"{game_seconds}s ({game_seconds // 60}m {game_seconds % 60}s)",
            "real_seconds": real_seconds,
            "real_formatted": f"{real_minutes}m {real_secs}s"
        }

    # ===== 3. TURNOS DE EXPLORACAO (10 MINUTOS) =====

    def advance_exploration_turn(self, session_id: int, turns: int = 1):
        """Avancar turnos de exploracao (10 minutos cada).

        Args:
            session_id: ID da sessao de jogo
            turns: Numero de turnos a avancar (padrao: 1)

        Returns:
            Total de turnos de exploracao
        """
        session = GameSession.query.get(session_id)
        if not session:
            return 0

        session.turnos_exploracao_total += turns

        # Avancar tempo no jogo tambem
        self.advance_game_time(session_id, minutes=turns * self.EXPLORATION_TURN_MINUTES)

        db.session.commit()
        return session.turnos_exploracao_total

    def get_exploration_turns(self, session_id: int) -> int:
        """Obter total de turnos de exploracao.

        Args:
            session_id: ID da sessao de jogo

        Returns:
            Numero de turnos
        """
        session = GameSession.query.get(session_id)
        return session.turnos_exploracao_total if session else 0

    # ===== 4. TEMPO NO JOGO (IN-GAME TIME) =====

    def advance_game_time(self, session_id: int, seconds: int = 0, minutes: int = 0, hours: int = 0, days: int = 0):
        """Avancar tempo no jogo.

        Args:
            session_id: ID da sessao de jogo
            seconds: Segundos a avancar
            minutes: Minutos a avancar
            hours: Horas a avancar
            days: Dias a avancar

        Returns:
            Dicionario com novo tempo no jogo, ou None se falha
        """
        session = GameSession.query.get(session_id)
        if not session:
            return None

        # Parse tempo actual (tentar com segundos primeiro, depois sem)
        try:
            current_time = datetime.strptime(session.tempo_jogo_atual, "%H:%M:%S")
        except (ValueError, TypeError):
            try:
                current_time = datetime.strptime(session.tempo_jogo_atual, "%H:%M")
            except (ValueError, TypeError):
                # Se falhar, usar tempo padrao
                current_time = datetime.strptime("08:00:00", "%H:%M:%S")
                session.tempo_jogo_atual = "08:00:00"

        # Adicionar tempo
        new_time = current_time + timedelta(seconds=seconds, minutes=minutes, hours=hours, days=days)

        # Calcular dias adicionais (rollover de 24h)
        days_passed = (new_time - current_time).days
        session.dia_jogo_atual += days_passed

        # Actualizar hora (manter apenas HH:MM:SS, ignorar dias)
        session.tempo_jogo_atual = new_time.strftime("%H:%M:%S")

        db.session.commit()

        return {
            "dia": session.dia_jogo_atual,
            "hora": session.tempo_jogo_atual,
            "formatted": f"Dia {session.dia_jogo_atual}, {session.tempo_jogo_atual}"
        }

    def get_game_time(self, session_id: int) -> dict:
        """Obter tempo actual no jogo.

        Args:
            session_id: ID da sessao de jogo

        Returns:
            Dicionario com tempo no jogo
        """
        session = GameSession.query.get(session_id)
        if not session:
            return {"dia": 1, "hora": "08:00:00", "formatted": "Dia 1, 08:00:00"}

        # Garantir que tem formato com segundos
        hora = session.tempo_jogo_atual
        if hora and hora.count(':') == 1:
            # Se só tem HH:MM, adicionar :00
            hora = hora + ":00"

        return {
            "dia": session.dia_jogo_atual,
            "hora": hora,
            "formatted": f"Dia {session.dia_jogo_atual}, {hora}"
        }

    def set_game_time(self, session_id: int, dia: int, hora: str):
        """Definir tempo no jogo manualmente.

        Args:
            session_id: ID da sessao de jogo
            dia: Dia a definir
            hora: Hora a definir (formato "HH:MM" ou "HH:MM:SS")

        Returns:
            True se sucesso, False caso contrario
        """
        session = GameSession.query.get(session_id)
        if not session:
            return False

        # Validar formato de hora (aceitar HH:MM ou HH:MM:SS)
        try:
            datetime.strptime(hora, "%H:%M:%S")
        except ValueError:
            try:
                # Se falhar com segundos, tentar sem segundos e adicionar :00
                datetime.strptime(hora, "%H:%M")
                hora = hora + ":00"
            except ValueError:
                return False

        session.dia_jogo_atual = dia
        session.tempo_jogo_atual = hora
        db.session.commit()
        return True

    # ===== DESCANSOS =====

    def register_rest(self, session_id: int, rest_type: str):
        """Registar descanso (curto ou longo).

        Args:
            session_id: ID da sessao de jogo
            rest_type: 'curto' (1h) ou 'longo' (8h)

        Returns:
            Dicionario com info do descanso, ou None se falha
        """
        session = GameSession.query.get(session_id)
        if not session:
            return None

        now = datetime.utcnow()

        if rest_type == 'curto':
            session.ultimo_descanso_curto = now
            hours_advanced = self.SHORT_REST_HOURS
        elif rest_type == 'longo':
            session.ultimo_descanso_longo = now
            hours_advanced = self.LONG_REST_HOURS
        else:
            return None

        # Avancar tempo no jogo
        game_time = self.advance_game_time(session_id, hours=hours_advanced)

        db.session.commit()

        return {
            "tipo": rest_type,
            "horas": hours_advanced,
            "registado_em": now.isoformat(),
            "novo_tempo_jogo": game_time
        }

    def get_last_rest_info(self, session_id: int) -> dict:
        """Obter informacao sobre ultimos descansos.

        Args:
            session_id: ID da sessao de jogo

        Returns:
            Dicionario com info dos descansos
        """
        session = GameSession.query.get(session_id)
        if not session:
            return {"curto": None, "longo": None}

        return {
            "curto": session.ultimo_descanso_curto.isoformat() if session.ultimo_descanso_curto else None,
            "longo": session.ultimo_descanso_longo.isoformat() if session.ultimo_descanso_longo else None
        }

    # ===== UTILIDADES =====

    def get_all_time_status(self, session_id: int) -> dict:
        """Obter estado completo de todos os sistemas de tempo.

        Args:
            session_id: ID da sessao de jogo

        Returns:
            Dicionario com todos os tempos
        """
        return {
            "session_duration": self.get_session_duration(session_id),
            "session_running": self.is_session_timer_running(session_id),
            "combat_time": self.get_combat_time(session_id),
            "exploration_turns": self.get_exploration_turns(session_id),
            "game_time": self.get_game_time(session_id),
            "last_rests": self.get_last_rest_info(session_id)
        }
