"""Rotas para o criador de personagens guiado."""

import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app import db
from app.models.session import SavedCharacter
from app.services.character_builder_service import (
    CharacterBuilderService,
    get_builder_session,
    save_builder_session,
    clear_builder_session,
    update_builder_step
)

builder_bp = Blueprint('builder', __name__, url_prefix='/criador')


@builder_bp.route('/')
def start():
    """Pagina inicial do criador - comeca um novo personagem."""
    clear_builder_session()
    return redirect(url_for('builder.step', step_num=1))


@builder_bp.route('/passo/<int:step_num>', methods=['GET', 'POST'])
def step(step_num):
    """Pagina de um passo especifico do wizard."""
    builder_data = get_builder_session()

    # Verificar se pode avancar para este passo
    if step_num > 1:
        # Verificar passos anteriores
        if step_num >= 2 and 'raca_id' not in builder_data:
            flash('Primeiro escolhe uma raca.', 'warning')
            return redirect(url_for('builder.step', step_num=1))
        if step_num >= 3 and 'classe_id' not in builder_data:
            flash('Primeiro escolhe uma classe.', 'warning')
            return redirect(url_for('builder.step', step_num=2))
        if step_num >= 4 and 'atributos' not in builder_data:
            flash('Primeiro define os atributos.', 'warning')
            return redirect(url_for('builder.step', step_num=3))

    if request.method == 'POST':
        return handle_step_post(step_num, builder_data)

    # Renderizar template do passo
    return render_step(step_num, builder_data)


def handle_step_post(step_num, builder_data):
    """Processar POST de um passo."""
    if step_num == 1:
        # Passo 1: Escolher Raca
        raca_id = request.form.get('raca_id')
        if not raca_id:
            flash('Escolhe uma raca.', 'danger')
            return redirect(url_for('builder.step', step_num=1))

        race = CharacterBuilderService.get_race(raca_id)
        if not race:
            flash('Raca invalida.', 'danger')
            return redirect(url_for('builder.step', step_num=1))

        update_builder_step({
            'raca_id': raca_id,
            'raca': race
        })
        return redirect(url_for('builder.step', step_num=2))

    elif step_num == 2:
        # Passo 2: Escolher Classe
        classe_id = request.form.get('classe_id')
        if not classe_id:
            flash('Escolhe uma classe.', 'danger')
            return redirect(url_for('builder.step', step_num=2))

        cls = CharacterBuilderService.get_class(classe_id)
        if not cls:
            flash('Classe invalida.', 'danger')
            return redirect(url_for('builder.step', step_num=2))

        # Guardar opcoes de classe (dominio, estilo de luta, etc.)
        opcoes_classe = {}
        if 'dominios' in cls:
            dominio_id = request.form.get('dominio_id')
            if dominio_id:
                opcoes_classe['dominio_id'] = dominio_id
        if 'estilos_luta' in cls:
            estilo_id = request.form.get('estilo_id')
            if estilo_id:
                opcoes_classe['estilo_id'] = estilo_id

        update_builder_step({
            'classe_id': classe_id,
            'classe': cls,
            'opcoes_classe': opcoes_classe
        })
        return redirect(url_for('builder.step', step_num=3))

    elif step_num == 3:
        # Passo 3: Atributos
        metodo = request.form.get('metodo', 'array')
        atributos = {}

        for attr in ['forca', 'destreza', 'constituicao', 'inteligencia', 'sabedoria', 'carisma']:
            try:
                atributos[attr] = int(request.form.get(attr, 10))
            except ValueError:
                atributos[attr] = 10

        # Aplicar bonus raciais
        race = builder_data.get('raca', {})
        bonus = race.get('bonus_atributos_total', race.get('bonus_atributos', {}))
        atributos_finais = {}
        for attr, val in atributos.items():
            atributos_finais[attr] = val + bonus.get(attr, 0)

        update_builder_step({
            'metodo_atributos': metodo,
            'atributos_base': atributos,
            'atributos': atributos_finais
        })
        return redirect(url_for('builder.step', step_num=4))

    elif step_num == 4:
        # Passo 4: Stats Derivados - apenas confirmar
        # Calcular HP e AC
        builder_data = get_builder_session()
        atributos = builder_data.get('atributos', {})
        classe = builder_data.get('classe', {})

        hp = CharacterBuilderService.calculate_hp(
            atributos.get('constituicao', 10),
            classe
        )
        ac = CharacterBuilderService.calculate_ac(
            atributos.get('destreza', 10)
        )

        update_builder_step({
            'hp_max': hp,
            'ac_base': ac
        })
        return redirect(url_for('builder.step', step_num=5))

    elif step_num == 5:
        # Passo 5: Equipamento
        equipamento = request.form.getlist('equipamento')
        armas = request.form.getlist('armas')
        armadura = request.form.get('armadura')

        # Calcular AC com armadura escolhida
        builder_data = get_builder_session()
        atributos = builder_data.get('atributos', {})

        ac = 10 + CharacterBuilderService.calculate_modifier(atributos.get('destreza', 10))

        # Simplificado: armaduras comuns
        armaduras_ac = {
            'couro': 11,
            'couro_batido': 12,
            'cota_malha': 13,
            'cota_escamas': 14,
            'cota_malha_pesada': 16,
            'armadura_placas': 18
        }

        if armadura in armaduras_ac:
            if armadura in ['cota_malha_pesada', 'armadura_placas']:
                ac = armaduras_ac[armadura]
            else:
                dex_mod = CharacterBuilderService.calculate_modifier(atributos.get('destreza', 10))
                if armadura in ['cota_malha', 'cota_escamas']:
                    ac = armaduras_ac[armadura] + min(dex_mod, 2)
                else:
                    ac = armaduras_ac[armadura] + dex_mod

        escudo = 'escudo' in equipamento
        if escudo:
            ac += 2

        update_builder_step({
            'equipamento': equipamento,
            'armas': armas,
            'armadura': armadura,
            'ac': ac,
            'escudo': escudo
        })
        return redirect(url_for('builder.step', step_num=6))

    elif step_num == 6:
        # Passo 6: Ataques e Magias
        ataques = []

        # Processar ataques das armas
        builder_data = get_builder_session()
        armas = builder_data.get('armas', [])
        atributos = builder_data.get('atributos', {})

        for arma in armas:
            ataque = criar_ataque_arma(arma, atributos)
            if ataque:
                ataques.append(ataque)

        # Truques (se classe tiver magia)
        truques = request.form.getlist('truques')

        update_builder_step({
            'ataques': ataques,
            'truques': truques
        })
        return redirect(url_for('builder.step', step_num=7))

    elif step_num == 7:
        # Passo 7: Finalizar
        nome_personagem = request.form.get('nome_personagem', 'Aventureiro')

        builder_data = get_builder_session()
        builder_data['nome'] = nome_personagem

        # Guardar personagem
        character_data = compile_character(builder_data)

        saved_char = SavedCharacter(
            nome=nome_personagem,
            classe=builder_data.get('classe', {}).get('nome', 'Desconhecido'),
            raca=builder_data.get('raca', {}).get('nome', 'Desconhecido'),
            nivel=1,
            character_data=json.dumps(character_data, ensure_ascii=False)
        )
        db.session.add(saved_char)
        db.session.commit()

        clear_builder_session()

        flash(f'Personagem "{nome_personagem}" criado com sucesso!', 'success')

        # Verificar se veio de uma sessao
        session_id = request.form.get('session_id')
        if session_id:
            return redirect(url_for('session.dashboard', session_id=session_id))

        return redirect(url_for('builder.complete', character_id=saved_char.id))

    return redirect(url_for('builder.step', step_num=step_num))


def render_step(step_num, builder_data):
    """Renderizar template de um passo."""
    context = {
        'step_num': step_num,
        'total_steps': 7,
        'builder_data': builder_data
    }

    if step_num == 1:
        context['races'] = CharacterBuilderService.get_races()
        return render_template('builder/step1_race.html', **context)

    elif step_num == 2:
        context['classes'] = CharacterBuilderService.get_classes()
        return render_template('builder/step2_class.html', **context)

    elif step_num == 3:
        context['standard_array'] = CharacterBuilderService.get_standard_array()
        context['point_buy'] = CharacterBuilderService.get_point_buy_config()
        return render_template('builder/step3_abilities.html', **context)

    elif step_num == 4:
        # Calcular stats derivados
        atributos = builder_data.get('atributos', {})
        classe = builder_data.get('classe', {})

        context['hp'] = CharacterBuilderService.calculate_hp(
            atributos.get('constituicao', 10), classe
        )
        context['ac'] = CharacterBuilderService.calculate_ac(
            atributos.get('destreza', 10)
        )
        context['modifiers'] = {
            attr: CharacterBuilderService.calculate_modifier(val)
            for attr, val in atributos.items()
        }
        return render_template('builder/step4_derived.html', **context)

    elif step_num == 5:
        context['equipment'] = CharacterBuilderService.get_equipment()
        return render_template('builder/step5_equipment.html', **context)

    elif step_num == 6:
        context['equipment'] = CharacterBuilderService.get_equipment()
        return render_template('builder/step6_attacks.html', **context)

    elif step_num == 7:
        # Compilar preview do personagem
        context['preview'] = compile_character(builder_data)
        return render_template('builder/step7_review.html', **context)

    return redirect(url_for('builder.start'))


def criar_ataque_arma(arma_id, atributos):
    """Criar dados de ataque para uma arma."""
    equipment = CharacterBuilderService.get_equipment()

    # Procurar arma
    arma = None
    for categoria in ['armas_simples', 'armas_marciais']:
        for tipo in ['melee', 'distancia']:
            armas = equipment.get(categoria, {}).get(tipo, [])
            for a in armas:
                if a['id'] == arma_id:
                    arma = a
                    break
            if arma:
                break
        if arma:
            break

    if not arma:
        return None

    # Determinar atributo (Forca ou Destreza para finesse)
    propriedades = arma.get('propriedades', [])
    is_finesse = any('finesse' in p.lower() for p in propriedades)
    is_ranged = arma_id in [a['id'] for a in equipment.get('armas_simples', {}).get('distancia', [])] or \
                arma_id in [a['id'] for a in equipment.get('armas_marciais', {}).get('distancia', [])]

    if is_ranged:
        mod = CharacterBuilderService.calculate_modifier(atributos.get('destreza', 10))
    elif is_finesse:
        str_mod = CharacterBuilderService.calculate_modifier(atributos.get('forca', 10))
        dex_mod = CharacterBuilderService.calculate_modifier(atributos.get('destreza', 10))
        mod = max(str_mod, dex_mod)
    else:
        mod = CharacterBuilderService.calculate_modifier(atributos.get('forca', 10))

    bonus = mod + 2  # +2 de proficiencia ao nivel 1
    dano = arma.get('dano', '1d6')

    return {
        'nome': arma['nome'],
        'bonus': f"+{bonus}" if bonus >= 0 else str(bonus),
        'dano': f"{dano}{'+' + str(mod) if mod >= 0 else str(mod)}" if mod != 0 else dano,
        'tipo_dano': arma.get('tipo_dano', 'impacto')
    }


def compile_character(builder_data):
    """Compilar dados finais do personagem."""
    race = builder_data.get('raca', {})
    cls = builder_data.get('classe', {})
    atributos = builder_data.get('atributos', {})

    character = {
        'id': builder_data.get('nome', 'personagem').lower().replace(' ', '_'),
        'nome': builder_data.get('nome', 'Aventureiro'),
        'classe': cls.get('nome', 'Desconhecido'),
        'nivel': 1,
        'raca': race.get('nome_completo', race.get('nome', 'Desconhecido')),
        'antecedente': '',
        'alinhamento': '',

        # Atributos
        'forca': atributos.get('forca', 10),
        'destreza': atributos.get('destreza', 10),
        'constituicao': atributos.get('constituicao', 10),
        'inteligencia': atributos.get('inteligencia', 10),
        'sabedoria': atributos.get('sabedoria', 10),
        'carisma': atributos.get('carisma', 10),

        # Stats de combate
        'hp_max': builder_data.get('hp_max', 10),
        'ac': builder_data.get('ac', 10),
        'velocidade': race.get('velocidade', '9m'),
        'bonus_proficiencia': 2,

        # Proficiencias
        'salvaguardas': cls.get('salvaguardas', []),
        'pericias': [],

        # Combate
        'ataques': builder_data.get('ataques', []),

        # Equipamento
        'armas': builder_data.get('armas', []),
        'armadura': builder_data.get('armadura', ''),
        'equipamento': builder_data.get('equipamento', []),

        # Caracteristicas
        'caracteristicas': [],

        # Magia (se aplicavel)
        'magias_conhecidas': {},
        'espacos_magia': {}
    }

    # Adicionar caracteristicas da raca
    for carac in race.get('caracteristicas_todas', race.get('caracteristicas', [])):
        character['caracteristicas'].append(carac.get('nome', str(carac)))

    # Adicionar caracteristicas da classe
    for carac in cls.get('caracteristicas_nivel_1', []):
        character['caracteristicas'].append(carac.get('nome', str(carac)))

    # Magia
    if cls.get('magias', False):
        character['atributo_magia'] = cls.get('atributo_magia', '')
        if cls.get('truques_nivel_1'):
            character['magias_conhecidas']['truques'] = builder_data.get('truques', [])
        if cls.get('espacos_magia_nivel_1'):
            character['espacos_magia'] = cls.get('espacos_magia_nivel_1', {})

    return character


@builder_bp.route('/completo/<int:character_id>')
def complete(character_id):
    """Pagina de personagem completo."""
    character = SavedCharacter.query.get_or_404(character_id)
    char_data = character.get_character_data()

    return render_template(
        'builder/complete.html',
        character=character,
        char_data=char_data
    )


@builder_bp.route('/api/racas')
def api_races():
    """API para obter racas."""
    return jsonify(CharacterBuilderService.get_races())


@builder_bp.route('/api/classes')
def api_classes():
    """API para obter classes."""
    return jsonify(CharacterBuilderService.get_classes())


@builder_bp.route('/api/calcular', methods=['POST'])
def api_calculate():
    """API para calcular stats derivados."""
    data = request.get_json()

    atributos = data.get('atributos', {})
    classe_id = data.get('classe_id')

    cls = CharacterBuilderService.get_class(classe_id) if classe_id else {}

    hp = CharacterBuilderService.calculate_hp(
        atributos.get('constituicao', 10),
        cls
    )
    ac = CharacterBuilderService.calculate_ac(
        atributos.get('destreza', 10)
    )

    modifiers = {
        attr: CharacterBuilderService.calculate_modifier(val)
        for attr, val in atributos.items()
    }

    return jsonify({
        'hp': hp,
        'ac': ac,
        'modifiers': modifiers
    })
