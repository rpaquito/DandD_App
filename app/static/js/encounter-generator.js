/**
 * Gerador de Encontros - Frontend
 *
 * Gera encontros balanceados usando o sistema de XP do D&D 5e.
 */

// Estado global
let currentEncounter = null;

/**
 * Atualiza os inputs de níveis dos jogadores baseado no tamanho do grupo
 */
function updatePartyLevels() {
    const partySize = parseInt(document.getElementById('party-size').value) || 4;
    const container = document.getElementById('party-levels-container');

    // Limpar container de forma segura
    while (container.firstChild) {
        container.removeChild(container.firstChild);
    }

    // Criar inputs para cada jogador
    for (let i = 0; i < partySize; i++) {
        const col = document.createElement('div');
        col.className = 'col-6 col-sm-4 col-md-3';

        const inputGroup = document.createElement('div');
        inputGroup.className = 'input-group input-group-sm';

        const span = document.createElement('span');
        span.className = 'input-group-text bg-secondary text-light border-secondary';
        span.textContent = `J${i + 1}`;
        inputGroup.appendChild(span);

        const input = document.createElement('input');
        input.type = 'number';
        input.className = 'form-control bg-dark text-light border-secondary';
        input.id = `player-level-${i}`;
        input.min = '1';
        input.max = '20';
        input.value = '1';
        inputGroup.appendChild(input);

        col.appendChild(inputGroup);
        container.appendChild(col);
    }
}

/**
 * Obtém os níveis dos jogadores dos inputs
 */
function getPartyLevels() {
    const partySize = parseInt(document.getElementById('party-size').value) || 4;
    const levels = [];

    for (let i = 0; i < partySize; i++) {
        const input = document.getElementById(`player-level-${i}`);
        if (input) {
            const level = parseInt(input.value) || 1;
            levels.push(Math.max(1, Math.min(20, level)));
        }
    }

    return levels;
}

/**
 * Gera um encontro balanceado
 */
async function generateEncounter() {
    try {
        const partyLevels = getPartyLevels();
        const difficulty = document.getElementById('difficulty').value;
        const questId = document.getElementById('quest-filter').value;
        const maxMonsters = parseInt(document.getElementById('max-monsters').value) || 10;

        // Validar
        if (!partyLevels || partyLevels.length === 0) {
            showNotification('Configura os níveis dos jogadores', 'warning');
            return;
        }

        // Mostrar loading
        showNotification('A gerar encontro...', 'info');

        // Fazer request ao backend
        const response = await fetch('/gerador-encontros/gerar', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                party_size: partyLevels.length,
                party_levels: partyLevels,
                difficulty: difficulty,
                quest_id: questId,
                max_monsters: maxMonsters,
                min_monsters: 1
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Erro ao gerar encontro');
        }

        const encounter = await response.json();
        currentEncounter = encounter;

        // Renderizar resultado
        displayEncounter(encounter);

        showNotification('Encontro gerado com sucesso!', 'success');

    } catch (error) {
        console.error('Erro ao gerar encontro:', error);
        showNotification(`Erro: ${error.message}`, 'danger');
    }
}

/**
 * Renderiza o encontro gerado na UI usando safe DOM methods
 */
function displayEncounter(encounter) {
    // Mostrar card de resultado, esconder placeholder
    document.getElementById('encounter-result').style.display = 'block';
    document.getElementById('empty-state').style.display = 'none';

    // Atualizar métricas
    const difficultyElement = document.getElementById('result-difficulty');
    difficultyElement.textContent = getDifficultyLabel(encounter.actual_difficulty);
    difficultyElement.className = `h4 mb-0 ${getDifficultyColor(encounter.actual_difficulty)}`;

    document.getElementById('result-budget').textContent = encounter.xp_budget;
    document.getElementById('result-adjusted').textContent = encounter.adjusted_xp;
    document.getElementById('result-multiplier').textContent = `${encounter.multiplier}x`;
    document.getElementById('result-count').textContent = encounter.num_monsters;

    // Renderizar lista de monstros
    renderMonstersList(encounter.monsters);
}

/**
 * Renderiza a lista de monstros usando safe DOM methods
 */
function renderMonstersList(monsters) {
    const container = document.getElementById('monsters-list');

    // Limpar container de forma segura
    while (container.firstChild) {
        container.removeChild(container.firstChild);
    }

    // Criar card para cada tipo de monstro
    monsters.forEach(monster => {
        const col = document.createElement('div');
        col.className = 'col-md-6';

        const card = createMonsterCard(monster);
        col.appendChild(card);
        container.appendChild(col);
    });
}

/**
 * Cria card de monstro usando safe DOM methods
 */
function createMonsterCard(monster) {
    const card = document.createElement('div');
    card.className = 'card bg-secondary border-danger';

    // Header
    const header = document.createElement('div');
    header.className = 'card-header border-danger bg-danger bg-opacity-10';

    const headerRow = document.createElement('div');
    headerRow.className = 'd-flex justify-content-between align-items-center';

    const nameDiv = document.createElement('div');
    const nameStrong = document.createElement('strong');
    nameStrong.className = 'text-danger';
    nameStrong.textContent = monster.nome;
    nameDiv.appendChild(nameStrong);

    const quantityBadge = document.createElement('span');
    quantityBadge.className = 'badge bg-danger';
    quantityBadge.textContent = `${monster.quantity}x`;

    headerRow.appendChild(nameDiv);
    headerRow.appendChild(quantityBadge);
    header.appendChild(headerRow);
    card.appendChild(header);

    // Body
    const body = document.createElement('div');
    body.className = 'card-body';

    // Stats row
    const statsRow = document.createElement('div');
    statsRow.className = 'row g-2 mb-2';

    // AC
    const acCol = document.createElement('div');
    acCol.className = 'col-4';
    const acText = document.createElement('small');
    acText.className = 'text-muted';
    acText.textContent = 'AC: ';
    const acValue = document.createElement('strong');
    acValue.textContent = monster.ac;
    acText.appendChild(acValue);
    acCol.appendChild(acText);

    // HP
    const hpCol = document.createElement('div');
    hpCol.className = 'col-4';
    const hpText = document.createElement('small');
    hpText.className = 'text-muted';
    hpText.textContent = 'HP: ';
    const hpValue = document.createElement('strong');
    hpValue.textContent = monster.hp_max;
    hpText.appendChild(hpValue);
    hpCol.appendChild(hpText);

    // CR
    const crCol = document.createElement('div');
    crCol.className = 'col-4';
    const crText = document.createElement('small');
    crText.className = 'text-muted';
    crText.textContent = 'CR: ';
    const crValue = document.createElement('strong');
    crValue.textContent = monster.cr;
    crText.appendChild(crValue);
    crCol.appendChild(crText);

    statsRow.appendChild(acCol);
    statsRow.appendChild(hpCol);
    statsRow.appendChild(crCol);
    body.appendChild(statsRow);

    // Type
    const typeDiv = document.createElement('div');
    typeDiv.className = 'mb-2';
    const typeSmall = document.createElement('small');
    typeSmall.className = 'text-muted';
    const typeIcon = document.createElement('i');
    typeIcon.className = 'bi bi-tag me-1';
    typeSmall.appendChild(typeIcon);
    const typeText = document.createTextNode(monster.tipo);
    typeSmall.appendChild(typeText);
    typeDiv.appendChild(typeSmall);
    body.appendChild(typeDiv);

    // XP info
    const xpDiv = document.createElement('div');
    xpDiv.className = 'bg-dark rounded p-2';

    const xpRow = document.createElement('div');
    xpRow.className = 'd-flex justify-content-between';

    const xpEachDiv = document.createElement('div');
    const xpEachSmall = document.createElement('small');
    xpEachSmall.textContent = 'XP cada: ';
    const xpEachBadge = document.createElement('span');
    xpEachBadge.className = 'badge bg-warning text-dark';
    xpEachBadge.textContent = monster.xp;
    xpEachSmall.appendChild(xpEachBadge);
    xpEachDiv.appendChild(xpEachSmall);

    const xpTotalDiv = document.createElement('div');
    const xpTotalSmall = document.createElement('small');
    xpTotalSmall.textContent = 'Total: ';
    const xpTotalBadge = document.createElement('span');
    xpTotalBadge.className = 'badge bg-success';
    xpTotalBadge.textContent = monster.xp * monster.quantity;
    xpTotalSmall.appendChild(xpTotalBadge);
    xpTotalDiv.appendChild(xpTotalSmall);

    xpRow.appendChild(xpEachDiv);
    xpRow.appendChild(xpTotalDiv);
    xpDiv.appendChild(xpRow);
    body.appendChild(xpDiv);

    card.appendChild(body);

    return card;
}

/**
 * Adiciona o encontro ao combat tracker da sessão
 */
async function addToCombat() {
    if (!currentEncounter) {
        showNotification('Nenhum encontro gerado para adicionar', 'warning');
        return;
    }

    const sessionId = document.getElementById('session-id').value;
    if (!sessionId) {
        showNotification('Nenhuma sessão activa', 'warning');
        return;
    }

    try {
        showNotification('A adicionar monstros ao combate...', 'info');

        const response = await fetch('/gerador-encontros/adicionar-combate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                session_id: parseInt(sessionId),
                monsters: currentEncounter.monsters
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Erro ao adicionar ao combate');
        }

        const result = await response.json();
        showNotification(result.message, 'success');

        // Redirecionar para combat tracker após 1 segundo
        setTimeout(() => {
            window.location.href = `/sessao/${sessionId}#combate`;
        }, 1500);

    } catch (error) {
        console.error('Erro ao adicionar ao combate:', error);
        showNotification(`Erro: ${error.message}`, 'danger');
    }
}

/**
 * Retorna label traduzido de dificuldade
 */
function getDifficultyLabel(difficulty) {
    const labels = {
        'trivial': 'Trivial',
        'easy': 'Fácil',
        'medium': 'Médio',
        'hard': 'Difícil',
        'deadly': 'Mortal'
    };
    return labels[difficulty] || difficulty;
}

/**
 * Retorna classe de cor para dificuldade
 */
function getDifficultyColor(difficulty) {
    const colors = {
        'trivial': 'text-secondary',
        'easy': 'text-success',
        'medium': 'text-warning',
        'hard': 'text-danger',
        'deadly': 'text-danger fw-bold'
    };
    return colors[difficulty] || 'text-light';
}

/**
 * Mostra notificação (usa sistema global se disponível)
 */
function showNotification(message, type = 'info') {
    // Usar sistema global se disponível
    if (window.DnDCompanion && window.DnDCompanion.showNotification) {
        window.DnDCompanion.showNotification(message, type);
        return;
    }

    // Fallback: alert simples
    console.log(`[${type.toUpperCase()}] ${message}`);
    if (type === 'danger' || type === 'warning') {
        alert(message);
    }
}
