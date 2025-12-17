"""Serviço para carregar e gerir aventuras a partir de ficheiros JSON."""

import json
import os
from flask import current_app
from app.models.quest import Quest, QuestStep, NPC
from app.models.character import Monster


class QuestLoader:
    """Carrega aventuras a partir de ficheiros JSON."""

    def __init__(self):
        self._quests_cache = {}

    def _get_quests_folder(self) -> str:
        """Obter pasta de aventuras."""
        return current_app.config.get('QUESTS_FOLDER', 'app/data/quests')

    def get_all_quests(self) -> list:
        """Obter lista de todas as aventuras disponíveis."""
        quests = []
        quests_folder = self._get_quests_folder()

        if not os.path.exists(quests_folder):
            return quests

        for filename in os.listdir(quests_folder):
            if filename.endswith('.json'):
                quest_id = filename[:-5]  # Remover .json
                quest = self.get_quest(quest_id)
                if quest:
                    quests.append(quest)

        return quests

    def get_quest(self, quest_id: str) -> Quest | None:
        """Carregar uma aventura específica."""
        if quest_id in self._quests_cache:
            return self._quests_cache[quest_id]

        quests_folder = self._get_quests_folder()
        filepath = os.path.join(quests_folder, f'{quest_id}.json')

        if not os.path.exists(filepath):
            return None

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        quest = self._parse_quest(quest_id, data)
        self._quests_cache[quest_id] = quest
        return quest

    def _parse_quest(self, quest_id: str, data: dict) -> Quest:
        """Converter dados JSON numa Quest."""
        # Parse NPCs
        npcs = {}
        for npc_data in data.get('npcs', []):
            npc = NPC(
                id=npc_data['id'],
                nome=npc_data['nome'],
                descricao=npc_data.get('descricao', ''),
                personalidade=npc_data.get('personalidade', ''),
                motivacao=npc_data.get('motivacao', ''),
                dialogos=npc_data.get('dialogos', []),
                localizacao=npc_data.get('localizacao', '')
            )
            npcs[npc.id] = npc

        # Parse Monstros
        monstros = {}
        for monster_data in data.get('monstros', []):
            monster = Monster(
                id=monster_data['id'],
                nome=monster_data['nome'],
                tamanho=monster_data.get('tamanho', 'Médio'),
                tipo=monster_data.get('tipo', 'Humanoide'),
                alinhamento=monster_data.get('alinhamento', 'Neutro'),
                ac=monster_data.get('ac', 10),
                hp_max=monster_data.get('hp_max', 10),
                hp_dice=monster_data.get('hp_dice', '2d8'),
                velocidade=monster_data.get('velocidade', '9m'),
                forca=monster_data.get('forca', 10),
                destreza=monster_data.get('destreza', 10),
                constituicao=monster_data.get('constituicao', 10),
                inteligencia=monster_data.get('inteligencia', 10),
                sabedoria=monster_data.get('sabedoria', 10),
                carisma=monster_data.get('carisma', 10),
                cr=monster_data.get('cr', '1/4'),
                xp=monster_data.get('xp', 50),
                acoes=monster_data.get('acoes', []),
                resistencias=monster_data.get('resistencias', []),
                imunidades=monster_data.get('imunidades', []),
                vulnerabilidades=monster_data.get('vulnerabilidades', []),
                imunidades_condicao=monster_data.get('imunidades_condicao', []),
                sentidos=monster_data.get('sentidos', ''),
                idiomas=monster_data.get('idiomas', []),
                habilidades_especiais=monster_data.get('habilidades_especiais', [])
            )
            monstros[monster.id] = monster

        # Parse Passos
        passos = []
        for step_data in data.get('passos', []):
            step = QuestStep(
                id=step_data['id'],
                titulo=step_data['titulo'],
                texto_jogadores=step_data.get('texto_jogadores', ''),
                notas_mestre=step_data.get('notas_mestre', ''),
                dicas_improvisacao=step_data.get('dicas_improvisacao', []),
                npcs=step_data.get('npcs', []),
                monstros=step_data.get('monstros', []),
                proximos_passos=step_data.get('proximos_passos', []),
                tipo=step_data.get('tipo', 'narrativa'),
                recompensas=step_data.get('recompensas', [])
            )
            passos.append(step)

        return Quest(
            id=quest_id,
            titulo=data.get('titulo', 'Aventura sem nome'),
            descricao=data.get('descricao', ''),
            nivel_min=data.get('nivel_min', 1),
            nivel_max=data.get('nivel_max', 3),
            passos=passos,
            npcs=npcs,
            monstros=monstros,
            mapas=data.get('mapas', [])
        )

    def reload_quest(self, quest_id: str) -> Quest | None:
        """Forçar recarregamento de uma aventura."""
        if quest_id in self._quests_cache:
            del self._quests_cache[quest_id]
        return self.get_quest(quest_id)
