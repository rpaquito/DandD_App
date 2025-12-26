"""Servico para gestao de sessoes de jogo."""

import json
import os
from flask import current_app
from app import db
from app.models.session import GameSession, SessionPlayer, SessionCombat, SavedCharacter


class SessionService:
    """Servico para operacoes com sessoes de jogo."""

    def get_all_sessions(self):
        """Obter todas as sessoes ordenadas por data de atualizacao."""
        return GameSession.query.order_by(GameSession.atualizado_em.desc()).all()

    def get_active_sessions(self):
        """Obter sessoes activas."""
        return GameSession.query.filter_by(estado='activa').order_by(
            GameSession.atualizado_em.desc()
        ).all()

    def get_session(self, session_id):
        """Obter uma sessao por ID."""
        return GameSession.query.get(session_id)

    def get_sessions_for_quest(self, quest_id):
        """Obter todas as sessoes de uma aventura."""
        return GameSession.get_for_quest(quest_id)

    def count_sessions_for_quest(self, quest_id):
        """Contar sessoes activas/pausadas de uma aventura."""
        return GameSession.count_for_quest(quest_id)

    def can_create_session_for_quest(self, quest_id):
        """Verificar se pode criar nova sessao (max 2 por aventura)."""
        return GameSession.can_create_for_quest(quest_id)

    def create_quest_session(self, quest_id, quest_title):
        """Criar uma nova sessao para uma aventura."""
        if not self.can_create_session_for_quest(quest_id):
            return None

        # Determinar numero da sessao
        count = self.count_sessions_for_quest(quest_id)
        nome = f"{quest_title} - Sessao {count + 1}"

        session = GameSession(nome=nome, quest_id=quest_id)
        db.session.add(session)
        db.session.commit()
        return session

    def create_session(self, nome, quest_id=None):
        """Criar uma nova sessao."""
        session = GameSession(nome=nome, quest_id=quest_id)
        db.session.add(session)
        db.session.commit()
        return session

    def update_session(self, session_id, **kwargs):
        """Atualizar uma sessao."""
        session = self.get_session(session_id)
        if not session:
            return None

        for key, value in kwargs.items():
            if hasattr(session, key):
                setattr(session, key, value)

        db.session.commit()
        return session

    def delete_session(self, session_id):
        """Apagar uma sessao e todos os dados associados."""
        session = self.get_session(session_id)
        if not session:
            return False

        db.session.delete(session)
        db.session.commit()
        return True

    def set_quest(self, session_id, quest_id):
        """Definir a aventura de uma sessao."""
        return self.update_session(session_id, quest_id=quest_id, passo_atual=1)

    def update_progress(self, session_id, step_id):
        """Atualizar o progresso na aventura."""
        return self.update_session(session_id, passo_atual=step_id)

    def add_player_from_template(self, session_id, template_data, nome_jogador):
        """Adicionar um jogador a partir de um template de personagem."""
        session = self.get_session(session_id)
        if not session:
            return None

        player = SessionPlayer(
            session_id=session_id,
            nome_jogador=nome_jogador,
            character_data=json.dumps(template_data, ensure_ascii=False),
            hp_atual=template_data.get('hp_max', 10),
            hp_max=template_data.get('hp_max', 10)
        )
        db.session.add(player)
        db.session.commit()
        return player

    def add_player_from_saved(self, session_id, saved_character_id, nome_jogador):
        """Adicionar um jogador a partir de um personagem guardado."""
        session = self.get_session(session_id)
        saved_char = SavedCharacter.query.get(saved_character_id)
        if not session or not saved_char:
            return None

        char_data = saved_char.get_character_data()
        player = SessionPlayer(
            session_id=session_id,
            nome_jogador=nome_jogador,
            character_data=saved_char.character_data,
            hp_atual=char_data.get('hp_max', 10),
            hp_max=char_data.get('hp_max', 10)
        )
        db.session.add(player)
        db.session.commit()
        return player

    def add_custom_player(self, session_id, nome_jogador, character_data):
        """Adicionar um jogador com dados personalizados."""
        session = self.get_session(session_id)
        if not session:
            return None

        player = SessionPlayer(
            session_id=session_id,
            nome_jogador=nome_jogador,
            character_data=json.dumps(character_data, ensure_ascii=False),
            hp_atual=character_data.get('hp_max', 10),
            hp_max=character_data.get('hp_max', 10)
        )
        db.session.add(player)
        db.session.commit()
        return player

    def get_session_players(self, session_id):
        """Obter todos os jogadores de uma sessao."""
        return SessionPlayer.query.filter_by(session_id=session_id).all()

    def get_player(self, player_id):
        """Obter um jogador por ID."""
        return SessionPlayer.query.get(player_id)

    def update_player(self, player_id, **kwargs):
        """Atualizar um jogador."""
        player = self.get_player(player_id)
        if not player:
            return None

        for key, value in kwargs.items():
            if hasattr(player, key):
                setattr(player, key, value)

        db.session.commit()
        return player

    def update_player_hp(self, player_id, hp_change, is_damage=True):
        """Atualizar HP de um jogador."""
        player = self.get_player(player_id)
        if not player:
            return None

        if is_damage:
            player.hp_atual = max(0, player.hp_atual - hp_change)
        else:
            player.hp_atual = min(player.hp_max, player.hp_atual + hp_change)

        db.session.commit()
        return player

    def toggle_player_condition(self, player_id, condition):
        """Adicionar ou remover uma condicao de um jogador."""
        player = self.get_player(player_id)
        if not player:
            return None

        condicoes = player.get_condicoes()
        if condition in condicoes:
            condicoes.remove(condition)
        else:
            condicoes.append(condition)

        player.set_condicoes(condicoes)
        db.session.commit()
        return player

    def remove_player(self, player_id):
        """Remover um jogador de uma sessao."""
        player = self.get_player(player_id)
        if not player:
            return False

        db.session.delete(player)
        db.session.commit()
        return True

    def get_session_combat(self, session_id):
        """Obter o estado de combate de uma sessao."""
        return SessionCombat.query.filter_by(session_id=session_id).first()

    def start_combat(self, session_id, participants, quest_step_id=None):
        """Iniciar um combate numa sessao."""
        combat = self.get_session_combat(session_id)

        if not combat:
            combat = SessionCombat(session_id=session_id)
            db.session.add(combat)

        combat.activo = True
        combat.ronda_atual = 1
        combat.turno_atual = 0
        combat.quest_step_id = quest_step_id
        combat.set_participantes(participants)

        db.session.commit()
        return combat

    def end_combat(self, session_id):
        """Terminar um combate e sincronizar estado dos jogadores."""
        combat = self.get_session_combat(session_id)
        if not combat or not combat.activo:
            return None

        # Sincronizar HP e condicoes dos jogadores
        participants = combat.get_participantes()
        for p in participants:
            if p.get('tipo') == 'jogador' and p.get('id', '').startswith('player_'):
                try:
                    player_id = int(p['id'].replace('player_', ''))
                    player = self.get_player(player_id)
                    if player:
                        player.hp_atual = p.get('hp_atual', player.hp_atual)
                        player.set_condicoes(p.get('condicoes', []))
                except (ValueError, TypeError):
                    pass

        combat.activo = False
        db.session.commit()
        return combat

    # ===== SISTEMA DE XP =====

    # Tabela de XP para subir de nivel (D&D 5e PHB p.15)
    LEVEL_XP_THRESHOLDS = {
        1: 0,
        2: 300,
        3: 900,
        4: 2700,
        5: 6500,
        6: 14000,
        7: 23000,
        8: 34000,
        9: 48000,
        10: 64000,
        11: 85000,
        12: 100000,
        13: 120000,
        14: 140000,
        15: 165000,
        16: 195000,
        17: 225000,
        18: 265000,
        19: 305000,
        20: 355000
    }

    def award_xp_to_session(self, session_id, total_xp, source='combat', description=''):
        """
        Atribui XP a todos os jogadores de uma sessão.

        Args:
            session_id: ID da sessão
            total_xp: XP total a dividir pelos jogadores
            source: Origem do XP ('combat', 'milestone', 'quest')
            description: Descrição do que gerou o XP

        Returns:
            Dicionário com:
            {
                'xp_per_player': 100,
                'players_leveled_up': [player_id1, player_id2],
                'players_updated': [player_dict1, player_dict2, ...]
            }
        """
        players = self.get_session_players(session_id)
        if not players:
            return None

        xp_per_player = total_xp // len(players)
        leveled_up = []
        updated_players = []

        for player in players:
            old_xp = player.xp_total
            old_level = self._get_level_from_xp(old_xp)

            # Adicionar XP
            player.xp_total += xp_per_player
            new_level = self._get_level_from_xp(player.xp_total)

            # Verificar level up
            if new_level > old_level:
                leveled_up.append(player.id)

                # Atualizar nivel no character_data
                char_data = player.get_character_data()
                char_data['nivel'] = new_level
                player.set_character_data(char_data)

            updated_players.append(player.to_dict())

        db.session.commit()

        return {
            'xp_per_player': xp_per_player,
            'total_xp': total_xp,
            'source': source,
            'description': description,
            'players_leveled_up': leveled_up,
            'players_updated': updated_players,
            'num_players': len(players)
        }

    def _get_level_from_xp(self, total_xp):
        """
        Determina o nível baseado no XP total acumulado.

        Args:
            total_xp: XP total do personagem

        Returns:
            int: Nível do personagem (1-20)
        """
        # Procurar de trás para frente para encontrar o nível correto
        for level in range(20, 0, -1):
            if total_xp >= self.LEVEL_XP_THRESHOLDS[level]:
                return level
        return 1

    def get_xp_to_next_level(self, player_id):
        """
        Calcula quanto XP falta para o próximo nível.

        Args:
            player_id: ID do jogador

        Returns:
            Dicionário com informação de progresso:
            {
                'current_level': 2,
                'next_level': 3,
                'current_xp': 500,
                'needed_xp': 900,
                'remaining_xp': 400,
                'progress_percent': 55.5
            }
        """
        player = self.get_player(player_id)
        if not player:
            return None

        current_level = self._get_level_from_xp(player.xp_total)
        next_level = min(current_level + 1, 20)

        current_threshold = self.LEVEL_XP_THRESHOLDS[current_level]
        needed_threshold = self.LEVEL_XP_THRESHOLDS[next_level]

        # XP relativo ao nível atual
        xp_in_current_level = player.xp_total - current_threshold
        xp_needed_for_next = needed_threshold - current_threshold

        # Percentagem de progresso no nível atual
        if xp_needed_for_next > 0:
            progress_percent = (xp_in_current_level / xp_needed_for_next) * 100
        else:
            progress_percent = 100  # Nível máximo

        return {
            'player_id': player_id,
            'current_level': current_level,
            'next_level': next_level,
            'current_xp': player.xp_total,
            'needed_xp': needed_threshold,
            'remaining_xp': needed_threshold - player.xp_total,
            'xp_in_current_level': xp_in_current_level,
            'xp_needed_for_next': xp_needed_for_next,
            'progress_percent': round(progress_percent, 1)
        }

    def get_session_xp_overview(self, session_id):
        """
        Obtem visão geral do XP de todos os jogadores numa sessão.

        Args:
            session_id: ID da sessão

        Returns:
            Lista de dicionários com progresso de XP de cada jogador
        """
        players = self.get_session_players(session_id)
        overview = []

        for player in players:
            progress = self.get_xp_to_next_level(player.id)
            if progress:
                progress['nome_jogador'] = player.nome_jogador
                char_data = player.get_character_data()
                progress['nome_personagem'] = char_data.get('nome', 'Desconhecido')
                overview.append(progress)

        return overview


def load_character_templates():
    """Carrega os templates de personagens pre-criados."""
    characters_file = os.path.join(
        current_app.root_path, 'data', 'characters.json'
    )
    if os.path.exists(characters_file):
        with open(characters_file, 'r', encoding='utf-8') as f:
            return json.load(f).get('personagens', [])
    return []


def get_saved_characters():
    """Obter todos os personagens guardados."""
    return SavedCharacter.query.order_by(SavedCharacter.atualizado_em.desc()).all()
