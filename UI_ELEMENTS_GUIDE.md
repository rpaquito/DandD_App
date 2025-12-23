# Guia de Elementos UI Gerados

**✅ STATUS:** Todos os 20 UI elements gerados e totalmente integrados

Este guia documenta como usar os elementos visuais gerados por IA integrados no DM Companion.

## 📁 Estrutura de Ficheiros

```
app/static/img/
├── ui/
│   ├── hero-banner.webp        (125KB) - Banner principal 16:9
│   ├── divider-ornate.webp     (112KB) - Divisor ornamentado
│   ├── divider-simple.webp     (18KB)  - Divisor simples
│   └── divider-arcane.webp     (62KB)  - Divisor místico
├── logos/
│   └── app-logo.webp           (17KB)  - Logo da aplicação 1:1
├── conditions/                  (13 ícones de condições)
│   ├── agarrado.webp
│   ├── assustado.webp
│   ├── atordoado.webp
│   ├── cego.webp
│   ├── encantado.webp
│   ├── envenenado.webp
│   ├── incapacitado.webp
│   ├── inconsciente.webp
│   ├── invisivel.webp
│   ├── paralisado.webp
│   ├── petrificado.webp
│   ├── caido.webp
│   └── impedido.webp
└── backgrounds/
    └── texture-dark.webp       (48KB)  - Textura de fundo tileable
```

## 🎨 Classes CSS Disponíveis

### Background Texture
O fundo escuro com textura está aplicado automaticamente em `body`:
```css
body {
    background-image: url('/static/img/backgrounds/texture-dark.webp');
    background-repeat: repeat;
}
```

### Hero Banner
Para adicionar o banner heróico em qualquer página:
```html
<div class="hero-banner text-center">
    <h1 class="display-4">Título</h1>
    <p class="lead">Subtítulo</p>
</div>
```

### App Logo
O logo já está integrado na navbar em `base.html`:
```html
<img src="{{ url_for('static', filename='img/logos/app-logo.webp') }}"
     alt="Logo" class="app-logo">
```

### Divisores Decorativos
Use em templates para separar secções:
```html
<!-- Ornamentado (para secções importantes) -->
<div class="divider-ornate"></div>

<!-- Simples (para separação básica) -->
<div class="divider-simple"></div>

<!-- Místico (para conteúdo mágico/arcano) -->
<div class="divider-arcane"></div>
```

### Ícones de Condições

#### Método 1: Ícone Simples
```html
<img src="{{ url_for('static', filename='img/conditions/envenenado.webp') }}"
     alt="Envenenado" class="condition-icon">
```

Tamanhos disponíveis:
- `.condition-icon` - 32x32px (padrão)
- `.condition-icon-sm` - 24x24px (pequeno)
- `.condition-icon-lg` - 48x48px (grande)

#### Método 2: Badge com Ícone
```html
<span class="condition-badge-with-icon">
    <img src="{{ url_for('static', filename='img/conditions/paralisado.webp') }}"
         alt="Paralisado">
    Paralisado
</span>
```

#### Método 3: Usar CONDICOES_5E (Recomendado)
No código Python, as imagens estão mapeadas em `app/models/combat.py`:

```python
from app.models.combat import CONDICOES_5E

# Aceder à imagem de uma condição
condicao = CONDICOES_5E['envenenado']
print(condicao['imagem'])  # '/static/img/conditions/envenenado.webp'
```

No template Jinja2:
```html
{% set condicao = CONDICOES_5E['agarrado'] %}
<img src="{{ condicao.imagem }}" alt="{{ condicao.nome }}" class="condition-icon">
<span>{{ condicao.nome }}</span>
```

## 🗺️ Mapeamento de Condições

| Chave Python | Nome PT | Ficheiro |
|--------------|---------|----------|
| `agarrado` | Agarrado | `agarrado.webp` |
| `amedrontado` | Amedrontado | `assustado.webp` |
| `atordoado` | Atordoado | `atordoado.webp` |
| `cego` | Cego | `cego.webp` |
| `enfeiticado` | Enfeitiçado | `encantado.webp` |
| `envenenado` | Envenenado | `envenenado.webp` |
| `incapacitado` | Incapacitado | `incapacitado.webp` |
| `inconsciente` | Inconsciente | `inconsciente.webp` |
| `invisivel` | Invisível | `invisivel.webp` |
| `paralisado` | Paralisado | `paralisado.webp` |
| `petrificado` | Petrificado | `petrificado.webp` |
| `propenso` | Caído/Propenso | `caido.webp` |
| `restringido` | Restringido | `impedido.webp` |
| `surdo` | Surdo | `surdo.webp` |

**Nota:** `exausto` e `concentrando` ainda usam Bootstrap Icons (não foram gerados).

## 💡 Exemplos Práticos

### Mostrar Condições de um Personagem
```html
<div class="card">
    <div class="card-header">Condições Ativas</div>
    <div class="card-body">
        {% for condicao_key in personagem.condicoes %}
            {% set cond = CONDICOES_5E[condicao_key] %}
            <span class="condition-badge-with-icon"
                  title="{{ cond.descricao }}">
                <img src="{{ cond.imagem }}" alt="{{ cond.nome }}">
                {{ cond.nome }}
            </span>
        {% endfor %}
    </div>
</div>
```

### Página de Aventura com Banner e Divisores
```html
{% extends "base.html" %}

{% block content %}
<div class="container">
    <!-- Hero Banner -->
    <div class="hero-banner text-center">
        <h1>{{ quest.titulo }}</h1>
        <p class="lead">{{ quest.descricao }}</p>
    </div>

    <div class="divider-ornate"></div>

    <!-- Conteúdo da Aventura -->
    <div class="row">
        <div class="col-md-8">
            <p>{{ quest.introducao }}</p>
        </div>
    </div>

    <div class="divider-simple"></div>

    <!-- Mais secções -->
</div>
{% endblock %}
```

## 🎯 Próximos Passos

Elementos ainda por gerar:
- [ ] Mapas overview das quests
- [ ] Mapas tácticos de combate
- [ ] Retratos de personagens (6 pré-criados)
- [ ] Retratos de NPCs
- [ ] Tokens de monstros

## 🔧 Personalização

Para adicionar novos elementos visuais:
1. Gerar imagem usando Z-Image-Turbo
2. Guardar em `/app/static/img/[categoria]/`
3. Adicionar classe CSS em `style.css`
4. Documentar uso neste ficheiro

## 📝 Notas Técnicas

- **Formato:** Todos os ficheiros são `.webp` (compressão superior)
- **Resolução:** Varia por tipo (logos 1:1, banners 16:9, ícones 1:1)
- **Performance:** Total ~600KB de assets UI (lightweight)
- **Compatibilidade:** WebP suportado em todos os browsers modernos
