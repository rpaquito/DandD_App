/**
 * Sistema de Notas de Sessão com Autosave
 *
 * Fornece funcionalidade de autosave para as notas da sessão,
 * guardando automaticamente após 3 segundos de inatividade.
 */

let notesAutosaveTimeout = null;
const AUTOSAVE_DELAY = 3000; // 3 segundos após parar de escrever

/**
 * Configura o sistema de autosave para o textarea de notas
 */
function setupNotesAutosave() {
    const textarea = document.getElementById('session-notes');
    if (!textarea) {
        console.warn('Textarea de notas não encontrado');
        return;
    }

    // Event listener para input
    textarea.addEventListener('input', function() {
        // Limpar timeout anterior se existir
        if (notesAutosaveTimeout) {
            clearTimeout(notesAutosaveTimeout);
        }

        // Mostrar status "A escrever..."
        updateNotesSaveStatus('A escrever...', 'text-muted');

        // Agendar save após delay
        notesAutosaveTimeout = setTimeout(() => {
            saveNotes(true); // autosave = true
        }, AUTOSAVE_DELAY);
    });

    console.log('Sistema de autosave de notas iniciado');
}

/**
 * Guarda as notas no servidor
 * @param {boolean} isAutosave - Se true, é um autosave (não mostra notificação)
 */
async function saveNotes(isAutosave = false) {
    const textarea = document.getElementById('session-notes');
    if (!textarea) {
        console.error('Textarea de notas não encontrado');
        return;
    }

    const notas = textarea.value;

    // Atualizar status
    updateNotesSaveStatus('A guardar...', 'text-info');

    try {
        // Obter session ID do window ou do elemento
        const sessionId = window.sessionId || textarea.dataset.sessionId;
        if (!sessionId) {
            throw new Error('Session ID não encontrado');
        }

        const response = await fetch(`/sessao/${sessionId}/notas`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: 'notas=' + encodeURIComponent(notas)
        });

        if (response.ok) {
            // Sucesso
            updateNotesSaveStatus('Guardado!', 'text-success');

            // Limpar status após 2 segundos
            setTimeout(() => {
                updateNotesSaveStatus('', '');
            }, 2000);

            // Se não for autosave, mostrar notificação
            if (!isAutosave && window.DnDCompanion && window.DnDCompanion.showNotification) {
                window.DnDCompanion.showNotification('Notas guardadas com sucesso!', 'success');
            }
        } else {
            throw new Error('Erro ao guardar notas: ' + response.status);
        }
    } catch (error) {
        console.error('Erro ao guardar notas:', error);
        updateNotesSaveStatus('Erro ao guardar', 'text-danger');

        // Se não for autosave, mostrar erro ao utilizador
        if (!isAutosave) {
            alert('Erro ao guardar notas. Por favor tenta novamente.');
        }
    }
}

/**
 * Atualiza o texto e cor do status de save
 * @param {string} text - Texto a mostrar
 * @param {string} cssClass - Classe CSS para cor (text-success, text-danger, etc)
 */
function updateNotesSaveStatus(text, cssClass = '') {
    const statusElement = document.getElementById('notes-save-status');
    if (statusElement) {
        statusElement.textContent = text;

        // Remover classes anteriores de cor
        statusElement.className = '';

        // Adicionar nova classe
        if (cssClass) {
            statusElement.className = cssClass;
        }
    }
}

// Inicializar quando a página carrega
document.addEventListener('DOMContentLoaded', function() {
    console.log('Session notes script carregado');
    setupNotesAutosave();
});
