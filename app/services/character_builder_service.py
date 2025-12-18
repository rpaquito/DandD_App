"""Servico para o criador de personagens guiado."""

import json
import os
from flask import current_app, session


class CharacterBuilderService:
    """Servico para carregar dados D&D e gerir o processo de criacao."""

    _races_cache = None
    _classes_cache = None
    _equipment_cache = None

    @classmethod
    def get_races(cls):
        """Obter todas as racas disponiveis."""
        if cls._races_cache is None:
            races_file = os.path.join(
                current_app.root_path, 'data', 'races.json'
            )
            with open(races_file, 'r', encoding='utf-8') as f:
                cls._races_cache = json.load(f)
        return cls._races_cache.get('racas', [])

    @classmethod
    def get_race(cls, race_id):
        """Obter uma raca especifica por ID."""
        races = cls.get_races()
        for race in races:
            if race['id'] == race_id:
                return race
            # Verificar subracas
            for subrace in race.get('subracas', []):
                if subrace['id'] == race_id:
                    # Combinar raca base com subraca
                    combined = race.copy()
                    combined['subraca'] = subrace
                    combined['nome_completo'] = f"{race['nome']} ({subrace['nome']})"
                    # Combinar bonus de atributos
                    combined_bonus = race.get('bonus_atributos', {}).copy()
                    for attr, val in subrace.get('bonus_atributos', {}).items():
                        combined_bonus[attr] = combined_bonus.get(attr, 0) + val
                    combined['bonus_atributos_total'] = combined_bonus
                    # Combinar caracteristicas
                    combined['caracteristicas_todas'] = (
                        race.get('caracteristicas', []) +
                        subrace.get('caracteristicas', [])
                    )
                    return combined
        return None

    @classmethod
    def get_classes(cls):
        """Obter todas as classes disponiveis."""
        if cls._classes_cache is None:
            classes_file = os.path.join(
                current_app.root_path, 'data', 'classes.json'
            )
            with open(classes_file, 'r', encoding='utf-8') as f:
                cls._classes_cache = json.load(f)
        return cls._classes_cache.get('classes', [])

    @classmethod
    def get_class(cls, class_id):
        """Obter uma classe especifica por ID."""
        classes = cls.get_classes()
        for cls_data in classes:
            if cls_data['id'] == class_id:
                return cls_data
        return None

    @classmethod
    def get_equipment(cls):
        """Obter todo o equipamento disponivel."""
        if cls._equipment_cache is None:
            equipment_file = os.path.join(
                current_app.root_path, 'data', 'equipment.json'
            )
            with open(equipment_file, 'r', encoding='utf-8') as f:
                cls._equipment_cache = json.load(f)
        return cls._equipment_cache

    @classmethod
    def get_standard_array(cls):
        """Obter o array padrao de atributos."""
        if cls._classes_cache is None:
            cls.get_classes()
        return cls._classes_cache.get('array_padrao', [15, 14, 13, 12, 10, 8])

    @classmethod
    def get_point_buy_config(cls):
        """Obter configuracao de compra de pontos."""
        if cls._classes_cache is None:
            cls.get_classes()
        return cls._classes_cache.get('ponto_compra', {
            'pontos_disponiveis': 27,
            'custos': {str(i): max(0, i - 8) for i in range(8, 16)}
        })

    @staticmethod
    def calculate_modifier(score):
        """Calcular modificador de atributo."""
        return (score - 10) // 2

    @staticmethod
    def calculate_hp(constitution, class_data, level=1):
        """Calcular pontos de vida."""
        con_mod = CharacterBuilderService.calculate_modifier(constitution)
        base_hp = class_data.get('hp_nivel_1', 8)
        return base_hp + con_mod

    @staticmethod
    def calculate_ac(dexterity, armor=None, shield=False):
        """Calcular classe de armadura base."""
        dex_mod = CharacterBuilderService.calculate_modifier(dexterity)

        if armor is None:
            # Sem armadura
            ac = 10 + dex_mod
        elif armor.get('tipo') == 'leve':
            ac = armor.get('ac_base', 11) + dex_mod
        elif armor.get('tipo') == 'media':
            ac = armor.get('ac_base', 12) + min(dex_mod, 2)
        elif armor.get('tipo') == 'pesada':
            ac = armor.get('ac_base', 14)
        else:
            ac = 10 + dex_mod

        if shield:
            ac += 2

        return ac


def get_builder_session():
    """Obter dados do personagem em construcao da sessao."""
    return session.get('character_builder', {})


def save_builder_session(data):
    """Guardar dados do personagem em construcao na sessao."""
    session['character_builder'] = data
    session.modified = True


def clear_builder_session():
    """Limpar dados do personagem em construcao."""
    session.pop('character_builder', None)
    session.modified = True


def update_builder_step(step_data):
    """Atualizar um passo especifico do builder."""
    builder_data = get_builder_session()
    builder_data.update(step_data)
    save_builder_session(builder_data)
    return builder_data
