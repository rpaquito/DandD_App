"""
Serviço de Geração de Encontros

Gera encontros balanceados usando o sistema de XP budgets do D&D 5ª Edição.
"""

import random
from typing import List, Dict, Optional, Tuple


class EncounterGeneratorService:
    """Serviço para gerar encontros balanceados por dificuldade."""

    # Tabela de XP Thresholds por nível (D&D 5e)
    XP_THRESHOLDS = {
        1: {'easy': 25, 'medium': 50, 'hard': 75, 'deadly': 100},
        2: {'easy': 50, 'medium': 100, 'hard': 150, 'deadly': 200},
        3: {'easy': 75, 'medium': 150, 'hard': 225, 'deadly': 400},
        4: {'easy': 125, 'medium': 250, 'hard': 375, 'deadly': 500},
        5: {'easy': 250, 'medium': 500, 'hard': 750, 'deadly': 1100},
        6: {'easy': 300, 'medium': 600, 'hard': 900, 'deadly': 1400},
        7: {'easy': 350, 'medium': 750, 'hard': 1100, 'deadly': 1700},
        8: {'easy': 450, 'medium': 900, 'hard': 1400, 'deadly': 2100},
        9: {'easy': 550, 'medium': 1100, 'hard': 1600, 'deadly': 2400},
        10: {'easy': 600, 'medium': 1200, 'hard': 1900, 'deadly': 2800},
        11: {'easy': 800, 'medium': 1600, 'hard': 2400, 'deadly': 3600},
        12: {'easy': 1000, 'medium': 2000, 'hard': 3000, 'deadly': 4500},
        13: {'easy': 1100, 'medium': 2200, 'hard': 3400, 'deadly': 5100},
        14: {'easy': 1250, 'medium': 2500, 'hard': 3800, 'deadly': 5700},
        15: {'easy': 1400, 'medium': 2800, 'hard': 4300, 'deadly': 6400},
        16: {'easy': 1600, 'medium': 3200, 'hard': 4800, 'deadly': 7200},
        17: {'easy': 2000, 'medium': 3900, 'hard': 5900, 'deadly': 8800},
        18: {'easy': 2100, 'medium': 4200, 'hard': 6300, 'deadly': 9500},
        19: {'easy': 2400, 'medium': 4900, 'hard': 7300, 'deadly': 10900},
        20: {'easy': 2800, 'medium': 5700, 'hard': 8500, 'deadly': 12700}
    }

    # Multiplicadores de Encontro (D&D 5e)
    # Baseado no número de monstros
    MULTIPLIERS = [
        (1, 1.0),      # 1 monstro
        (2, 1.5),      # 2 monstros
        (3, 2.0),      # 3-6 monstros
        (7, 2.5),      # 7-10 monstros
        (11, 3.0),     # 11-14 monstros
        (15, 4.0)      # 15+ monstros
    ]

    def calculate_xp_budget(self, party_levels: List[int], difficulty: str) -> int:
        """
        Calcula o XP budget para o encontro baseado nos níveis do grupo.

        Args:
            party_levels: Lista de níveis dos jogadores
            difficulty: Dificuldade ('easy', 'medium', 'hard', 'deadly')

        Returns:
            XP total do budget
        """
        if not party_levels:
            return 0

        if difficulty not in ['easy', 'medium', 'hard', 'deadly']:
            difficulty = 'medium'

        total_xp = 0
        for level in party_levels:
            # Limitar nível entre 1 e 20
            level = max(1, min(20, level))
            total_xp += self.XP_THRESHOLDS[level][difficulty]

        return total_xp

    def get_encounter_multiplier(self, num_monsters: int) -> float:
        """
        Retorna o multiplicador de encontro baseado no número de monstros.

        Args:
            num_monsters: Número de monstros no encontro

        Returns:
            Multiplicador (1.0, 1.5, 2.0, 2.5, 3.0, ou 4.0)
        """
        if num_monsters <= 0:
            return 1.0

        # Encontrar multiplicador apropriado
        for threshold, multiplier in self.MULTIPLIERS:
            if num_monsters < threshold:
                return multiplier

        # Se for 15+ monstros
        return 4.0

    def _select_monsters(
        self,
        monster_pool: List[Dict],
        budget: int,
        max_monsters: int = 10,
        min_monsters: int = 1
    ) -> List[Dict]:
        """
        Seleciona monstros do pool usando algoritmo greedy randomizado.

        Args:
            monster_pool: Lista de monstros disponíveis
            budget: XP budget para o encontro
            max_monsters: Número máximo de monstros
            min_monsters: Número mínimo de monstros

        Returns:
            Lista de monstros selecionados com quantidades
        """
        if not monster_pool or budget <= 0:
            return []

        # Filtrar monstros muito caros (mais de 50% do budget)
        affordable = [m for m in monster_pool if m.get('xp', 0) <= budget * 0.5]
        if not affordable:
            # Se todos são muito caros, pegar o mais barato
            affordable = [min(monster_pool, key=lambda m: m.get('xp', 0))]

        selected = []
        remaining_budget = budget
        remaining_slots = max_monsters

        # Algoritmo greedy com randomização
        attempts = 0
        max_attempts = 50

        while remaining_slots > 0 and attempts < max_attempts:
            attempts += 1

            # Filtrar monstros que cabem no budget com multiplicador
            candidates = []
            for monster in affordable:
                xp = monster.get('xp', 0)
                # Simular adição deste monstro
                test_total = sum(m['xp'] * m['quantity'] for m in selected) + xp
                test_count = sum(m['quantity'] for m in selected) + 1
                adjusted_xp = test_total * self.get_encounter_multiplier(test_count)

                if adjusted_xp <= budget * 1.2:  # Margem de 20%
                    candidates.append(monster)

            if not candidates:
                break

            # Escolher aleatoriamente entre os candidatos
            chosen = random.choice(candidates)

            # Verificar se já existe na lista
            existing = next((m for m in selected if m['id'] == chosen['id']), None)
            if existing and remaining_slots > 0:
                existing['quantity'] += 1
                remaining_slots -= 1
            elif remaining_slots > 0:
                selected.append({
                    'id': chosen['id'],
                    'nome': chosen['nome'],
                    'xp': chosen['xp'],
                    'cr': chosen.get('cr', '0'),
                    'tipo': chosen.get('tipo', 'Desconhecido'),
                    'ac': chosen.get('ac', 10),
                    'hp_max': chosen.get('hp_max', 10),
                    'quantity': 1
                })
                remaining_slots -= 1

            # Recalcular budget restante
            current_total = sum(m['xp'] * m['quantity'] for m in selected)
            current_count = sum(m['quantity'] for m in selected)
            current_adjusted = current_total * self.get_encounter_multiplier(current_count)

            if current_adjusted >= budget * 0.9:  # 90% do budget atingido
                break

        # Se não atingiu mínimo de monstros, adicionar mais
        current_count = sum(m['quantity'] for m in selected)
        if current_count < min_monsters and affordable:
            cheapest = min(affordable, key=lambda m: m.get('xp', 0))
            needed = min_monsters - current_count

            existing = next((m for m in selected if m['id'] == cheapest['id']), None)
            if existing:
                existing['quantity'] += needed
            else:
                selected.append({
                    'id': cheapest['id'],
                    'nome': cheapest['nome'],
                    'xp': cheapest['xp'],
                    'cr': cheapest.get('cr', '0'),
                    'tipo': cheapest.get('tipo', 'Desconhecido'),
                    'ac': cheapest.get('ac', 10),
                    'hp_max': cheapest.get('hp_max', 10),
                    'quantity': needed
                })

        return selected

    def generate_encounter(
        self,
        party_levels: List[int],
        difficulty: str,
        monster_pool: List[Dict],
        max_monsters: int = 10,
        min_monsters: int = 1
    ) -> Dict:
        """
        Gera um encontro balanceado.

        Args:
            party_levels: Lista de níveis dos jogadores
            difficulty: Dificuldade ('easy', 'medium', 'hard', 'deadly')
            monster_pool: Pool de monstros disponíveis
            max_monsters: Número máximo de monstros
            min_monsters: Número mínimo de monstros

        Returns:
            Dicionário com informações do encontro gerado:
            {
                'difficulty': str,
                'party_size': int,
                'party_levels': list,
                'xp_budget': int,
                'monsters': list,
                'total_xp': int,
                'adjusted_xp': int,
                'multiplier': float,
                'num_monsters': int
            }
        """
        # Calcular budget
        xp_budget = self.calculate_xp_budget(party_levels, difficulty)

        # Selecionar monstros
        selected_monsters = self._select_monsters(
            monster_pool,
            xp_budget,
            max_monsters,
            min_monsters
        )

        # Calcular XP total e ajustado
        total_xp = sum(m['xp'] * m['quantity'] for m in selected_monsters)
        num_monsters = sum(m['quantity'] for m in selected_monsters)
        multiplier = self.get_encounter_multiplier(num_monsters)
        adjusted_xp = int(total_xp * multiplier)

        return {
            'difficulty': difficulty,
            'party_size': len(party_levels),
            'party_levels': party_levels,
            'xp_budget': xp_budget,
            'monsters': selected_monsters,
            'total_xp': total_xp,
            'adjusted_xp': adjusted_xp,
            'multiplier': multiplier,
            'num_monsters': num_monsters
        }

    def get_difficulty_from_xp(
        self,
        party_levels: List[int],
        adjusted_xp: int
    ) -> str:
        """
        Determina a dificuldade real de um encontro baseado no XP ajustado.

        Args:
            party_levels: Lista de níveis dos jogadores
            adjusted_xp: XP ajustado do encontro

        Returns:
            Dificuldade estimada ('trivial', 'easy', 'medium', 'hard', 'deadly')
        """
        if not party_levels:
            return 'medium'

        # Calcular thresholds para o grupo
        thresholds = {
            'easy': self.calculate_xp_budget(party_levels, 'easy'),
            'medium': self.calculate_xp_budget(party_levels, 'medium'),
            'hard': self.calculate_xp_budget(party_levels, 'hard'),
            'deadly': self.calculate_xp_budget(party_levels, 'deadly')
        }

        if adjusted_xp < thresholds['easy']:
            return 'trivial'
        elif adjusted_xp < thresholds['medium']:
            return 'easy'
        elif adjusted_xp < thresholds['hard']:
            return 'medium'
        elif adjusted_xp < thresholds['deadly']:
            return 'hard'
        else:
            return 'deadly'
