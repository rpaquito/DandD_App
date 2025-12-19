# Companheiro de Mestre de Dungeon

Uma aplicação web local para ajudar novos Mestres de Dungeon a conduzir aventuras de Dungeons & Dragons 5ª Edição.

![D&D 5e](https://img.shields.io/badge/D%26D-5ª%20Edição-red)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Flask](https://img.shields.io/badge/Flask-2.x-green)
![Português](https://img.shields.io/badge/Idioma-Português%20PT-yellow)

## Índice

- [Funcionalidades](#funcionalidades)
- [Instalação](#instalação)
- [Utilização](#utilização)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Criar Novas Aventuras](#criar-novas-aventuras)
- [Personalizar Personagens](#personalizar-personagens)
- [Contribuir](#contribuir)

---

## Funcionalidades

### Guia de Aventuras Passo-a-Passo
- Navegação estruturada pela história
- Texto descritivo para ler aos jogadores
- Notas privadas do Mestre
- Dicas de improvisação contextuais
- Suporte para múltiplas aventuras

### Gestão de Jogadores
- 6 personagens pré-criados equilibrados
- Adicionar jogadores à sessão
- Gestão de HP em tempo real
- Sistema de condições (Envenenado, Cego, etc.)
- Fichas imprimíveis individuais ou em grupo

### Rastreador de Combate
- Lista de iniciativa ordenável
- Gestão de HP de jogadores e monstros
- Referência rápida de condições
- Dicas de táticas para o Mestre
- CDs de referência

### Materiais Imprimíveis
- Fichas de personagem pré-preenchidas
- Fichas de personagem em branco
- Mapas de aventura
- Fichas de monstros (em desenvolvimento)

### Rastreamento de Tempo (4 Sistemas)
- **Tempo de Sessão**: Cronómetro real-world com start/pause
- **Rondas de Combate**: 6 segundos por ronda (D&D 5e)
- **Turnos de Exploração**: 10 minutos por turno
- **Tempo no Jogo**: Hora do dia, dias decorridos, rastreamento de descansos

### Mapas Tácticos Interactivos
- Grelha visual com drag-and-drop de entidades
- Posicionamento de jogadores, NPCs e monstros
- Tamanho de grelha variável por passo (10x10, 20x20, etc.)
- Filtros de visibilidade por tipo de entidade
- Suporte para imagens de fundo
- Cada quadrado = 1.5m (5 pés D&D)

### Ferramentas Auxiliares
- Rolador de dados virtual (d4 a d20)
- Página de ajuda completa
- Glossário de termos D&D
- Interface totalmente em português

---

## Instalação

### Requisitos
- Python 3.8 ou superior
- pip (gestor de pacotes Python)

### Passos

1. **Clonar ou descarregar o projeto**
```bash
cd /caminho/para/DandD_App
```

2. **Criar ambiente virtual (recomendado)**
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate     # Windows
```

3. **Instalar dependências**
```bash
pip install -r requirements.txt
```

4. **Executar a aplicação**
```bash
python run.py
```

5. **Aceder no browser**
```
http://localhost:5001
```

> **Nota**: A aplicação usa a porta 5001 porque a porta 5000 está ocupada pelo AirPlay no macOS.

---

## Utilização

### Início Rápido (5 minutos)

1. **Adicionar Jogadores**
   - Ir a "Jogadores" no menu
   - Escolher personagens pré-criados para cada pessoa
   - Dar o nome real de cada jogador

2. **Imprimir Fichas**
   - Clicar em "Imprimir Todos"
   - Distribuir uma ficha a cada jogador

3. **Iniciar Aventura**
   - Na página inicial, clicar em "Iniciar Aventura"
   - Seguir o guia passo-a-passo

### Durante a Sessão

**Navegação e Combate:**
- **Navegação**: Usar botões "Anterior/Próximo" ou barra lateral
- **Combate**: Abrir rastreador, adicionar participantes, ordenar por iniciativa
- **HP**: Usar botões +/- para dano e cura
- **Dados**: Clicar no botão "Dados" no menu para rolar dados virtuais

**Gestão de Tempo** (Painel da Sessão):
1. **Iniciar Cronómetro**: Clicar em "Iniciar" no painel de tempo
   - O cronómetro corre automaticamente
   - Pausar quando houver intervalo
   - Tempo total acumula mesmo entre sessões

2. **Avançar Tempo no Jogo**:
   - Usar botões rápidos: +10min, +1h, +8h, +1 dia
   - Tempo avança automaticamente durante exploração e combate

3. **Registar Descansos**:
   - Descanso Curto: 1 hora (restaurar alguns recursos)
   - Descanso Longo: 8 horas (restaurar HP e recursos completos)

**Mapas Tácticos** (Passos de Combate):
1. **Ver Mapa**: Aparece automaticamente em passos com combate quando há sessão activa

2. **Mover Entidades**:
   - Arrastar tokens no mapa
   - Posições sincronizam automaticamente com a base de dados
   - Outros dispositivos veem mudanças após refresh

3. **Filtros de Visibilidade**:
   - **Jogadores** (verde): Mostrar/esconder party
   - **NPCs** (azul): Mostrar/esconder aliados e neutrals
   - **Monstros** (vermelho): Esconder até revelar aos jogadores

4. **Informação de Distâncias**:
   - Cada quadrado = 1.5m (5 pés D&D)
   - Movimento normal = 6 quadrados (9 metros)
   - Distância de alcance de magia típica = 10-20 quadrados

5. **Dicas de Uso**:
   - Esconder monstros no início (botão vermelho)
   - Revelar quando jogadores os vêem
   - Usar para calcular movimento e alcance de ataques
   - Deixar posições para próxima sessão (persistem automaticamente)

---

## Estrutura do Projeto

```
DandD_App/
├── app/
│   ├── __init__.py              # Inicialização Flask
│   ├── routes/
│   │   ├── main.py              # Rotas principais
│   │   ├── quest.py             # Navegação de aventuras
│   │   ├── combat.py            # Rastreador de combate
│   │   ├── players.py           # Gestão de jogadores
│   │   └── print.py             # Versões imprimíveis
│   ├── services/
│   │   └── quest_loader.py      # Carregamento de aventuras
│   ├── models/
│   │   └── combat.py            # Lógica de combate
│   ├── templates/               # Templates HTML (Jinja2)
│   │   ├── base.html            # Template base
│   │   ├── index.html           # Página inicial
│   │   ├── help.html            # Página de ajuda
│   │   ├── characters.html      # Lista de personagens
│   │   ├── quest/               # Templates de aventura
│   │   ├── combat/              # Templates de combate
│   │   ├── players/             # Templates de jogadores
│   │   └── print/               # Templates de impressão
│   ├── static/
│   │   ├── css/style.css        # Estilos personalizados
│   │   └── js/
│   │       ├── main.js          # JavaScript principal
│   │       └── combat.js        # JavaScript do combate
│   └── data/
│       ├── quests/              # Aventuras em JSON
│       │   └── cripta-reis-esquecidos.json
│       ├── characters.json      # Personagens pré-criados
│       └── players.json         # Jogadores da sessão
├── instance/
│   └── app.db                   # Base de dados SQLite
├── config.py                    # Configurações
├── run.py                       # Ponto de entrada
├── requirements.txt             # Dependências
├── CLAUDE.md                    # Guia para desenvolvimento
└── README.md                    # Este ficheiro
```

---

## Criar Novas Aventuras

As aventuras são ficheiros JSON na pasta `app/data/quests/`. Para criar uma nova aventura, segue este template:

### Template de Aventura

```json
{
  "id": "nome-da-aventura",
  "titulo": "Nome da Aventura",
  "descricao": "Uma breve descrição da aventura para a página inicial",
  "nivel_min": 1,
  "nivel_max": 3,
  "passos": [
    {
      "id": 1,
      "titulo": "Nome do Primeiro Passo",
      "tipo": "narrativa",
      "texto_jogadores": "Texto descritivo para ler em voz alta aos jogadores. Descreve o ambiente, atmosfera e o que os personagens veem, ouvem e sentem.",
      "notas_mestre": "Informação secreta apenas para o Mestre. Inclui motivações ocultas, segredos e consequências de ações.",
      "dicas_improvisacao": [
        "Se os jogadores perguntarem sobre X, diz Y",
        "Se tentarem fazer Z, permite com teste de dificuldade 15"
      ],
      "npcs": ["id_do_npc"],
      "monstros": [],
      "proximos_passos": [2]
    },
    {
      "id": 2,
      "titulo": "Encontro de Combate",
      "tipo": "combate",
      "texto_jogadores": "De repente, criaturas hostis emergem das sombras!",
      "notas_mestre": "Este combate deve ser desafiante mas não letal. Ajusta HP dos monstros se necessário.",
      "dicas_improvisacao": [
        "Se o combate estiver muito difícil, faz os monstros fugirem",
        "Se estiver muito fácil, adiciona mais um monstro"
      ],
      "npcs": [],
      "monstros": ["esqueleto"],
      "proximos_passos": [3]
    }
  ],
  "npcs": {
    "taverneiro": {
      "nome": "Gonçalo, o Taverneiro",
      "descricao": "Homem robusto de meia-idade com barba grisalha",
      "personalidade": "Amigável mas desconfiado de estranhos. Adora contar histórias.",
      "segredo": "Sabe mais sobre a cripta do que deixa transparecer",
      "dialogos": [
        "Bem-vindos à minha humilde taverna!",
        "A cripta? *baixa a voz* Ninguém que lá entrou voltou o mesmo...",
        "Se querem ir, levem tochas. Muitas tochas."
      ]
    }
  },
  "monstros": {
    "esqueleto": {
      "nome": "Esqueleto",
      "hp": 13,
      "ac": 13,
      "velocidade": "9m",
      "cr": "1/4",
      "xp": 50,
      "vulnerabilidades": ["contundente"],
      "imunidades": ["veneno", "exaustão"],
      "ataques": [
        {
          "nome": "Espada Curta",
          "bonus": "+4",
          "dano": "1d6+2 perfurante",
          "descricao": "Ataque corpo-a-corpo"
        },
        {
          "nome": "Arco Curto",
          "bonus": "+4",
          "dano": "1d6+2 perfurante",
          "alcance": "24/96m"
        }
      ],
      "taticas": "Esqueletos são agressivos mas não estratégicos. Atacam o inimigo mais próximo."
    }
  },
  "mapa_overview": {
    "grid_largura": 30,
    "grid_altura": 20,
    "imagem_fundo": "/static/maps/cripta-overview.png",
    "locais": [
      {
        "id": "entrada",
        "nome": "Entrada da Cripta",
        "x": 5,
        "y": 10,
        "passos_associados": [1]
      },
      {
        "id": "corredor",
        "nome": "Corredor Principal",
        "x": 15,
        "y": 10,
        "passos_associados": [2, 3]
      }
    ]
  },
  "mapas": [
    {
      "nome": "Mapa da Cripta",
      "descricao": "Mapa geral da dungeon"
    }
  ]
}
```

### Tipos de Passos

| Tipo | Descrição | Uso |
|------|-----------|-----|
| `narrativa` | Cenas de roleplay e exploração | Início, transições, descobertas |
| `combate` | Encontros de combate | Batalhas, emboscadas |
| `puzzle` | Enigmas e armadilhas | Portas trancadas, charadas |
| `social` | Interações com NPCs | Negociações, interrogatórios |

### Mapas Tácticos em Passos

Para adicionar um mapa táctico a um passo específico (especialmente combates), adiciona o campo `mapa_tatico`:

```json
{
  "id": 2,
  "titulo": "Encontro de Combate",
  "tipo": "combate",
  "mapa_tatico": {
    "grid_largura": 15,
    "grid_altura": 15,
    "metros_por_quadrado": 1.5,
    "imagem_fundo": "/static/maps/sala-combate.png",
    "posicoes_iniciais": {
      "jogadores": [
        {"indice": 0, "x": 2, "y": 7},
        {"indice": 1, "x": 3, "y": 7},
        {"indice": 2, "x": 2, "y": 8},
        {"indice": 3, "x": 3, "y": 8}
      ],
      "monstros": [
        {"id": "esqueleto", "instancia": 0, "x": 12, "y": 7},
        {"id": "esqueleto", "instancia": 1, "x": 12, "y": 8}
      ],
      "npcs": []
    },
    "terreno": [
      {"tipo": "arvore", "x": 7, "y": 7, "bloqueante": true},
      {"tipo": "pedra", "x": 8, "y": 9, "bloqueante": false}
    ]
  }
}
```

**Campos do Mapa Táctico:**
- `grid_largura`: Número de quadrados horizontal (recomendado: 10-20)
- `grid_altura`: Número de quadrados vertical
- `metros_por_quadrado`: Tamanho de cada quadrado em metros (padrão: 1.5m = 5 pés D&D)
- `imagem_fundo`: Caminho para imagem de fundo (opcional)
- `posicoes_iniciais`: Posições de partida para jogadores, monstros e NPCs
  - `jogadores`: Array com índice (0=primeiro jogador) e coordenadas x,y
  - `monstros`: Array com id do monstro, instancia (para múltiplos do mesmo tipo) e coordenadas
  - `npcs`: Array com id do NPC e coordenadas
- `terreno`: Elementos de terreno (árvores, pedras, móveis, etc.)

### Boas Práticas

1. **Texto para Jogadores**: Escreve na segunda pessoa ("Vocês veem...") e usa linguagem evocativa
2. **Notas do Mestre**: Inclui sempre alternativas e consequências
3. **Dicas de Improvisação**: Antecipa perguntas comuns dos jogadores
4. **Múltiplos Caminhos**: Usa `proximos_passos` com várias opções quando apropriado
5. **Monstros Equilibrados**: Para nível 1, usa CR 1/4 a 1/2 máximo
6. **Mapas Tácticos**: Usa grelhas 10x10 para salas pequenas, 15x15 para médias, 20x20 para grandes
7. **Posições Iniciais**: Coloca jogadores juntos (party) e monstros a distância interessante (não demasiado perto)

---

## Personalizar Personagens

Os personagens pré-criados estão em `app/data/characters.json`. Podes modificar os existentes ou adicionar novos.

### Template de Personagem

```json
{
  "id": "identificador-unico",
  "nome": "Nome do Personagem",
  "classe": "Guerreiro",
  "nivel": 1,
  "raca": "Humano",
  "antecedente": "Soldado",
  "alinhamento": "Leal Bom",

  "forca": 16,
  "destreza": 12,
  "constituicao": 14,
  "inteligencia": 10,
  "sabedoria": 12,
  "carisma": 10,

  "hp_max": 12,
  "ac": 18,
  "velocidade": "9m",
  "bonus_proficiencia": 2,

  "salvaguardas": ["Força", "Constituição"],
  "pericias": ["Atletismo", "Intimidação"],

  "armas": ["Espada Longa", "Escudo"],
  "armadura": "Cota de Malha + Escudo",
  "equipamento": ["Mochila", "Corda 15m", "Rações (5 dias)"],

  "caracteristicas": [
    "Estilo de Luta: Defesa (+1 AC)",
    "Retomar Fôlego (1d10+1 HP, 1x/descanso curto)"
  ],

  "ataques": [
    {
      "nome": "Espada Longa",
      "bonus": "+5",
      "dano": "1d8+3 cortante"
    }
  ],

  "descricao": "Breve descrição do personagem e sua personalidade."
}
```

### Personagens com Magia

Para classes com magia, adiciona:

```json
{
  "magias_conhecidas": {
    "truques": ["Raio de Gelo", "Luz", "Mão Mágica"],
    "nivel_1": ["Mísseis Mágicos", "Escudo", "Sono"]
  },
  "espacos_magia": {
    "nivel_1": 2
  }
}
```

### Classes Disponíveis

- Guerreiro
- Mago
- Clérigo
- Ladino
- Ranger
- Paladino
- Bárbaro
- Bardo
- Druida
- Monge
- Feiticeiro
- Bruxo

### Raças Comuns

- Humano
- Elfo (Alto, Floresta)
- Anão (Colina, Montanha)
- Halfling (Pés-Leves, Robusto)
- Meio-Elfo
- Meio-Orc
- Gnomo
- Tiefling
- Draconato

---

## Referência Rápida D&D 5e

### Modificadores de Atributo

| Valor | Modificador |
|-------|-------------|
| 1 | -5 |
| 2-3 | -4 |
| 4-5 | -3 |
| 6-7 | -2 |
| 8-9 | -1 |
| 10-11 | +0 |
| 12-13 | +1 |
| 14-15 | +2 |
| 16-17 | +3 |
| 18-19 | +4 |
| 20 | +5 |

### CDs Comuns

| Dificuldade | CD |
|-------------|-----|
| Muito Fácil | 5 |
| Fácil | 10 |
| Médio | 15 |
| Difícil | 20 |
| Muito Difícil | 25 |
| Quase Impossível | 30 |

### Condições

- **Cego**: Falha automática em testes que requerem visão
- **Encantado**: Não pode atacar quem encantou
- **Assustado**: Desvantagem enquanto vê a fonte do medo
- **Agarrado**: Velocidade 0
- **Incapacitado**: Não pode tomar ações ou reações
- **Invisível**: Impossível de ver sem magia
- **Paralisado**: Incapacitado, falha automática em FOR/DES
- **Petrificado**: Transformado em pedra
- **Envenenado**: Desvantagem em ataques e testes
- **Caído**: Desvantagem em ataques, ataques a 1.5m têm vantagem
- **Impedido**: Velocidade 0, ataques têm vantagem/desvantagem
- **Atordoado**: Incapacitado, fala incoerente
- **Inconsciente**: Caído, incapacitado, larga objetos

---

## Resolução de Problemas

### A aplicação não inicia

```bash
# Verificar se o ambiente virtual está ativo
source venv/bin/activate

# Reinstalar dependências
pip install -r requirements.txt
```

### Porta 5000 ocupada (macOS)

A porta 5000 é usada pelo AirPlay. A aplicação já usa 5001 por defeito.

### Aventuras não aparecem

1. Verificar que o ficheiro JSON está em `app/data/quests/`
2. Validar que o JSON está bem formatado
3. Reiniciar o servidor

### Estilos não atualizam

O Flask em modo debug recarrega automaticamente. Se não funcionar:
```bash
# Parar servidor (Ctrl+C) e reiniciar
python run.py
```

---

## Contribuir

### Reportar Problemas
Abre uma issue descrevendo:
- O que tentaste fazer
- O que aconteceu
- O que esperavas que acontecesse

### Adicionar Aventuras
1. Cria a aventura seguindo o template
2. Testa localmente
3. Submete um pull request

### Melhorar Código
1. Segue as convenções existentes
2. Testa as alterações
3. Documenta mudanças significativas

---

## Licença

Este projeto é para uso pessoal e educacional. D&D e Dungeons & Dragons são marcas registadas da Wizards of the Coast.

---

## Créditos

- **Framework**: Flask
- **UI**: Bootstrap 5
- **Ícones**: Bootstrap Icons
- **Sistema de Jogo**: Dungeons & Dragons 5ª Edição (Wizards of the Coast)

---

*Boas aventuras!* 🎲
