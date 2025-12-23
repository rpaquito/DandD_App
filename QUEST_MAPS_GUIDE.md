# Guia de Mapas de Aventuras

**✅ STATUS: 10/16 MAPAS COMPLETOS E INTEGRADOS (23 Dez 2025)**

Este guia documenta os mapas gerados por IA para as quests do DM Companion.

## 📊 Estado Atual (23 Dez 2025, 11:20)

**Overview Maps:** ✅ 3/3 completos e integrados (100%)
**Tactical Maps:** ✅ 10/16 completos e integrados (63%)
**GPU Quota:** ✅ Disponível para futuros mapas
**Restantes:** 6 mapas regulares da Irmandade (podem ser gerados quando necessário)

---

## 📊 Status Detalhado

### ✅ Mapas Overview (3/3 Completos)
| Quest | Ficheiro | Tamanho | Status |
|-------|----------|---------|--------|
| A Cripta dos Reis Esquecidos | `cripta-reis-esquecidos.webp` | 196KB | ✅ |
| Sombras do Império Estelar | `sombras-imperio-estelar.webp` | 169KB | ✅ |
| A Irmandade do Anel Sombrio | `irmandade-anel-sombrio.webp` | 222KB | ✅ |

**Localização:** `/app/static/img/maps/overview/`

### ✅ Mapas Tácticos - A Cripta dos Reis Esquecidos (2/2 Completos)
| Step | Encontro | Ficheiro | Status |
|------|----------|----------|--------|
| 6 | As Câmaras dos Guardiões (4 esqueletos) | `cripta-step6-camara-guardioes.webp` | ✅ Integrado |
| 10 | A Sala do Trono (Boss: Cavaleiro Fantasma) | `cripta-step10-sala-trono.webp` | ✅ Integrado |

### ✅ Mapas Tácticos - Sombras do Império Estelar (5/5 Completos)
| Step | Encontro | Ficheiro | Status |
|------|----------|----------|--------|
| 3 | Emboscada Imperial (4 soldados) | `sombras-step3-emboscada-imperial.webp` | ✅ Integrado |
| 4 | Perseguição nas Docas (3 caçadores) | `sombras-step4-perseguicao-docas.webp` | ✅ Integrado |
| 6 | A Entrada do Templo (2 guardiões) | `sombras-step6-entrada-templo.webp` | ✅ Integrado |
| 9 | Os Acólitos das Sombras (4 acólitos) | `sombras-step9-acolitos-sombras.webp` | ✅ Integrado |
| 10 | O Senhor das Sombras (Boss) | `sombras-step10-senhor-sombras.webp` | ✅ Integrado |

### 🟡 Mapas Tácticos - A Irmandade do Anel Sombrio (3/9 - Boss Fights Completos)
| Step | Encontro | Ficheiro | Status |
|------|----------|----------|--------|
| 4 | Os Cavaleiros Negros | - | ⏳ Pendente |
| 8 | Lobos das Sombras | - | ⏳ Pendente |
| 10 | A Emboscada nas Minas | - | ⏳ Pendente |
| 12 | O Troll das Cavernas | - | ⏳ Pendente |
| 13 | O Demónio de Sombra e Fogo (Boss) | `irmandade-step13-balrog.webp` | ✅ Integrado |
| 17 | A Emboscada nas Cataratas | - | ⏳ Pendente |
| 20 | Os Mortos Caminham | - | ⏳ Pendente |
| 22 | O Covil de Shelob (Boss) | `irmandade-step22-shelob.webp` | ✅ Integrado |
| 23 | A Torre da Lua (Boss Final) | `irmandade-step23-torre-lua.webp` | ✅ Integrado |

**Localização:** `/app/static/img/maps/tactical/`

## 🎨 Como Usar os Mapas

### Mapas Overview no Template

Os mapas overview servem para dar contexto visual da jornada da quest. Adiciona ao template da quest:

```html
<!-- Em templates/quest_overview.html -->
<div class="quest-overview-map mb-4">
    <img src="{{ url_for('static', filename='img/maps/overview/cripta-reis-esquecidos.webp') }}"
         alt="Mapa da Aventura" class="img-fluid rounded">
</div>
```

Com CSS para estilização:

```css
.quest-overview-map {
    border: 3px solid #8b5a2b;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 5px 15px rgba(0,0,0,0.3);
}

.quest-overview-map img {
    transition: transform 0.3s ease;
}

.quest-overview-map img:hover {
    transform: scale(1.02);
}
```

### Mapas Tácticos no Sistema de Combate

Os mapas tácticos já estão integrados no sistema de mapas do projeto (ver `CLAUDE.md`):

```python
# Em cada passo do JSON da quest, adicionar:
{
    "id": 6,
    "titulo": "As Câmaras dos Guardiões",
    "tipo": "combate",
    "mapa_tatico": {
        "grid_largura": 12,
        "grid_altura": 12,
        "metros_por_quadrado": 1.5,
        "imagem_fundo": "/static/img/maps/tactical/cripta-step6-camara-guardioes.webp",
        "posicoes_iniciais": {
            "jogadores": [
                {"indice": 0, "x": 2, "y": 6},
                {"indice": 1, "x": 3, "y": 6}
            ],
            "monstros": [
                {"id": "esqueleto", "instancia": 0, "x": 9, "y": 4},
                {"id": "esqueleto", "instancia": 1, "x": 9, "y": 8},
                {"id": "esqueleto", "instancia": 2, "x": 10, "y": 6}
            ]
        }
    }
}
```

O mapa será exibido automaticamente na interface de combate com a grelha overlay e sistema de posicionamento drag-and-drop.

## 🔄 Continuação da Geração

### GPU Quota Limite Atingido

O serviço Z-Image-Turbo atingiu o limite de quota gratuita (60s de GPU). **Quota reseta às ~10:45 de 23 de Dezembro de 2025**.

### Como Continuar Depois

Executar o seguinte código Python para gerar os mapas restantes:

```python
# Usar o MCP server hf-mcp-server com gr2_z_image_turbo_generate

# Sombras do Império Estelar - Step 3
prompt_step3 = "Top-down tactical battle map, sci-fi urban street ambush scene, futuristic city alley with Imperial soldiers, cyberpunk environment with crates and cover, grid-based combat map"
resolution = "1152x896 ( 9:7 )"

# Repetir para steps 4, 6, 9, 10...
```

Ou usar Claude Code novamente:

```bash
# Na conversa com Claude Code
"Continue gerando os mapas tácticos restantes para Sombras do Império Estelar"
```

### Prompts Recomendados para Mapas Restantes

**Sombras do Império Estelar:**

- Step 3 (Emboscada): "Top-down tactical battle map, sci-fi urban street ambush, futuristic city with cover"
- Step 4 (Docas): "Top-down tactical battle map, space port docks chase, industrial warehouse with cargo"
- Step 6 (Templo): "Top-down tactical battle map, ancient mystical temple entrance, stone guardians"
- Step 9 (Acólitos): "Top-down tactical battle map, dark temple interior, shadow cult chamber"
- Step 10 (Boss): "Top-down tactical battle map, shadow lord throne room, epic boss arena"

**A Irmandade do Anel Sombrio (Prioridade Alta):**

- Step 13 (Balrog): "Top-down tactical battle map, bridge over underground chasm, Balrog demon boss"
- Step 22 (Shelob): "Top-down tactical battle map, giant spider lair with webs, dark cavern"
- Step 23 (Boss Final): "Top-down tactical battle map, dark tower throne room, epic final battle"

## 📝 Atualização dos Ficheiros JSON

Depois de gerar os mapas, atualizar os ficheiros JSON das quests em `/app/data/quests/`:

1. **cripta-reis-esquecidos.json** - ✅ Pronto para atualizar (2 mapas disponíveis)
2. **sombras-imperio-estelar.json** - ⏳ Aguardar geração dos 5 mapas
3. **a-irmandade-do-anel-sombrio.json** - ⏳ Aguardar geração dos mapas prioritários

### Exemplo de Atualização

```json
{
  "id": 6,
  "titulo": "As Câmaras dos Guardiões",
  "tipo": "combate",
  "mapa_tatico": {
    "grid_largura": 12,
    "grid_altura": 12,
    "metros_por_quadrado": 1.5,
    "imagem_fundo": "/static/img/maps/tactical/cripta-step6-camara-guardioes.webp",
    "posicoes_iniciais": {
      "jogadores": [
        {"indice": 0, "x": 2, "y": 6},
        {"indice": 1, "x": 3, "y": 6},
        {"indice": 2, "x": 2, "y": 5},
        {"indice": 3, "x": 3, "y": 7}
      ],
      "monstros": [
        {"id": "esqueleto", "instancia": 0, "x": 9, "y": 4},
        {"id": "esqueleto", "instancia": 1, "x": 9, "y": 8},
        {"id": "esqueleto", "instancia": 2, "x": 10, "y": 5},
        {"id": "esqueleto", "instancia": 3, "x": 10, "y": 7}
      ]
    }
  },
  "monstros": ["esqueleto", "esqueleto", "esqueleto", "esqueleto"]
}
```

## 🎯 Próximos Passos

1. **Aguardar reset de quota** (23 Dez 2025 ~10:45)
2. **Gerar mapas tácticos restantes:**
   - Sombras do Império Estelar: 5 mapas
   - A Irmandade: 3-4 mapas prioritários (Boss fights)
3. **Atualizar JSON files** com referências aos mapas
4. **Testar integração** no browser
5. **Documentar posições iniciais** para cada encontro

## 💡 Alternativas para Geração

Se não quiseres esperar pela quota reset:

1. **Usar outro modelo Hugging Face** (ex: FLUX, Stable Diffusion)
2. **Usar serviço local** (se tiveres GPU)
3. **Usar DALL-E ou MidJourney** (serviços pagos)
4. **Usar mapas placeholder** temporariamente

## 📊 Estatísticas

- **Total de mapas necessários:** 19
- **Mapas gerados:** 5 (26%)
- **Mapas pendentes:** 14 (74%)
- **Tamanho total atual:** ~600KB
- **Tamanho estimado final:** ~2.3MB
