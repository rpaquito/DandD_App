/**
 * Companheiro de Mestre de Dungeon
 * Sistema de Combate - JavaScript
 * Usando métodos DOM seguros (sem innerHTML)
 */

// Estado do combate (global para acesso por outros componentes)
window.combatState = {
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

                    // Se monstro foi derrotado, adicionar à calculadora de XP
                    if (p.hp_atual === 0 && p.tipo === 'monstro' && typeof addMonsterToXPCalc === 'function') {
                        const xpValue = p.xp || 50; // XP padrão se não especificado
                        addMonsterToXPCalc(p.id, p.nome, xpValue);
                    }
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

            // Verificar se algum monstro foi derrotado e adicionar à calculadora de XP
            if (!isHealing && typeof addMonsterToXPCalc === 'function') {
                const defeated = combatState.participants.find(p =>
                    String(p.id) === String(targetId) && p.hp_atual === 0 && p.tipo === 'monstro'
                );
                if (defeated) {
                    const xpValue = defeated.xp || 50;
                    addMonsterToXPCalc(defeated.id, defeated.nome, xpValue);
                }
            }

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

    // Actualizar mapa tactico com participante activo
    if (window.mapGrid && combatState.participants.length > 0) {
        const activeParticipant = combatState.participants[combatState.currentTurn];
        if (activeParticipant) {
            window.mapGrid.setActiveParticipant(activeParticipant.id);
        }
    }

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

    // Botão Attack Roll (só em modo de sessão)
    if (window.sessionMode && !isDead) {
        const attackBtn = document.createElement('button');
        attackBtn.className = 'btn btn-outline-danger';
        attackBtn.title = 'Attack Roll';
        attackBtn.addEventListener('click', () => openAttackRollModal(p.id, p.nome));
        const attackIcon = document.createElement('i');
        attackIcon.className = 'bi bi-crosshair';
        attackBtn.appendChild(attackIcon);
        btnGroup.appendChild(attackBtn);
    }

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

    // Actualizar mapa tactico com participante activo
    if (window.mapGrid && combatState.participants.length > 0) {
        const activeParticipant = combatState.participants[combatState.currentTurn];
        if (activeParticipant) {
            window.mapGrid.setActiveParticipant(activeParticipant.id);
        }
        // Enriquecer entidades do mapa com dados atualizados
        if (typeof enrichMapEntitiesWithCombatData === 'function') {
            enrichMapEntitiesWithCombatData();
        }
    }
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

// ============================================
// Combat Log System
// ============================================

async function refreshCombatLog() {
    if (!window.sessionMode || !window.sessionId) return;

    try {
        const response = await fetch(`/combate/sessao/${window.sessionId}/log?limit=50`);
        const data = await response.json();

        if (data.logs) {
            renderCombatLog(data.logs);
        }
    } catch (error) {
        console.error('Erro ao carregar combat log:', error);
    }
}

function renderCombatLog(logs) {
    const container = document.getElementById('combat-log-container');
    if (!container) return;

    clearElement(container);

    if (logs.length === 0) {
        const emptyMsg = document.createElement('p');
        emptyMsg.className = 'text-muted small mb-0 text-center py-3';
        emptyMsg.textContent = 'Sem ações registadas';
        container.appendChild(emptyMsg);
        return;
    }

    // Mostrar logs do mais recente ao mais antigo
    logs.forEach(log => {
        const logEntry = document.createElement('div');
        logEntry.className = 'border-bottom border-secondary pb-2 mb-2';

        const logHeader = document.createElement('div');
        logHeader.className = 'd-flex justify-content-between align-items-start mb-1';

        const roundInfo = document.createElement('small');
        roundInfo.className = 'text-muted';
        roundInfo.textContent = `R${log.ronda}T${log.turno}`;
        logHeader.appendChild(roundInfo);

        const timestamp = new Date(log.timestamp);
        const timeText = document.createElement('small');
        timeText.className = 'text-muted';
        timeText.textContent = timestamp.toLocaleTimeString('pt-PT', { hour: '2-digit', minute: '2-digit' });
        logHeader.appendChild(timeText);

        logEntry.appendChild(logHeader);

        const message = document.createElement('p');
        message.className = 'mb-0 small';
        message.textContent = log.message;
        logEntry.appendChild(message);

        container.appendChild(logEntry);
    });

    // Scroll para o topo (mais recente)
    container.scrollTop = 0;
}

async function clearCombatLogUI() {
    if (!window.sessionMode || !window.sessionId) return;
    if (!confirm('Tens a certeza que queres limpar o histórico de combate?')) return;

    try {
        const response = await fetch(`/combate/sessao/${window.sessionId}/log/limpar`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({})
        });

        const data = await response.json();
        if (data.success) {
            renderCombatLog([]);
            showNotification(`${data.deleted} entradas removidas`, 'info');
        }
    } catch (error) {
        console.error('Erro ao limpar combat log:', error);
    }
}

// ============================================
// Attack Roll System
// ============================================

function openAttackRollModal(actorId, actorNome) {
    if (!window.sessionMode) {
        showNotification('Attack rolls só funcionam em modo de sessão', 'warning');
        return;
    }

    document.getElementById('attackActorId').value = actorId;
    document.getElementById('attackActorNome').value = actorNome;

    // Preencher dropdown de alvos
    const targetSelect = document.getElementById('attackTargetId');
    clearElement(targetSelect);

    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = 'Selecionar alvo...';
    targetSelect.appendChild(defaultOption);

    combatState.participants.forEach(p => {
        if (String(p.id) !== String(actorId) && p.hp_atual > 0) {
            const option = document.createElement('option');
            option.value = p.id;
            option.textContent = `${p.nome} (AC ${p.ac})`;
            option.dataset.ac = p.ac;
            option.dataset.nome = p.nome;
            targetSelect.appendChild(option);
        }
    });

    // Reset do modal
    document.getElementById('attackBonus').value = '0';
    document.getElementById('attackTargetAC').value = '10';
    document.getElementById('attackAdvantage').checked = false;
    document.getElementById('attackDisadvantage').checked = false;
    document.getElementById('attackResult').classList.add('d-none');
    document.getElementById('attackDamageButton').classList.add('d-none');

    new bootstrap.Modal(document.getElementById('attackRollModal')).show();
}

// Atualizar AC quando alvo é selecionado
document.addEventListener('DOMContentLoaded', function() {
    const targetSelect = document.getElementById('attackTargetId');
    if (targetSelect) {
        targetSelect.addEventListener('change', function() {
            const selectedOption = this.options[this.selectedIndex];
            if (selectedOption.dataset.ac) {
                document.getElementById('attackTargetAC').value = selectedOption.dataset.ac;
            }
        });
    }
});

async function performAttackRoll() {
    if (!window.sessionMode || !window.sessionId) return;

    const actorId = document.getElementById('attackActorId').value;
    const actorNome = document.getElementById('attackActorNome').value;
    const targetSelect = document.getElementById('attackTargetId');
    const targetOption = targetSelect.options[targetSelect.selectedIndex];

    if (!targetOption.value) {
        showNotification('Seleciona um alvo primeiro', 'warning');
        return;
    }

    const targetId = targetOption.value;
    const targetNome = targetOption.dataset.nome;
    const bonus = parseInt(document.getElementById('attackBonus').value) || 0;
    const targetAC = parseInt(document.getElementById('attackTargetAC').value) || 10;
    const advantage = document.getElementById('attackAdvantage').checked;
    const disadvantage = document.getElementById('attackDisadvantage').checked;

    try {
        const response = await fetch(`/combate/sessao/${window.sessionId}/atacar`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                actor_id: actorId,
                actor_nome: actorNome,
                target_id: targetId,
                target_nome: targetNome,
                bonus: bonus,
                target_ac: targetAC,
                advantage: advantage,
                disadvantage: disadvantage
            })
        });

        const result = await response.json();
        displayAttackResult(result);
        refreshCombatLog();
    } catch (error) {
        console.error('Erro no attack roll:', error);
        showNotification('Erro ao realizar ataque', 'danger');
    }
}

function displayAttackResult(result) {
    const resultDiv = document.getElementById('attackResult');
    clearElement(resultDiv);
    resultDiv.classList.remove('d-none');

    const resultContainer = document.createElement('div');

    // Linha 1: Resultado principal
    const mainResult = document.createElement('div');
    mainResult.className = 'mb-1';

    if (result.crit) {
        mainResult.textContent = '🎯 ';
        const critText = document.createElement('strong');
        critText.className = 'text-success';
        critText.textContent = 'CRÍTICO!';
        mainResult.appendChild(critText);
    } else if (result.crit_fail) {
        mainResult.textContent = '💥 ';
        const failText = document.createElement('strong');
        failText.className = 'text-danger';
        failText.textContent = 'FALHA CRÍTICA!';
        mainResult.appendChild(failText);
    } else if (result.hit) {
        mainResult.textContent = '⚔️ ';
        const hitText = document.createElement('strong');
        hitText.className = 'text-success';
        hitText.textContent = 'Acerta!';
        mainResult.appendChild(hitText);
    } else {
        mainResult.textContent = '❌ ';
        const missText = document.createElement('strong');
        missText.className = 'text-danger';
        missText.textContent = 'Erra';
        mainResult.appendChild(missText);
    }

    resultContainer.appendChild(mainResult);

    // Linha 2: Detalhes do roll
    const details = document.createElement('div');
    details.textContent = `d20: ${result.d20_result} + ${result.bonus} = `;
    const total = document.createElement('strong');
    total.textContent = result.total;
    details.appendChild(total);
    details.appendChild(document.createTextNode(` vs AC ${result.target_ac}`));
    resultContainer.appendChild(details);

    resultDiv.appendChild(resultContainer);

    // Mostrar botão de dano se acertou
    const damageBtn = document.getElementById('attackDamageButton');
    if (result.hit && !result.crit_fail) {
        damageBtn.classList.remove('d-none');
        damageBtn.dataset.crit = result.crit;
    } else {
        damageBtn.classList.add('d-none');
    }
}

function goToDamageFromAttack() {
    const isCrit = document.getElementById('attackDamageButton').dataset.crit === 'true';
    const targetSelect = document.getElementById('attackTargetId');
    const targetOption = targetSelect.options[targetSelect.selectedIndex];
    const actorId = document.getElementById('attackActorId').value;
    const actorNome = document.getElementById('attackActorNome').value;

    // Fechar modal de ataque
    bootstrap.Modal.getInstance(document.getElementById('attackRollModal')).hide();

    // Abrir modal de dano com info pré-preenchida
    openDamageRollModal(actorId, actorNome, targetOption.value, targetOption.dataset.nome, isCrit);
}

// ============================================
// Damage Roll System (Advanced)
// ============================================

function openDamageRollModal(actorId, actorNome, targetId, targetNome, isCrit) {
    if (!window.sessionMode) {
        showNotification('Damage rolls só funcionam em modo de sessão', 'warning');
        return;
    }

    document.getElementById('damageActorId').value = actorId;
    document.getElementById('damageActorNome').value = actorNome;
    document.getElementById('damageRollTargetId').value = targetId;
    document.getElementById('damageRollTargetNome').value = targetNome;

    document.getElementById('damageExpression').value = '1d6';
    document.getElementById('damageType').value = 'slashing';
    document.getElementById('damageCrit').checked = isCrit || false;
    document.getElementById('damageResistance').checked = false;
    document.getElementById('damageImmunity').checked = false;
    document.getElementById('damageVulnerability').checked = false;
    document.getElementById('damageRollResult').classList.add('d-none');

    new bootstrap.Modal(document.getElementById('damageRollModal')).show();
}

async function performDamageRoll() {
    if (!window.sessionMode || !window.sessionId) return;

    const actorId = document.getElementById('damageActorId').value;
    const actorNome = document.getElementById('damageActorNome').value;
    const targetId = document.getElementById('damageRollTargetId').value;
    const targetNome = document.getElementById('damageRollTargetNome').value;
    const diceExpression = document.getElementById('damageExpression').value;
    const damageType = document.getElementById('damageType').value;
    const crit = document.getElementById('damageCrit').checked;
    const resistance = document.getElementById('damageResistance').checked;
    const immunity = document.getElementById('damageImmunity').checked;
    const vulnerability = document.getElementById('damageVulnerability').checked;

    try {
        const response = await fetch(`/combate/sessao/${window.sessionId}/dano`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                actor_id: actorId,
                actor_nome: actorNome,
                target_id: targetId,
                target_nome: targetNome,
                dice_expression: diceExpression,
                damage_type: damageType,
                crit: crit,
                resistance: resistance,
                immunity: immunity,
                vulnerability: vulnerability
            })
        });

        const result = await response.json();
        displayDamageResult(result);
        renderInitiativeList();
        refreshCombatLog();

        // Atualizar combat state localmente
        const targetParticipant = combatState.participants.find(p => String(p.id) === String(targetId));
        if (targetParticipant) {
            targetParticipant.hp_atual = result.target_hp_atual;
        }

        // Adicionar a XP calc se matou o monstro
        if (result.target_hp_atual === 0) {
            const target = combatState.participants.find(p => String(p.id) === String(targetId));
            if (target && target.tipo === 'monstro' && typeof addMonsterToXPCalc === 'function') {
                const xpValue = target.xp || 50;
                addMonsterToXPCalc(target.id, target.nome, xpValue);
            }
        }

        // Fechar modal após 2 segundos
        setTimeout(() => {
            const modal = bootstrap.Modal.getInstance(document.getElementById('damageRollModal'));
            if (modal) modal.hide();
        }, 2000);

    } catch (error) {
        console.error('Erro no damage roll:', error);
        showNotification('Erro ao aplicar dano', 'danger');
    }
}

function displayDamageResult(result) {
    const resultDiv = document.getElementById('damageRollResult');
    clearElement(resultDiv);
    resultDiv.classList.remove('d-none');

    const resultContainer = document.createElement('div');

    // Linha 1: Emoji e dano total
    const mainLine = document.createElement('div');
    mainLine.className = 'mb-1';

    let emoji = '⚔️';
    if (result.crit) emoji = '💥';
    if (result.immunity) emoji = '🛡️';

    mainLine.textContent = `${emoji} `;
    const damageAmount = document.createElement('strong');
    damageAmount.textContent = result.final_damage;
    mainLine.appendChild(damageAmount);
    mainLine.appendChild(document.createTextNode(` de dano ${result.damage_type}`));
    resultContainer.appendChild(mainLine);

    // Linha 2: Detalhes
    const detailsLine = document.createElement('small');
    detailsLine.textContent = `Base: ${result.base_damage}`;

    if (result.immunity) {
        detailsLine.appendChild(document.createTextNode(' → IMUNE (0)'));
    } else if (result.resistance) {
        detailsLine.appendChild(document.createTextNode(' → Resistência (÷2)'));
    } else if (result.vulnerability) {
        detailsLine.appendChild(document.createTextNode(' → Vulnerável (×2)'));
    }

    if (result.crit) {
        detailsLine.appendChild(document.createTextNode(' | CRÍTICO (dados dobrados)'));
    }

    resultContainer.appendChild(detailsLine);
    resultDiv.appendChild(resultContainer);
}

// ============================================
// Spell Slots System
// ============================================

function openSpellSlotsModal(participantId, casterNome, casterId) {
    if (!window.sessionMode) {
        showNotification('Spell slots só funcionam em modo de sessão', 'warning');
        return;
    }

    document.getElementById('spellParticipantId').value = participantId;
    document.getElementById('spellCasterNome').value = casterNome;
    document.getElementById('spellCasterId').value = casterId;

    // Preencher dropdown de alvos
    const targetSelect = document.getElementById('spellTargetId');
    clearElement(targetSelect);

    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = 'Sem alvo específico';
    targetSelect.appendChild(defaultOption);

    combatState.participants.forEach(p => {
        if (p.hp_atual > 0) {
            const option = document.createElement('option');
            option.value = p.id;
            option.textContent = p.nome;
            option.dataset.nome = p.nome;
            targetSelect.appendChild(option);
        }
    });

    // Reset
    document.getElementById('spellName').value = '';
    document.getElementById('spellLevel').value = '0';
    document.getElementById('spellResult').classList.add('d-none');

    new bootstrap.Modal(document.getElementById('spellSlotsModal')).show();
}

async function castSpell() {
    if (!window.sessionMode || !window.sessionId) return;

    const participantId = document.getElementById('spellParticipantId').value;
    const actorId = document.getElementById('spellCasterId').value;
    const actorNome = document.getElementById('spellCasterNome').value;
    const spellName = document.getElementById('spellName').value || 'Magia';
    const spellLevel = parseInt(document.getElementById('spellLevel').value) || 0;

    const targetSelect = document.getElementById('spellTargetId');
    const targetOption = targetSelect.options[targetSelect.selectedIndex];
    const targetId = targetOption.value || null;
    const targetNome = targetOption.dataset.nome || null;

    try {
        const response = await fetch(`/combate/sessao/${window.sessionId}/magia`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                participant_id: participantId,
                actor_id: actorId,
                actor_nome: actorNome,
                spell_name: spellName,
                spell_level: spellLevel,
                target_id: targetId,
                target_nome: targetNome
            })
        });

        const result = await response.json();

        if (result.success) {
            showNotification(`✨ ${spellName} lançado!`, 'success');
            refreshCombatLog();

            // Fechar modal
            setTimeout(() => {
                const modal = bootstrap.Modal.getInstance(document.getElementById('spellSlotsModal'));
                if (modal) modal.hide();
            }, 1000);
        } else if (result.erro) {
            showNotification(result.erro, 'danger');
        }
    } catch (error) {
        console.error('Erro ao lançar magia:', error);
        showNotification('Erro ao lançar magia', 'danger');
    }
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

    // Refresh combat log on load (if in session mode)
    if (window.sessionMode && window.sessionId) {
        refreshCombatLog();

        // Auto-refresh combat log every 10 seconds
        setInterval(refreshCombatLog, 10000);
    }
});
