"""Serviço para cálculo de XP de encontros e marcos."""


class XPCalculatorService:
    """Calculadora de XP para encontros e marcos de aventura."""

    def calculate_encounter_xp(self, defeated_monsters):
        """
        Calcula XP total de monstros derrotados.

        Args:
            defeated_monsters: Lista de dicionários com estrutura:
                [
                    {'id': 'goblin', 'nome': 'Goblin', 'xp': 50, 'quantity': 3},
                    {'id': 'hobgoblin', 'nome': 'Hobgoblin', 'xp': 100, 'quantity': 1}
                ]

        Returns:
            Dicionário com:
            {
                'total_xp': 250,
                'breakdown': [
                    {'nome': 'Goblin', 'quantity': 3, 'xp_each': 50, 'xp_total': 150},
                    {'nome': 'Hobgoblin', 'quantity': 1, 'xp_each': 100, 'xp_total': 100}
                ]
            }
        """
        total = 0
        breakdown = []

        for monster in defeated_monsters:
            quantity = monster.get('quantity', 1)
            xp_each = monster.get('xp', 0)
            xp_total = xp_each * quantity

            total += xp_total

            breakdown.append({
                'id': monster.get('id', ''),
                'nome': monster.get('nome', monster.get('id', 'Monstro')),
                'quantity': quantity,
                'xp_each': xp_each,
                'xp_total': xp_total
            })

        return {
            'total_xp': total,
            'breakdown': breakdown
        }

    def calculate_milestone_xp(self, milestone_type='minor'):
        """
        Calcula XP para marcos (milestones) da aventura.

        Args:
            milestone_type: Tipo de marco
                - 'minor': Objetivo secundário completado (100 XP)
                - 'major': Objetivo principal completado (500 XP)
                - 'story': Momento épico da história (1000 XP)

        Returns:
            int: XP do marco
        """
        milestones = {
            'minor': 100,     # Completar objetivo secundário
            'major': 500,     # Completar objetivo principal
            'story': 1000     # Momento épico da história
        }
        return milestones.get(milestone_type, 0)

    def calculate_quest_completion_xp(self, quest_level_min, quest_level_max):
        """
        Calcula XP bónus por completar uma aventura inteira.

        Args:
            quest_level_min: Nível mínimo recomendado da aventura
            quest_level_max: Nível máximo recomendado da aventura

        Returns:
            int: XP de completar a aventura
        """
        # Fórmula: média dos níveis × 200
        avg_level = (quest_level_min + quest_level_max) / 2
        return int(avg_level * 200)
