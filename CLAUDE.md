# CLAUDE.md - Guia para Desenvolvimento do DM Companion

Este ficheiro fornece contexto para assistentes de IA que trabalham neste projeto.

## Visão Geral do Projeto

**Companheiro de Mestre de Dungeon** é uma aplicação web local em Python/Flask que ajuda novos Mestres de Dungeon a conduzir aventuras de D&D 5ª Edição. A aplicação está **totalmente em Português de Portugal**.

### Propósito
- Guiar novos DMs passo-a-passo durante aventuras
- Fornecer ferramentas de gestão de combate
- Oferecer personagens pré-criados para começar rapidamente
- Disponibilizar materiais imprimíveis

## Stack Tecnológico

- **Backend**: Flask 2.x com SQLAlchemy
- **Frontend**: Bootstrap 5, Vanilla JavaScript
- **Base de Dados**: SQLite (local)
- **Dados**: JSON para aventuras e personagens
- **Porta**: 5001 (não usar 5000 - conflito com AirPlay no macOS)

## Estrutura do Projeto

```
DandD_App/
├── app/
│   ├── __init__.py          # Factory function, registo de blueprints
│   ├── routes/
│   │   ├── main.py          # Rotas principais (index, personagens, ajuda)
│   │   ├── quest.py         # Navegação de aventuras
│   │   ├── combat.py        # Rastreador de combate
│   │   ├── players.py       # Gestão de jogadores
│   │   └── print.py         # Versões imprimíveis
│   ├── services/
│   │   └── quest_loader.py  # Carregamento de aventuras JSON
│   ├── models/
│   │   └── combat.py        # Condições 5e, lógica de combate
│   ├── templates/           # Templates Jinja2
│   ├── static/              # CSS, JS, imagens
│   └── data/
│       ├── quests/          # Ficheiros JSON de aventuras
│       ├── characters.json  # 6 personagens pré-criados
│       └── players.json     # Jogadores da sessão atual
├── config.py
├── run.py                   # Entry point (porta 5001)
└── requirements.txt
```

## Convenções de Código

### Python
- Docstrings em português
- Type hints quando útil
- Funções pequenas e focadas
- Usar blueprints para organização

### Templates Jinja2
- Herdar sempre de `base.html`
- Usar blocos: `title`, `content`, `extra_css`, `extra_js`
- Classes Bootstrap para styling
- Ícones: Bootstrap Icons (`bi-*`)

### JavaScript
- **IMPORTANTE**: Não usar `innerHTML` - usar métodos DOM seguros
- Usar `createElement`, `textContent`, `appendChild`
- Vanilla JS apenas, sem frameworks

### CSS
- Tema escuro por defeito
- Usar variáveis Bootstrap quando possível
- Media queries para impressão (`@media print`)

## Dados de Aventuras (JSON)

### Estrutura de uma Aventura
```json
{
  "id": "identificador-unico",
  "titulo": "Nome da Aventura",
  "descricao": "Descrição breve",
  "nivel_min": 1,
  "nivel_max": 3,
  "passos": [
    {
      "id": 1,
      "titulo": "Nome do Passo",
      "tipo": "narrativa|combate|puzzle|social",
      "texto_jogadores": "Texto para ler em voz alta",
      "notas_mestre": "Informação secreta",
      "dicas_improvisacao": ["Dica 1", "Dica 2"],
      "monstros": ["id_monstro"],
      "proximos_passos": [2, 3]
    }
  ],
  "npcs": {
    "id_npc": {
      "nome": "Nome",
      "descricao": "Descrição",
      "personalidade": "Traços",
      "dialogos": ["Fala 1", "Fala 2"]
    }
  },
  "monstros": {
    "id_monstro": {
      "nome": "Nome",
      "hp": 10,
      "ac": 12,
      "ataques": [...]
    }
  }
}
```

### Estrutura de Personagem
```json
{
  "id": "guerreiro",
  "nome": "Nome do Personagem",
  "classe": "Guerreiro",
  "nivel": 1,
  "raca": "Humano",
  "forca": 16,
  "destreza": 12,
  "constituicao": 14,
  "inteligencia": 10,
  "sabedoria": 12,
  "carisma": 10,
  "hp_max": 12,
  "ac": 18,
  "velocidade": "9m",
  "salvaguardas": ["Força", "Constituição"],
  "pericias": ["Atletismo", "Intimidação"],
  "ataques": [
    {"nome": "Espada", "bonus": "+5", "dano": "1d8+3"}
  ],
  "caracteristicas": ["Característica 1"],
  "equipamento": ["Item 1", "Item 2"]
}
```

## Sistema de Rastreamento de Tempo

A aplicação implementa um sistema de 4 níveis de rastreamento de tempo:

### 1. Tempo de Sessão (Real-world)
- Duração da sessão de jogo em tempo real
- Start/pause com acumulação de tempo
- Campos: `sessao_iniciada_em`, `sessao_pausada_em`, `tempo_total_segundos`

### 2. Rondas de Combate (6 segundos por ronda)
- Rastreamento preciso de combate D&D 5e
- Cada ronda = 6 segundos no mundo do jogo
- Campos: `tempo_inicio_combate`, `tempo_ronda_inicio`, `duracao_total_segundos`

### 3. Turnos de Exploração (10 minutos por turno)
- Exploração de masmorras e wilderness
- Cada turno = 10 minutos
- Campo: `turnos_exploracao_total`

### 4. Tempo no Jogo (In-game time)
- Hora do dia e dia da aventura
- Rastreamento de descansos (curto = 1h, longo = 8h)
- Campos: `tempo_jogo_atual` (HH:MM), `dia_jogo_atual`, `ultimo_descanso_curto`, `ultimo_descanso_longo`

### Serviço: TimeTrackingService

Localização: `/app/services/time_service.py`

**Métodos principais:**
```python
start_session_timer(session_id)           # Iniciar cronómetro
pause_session_timer(session_id)           # Pausar e acumular tempo
get_session_duration(session_id)          # Obter duração total
start_combat_round_timer(session_id)      # Timer de ronda de combate
get_combat_time(session_id)               # Tempo de combate (rounds e real)
advance_exploration_turn(session_id, turns=1)  # Avançar turnos (10min cada)
advance_game_time(session_id, minutes=0, hours=0, days=0)  # Avançar tempo no jogo
register_rest(session_id, rest_type)      # Registar descanso ('curto' ou 'longo')
```

## Sistema de Mapas e Posicionamento

Sistema híbrido de mapas tácticos com grelha:

### Tipos de Mapas

1. **Mapa Overview (Quest-level)**
   - Mapa global da aventura mostrando locais principais
   - Navegação entre áreas da quest
   - Configurável no JSON da quest: `mapa_overview`

2. **Mapas Tácticos (Step-level)**
   - Mapas detalhados por passo (especialmente combates)
   - Grelha variável por passo (10x10, 20x20, etc.)
   - Configurável em cada passo: `mapa_tatico`

### Modelos de Dados

**EntityPosition** (`/app/models/position.py`):
- Rastreia posição de jogadores, NPCs e monstros na grelha
- Campos: `entity_type`, `entity_id`, `grid_x`, `grid_y`, `visivel`, `token_cor`
- Unique constraint: uma posição por entidade por passo

**MapConfiguration** (`/app/models/position.py`):
- Configuração da grelha por passo
- Campos: `grid_width`, `grid_height`, `square_size_meters`, `background_image_url`
- Tamanho de quadrado padrão: 1.5m (5 pés D&D)

### Serviço: PositionService

Localização: `/app/services/position_service.py`

**Métodos principais:**
```python
initialize_step_map(session_id, step_id, map_config)  # Criar configuração de mapa
place_entities_initial(...)                           # Posicionar entidades nas posições iniciais
move_entity(session_id, step_id, entity_id, x, y)    # Mover entidade
get_all_positions(session_id, step_id)                # Obter todas as posições
toggle_entity_visibility(session_id, step_id, entity_id)  # Toggle visibilidade
```

### Componente Frontend: MapGrid

Localização: `/app/static/js/map-grid.js`

**Canvas HTML5** interactivo com:
- Grelha desenhada dinamicamente
- Drag-and-drop de entidades (snap-to-grid)
- Filtros de visibilidade (jogadores/NPCs/monstros)
- Tokens coloridos com nomes
- Suporte para imagens de fundo
- Touch events para mobile

### Extensões ao JSON de Quest

**Mapa Overview (raiz da quest):**
```json
{
  "mapa_overview": {
    "grid_largura": 30,
    "grid_altura": 20,
    "imagem_fundo": "/static/maps/quest-overview.png",
    "locais": [
      {
        "id": "valdouro",
        "nome": "Valdouro",
        "x": 5,
        "y": 5,
        "passos_associados": [1, 2, 3]
      }
    ]
  }
}
```

**Mapa Táctico (em cada passo):**
```json
{
  "id": 4,
  "mapa_tatico": {
    "grid_largura": 15,
    "grid_altura": 15,
    "metros_por_quadrado": 1.5,
    "imagem_fundo": "/static/maps/step-4-floresta.png",
    "posicoes_iniciais": {
      "jogadores": [
        {"indice": 0, "x": 2, "y": 7},
        {"indice": 1, "x": 3, "y": 7}
      ],
      "monstros": [
        {"id": "cavaleiro_negro", "instancia": 0, "x": 12, "y": 7}
      ],
      "npcs": []
    },
    "terreno": [
      {"tipo": "arvore", "x": 7, "y": 7, "bloqueante": true}
    ]
  }
}
```

### Exemplos Práticos: Mapas nas Quests Existentes

Todas as 3 quests incluídas têm mapas tácticos nos encontros de combate:

**A Cripta dos Reis Esquecidos (2 mapas):**
- Step 6: Câmara dos Guardiões - 4 esqueletos em câmara octogonal (12x12)
- Step 10: Sala do Trono - Boss fight com Cavaleiro Fantasma (16x14)

**Sombras do Império Estelar (5 mapas):**
- Step 3: Emboscada Imperial - 4 soldados (15x13)
- Step 4: Perseguição nas Docas - 3 caçadores (14x12)
- Step 6: Entrada do Templo - 2 guardiões de pedra (14x12)
- Step 9: Acólitos das Sombras - 4 acólitos (15x13)
- Step 10: Senhor das Sombras - Boss fight (16x14)

**A Irmandade do Anel Sombrio (9 mapas):**
- Inclui encontros variados desde emboscadas (7 inimigos, grid 18x15) até boss fights (16x14)

### Como Usar Mapas Tácticos

**1. Criar Sessão:**
```python
# Mapas só aparecem quando há sessão activa
session = session_service.create_session(nome="Minha Campanha", quest_id="cripta-reis-esquecidos")
```

**2. Navegar para Step com Combate:**
- Acessar `/aventura/cripta-reis-esquecidos/passo/6?session_id=1`
- O mapa aparece automaticamente se o step tem `mapa_tatico` definido

**3. Interagir com Mapa:**
- Arrastar entidades para mover (sincroniza automaticamente)
- Usar botões de filtro para mostrar/esconder tipos de entidades
- Posições persistem na base de dados
- Outros DMs/dispositivos veem mudanças após refresh

**4. Reinicializar Posições:**
```python
# API endpoint para recomeçar passo com posições iniciais
POST /mapa/sessao/{id}/passo/{step_id}/limpar
POST /mapa/sessao/{id}/passo/{step_id}/inicializar
```

### Diretrizes para Criar Novos Mapas

**Tamanhos de Grelha Recomendados:**
- Pequena (8x8 a 10x10): Combates em espaços apertados (corredores, quartos)
- Média (12x12 a 15x15): Combates standard (4-6 criaturas)
- Grande (16x16 a 20x20): Boss fights, batalhas épicas, áreas abertas
- Muito Grande (20x20+): Mapas de exploração, múltiplos grupos

**Posicionamento Inicial:**
- Jogadores: Entrada/lado oeste (x baixo)
- Monstros: Interior/lado este (x alto)
- Espaçamento: 2-4 quadrados entre grupos para movimento táctico
- Boss: Posição central ou ao fundo da sala

**Performance:**
- Grids até 30x30 funcionam bem
- Canvas renderiza a 60fps mesmo com 20+ entidades
- Mobile: Touch events funcionam igual a mouse

## Rotas Principais

| Rota | Blueprint | Descrição |
|------|-----------|-----------|
| `/` | main | Página inicial |
| `/personagens` | main | Personagens pré-criados |
| `/ajuda` | main | Página de ajuda |
| `/jogadores/` | players | Gestão de jogadores |
| `/aventura/<id>` | quest | Visão geral da aventura |
| `/aventura/<id>/passo/<n>` | quest | Passo específico |
| `/combate/` | combat | Rastreador de combate |
| `/imprimir/...` | print | Versões imprimíveis |
| `/sessao/<id>/tempo/iniciar` | session | Iniciar cronómetro de sessão |
| `/sessao/<id>/tempo/pausar` | session | Pausar cronómetro |
| `/sessao/<id>/tempo/status` | session | Estado de todos os tempos |
| `/sessao/<id>/tempo/avancar` | session | Avançar tempo no jogo |
| `/mapa/sessao/<id>/passo/<step>/posicoes` | map | Obter posições de entidades |
| `/mapa/sessao/<id>/passo/<step>/mover` | map | Mover entidade no mapa |
| `/mapa/sessao/<id>/passo/<step>/visibilidade` | map | Toggle visibilidade entidade |

## Padrões de Desenvolvimento

### Adicionar Nova Funcionalidade
1. Criar/modificar rota no blueprint apropriado
2. Criar template em `templates/`
3. Atualizar navegação se necessário
4. Adicionar CSS/JS se necessário

### Adicionar Nova Aventura
1. Criar ficheiro JSON em `app/data/quests/`
2. Seguir estrutura existente
3. Reiniciar servidor

### Modificar Personagens
1. Editar `app/data/characters.json`
2. Manter estrutura consistente
3. Testar impressão

## Condições D&D 5e (Português)

O ficheiro `app/models/combat.py` contém `CONDICOES_5E` com todas as condições traduzidas:
- Cego, Encantado, Surdo, Assustado, Agarrado
- Incapacitado, Invisível, Paralisado, Petrificado
- Envenenado, Caído, Impedido, Atordoado, Inconsciente

## Testes e Validação

- Verificar que todas as páginas carregam sem erros
- Testar impressão (Ctrl+P) em páginas imprimíveis
- Validar JSON de aventuras antes de adicionar
- Testar em diferentes tamanhos de ecrã

## Problemas Comuns

### Porta 5000 bloqueada (macOS)
O AirPlay usa porta 5000. Usar porta 5001.

### innerHTML bloqueado
Hooks de segurança bloqueiam innerHTML. Usar métodos DOM seguros.

### Templates não atualizam
Reiniciar servidor Flask (debug mode recarrega automaticamente).

## Comandos Úteis

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar servidor
python run.py

# Aceder à aplicação
open http://localhost:5001
```

## Extensões Futuras (Ideias)

- [ ] Gerador de encontros aleatórios
- [ ] Calculadora de XP
- [ ] Notas de sessão persistentes
- [ ] Exportação de dados
- [ ] Modo offline (PWA)
- [ ] Mais aventuras

## Contacto

Projeto desenvolvido como ferramenta pessoal para sessões de D&D.
