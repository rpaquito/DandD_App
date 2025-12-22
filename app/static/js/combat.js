/**
 * Companheiro de Mestre de Dungeon
 * Sistema de Combate - JavaScript
 * Usando métodos DOM seguros (sem innerHTML)
 */

// Estado do combate
let combatState = {
    participants: [],
    currentTurn: 0,
    round: 1
};

// Lista de condições disponíveis
const CONDITIONS_LIST = [
    'agarrado', 'amedrontado', 'atordoado', 'cego', 'enfeiticado',
    'envenenado', 'exausto', 'incapacitado', 'inconsciente', 'invisivel',
    'paralisado', 'petrificado', 'propenso', 'restringido', 'surdo', 'concentrando'
];

// ============================================
// Gestão de Participantes
// ============================================

async function loadCombat() {
    try {
        const response = await fetch('/combate/iniciativa');
        const data = await response.json();
        combatState.participants = data.participants || [];
        renderInitiativeList();
    } catch (error) {
        console.error('Erro ao carregar combate:', error);
    }
}

/**
 * Carrega participantes de uma sessao de combate guardada.
 * @param {Array} participants - Lista de participantes da sessao
 */
function loadSessionParticipants(participants) {
    combatState.participants = participants || [];
    renderInitiativeList();

    if (participants.length > 0) {
        showNotification('Combate carregado com ' + participants.length + ' participantes!', 'success');
    }
}

/**
 * Sincroniza o estado do combate com a sessao no servidor.
 */
async function syncSessionCombat() {
    if (!window.sessionMode || !window.sessionId) return;

    try {
        await fetch('/combate/sessao/' + window.sessionId + '/atualizar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                participants: combatState.participants,
                ronda: combatState.round,
                turno: combatState.currentTurn
            })
        });
    } catch (error) {
        console.error('Erro ao sincronizar combate com sessao:', error);
    }
}

async function addParticipant() {
    const nome = document.getElementById('participantName').value;
    const iniciativa = parseInt(document.getElementById('participantInit').value) || 10;
    const hp_max = parseInt(document.getElementById('participantHP').value) || 10;
    const ac = parseInt(document.getElementById('participantAC').value) || 10;
    const tipo = document.getElementById('participantType').value;

    if (!nome) {
        showNotification('Por favor, insere um nome.', 'warning');
        return;
    }

    try {
        const response = await fetch('/combate/iniciativa', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nome, iniciativa, hp_max, ac, tipo })
        });

        const data = await response.json();
        if (data.success) {
            combatState.participants = data.participants;
            renderInitiativeList();

            document.getElementById('participantName').value = '';
            document.getElementById('participantInit').value = '10';
            document.getElementById('participantHP').value = '10';
            document.getElementById('participantAC').value = '10';

            bootstrap.Modal.getInstance(document.getElementById('addParticipantModal')).hide();
            showNotification(nome + ' adicionado ao combate!', 'success');
        }
    } catch (error) {
        console.error('Erro ao adicionar participante:', error);
        showNotification('Erro ao adicionar participante.', 'danger');
    }
}

async function removeParticipant(id) {
    if (!confirm('Tens a certeza que queres remover este participante?')) return;

    try {
        const response = await fetch('/combate/remover', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id })
        });

        const data = await response.json();
        if (data.success) {
            combatState.participants = data.participants;
            renderInitiativeList();
            showNotification('Participante removido.', 'info');
        }
    } catch (error) {
        console.error('Erro ao remover participante:', error);
    }
}

async function clearCombat() {
    if (!confirm('Tens a certeza que queres limpar todo o combate?')) return;

    try {
        const response = await fetch('/combate/iniciativa/limpar', { method: 'POST' });
        const data = await response.json();
        if (data.success) {
            combatState.participants = [];
            combatState.currentTurn = 0;
            combatState.round = 1;
            renderInitiativeList();
            updateRoundCounter();
            showNotification('Combate limpo!', 'info');
        }
    } catch (error) {
        console.error('Erro ao limpar combate:', error);
    }
}

// ============================================
// Sistema de Dano e Cura
// ============================================

function openDamageModal(id, nome) {
    document.getElementById('damageTargetId').value = id;
    document.getElementById('damageModalTitle').textContent = 'Dano/Cura - ' + nome;
    document.getElementById('damageAmount').value = '';
    new bootstrap.Modal(document.getElementById('damageModal')).show();
}

async function applyDamage(isHealing) {
    const targetId = document.getElementById('damageTargetId').value;
    const amount = parseInt(document.getElementById('damageAmount').value) || 0;

    if (amount <= 0) {
        showNotification('Insere um valor válido.', 'warning');
        return;
    }

    // Em modo de sessao, aplicar localmente e sincronizar
    if (window.sessionMode) {
        for (let p of combatState.participants) {
            if (String(p.id) === String(targetId)) {
                if (isHealing) {
                    p.hp_atual = Math.min(p.hp_atual + amount, p.hp_max);
                } else {
                    p.hp_atual = Math.max(p.hp_atual - amount, 0);
                }
                break;
            }
        }
        renderInitiativeList();
        bootstrap.Modal.getInstance(document.getElementById('damageModal')).hide();
        syncSessionCombat();

        const msg = isHealing ? '+' + amount + ' HP curado!' : '-' + amount + ' HP de dano!';
        showNotification(msg, isHealing ? 'success' : 'danger');
        return;
    }

    // Modo normal via API
    try {
        const response = await fetch('/combate/dano', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: parseInt(targetId), amount, healing: isHealing })
        });

        const data = await response.json();
        if (data.success) {
            combatState.participants = data.participants;
            renderInitiativeList();
            bootstrap.Modal.getInstance(document.getElementById('damageModal')).hide();

            const msg = isHealing ? '+' + amount + ' HP curado!' : '-' + amount + ' HP de dano!';
            showNotification(msg, isHealing ? 'success' : 'danger');
        }
    } catch (error) {
        console.error('Erro ao aplicar dano/cura:', error);
    }
}

// ============================================
// Sistema de Condições
// ============================================

async function toggleCondition(id, condition) {
    // Em modo de sessao, aplicar localmente e sincronizar
    if (window.sessionMode) {
        for (let p of combatState.participants) {
            if (String(p.id) === String(id)) {
                if (!p.condicoes) p.condicoes = [];
                const idx = p.condicoes.indexOf(condition);
                if (idx >= 0) {
                    p.condicoes.splice(idx, 1);
                } else {
                    p.condicoes.push(condition);
                }
                break;
            }
        }
        renderInitiativeList();
        syncSessionCombat();
        return;
    }

    // Modo normal via API
    try {
        const response = await fetch('/combate/condicao', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id, condition })
        });

        const data = await response.json();
        if (data.success) {
            combatState.participants = data.participants;
            renderInitiativeList();
        }
    } catch (error) {
        console.error('Erro ao alternar condição:', error);
    }
}

// ============================================
// Controlo de Turnos
// ============================================

function nextTurn() {
    if (combatState.participants.length === 0) return;

    combatState.currentTurn++;
    if (combatState.currentTurn >= combatState.participants.length) {
        combatState.currentTurn = 0;
        combatState.round++;
        updateRoundCounter();
        showNotification('Ronda ' + combatState.round + '!', 'warning');
    }

    renderInitiativeList();

    // Sincronizar com sessao se em modo de sessao
    if (window.sessionMode) {
        syncSessionCombat();
    }
}

function sortByInitiative() {
    combatState.participants.sort((a, b) => b.iniciativa - a.iniciativa);
    renderInitiativeList();
    showNotification('Lista ordenada por iniciativa.', 'info');
}

function updateRoundCounter() {
    const counter = document.getElementById('roundCounter');
    if (counter) {
        counter.textContent = 'Ronda: ' + combatState.round;
    }
}

// ============================================
// Renderização Segura da Interface
// ============================================

function clearElement(element) {
    while (element.firstChild) {
        element.removeChild(element.firstChild);
    }
}

function createParticipantCard(p, index) {
    const hpPercent = (p.hp_atual / p.hp_max) * 100;
    const hpClass = hpPercent <= 25 ? 'critical' : hpPercent <= 50 ? 'low' : '';
    const isActive = index === combatState.currentTurn;
    const isDead = p.hp_atual <= 0;

    const card = document.createElement('div');
    card.className = 'card mb-2 participant-card border-secondary';
    if (isActive) card.classList.add('active-turn', 'border-warning');
    if (isDead) card.classList.add('opacity-50');

    const cardBody = document.createElement('div');
    cardBody.className = 'card-body p-3';

    const row = document.createElement('div');
    row.className = 'row align-items-center';

    // Coluna 1: Iniciativa e Nome
    const col1 = document.createElement('div');
    col1.className = 'col-md-4';

    const nameContainer = document.createElement('div');
    nameContainer.className = 'd-flex align-items-center';

    const initBadge = document.createElement('span');
    initBadge.className = 'badge me-2 fs-6 ' + (isActive ? 'bg-warning text-dark' : 'bg-secondary');
    initBadge.textContent = p.iniciativa;
    nameContainer.appendChild(initBadge);

    const nameDiv = document.createElement('div');
    const nameHeading = document.createElement('h6');
    nameHeading.className = 'mb-0';

    const typeIcon = document.createElement('i');
    typeIcon.className = 'bi me-1 ' + (p.tipo === 'jogador' ? 'bi-person-fill text-success' :
                                        p.tipo === 'npc' ? 'bi-person text-info' : 'bi-bug text-danger');
    nameHeading.appendChild(typeIcon);
    nameHeading.appendChild(document.createTextNode(p.nome));

    if (isDead) {
        const deadBadge = document.createElement('span');
        deadBadge.className = 'badge bg-danger ms-1';
        deadBadge.textContent = 'Morto';
        nameHeading.appendChild(deadBadge);
    }
    nameDiv.appendChild(nameHeading);

    const acInfo = document.createElement('small');
    acInfo.className = 'text-muted';
    acInfo.textContent = 'AC: ' + p.ac;
    nameDiv.appendChild(acInfo);

    nameContainer.appendChild(nameDiv);
    col1.appendChild(nameContainer);

    // Coluna 2: HP Bar
    const col2 = document.createElement('div');
    col2.className = 'col-md-4';

    const hpContainer = document.createElement('div');
    hpContainer.className = 'd-flex align-items-center';

    const hpBarOuter = document.createElement('div');
    hpBarOuter.className = 'flex-grow-1 me-2';

    const hpBarContainer = document.createElement('div');
    hpBarContainer.className = 'hp-bar-container';

    const hpBar = document.createElement('div');
    hpBar.className = 'hp-bar ' + hpClass;
    hpBar.style.width = Math.max(0, hpPercent) + '%';
    hpBarContainer.appendChild(hpBar);
    hpBarOuter.appendChild(hpBarContainer);
    hpContainer.appendChild(hpBarOuter);

    const hpBadge = document.createElement('span');
    hpBadge.className = 'badge ' + (hpPercent <= 25 ? 'bg-danger' : hpPercent <= 50 ? 'bg-warning' : 'bg-success');
    hpBadge.textContent = p.hp_atual + '/' + p.hp_max;
    hpContainer.appendChild(hpBadge);

    col2.appendChild(hpContainer);

    // Condições ativas
    if (p.condicoes && p.condicoes.length > 0) {
        const conditionsDiv = document.createElement('div');
        conditionsDiv.className = 'mt-1';
        p.condicoes.forEach(c => {
            const condBadge = document.createElement('span');
            condBadge.className = 'badge bg-warning text-dark condition-badge me-1';
            condBadge.textContent = c + ' ×';
            condBadge.style.cursor = 'pointer';
            condBadge.addEventListener('click', () => toggleCondition(p.id, c));
            conditionsDiv.appendChild(condBadge);
        });
        col2.appendChild(conditionsDiv);
    }

    // Coluna 3: Ações
    const col3 = document.createElement('div');
    col3.className = 'col-md-4 text-end';

    const btnGroup = document.createElement('div');
    btnGroup.className = 'btn-group btn-group-sm';

    // Botão Dano
    const damageBtn = document.createElement('button');
    damageBtn.className = 'btn btn-outline-danger';
    damageBtn.title = 'Dano/Cura';
    damageBtn.addEventListener('click', () => openDamageModal(p.id, p.nome));
    const damageIcon = document.createElement('i');
    damageIcon.className = 'bi bi-heart-pulse';
    damageBtn.appendChild(damageIcon);
    btnGroup.appendChild(damageBtn);

    // Dropdown Condições
    const condDropdownGroup = document.createElement('div');
    condDropdownGroup.className = 'btn-group btn-group-sm';

    const condBtn = document.createElement('button');
    condBtn.className = 'btn btn-outline-warning dropdown-toggle';
    condBtn.setAttribute('data-bs-toggle', 'dropdown');
    condBtn.title = 'Condições';
    const condIcon = document.createElement('i');
    condIcon.className = 'bi bi-exclamation-triangle';
    condBtn.appendChild(condIcon);
    condDropdownGroup.appendChild(condBtn);

    const condDropdown = document.createElement('ul');
    condDropdown.className = 'dropdown-menu dropdown-menu-dark dropdown-menu-end';

    CONDITIONS_LIST.forEach(c => {
        const li = document.createElement('li');
        const link = document.createElement('a');
        link.className = 'dropdown-item';
        if (p.condicoes && p.condicoes.includes(c)) {
            link.classList.add('active');
            const checkIcon = document.createElement('i');
            checkIcon.className = 'bi bi-check me-1';
            link.appendChild(checkIcon);
        }
        link.appendChild(document.createTextNode(c.charAt(0).toUpperCase() + c.slice(1)));
        link.href = '#';
        link.addEventListener('click', (e) => {
            e.preventDefault();
            toggleCondition(p.id, c);
        });
        li.appendChild(link);
        condDropdown.appendChild(li);
    });

    condDropdownGroup.appendChild(condDropdown);
    btnGroup.appendChild(condDropdownGroup);

    // Botão Remover
    const removeBtn = document.createElement('button');
    removeBtn.className = 'btn btn-outline-secondary';
    removeBtn.title = 'Remover';
    removeBtn.addEventListener('click', () => removeParticipant(p.id));
    const removeIcon = document.createElement('i');
    removeIcon.className = 'bi bi-trash';
    removeBtn.appendChild(removeIcon);
    btnGroup.appendChild(removeBtn);

    col3.appendChild(btnGroup);

    row.appendChild(col1);
    row.appendChild(col2);
    row.appendChild(col3);
    cardBody.appendChild(row);
    card.appendChild(cardBody);

    return card;
}

function renderInitiativeList() {
    const container = document.getElementById('initiativeList');
    const emptyMessage = document.getElementById('emptyMessage');

    if (!container) return;

    clearElement(container);

    if (combatState.participants.length === 0) {
        if (emptyMessage) emptyMessage.style.display = 'block';
        return;
    }

    if (emptyMessage) emptyMessage.style.display = 'none';

    combatState.participants.forEach((p, index) => {
        container.appendChild(createParticipantCard(p, index));
    });

    // Atualizar highlight das condições
    updateConditionHighlights();
}

// ============================================
// Calculadora de Dados
// ============================================

function rollDice() {
    const expression = document.getElementById('diceExpression').value;
    const resultDiv = document.getElementById('diceCalcResult');

    if (!resultDiv) return;

    clearElement(resultDiv);

    if (!expression) {
        const placeholder = document.createElement('span');
        placeholder.className = 'text-muted';
        placeholder.textContent = 'Insere uma expressão (ex: 2d6+3)';
        resultDiv.appendChild(placeholder);
        return;
    }

    const result = window.DnDCompanion.parseDiceExpression(expression);

    if (result.error) {
        const errorSpan = document.createElement('span');
        errorSpan.className = 'text-danger';
        errorSpan.textContent = result.error;
        resultDiv.appendChild(errorSpan);
        return;
    }

    resultDiv.appendChild(window.DnDCompanion.createDiceResultElement(result.total, result.rolls, result.modifier));
}

// ============================================
// Utilitários
// ============================================

function showNotification(message, type) {
    if (window.DnDCompanion && window.DnDCompanion.showNotification) {
        window.DnDCompanion.showNotification(message, type);
    } else {
        console.log('[' + type + '] ' + message);
    }
}

// ============================================
// Highlight de Condições Ativas
// ============================================

/**
 * Atualiza o highlight dos botões de condições 5e baseado nas condições ativas dos participantes
 */
function updateConditionHighlights() {
    // Recolher todas as condições ativas de todos os participantes
    const activeConditions = new Set();

    combatState.participants.forEach(participant => {
        if (participant.condicoes && participant.condicoes.length > 0) {
            participant.condicoes.forEach(cond => {
                // Normalizar nome da condição para lowercase e sem acentos
                const normalizedCond = cond.toLowerCase()
                    .normalize('NFD')
                    .replace(/[\u0300-\u036f]/g, '')
                    .trim();
                activeConditions.add(normalizedCond);
            });
        }
    });

    // Atualizar todos os botões de condições
    document.querySelectorAll('.condition-ref').forEach(button => {
        const buttonText = button.textContent.toLowerCase()
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .trim();

        if (activeConditions.has(buttonText)) {
            // Condição ativa - highlight
            button.classList.remove('btn-outline-secondary');
            button.classList.add('btn-warning', 'text-dark');
        } else {
            // Condição não ativa - normal
            button.classList.remove('btn-warning', 'text-dark');
            button.classList.add('btn-outline-secondary');
        }
    });
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('addParticipantForm');
    if (form) {
        form.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                addParticipant();
            }
        });
    }

    const diceExpr = document.getElementById('diceExpression');
    if (diceExpr) {
        diceExpr.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                rollDice();
            }
        });
    }
});
