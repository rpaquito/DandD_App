"""Modelos para personagens e monstros."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Monster:
    """Um monstro do D&D 5e."""
    id: str
    nome: str
    tamanho: str  # Minúsculo, Pequeno, Médio, Grande, Enorme, Colossal
    tipo: str  # Morto-vivo, Besta, Humanoide, etc.
    alinhamento: str = "Neutro"

    # Estatísticas de combate
    ac: int = 10
    hp_max: int = 10
    hp_dice: str = "2d8"  # Dados de vida
    velocidade: str = "9m"

    # Atributos (6 stats)
    forca: int = 10
    destreza: int = 10
    constituicao: int = 10
    inteligencia: int = 10
    sabedoria: int = 10
    carisma: int = 10

    # Combate
    cr: str = "1/4"  # Challenge Rating
    xp: int = 50
    acoes: list = field(default_factory=list)  # Lista de ações
    acoes_bonus: list = field(default_factory=list)
    reacoes: list = field(default_factory=list)
    acoes_lendarias: list = field(default_factory=list)

    # Defesas
    resistencias: list = field(default_factory=list)
    imunidades: list = field(default_factory=list)
    vulnerabilidades: list = field(default_factory=list)
    imunidades_condicao: list = field(default_factory=list)

    # Sentidos e habilidades
    sentidos: str = "visão no escuro 18m"
    idiomas: list = field(default_factory=list)
    habilidades_especiais: list = field(default_factory=list)

    def get_modifier(self, stat_value: int) -> int:
        """Calcular modificador de atributo."""
        return (stat_value - 10) // 2

    @property
    def mod_forca(self) -> int:
        return self.get_modifier(self.forca)

    @property
    def mod_destreza(self) -> int:
        return self.get_modifier(self.destreza)

    @property
    def mod_constituicao(self) -> int:
        return self.get_modifier(self.constituicao)

    @property
    def mod_inteligencia(self) -> int:
        return self.get_modifier(self.inteligencia)

    @property
    def mod_sabedoria(self) -> int:
        return self.get_modifier(self.sabedoria)

    @property
    def mod_carisma(self) -> int:
        return self.get_modifier(self.carisma)


@dataclass
class Character:
    """Ficha de personagem jogável."""
    nome: str
    classe: str
    nivel: int = 1
    raca: str = "Humano"

    # Atributos
    forca: int = 10
    destreza: int = 10
    constituicao: int = 10
    inteligencia: int = 10
    sabedoria: int = 10
    carisma: int = 10

    # Combate
    ac: int = 10
    hp_max: int = 10
    hp_atual: int = 10
    velocidade: str = "9m"

    # Proficiências
    bonus_proficiencia: int = 2
    pericias_proficientes: list = field(default_factory=list)
    salvaguardas_proficientes: list = field(default_factory=list)

    # Equipamento e notas
    equipamento: list = field(default_factory=list)
    notas: str = ""
