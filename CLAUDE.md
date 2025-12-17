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
