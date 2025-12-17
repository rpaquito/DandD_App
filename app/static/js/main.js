/**
 * Companheiro de Mestre de Dungeon
 * JavaScript principal da aplicação
 */

// ============================================
// Sistema de Dados Virtuais
// ============================================

/**
 * Lança um dado do tipo especificado
 * @param {number} sides - Número de faces do dado
 * @returns {number} Resultado do lançamento
 */
function rollDie(sides) {
    return Math.floor(Math.random() * sides) + 1;
}

/**
 * Processa uma expressão de dados (ex: "2d6+3")
 * @param {string} expression - Expressão de dados
 * @returns {object} Resultado com total e detalhes
 */
function parseDiceExpression(expression) {
    const regex = /(\d+)?d(\d+)([+-]\d+)?/i;
    const match = expression.match(regex);

    if (!match) {
        return { error: 'Expressão inválida. Usa formato: 2d6+3' };
    }

    const count = parseInt(match[1]) || 1;
    const sides = parseInt(match[2]);
    const modifier = parseInt(match[3]) || 0;

    const rolls = [];
    for (let i = 0; i < count; i++) {
        rolls.push(rollDie(sides));
    }

    const total = rolls.reduce((a, b) => a + b, 0) + modifier;

    return {
        rolls: rolls,
        modifier: modifier,
        total: total,
        expression: `${count}d${sides}${modifier >= 0 ? '+' : ''}${modifier !== 0 ? modifier : ''}`
    };
}

/**
 * Cria elemento de resultado de dados de forma segura
 * @param {number} total - Total do lançamento
 * @param {array} rolls - Array com resultados individuais
 * @param {number} mod - Modificador
 * @returns {DocumentFragment} Fragmento DOM com o resultado
 */
function createDiceResultElement(total, rolls, mod) {
    const fragment = document.createDocumentFragment();

    const container = document.createElement('div');
    container.className = 'dice-result-animation';

    const totalSpan = document.createElement('span');
    totalSpan.className = 'fs-2 text-warning fw-bold';
    totalSpan.textContent = total;
    container.appendChild(totalSpan);

    const detailsDiv = document.createElement('div');
    detailsDiv.className = 'small text-muted mt-1';
    let detailText = '[' + rolls.join(' + ') + ']';
    if (mod !== 0) {
        detailText += (mod > 0 ? ' + ' : ' - ') + Math.abs(mod);
    }
    detailsDiv.textContent = detailText;
    container.appendChild(detailsDiv);

    fragment.appendChild(container);
    return fragment;
}

// Event listeners para botões de dados no modal
document.addEventListener('DOMContentLoaded', function() {
    const diceBtns = document.querySelectorAll('.dice-btn');
    const diceResult = document.getElementById('diceResult');
    const diceCount = document.getElementById('diceCount');
    const diceModifier = document.getElementById('diceModifier');

    diceBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const dice = this.dataset.dice;
            const sides = parseInt(dice.replace('d', ''));
            const count = parseInt(diceCount?.value) || 1;
            const mod = parseInt(diceModifier?.value) || 0;

            const rolls = [];
            for (let i = 0; i < count; i++) {
                rolls.push(rollDie(sides));
            }

            const total = rolls.reduce((a, b) => a + b, 0) + mod;

            if (diceResult) {
                // Limpar conteúdo anterior de forma segura
                while (diceResult.firstChild) {
                    diceResult.removeChild(diceResult.firstChild);
                }
                diceResult.appendChild(createDiceResultElement(total, rolls, mod));
            }
        });
    });
});


// ============================================
// Utilitários de UI
// ============================================

/**
 * Mostra uma notificação temporária
 * @param {string} message - Mensagem a mostrar
 * @param {string} type - Tipo: success, danger, warning, info
 */
function showNotification(message, type = 'info') {
    const container = document.querySelector('.container') || document.body;

    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alert.style.cssText = 'top: 80px; right: 20px; z-index: 9999; max-width: 400px;';

    // Adicionar texto de forma segura
    const textNode = document.createTextNode(message);
    alert.appendChild(textNode);

    // Criar botão de fechar
    const closeBtn = document.createElement('button');
    closeBtn.type = 'button';
    closeBtn.className = 'btn-close';
    closeBtn.setAttribute('data-bs-dismiss', 'alert');
    alert.appendChild(closeBtn);

    container.appendChild(alert);

    // Auto-remover após 5 segundos
    setTimeout(() => {
        alert.classList.remove('show');
        setTimeout(() => alert.remove(), 150);
    }, 5000);
}

/**
 * Formata um número com sinal (+/-)
 * @param {number} num - Número a formatar
 * @returns {string} Número formatado com sinal
 */
function formatModifier(num) {
    return num >= 0 ? `+${num}` : `${num}`;
}

/**
 * Calcula o modificador de atributo D&D
 * @param {number} score - Valor do atributo (1-30)
 * @returns {number} Modificador
 */
function calculateModifier(score) {
    return Math.floor((score - 10) / 2);
}


// ============================================
// Gerador de Nomes Aleatórios (Português)
// ============================================

const nomesPortugueses = {
    masculinos: [
        'Afonso', 'Álvaro', 'Bernardo', 'Diogo', 'Duarte', 'Estêvão',
        'Fernando', 'Gaspar', 'Gonçalo', 'Henrique', 'João', 'Jorge',
        'Lourenço', 'Manuel', 'Martim', 'Nuno', 'Pedro', 'Rodrigo',
        'Sebastião', 'Tomás', 'Vasco', 'Vicente'
    ],
    femininos: [
        'Aldonça', 'Beatriz', 'Branca', 'Catarina', 'Constança', 'Elvira',
        'Filipa', 'Guiomar', 'Helena', 'Inês', 'Isabel', 'Joana',
        'Leonor', 'Luísa', 'Maria', 'Margarida', 'Mécia', 'Teresa'
    ],
    apelidos: [
        'da Silva', 'Fernandes', 'Gonçalves', 'Lopes', 'Martins',
        'Mendes', 'Oliveira', 'Pereira', 'Ribeiro', 'Rodrigues',
        'Santos', 'Sousa', 'Ferreira', 'Costa', 'Carvalho'
    ],
    alcunhas: [
        'o Bravo', 'o Sábio', 'o Justo', 'o Forte', 'o Temível',
        'o Velho', 'o Jovem', 'o Grande', 'o Belo', 'o Negro',
        'o Ruivo', 'Mão de Ferro', 'Olhos de Águia', 'Pé Ligeiro'
    ]
};

/**
 * Gera um nome aleatório
 * @param {string} genero - 'masculino', 'feminino', ou 'aleatorio'
 * @param {boolean} comAlcunha - Se deve incluir alcunha
 * @returns {string} Nome gerado
 */
function gerarNome(genero = 'aleatorio', comAlcunha = false) {
    if (genero === 'aleatorio') {
        genero = Math.random() > 0.5 ? 'masculino' : 'feminino';
    }

    const nomes = genero === 'masculino' ? nomesPortugueses.masculinos : nomesPortugueses.femininos;
    const nome = nomes[Math.floor(Math.random() * nomes.length)];
    const apelido = nomesPortugueses.apelidos[Math.floor(Math.random() * nomesPortugueses.apelidos.length)];

    let nomeCompleto = `${nome} ${apelido}`;

    if (comAlcunha && Math.random() > 0.5) {
        const alcunha = nomesPortugueses.alcunhas[Math.floor(Math.random() * nomesPortugueses.alcunhas.length)];
        nomeCompleto += `, ${alcunha}`;
    }

    return nomeCompleto;
}


// ============================================
// Exportar funções para uso global
// ============================================

window.DnDCompanion = {
    rollDie,
    parseDiceExpression,
    showNotification,
    formatModifier,
    calculateModifier,
    gerarNome,
    createDiceResultElement
};
