"""
Serviço de Rolls de Combate

Implementa mecânicas de attack rolls e damage rolls do D&D 5ª Edição.
"""

import random
import re
from typing import Dict, Tuple, Optional


class CombatRollService:
    """Serviço para rolls de ataque e dano."""

    @staticmethod
    def roll_d20(advantage: bool = False, disadvantage: bool = False) -> Tuple[int, Dict]:
        """
        Rola 1d20 com possível vantagem ou desvantagem.

        Args:
            advantage: Se tem vantagem (rolar 2d20, pegar o maior)
            disadvantage: Se tem desvantagem (rolar 2d20, pegar o menor)

        Returns:
            Tuple[int, dict]: (resultado final, detalhes do roll)
        """
        # Se tem ambos, cancelam-se
        if advantage and disadvantage:
            advantage = False
            disadvantage = False

        roll1 = random.randint(1, 20)

        if advantage or disadvantage:
            roll2 = random.randint(1, 20)
            if advantage:
                result = max(roll1, roll2)
                return result, {
                    'rolls': [roll1, roll2],
                    'result': result,
                    'advantage': True,
                    'dropped': min(roll1, roll2)
                }
            else:  # disadvantage
                result = min(roll1, roll2)
                return result, {
                    'rolls': [roll1, roll2],
                    'result': result,
                    'disadvantage': True,
                    'dropped': max(roll1, roll2)
                }
        else:
            return roll1, {
                'rolls': [roll1],
                'result': roll1
            }

    @staticmethod
    def roll_attack(
        bonus: int,
        target_ac: int,
        advantage: bool = False,
        disadvantage: bool = False
    ) -> Dict:
        """
        Rola um attack roll.

        Args:
            bonus: Bónus de ataque
            target_ac: AC do alvo
            advantage: Vantagem no roll
            disadvantage: Desvantagem no roll

        Returns:
            Dict com resultado do ataque:
            {
                'd20_result': int,
                'd20_details': dict,
                'bonus': int,
                'total': int,
                'target_ac': int,
                'hit': bool,
                'crit': bool,
                'crit_fail': bool
            }
        """
        d20_result, d20_details = CombatRollService.roll_d20(advantage, disadvantage)

        total = d20_result + bonus
        hit = total >= target_ac
        crit = d20_result == 20
        crit_fail = d20_result == 1

        # Critical hit sempre acerta (excepto se o alvo é impossível de atingir)
        if crit:
            hit = True
        # Critical fail sempre falha
        if crit_fail:
            hit = False

        return {
            'd20_result': d20_result,
            'd20_details': d20_details,
            'bonus': bonus,
            'total': total,
            'target_ac': target_ac,
            'hit': hit,
            'crit': crit,
            'crit_fail': crit_fail
        }

    @staticmethod
    def parse_dice_expression(expression: str) -> Tuple[int, int, int]:
        """
        Parse uma expressão de dados (ex: "2d6+3", "1d8", "3d4-1").

        Args:
            expression: Expressão de dados

        Returns:
            Tuple[int, int, int]: (número de dados, lados, modificador)
        """
        expression = expression.strip().lower().replace(' ', '')

        # Padrão: XdY+Z ou XdY-Z ou XdY
        match = re.match(r'(\d+)?d(\d+)([+-]\d+)?', expression)

        if not match:
            # Tentar apenas número (dano fixo)
            if expression.isdigit():
                return 0, 0, int(expression)
            return 1, 6, 0  # Padrão fallback

        num_dice = int(match.group(1)) if match.group(1) else 1
        dice_sides = int(match.group(2))
        modifier = int(match.group(3)) if match.group(3) else 0

        return num_dice, dice_sides, modifier

    @staticmethod
    def roll_dice(num_dice: int, dice_sides: int, modifier: int = 0, crit: bool = False) -> Dict:
        """
        Rola dados.

        Args:
            num_dice: Número de dados
            dice_sides: Lados de cada dado
            modifier: Modificador a adicionar
            crit: Se é critical hit (dobra os dados)

        Returns:
            Dict com resultado:
            {
                'rolls': [int],
                'total_dice': int,
                'modifier': int,
                'total': int,
                'crit': bool
            }
        """
        # Em critical, dobra os dados
        actual_num_dice = num_dice * 2 if crit else num_dice

        rolls = [random.randint(1, dice_sides) for _ in range(actual_num_dice)]
        total_dice = sum(rolls)
        total = total_dice + modifier

        return {
            'rolls': rolls,
            'total_dice': total_dice,
            'modifier': modifier,
            'total': max(0, total),  # Nunca negativo
            'crit': crit
        }

    @staticmethod
    def roll_damage(
        dice_expression: str,
        damage_type: str = "slashing",
        crit: bool = False,
        resistance: bool = False,
        immunity: bool = False,
        vulnerability: bool = False
    ) -> Dict:
        """
        Rola dano com modificadores de resistência.

        Args:
            dice_expression: Expressão de dados (ex: "2d6+3")
            damage_type: Tipo de dano
            crit: Se é critical hit
            resistance: Se alvo tem resistência
            immunity: Se alvo é imune
            vulnerability: Se alvo é vulnerável

        Returns:
            Dict com resultado:
            {
                'expression': str,
                'damage_type': str,
                'roll_result': dict,
                'base_damage': int,
                'final_damage': int,
                'resistance': bool,
                'immunity': bool,
                'vulnerability': bool,
                'crit': bool
            }
        """
        num_dice, dice_sides, modifier = CombatRollService.parse_dice_expression(dice_expression)
        roll_result = CombatRollService.roll_dice(num_dice, dice_sides, modifier, crit)

        base_damage = roll_result['total']
        final_damage = base_damage

        # Aplicar modificadores
        if immunity:
            final_damage = 0
        elif resistance:
            final_damage = final_damage // 2  # Metade (arredondado para baixo)
        elif vulnerability:
            final_damage = final_damage * 2  # Dobro

        return {
            'expression': dice_expression,
            'damage_type': damage_type,
            'roll_result': roll_result,
            'base_damage': base_damage,
            'final_damage': final_damage,
            'resistance': resistance,
            'immunity': immunity,
            'vulnerability': vulnerability,
            'crit': crit
        }

    @staticmethod
    def parse_attack_from_monster_action(action_text: str) -> Optional[Dict]:
        """
        Extrai informação de ataque de uma descrição de ação de monstro.

        Formato esperado: "Ataque corpo a corpo com arma: +X para acertar, ... Acerto: YdZ+W de dano tipo."

        Args:
            action_text: Texto da descrição da ação

        Returns:
            Dict com {bonus, damage_expression, damage_type} ou None
        """
        if not action_text:
            return None

        # Extrair bónus de ataque (+X para acertar)
        attack_match = re.search(r'\+(\d+)\s+para acertar', action_text, re.IGNORECASE)
        bonus = int(attack_match.group(1)) if attack_match else 0

        # Extrair dano (Acerto: XdY+Z)
        damage_match = re.search(r'Acerto:\s*(\d+\s*\(\s*\d+d\d+[+-]?\d*\s*\))', action_text, re.IGNORECASE)
        if not damage_match:
            # Tentar formato mais simples
            damage_match = re.search(r'(\d+d\d+[+-]?\d*)', action_text)

        damage_expression = "1d6"  # Padrão
        if damage_match:
            damage_str = damage_match.group(1)
            # Extrair apenas a expressão de dados
            dice_expr_match = re.search(r'(\d+d\d+[+-]?\d*)', damage_str)
            if dice_expr_match:
                damage_expression = dice_expr_match.group(1)

        # Extrair tipo de dano
        damage_type = "slashing"  # Padrão
        type_patterns = [
            (r'perfurante', 'piercing'),
            (r'cortante', 'slashing'),
            (r'contundente', 'bludgeoning'),
            (r'fogo', 'fire'),
            (r'gelo', 'cold'),
            (r'elétrico', 'lightning'),
            (r'ácido', 'acid'),
            (r'veneno', 'poison'),
            (r'psíquico', 'psychic'),
            (r'necrótico', 'necrotic'),
            (r'radiante', 'radiant'),
            (r'trovão', 'thunder')
        ]

        for pattern, dtype in type_patterns:
            if re.search(pattern, action_text, re.IGNORECASE):
                damage_type = dtype
                break

        return {
            'bonus': bonus,
            'damage_expression': damage_expression,
            'damage_type': damage_type
        }
