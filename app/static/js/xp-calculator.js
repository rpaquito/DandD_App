/**
 * Sistema de Calculadora de XP
 *
 * Calcula XP de monstros derrotados e atribui aos jogadores com tracking de level ups.
 */

// Estado da calculadora de XP
let xpCalculatorState = {
    monsters: [],  // Monstros derrotados para calcular XP
    totalXP: 0,
    partySize: 0
};

/**
 * Adiciona um monstro à calculadora de XP
 * @param {string} monsterId - ID do monstro
 * @param {string} monsterName - Nome do monstro
 * @param {number} xp - XP do monstro
 */
function addMonsterToXPCalc(monsterId, monsterName, xp) {
    // Verificar se já existe
    const existing = xpCalculatorState.monsters.find(m => m.id === monsterId);

    if (existing) {
        existing.quantity++;
    } else {
        xpCalculatorState.monsters.push({
            id: monsterId,
            nome: monsterName,
            xp: xp,
            quantity: 1
        });
    }

    updateXPCalculator();
}

/**
 * Remove um monstro da calculadora de XP
 * @param {string} monsterId - ID do monstro a remover
 */
function removeMonsterFromXPCalc(monsterId) {
    xpCalculatorState.monsters = xpCalculatorState.monsters.filter(m => m.id !== monsterId);
    updateXPCalculator();
}

/**
 * Diminui a quantidade de um monstro
 * @param {string} monsterId - ID do monstro
 */
function decreaseMonsterQuantity(monsterId) {
    const monster = xpCalculatorState.monsters.find(m => m.id === monsterId);
    if (monster) {
        monster.quantity--;
        if (monster.quantity <= 0) {
            removeMonsterFromXPCalc(monsterId);
        } else {
            updateXPCalculator();
        }
    }
}

/**
 * Atualiza a calculadora de XP (calcula e renderiza)
 */
async function updateXPCalculator() {
    if (xpCalculatorState.monsters.length === 0) {
        // Lista vazia
        xpCalculatorState.totalXP = 0;
        renderXPMonstersList([]);
        updateXPDisplay(0, 0);
        return;
    }

    try {
        // Calcular XP no servidor
        const response = await fetch(`/sessao/${window.sessionId}/xp/calcular-combate`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                monsters: xpCalculatorState.monsters
            })
        });

        if (!response.ok) {
            throw new Error('Erro ao calcular XP');
        }

        const result = await response.json();
        xpCalculatorState.totalXP = result.total_xp;

        // Renderizar lista de monstros
        renderXPMonstersList(result.breakdown);

        // Atualizar displays de XP
        updateXPDisplay(result.total_xp, xpCalculatorState.partySize);
    } catch (error) {
        console.error('Erro ao atualizar calculadora de XP:', error);
    }
}

/**
 * Renderiza a lista de monstros na UI usando métodos DOM seguros
 * @param {Array} breakdown - Lista de monstros com XP calculado
 */
function renderXPMonstersList(breakdown) {
    const container = document.getElementById('xp-monsters-list');
    if (!container) return;

    // Limpar container de forma segura
    while (container.firstChild) {
        container.removeChild(container.firstChild);
    }

    if (breakdown.length === 0) {
        // Mensagem vazia
        const empty = document.createElement('p');
        empty.className = 'text-muted small mb-0';
        empty.textContent = 'Sem monstros derrotados';
        container.appendChild(empty);
        return;
    }

    // Criar item para cada monstro
    breakdown.forEach(monster => {
        const item = document.createElement('div');
        item.className = 'd-flex justify-content-between align-items-center mb-2 p-2 bg-secondary rounded';

        // Nome e quantidade
        const nameSection = document.createElement('div');
        nameSection.className = 'flex-grow-1';

        const nameText = document.createElement('span');
        nameText.className = 'small';
        nameText.textContent = `${monster.quantity}x ${monster.nome}`;
        nameSection.appendChild(nameText);

        const xpText = document.createElement('small');
        xpText.className = 'text-muted d-block';
        xpText.textContent = `${monster.xp_each} XP cada`;
        nameSection.appendChild(xpText);

        // XP total
        const xpTotal = document.createElement('span');
        xpTotal.className = 'text-warning fw-bold me-2';
        xpTotal.textContent = `${monster.xp_total} XP`;

        // Botões
        const buttons = document.createElement('div');
        buttons.className = 'd-flex gap-1';

        // Botão diminuir
        const decreaseBtn = document.createElement('button');
        decreaseBtn.className = 'btn btn-sm btn-outline-warning';
        decreaseBtn.style.padding = '0 6px';
        const decreaseIcon = document.createElement('i');
        decreaseIcon.className = 'bi bi-dash';
        decreaseBtn.appendChild(decreaseIcon);
        decreaseBtn.onclick = () => decreaseMonsterQuantity(monster.id);
        buttons.appendChild(decreaseBtn);

        // Botão remover
        const removeBtn = document.createElement('button');
        removeBtn.className = 'btn btn-sm btn-outline-danger';
        removeBtn.style.padding = '0 6px';
        const removeIcon = document.createElement('i');
        removeIcon.className = 'bi bi-x';
        removeBtn.appendChild(removeIcon);
        removeBtn.onclick = () => removeMonsterFromXPCalc(monster.id);
        buttons.appendChild(removeBtn);

        // Montar item
        item.appendChild(nameSection);
        item.appendChild(xpTotal);
        item.appendChild(buttons);
        container.appendChild(item);
    });
}

/**
 * Atualiza os displays de XP total e por jogador
 * @param {number} totalXP - XP total
 * @param {number} partySize - Tamanho do grupo
 */
function updateXPDisplay(totalXP, partySize) {
    const totalElement = document.getElementById('xp-total');
    const perPlayerElement = document.getElementById('xp-per-player');

    if (totalElement) {
        totalElement.textContent = totalXP;
    }

    if (perPlayerElement && partySize > 0) {
        const perPlayer = Math.floor(totalXP / partySize);
        perPlayerElement.textContent = perPlayer;
    } else if (perPlayerElement) {
        perPlayerElement.textContent = '0';
    }
}

/**
 * Atribui XP ao grupo
 */
async function awardXPToParty() {
    if (xpCalculatorState.totalXP === 0) {
        showNotification('Sem XP para atribuir!', 'warning');
        return;
    }

    if (!window.sessionId) {
        showNotification('Erro: Session ID não encontrado', 'danger');
        return;
    }

    try {
        const response = await fetch(`/sessao/${window.sessionId}/xp/atribuir`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                total_xp: xpCalculatorState.totalXP,
                source: 'combat',
                description: 'Combate vencido'
            })
        });

        if (!response.ok) {
            throw new Error('Erro ao atribuir XP');
        }

        const result = await response.json();

        // Mostrar notificação
        showNotification(result.message, 'success');

        // Se houver level ups, mostrar modal
        if (result.level_up && result.players_leveled_up && result.players_leveled_up.length > 0) {
            showLevelUpModal(result.players_updated, result.players_leveled_up);
        }

        // Limpar calculadora
        xpCalculatorState.monsters = [];
        xpCalculatorState.totalXP = 0;
        updateXPCalculator();

        // Recarregar página após 2 segundos se houver level up
        if (result.level_up) {
            setTimeout(() => {
                window.location.reload();
            }, 3000);
        }
    } catch (error) {
        console.error('Erro ao atribuir XP:', error);
        showNotification('Erro ao atribuir XP. Tenta novamente.', 'danger');
    }
}

/**
 * Mostra modal de level up
 * @param {Array} players - Lista de jogadores atualizados
 * @param {Array} leveledUpIds - IDs dos jogadores que subiram de nível
 */
function showLevelUpModal(players, leveledUpIds) {
    const modal = document.getElementById('levelUpModal');
    if (!modal) {
        console.warn('Modal de level up não encontrado');
        return;
    }

    // Encontrar primeiro jogador que subiu de nível
    const leveledUpPlayer = players.find(p => leveledUpIds.includes(p.id));
    if (!leveledUpPlayer) return;

    // Atualizar conteúdo do modal
    const playerNameElement = document.getElementById('levelup-player-name');
    const newLevelElement = document.getElementById('levelup-new-level');

    if (playerNameElement) {
        playerNameElement.textContent = leveledUpPlayer.nome_personagem || leveledUpPlayer.nome_jogador;
    }

    if (newLevelElement) {
        newLevelElement.textContent = leveledUpPlayer.nivel;
    }

    // Mostrar modal usando Bootstrap
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();

    // Se houver mais jogadores, mostrar sucessivamente
    if (leveledUpIds.length > 1) {
        modal.addEventListener('hidden.bs.modal', function handler() {
            modal.removeEventListener('hidden.bs.modal', handler);

            // Remover o primeiro da lista e mostrar o próximo
            const remainingIds = leveledUpIds.slice(1);
            if (remainingIds.length > 0) {
                setTimeout(() => {
                    showLevelUpModal(players, remainingIds);
                }, 500);
            }
        });
    }
}

/**
 * Adiciona automaticamente monstros derrotados ao XP calculator
 * Chamado quando um monstro é derrotado (HP = 0)
 */
function autoAddDefeatedToXP() {
    if (!window.combatState) return;

    combatState.participants.forEach(p => {
        if (p.tipo === 'monstro' && p.hp_atual === 0) {
            // Verificar se já não foi adicionado
            const inCalc = xpCalculatorState.monsters.find(m => m.id === p.id);
            if (!inCalc) {
                const xp = p.xp || 50;  // XP padrão se não especificado
                addMonsterToXPCalc(p.id, p.nome, xp);
            }
        }
    });
}

/**
 * Limpa a calculadora de XP
 */
function clearXPCalculator() {
    xpCalculatorState.monsters = [];
    xpCalculatorState.totalXP = 0;
    updateXPCalculator();
}

/**
 * Mostra uma notificação (usa sistema global se disponível)
 * @param {string} message - Mensagem a mostrar
 * @param {string} type - Tipo de notificação (success, danger, warning, info)
 */
function showNotification(message, type = 'info') {
    // Usar sistema global se disponível
    if (window.DnDCompanion && window.DnDCompanion.showNotification) {
        window.DnDCompanion.showNotification(message, type);
        return;
    }

    // Fallback: alert simples
    alert(message);
}

/**
 * Inicializa a calculadora de XP
 * Deve ser chamado quando a página carrega
 */
function initXPCalculator(sessionId, partySize = 0) {
    window.sessionId = sessionId;
    xpCalculatorState.partySize = partySize;

    console.log('XP Calculator inicializado:', {
        sessionId,
        partySize
    });

    // Atualizar display inicial
    updateXPDisplay(0, partySize);
}

// Export para uso global se necessário
if (typeof window !== 'undefined') {
    window.XPCalculator = {
        init: initXPCalculator,
        addMonster: addMonsterToXPCalc,
        removeMonster: removeMonsterFromXPCalc,
        update: updateXPCalculator,
        award: awardXPToParty,
        clear: clearXPCalculator,
        autoAddDefeated: autoAddDefeatedToXP
    };
}
