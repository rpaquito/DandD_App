"""Modelos para aventuras/quests."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class NPC:
    """Personagem não-jogável."""
    id: str
    nome: str
    descricao: str
    personalidade: str = ""
    motivacao: str = ""
    dialogos: list = field(default_factory=list)
    localizacao: str = ""


@dataclass
class QuestStep:
    """Um passo/cena da aventura."""
    id: int
    titulo: str
    texto_jogadores: str  # Texto para ler aos jogadores
    notas_mestre: str = ""  # Notas privadas para o Mestre
    dicas_improvisacao: list = field(default_factory=list)
    npcs: list = field(default_factory=list)  # IDs dos NPCs presentes
    monstros: list = field(default_factory=list)  # IDs dos monstros
    proximos_passos: list = field(default_factory=list)  # IDs dos passos seguintes
    tipo: str = "narrativa"  # narrativa, combate, puzzle, social
    recompensas: list = field(default_factory=list)


@dataclass
class Quest:
    """Uma aventura completa."""
    id: str
    titulo: str
    descricao: str
    nivel_min: int = 1
    nivel_max: int = 3
    passos: list = field(default_factory=list)
    npcs: dict = field(default_factory=dict)  # id -> NPC
    monstros: dict = field(default_factory=dict)  # id -> Monster
    mapas: list = field(default_factory=list)

    def get_step(self, step_id: int) -> Optional[QuestStep]:
        """Obter um passo pelo ID."""
        for step in self.passos:
            if step.id == step_id:
                return step
        return None

    def get_npc(self, npc_id: str) -> Optional[NPC]:
        """Obter um NPC pelo ID."""
        return self.npcs.get(npc_id)

    def get_npcs_for_step(self, step: QuestStep) -> list:
        """Obter todos os NPCs presentes num passo."""
        return [self.npcs[npc_id] for npc_id in step.npcs if npc_id in self.npcs]

    def get_monsters_for_step(self, step: QuestStep) -> list:
        """Obter todos os monstros num passo."""
        return [self.monstros[m_id] for m_id in step.monstros if m_id in self.monstros]
