# Plano de Geração de Retratos de Personagens

**✅ STATUS: COMPLETO E INTEGRADO (23 Dez 2025)**

Este ficheiro contém os prompts utilizados para gerar os 6 retratos de personagens pré-criados.

## 📊 Estado Atual

**Status:** ✅ 6/6 Gerados e Totalmente Integrados
**Data:** 23 Dez 2025, 11:20
**Personagens:** 6 retratos completos (~506KB total)
**Formato:** Portrait 2:3 (832x1248px)
**Localização:** `/app/static/img/characters/`
**Integração:** ✅ `characters.json` + `characters.html` com hover effects

## 🚀 Como Usar Este Ficheiro

1. **Copiar prompt** da secção do personagem
2. **Gerar imagem** usando:
   - Z-Image-Turbo (gratuito após reset)
   - DALL-E 3 (pago, ~$0.08 por imagem)
   - Midjourney (pago, plano mensal)
3. **Guardar como** `[classe]-[nome].webp`
4. **Integrar** usando `INTEGRATION_GUIDE.md`

## 🎭 Personagens e Prompts

### 1. Rodrigo Espada-de-Ferro (Guerreiro)
**Ficheiro:** `guerreiro-rodrigo.webp`

**Prompt:**
```
D&D character portrait, male human fighter veteran warrior, wearing chainmail armor with shield, iron longsword at side, battle-scarred face with determined expression, military bearing, professional fantasy character art, heroic pose, medieval knight aesthetic
```

**Detalhes:**
- Classe: Guerreiro (Fighter)
- Raça: Humano
- Background: Soldado
- Aparência: Veterano de guerra, cicatrizes, postura militar
- Equipamento: Cota de malha, escudo, espada longa

---

### 2. Beatriz dos Arcanos (Mago)
**Ficheiro:** `mago-beatriz.webp`

**Prompt:**
```
D&D character portrait, female high elf wizard scholar, elegant arcane robes with mystical patterns, holding ornate wooden staff, grimoire at belt, intelligent scholarly expression, long flowing hair, professional fantasy character art, magical aura, wise and studious appearance
```

**Detalhes:**
- Classe: Mago (Wizard)
- Raça: Elfo Alto
- Background: Sábio
- Aparência: Estudiosa elegante, cabelo longo, expressão inteligente
- Equipamento: Robes arcanas, bordão ornamentado, grimório

---

### 3. Padre Martim da Luz (Clérigo)
**Ficheiro:** `clerigo-martim.webp`

**Prompt:**
```
D&D character portrait, male human cleric priest of light, wearing chainmail armor with holy symbol, benevolent and wise expression, kind eyes, religious vestments over armor, divine radiance, professional fantasy character art, healing hands pose, sacred guardian aesthetic
```

**Detalhes:**
- Classe: Clérigo (Cleric)
- Raça: Humano
- Background: Acólito
- Domínio: Vida
- Aparência: Padre compassivo, olhos bondosos, aura divina
- Equipamento: Cota de malha, símbolo sagrado, vestimentas religiosas

---

### 4. Inês Sombra-Veloz (Ladino)
**Ficheiro:** `ladino-ines.webp`

**Prompt:**
```
D&D character portrait, female halfling rogue lightfoot, wearing dark leather armor, dual short swords at waist, mischievous clever expression, nimble and agile appearance, small stature, professional fantasy character art, stealthy adventurer pose, cunning thief aesthetic
```

**Detalhes:**
- Classe: Ladino (Rogue)
- Raça: Halfling Pés-Leves
- Background: Criminoso
- Aparência: Pequena, ágil, expressão astuta e travessa
- Equipamento: Armadura de couro, duas espadas curtas, ferramentas de ladrão

---

### 5. Vasco Guardião-da-Floresta (Ranger)
**Ficheiro:** `ranger-vasco.webp`

**Prompt:**
```
D&D character portrait, male wood elf ranger forest guardian, wearing studded leather armor with forest green cloak, longbow on back, calm vigilant expression, connected to nature, professional fantasy character art, wilderness protector pose, natural hunter aesthetic
```

**Detalhes:**
- Classe: Ranger
- Raça: Elfo da Floresta
- Background: Forasteiro
- Aparência: Guardião da floresta, calmo e vigilante, conexão com natureza
- Equipamento: Armadura de couro batido, arco longo, manto verde

---

### 6. Leonor Escudo-Sagrado (Paladino)
**Ficheiro:** `paladino-leonor.webp`

**Prompt:**
```
D&D character portrait, female human paladin holy knight, wearing shining chainmail armor with shield bearing holy symbol, longsword at side, noble and righteous expression, commanding presence, professional fantasy character art, heroic leader pose, divine champion aesthetic
```

**Detalhes:**
- Classe: Paladino (Paladin)
- Raça: Humana
- Background: Nobre
- Aparência: Nobre e justa, presença comandante, aura divina
- Equipamento: Cota de malha brilhante, escudo com símbolo sagrado, espada longa

---

## 🚀 Como Gerar (Após Reset de Quota)

### Opção 1: Usando Claude Code

```
"Gera os 6 retratos de personagens usando os prompts em CHARACTER_PORTRAITS_PLAN.md"
```

Claude Code irá:
1. Ler os prompts deste ficheiro
2. Gerar cada retrato com Z-Image-Turbo
3. Guardar em `/app/static/img/characters/`
4. Atualizar `characters.json` com as referências

### Opção 2: Manual via MCP

```python
from mcp_hf import generate_image

for character in characters:
    image = generate_image(
        prompt=character['prompt'],
        resolution="832x1248 ( 2:3 )",
        steps=10
    )
    save_image(image, f"/app/static/img/characters/{character['filename']}")
```

### Opção 3: Script Python

Criar `generate_portraits.py`:

```python
#!/usr/bin/env python3
import requests
import json

# Ler prompts deste ficheiro
# Chamar API do Hugging Face
# Guardar imagens
```

---

## 📝 Atualização do characters.json

Depois de gerar os retratos, adicionar campo `portrait` a cada personagem:

```json
{
  "id": "guerreiro",
  "nome": "Rodrigo Espada-de-Ferro",
  "classe": "Guerreiro",
  "portrait": "/static/img/characters/guerreiro-rodrigo.webp",
  ...
}
```

Campos a adicionar:
- `guerreiro` → `"portrait": "/static/img/characters/guerreiro-rodrigo.webp"`
- `mago` → `"portrait": "/static/img/characters/mago-beatriz.webp"`
- `clerigo` → `"portrait": "/static/img/characters/clerigo-martim.webp"`
- `ladino` → `"portrait": "/static/img/characters/ladino-ines.webp"`
- `ranger` → `"portrait": "/static/img/characters/ranger-vasco.webp"`
- `paladino` → `"portrait": "/static/img/characters/paladino-leonor.webp"`

---

## 🎨 Uso nos Templates

### Página de Seleção de Personagens

```html
{% for char in personagens %}
<div class="character-card">
    <img src="{{ url_for('static', filename=char.portrait) }}"
         alt="{{ char.nome }}"
         class="character-portrait">
    <h3>{{ char.nome }}</h3>
    <p class="text-muted">{{ char.classe }} - {{ char.raca }}</p>
</div>
{% endfor %}
```

### CSS para Retratos

```css
.character-portrait {
    width: 100%;
    max-width: 300px;
    height: auto;
    border-radius: 8px;
    border: 3px solid #8b5a2b;
    box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    transition: transform 0.3s ease;
}

.character-portrait:hover {
    transform: scale(1.05);
    box-shadow: 0 6px 20px rgba(220, 53, 69, 0.4);
}

.character-card {
    text-align: center;
    padding: 20px;
    background: #2a2a2a;
    border-radius: 8px;
    transition: all 0.3s ease;
}

.character-card:hover {
    background: #3a3a3a;
    transform: translateY(-5px);
}
```

---

## 📊 Estimativa de Recursos

- **Tamanho por retrato:** ~150-200KB (WebP)
- **Total esperado:** ~900KB-1.2MB (6 retratos)
- **Tempo de geração:** ~2-3 minutos (com quota disponível)
- **Resolução:** 832x1248px (portrait 2:3)

---

## ✅ Checklist de Integração

Após gerar os retratos:

- [ ] Verificar que todos os 6 ficheiros foram criados
- [ ] Confirmar tamanhos de ficheiro razoáveis (<250KB cada)
- [ ] Atualizar `characters.json` com campos `portrait`
- [ ] Testar carregamento em `/personagens`
- [ ] Verificar responsividade mobile
- [ ] Adicionar CSS para hover effects
- [ ] Testar impressão de fichas de personagem
- [ ] Documentar em `UI_ELEMENTS_GUIDE.md`

---

## 🎯 Próximos Passos (Depois dos Retratos)

1. **Retratos de NPCs** (3-5 principais por quest)
2. **Tokens de Monstros** (criaturas recorrentes)
3. **Integração completa** nos templates
4. **Testes de UX** com todos os assets

---

## 💡 Alternativas (Se não quiseres esperar)

1. **DALL-E 3** via OpenAI API (pago, ~$0.04/imagem)
2. **Midjourney** (subscrição mensal)
3. **Stable Diffusion local** (se tiveres GPU)
4. **Placeholder images** temporárias
5. **Arte de stock** (procurar em itch.io, DriveThruRPG)

---

## 📖 Referências

- Resolução 2:3 ideal para retratos de personagens
- WebP oferece melhor compressão que PNG
- 832x1248px é suficiente para display e impressão
- Consistência de estilo importante entre os 6 retratos
