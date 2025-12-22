/**
 * TimeTracker - Gestao dos 4 sistemas de tempo da sessao
 *
 * Sistemas rastreados:
 * 1. Tempo de Sessao (real-world): Cronometro com start/pause
 * 2. Rondas de Combate: 6 segundos por ronda (D&D 5e)
 * 3. Turnos de Exploracao: 10 minutos por turno
 * 4. Tempo no Jogo: Hora do dia, dias decorridos, descansos
 *
 * Auto-actualiza a cada segundo quando o cronometro esta activo.
 */

class TimeTracker {
    constructor(sessionId, options = {}) {
        this.sessionId = sessionId;

        // Opcoes de configuracao
        this.options = {
            autoUpdate: options.autoUpdate !== false,  // Default: true
            updateInterval: options.updateInterval || 1000,  // 1 segundo
            onUpdate: options.onUpdate || null,  // Callback em cada update
            onError: options.onError || null  // Callback em erros
        };

        // Estado do tracker
        this.isRunning = false;
        this.updateTimer = null;

        // Elementos DOM (podem ser configurados depois)
        this.elements = {
            sessionDuration: null,
            sessionControls: null,
            combatTime: null,
            explorationTurns: null,
            gameTime: null
        };

        // Cache dos ultimos dados
        this.lastData = null;

        // Iniciar auto-update se configurado
        if (this.options.autoUpdate) {
            this.startAutoUpdate();
        }
    }

    /**
     * Configurar elementos DOM para exibicao automatica
     */
    setElements(elementIds) {
        this.elements.sessionDuration = elementIds.sessionDuration ?
            document.getElementById(elementIds.sessionDuration) : null;
        this.elements.sessionControls = elementIds.sessionControls ?
            document.getElementById(elementIds.sessionControls) : null;
        this.elements.combatTime = elementIds.combatTime ?
            document.getElementById(elementIds.combatTime) : null;
        this.elements.explorationTurns = elementIds.explorationTurns ?
            document.getElementById(elementIds.explorationTurns) : null;
        this.elements.gameTime = elementIds.gameTime ?
            document.getElementById(elementIds.gameTime) : null;
    }

    /**
     * Iniciar cronometro de sessao
     */
    async start() {
        try {
            const response = await fetch(`/sessao/${this.sessionId}/tempo/iniciar`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Falha ao iniciar cronometro');
            }

            this.isRunning = true;
            this.startAutoUpdate();
            await this.update();

            return true;
        } catch (error) {
            console.error('Erro ao iniciar cronometro:', error);
            if (this.options.onError) {
                this.options.onError(error);
            }
            return false;
        }
    }

    /**
     * Pausar cronometro de sessao
     */
    async pause() {
        try {
            const response = await fetch(`/sessao/${this.sessionId}/tempo/pausar`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Falha ao pausar cronometro');
            }

            const data = await response.json();
            this.isRunning = false;
            this.stopAutoUpdate();
            await this.update();

            return data.total_seconds;
        } catch (error) {
            console.error('Erro ao pausar cronometro:', error);
            if (this.options.onError) {
                this.options.onError(error);
            }
            return 0;
        }
    }

    /**
     * Obter estado completo de todos os sistemas de tempo
     */
    async update() {
        try {
            const response = await fetch(`/sessao/${this.sessionId}/tempo/status`);

            if (!response.ok) {
                throw new Error('Falha ao obter estado do tempo');
            }

            const data = await response.json();
            this.lastData = data;
            this.isRunning = data.session_running;

            // Actualizar elementos DOM se configurados
            this.updateDOM(data);

            // Callback personalizado
            if (this.options.onUpdate) {
                this.options.onUpdate(data);
            }

            return data;
        } catch (error) {
            console.error('Erro ao actualizar tempo:', error);
            if (this.options.onError) {
                this.options.onError(error);
            }
            return null;
        }
    }

    /**
     * Actualizar elementos DOM com dados de tempo
     */
    updateDOM(data) {
        // Duracao da sessao
        if (this.elements.sessionDuration) {
            const duration = data.session_duration;
            this.elements.sessionDuration.textContent = duration.formatted;
        }

        // Tempo de combate
        if (this.elements.combatTime) {
            const combat = data.combat_time;
            if (combat.rounds > 0) {
                this.elements.combatTime.textContent =
                    `Ronda ${combat.rounds} (${combat.real_formatted})`;
            } else {
                this.elements.combatTime.textContent = '-';
            }
        }

        // Turnos de exploracao
        if (this.elements.explorationTurns) {
            this.elements.explorationTurns.textContent = data.exploration_turns;
        }

        // Tempo no jogo
        if (this.elements.gameTime) {
            this.elements.gameTime.textContent = data.game_time.formatted;
        }
    }

    /**
     * Avancar tempo no jogo
     */
    async advanceGameTime(minutes = 0, hours = 0, days = 0) {
        try {
            const response = await fetch(`/sessao/${this.sessionId}/tempo/avancar`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ minutes, hours, days })
            });

            if (!response.ok) {
                throw new Error('Falha ao avancar tempo');
            }

            const data = await response.json();
            await this.update();

            return data;
        } catch (error) {
            console.error('Erro ao avancar tempo:', error);
            if (this.options.onError) {
                this.options.onError(error);
            }
            return null;
        }
    }

    /**
     * Definir tempo no jogo manualmente
     */
    async setGameTime(dia, hora) {
        try {
            const response = await fetch(`/sessao/${this.sessionId}/tempo/definir`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ dia, hora })
            });

            if (!response.ok) {
                throw new Error('Falha ao definir tempo');
            }

            const data = await response.json();
            await this.update();

            return data;
        } catch (error) {
            console.error('Erro ao definir tempo:', error);
            if (this.options.onError) {
                this.options.onError(error);
            }
            return null;
        }
    }

    /**
     * Registar descanso (curto ou longo)
     */
    async registerRest(restType) {
        if (restType !== 'curto' && restType !== 'longo') {
            console.error('Tipo de descanso invalido:', restType);
            return null;
        }

        try {
            const response = await fetch(`/sessao/${this.sessionId}/tempo/descanso`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ tipo: restType })
            });

            if (!response.ok) {
                throw new Error('Falha ao registar descanso');
            }

            const data = await response.json();
            await this.update();

            return data;
        } catch (error) {
            console.error('Erro ao registar descanso:', error);
            if (this.options.onError) {
                this.options.onError(error);
            }
            return null;
        }
    }

    /**
     * Avancar turnos de exploracao
     */
    async advanceExplorationTurns(turns = 1) {
        try {
            const response = await fetch(`/sessao/${this.sessionId}/tempo/exploracao/avancar`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ turnos: turns })
            });

            if (!response.ok) {
                throw new Error('Falha ao avancar exploracao');
            }

            const data = await response.json();
            await this.update();

            return data;
        } catch (error) {
            console.error('Erro ao avancar exploracao:', error);
            if (this.options.onError) {
                this.options.onError(error);
            }
            return null;
        }
    }

    /**
     * Iniciar actualizacao automatica
     */
    startAutoUpdate() {
        if (this.updateTimer) {
            return;  // Ja esta a correr
        }

        this.updateTimer = setInterval(() => {
            this.update();
        }, this.options.updateInterval);
    }

    /**
     * Parar actualizacao automatica
     */
    stopAutoUpdate() {
        if (this.updateTimer) {
            clearInterval(this.updateTimer);
            this.updateTimer = null;
        }
    }

    /**
     * Destruir tracker (limpar timers)
     */
    destroy() {
        this.stopAutoUpdate();
        this.lastData = null;
    }

    /**
     * Obter ultimos dados em cache
     */
    getLastData() {
        return this.lastData;
    }

    /**
     * Verificar se o cronometro esta a correr
     */
    isTimerRunning() {
        return this.isRunning;
    }

    /**
     * Formatar segundos para formato legivel
     */
    static formatSeconds(totalSeconds) {
        const hours = Math.floor(totalSeconds / 3600);
        const minutes = Math.floor((totalSeconds % 3600) / 60);
        const seconds = totalSeconds % 60;

        if (hours > 0) {
            return `${hours}h ${minutes}m ${seconds}s`;
        } else if (minutes > 0) {
            return `${minutes}m ${seconds}s`;
        } else {
            return `${seconds}s`;
        }
    }

    /**
     * Formatar tempo no jogo
     */
    static formatGameTime(dia, hora) {
        return `Dia ${dia}, ${hora}`;
    }
}

/**
 * Helper para criar botoes de controlo de tempo
 */
class TimeControlsBuilder {
    constructor(timeTracker) {
        this.tracker = timeTracker;
    }

    /**
     * Criar botao de start/pause
     */
    createStartPauseButton(containerId) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.warn(`Container "${containerId}" nao encontrado`);
            return;
        }

        const button = document.createElement('button');
        button.className = 'btn btn-success btn-sm me-2';

        const icon = document.createElement('i');
        icon.className = 'bi bi-play';
        button.appendChild(icon);

        const text = document.createTextNode(' Iniciar');
        button.appendChild(text);

        button.addEventListener('click', async () => {
            if (this.tracker.isTimerRunning()) {
                await this.tracker.pause();
                button.className = 'btn btn-success btn-sm me-2';

                // Limpar conteudo anterior
                while (button.firstChild) {
                    button.removeChild(button.firstChild);
                }

                const playIcon = document.createElement('i');
                playIcon.className = 'bi bi-play';
                button.appendChild(playIcon);
                button.appendChild(document.createTextNode(' Iniciar'));
            } else {
                await this.tracker.start();
                button.className = 'btn btn-warning btn-sm me-2';

                // Limpar conteudo anterior
                while (button.firstChild) {
                    button.removeChild(button.firstChild);
                }

                const pauseIcon = document.createElement('i');
                pauseIcon.className = 'bi bi-pause';
                button.appendChild(pauseIcon);
                button.appendChild(document.createTextNode(' Pausar'));
            }
        });

        container.appendChild(button);
        return button;
    }

    /**
     * Criar botoes de avanco de tempo
     */
    createGameTimeButtons(containerId) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.warn(`Container "${containerId}" nao encontrado`);
            return;
        }

        const buttonGroup = document.createElement('div');
        buttonGroup.className = 'btn-group btn-group-sm';

        const buttons = [
            { label: '+10min', minutes: 10 },
            { label: '+1h', hours: 1 },
            { label: '+8h', hours: 8 },
            { label: '+1 dia', days: 1 }
        ];

        buttons.forEach(config => {
            const btn = document.createElement('button');
            btn.className = 'btn btn-outline-info';
            btn.textContent = config.label;
            btn.addEventListener('click', () => {
                this.tracker.advanceGameTime(
                    config.minutes || 0,
                    config.hours || 0,
                    config.days || 0
                );
            });
            buttonGroup.appendChild(btn);
        });

        container.appendChild(buttonGroup);
        return buttonGroup;
    }

    /**
     * Criar botoes de descanso
     */
    createRestButtons(containerId) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.warn(`Container "${containerId}" nao encontrado`);
            return;
        }

        const buttonGroup = document.createElement('div');
        buttonGroup.className = 'btn-group btn-group-sm';

        // Descanso curto
        const shortRest = document.createElement('button');
        shortRest.className = 'btn btn-outline-warning';

        const shortIcon = document.createElement('i');
        shortIcon.className = 'bi bi-moon';
        shortRest.appendChild(shortIcon);

        shortRest.appendChild(document.createTextNode(' Descanso Curto (1h)'));
        shortRest.addEventListener('click', () => {
            this.tracker.registerRest('curto');
        });

        // Descanso longo
        const longRest = document.createElement('button');
        longRest.className = 'btn btn-outline-primary';

        const longIcon = document.createElement('i');
        longIcon.className = 'bi bi-moon-stars';
        longRest.appendChild(longIcon);

        longRest.appendChild(document.createTextNode(' Descanso Longo (8h)'));
        longRest.addEventListener('click', () => {
            this.tracker.registerRest('longo');
        });

        buttonGroup.appendChild(shortRest);
        buttonGroup.appendChild(longRest);
        container.appendChild(buttonGroup);

        return buttonGroup;
    }

    /**
     * Criar botao de avanco de exploracao
     */
    createExplorationButton(containerId) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.warn(`Container "${containerId}" nao encontrado`);
            return;
        }

        const button = document.createElement('button');
        button.className = 'btn btn-outline-warning btn-sm';

        const icon = document.createElement('i');
        icon.className = 'bi bi-compass';
        button.appendChild(icon);

        button.appendChild(document.createTextNode(' +1 Turno (10min)'));

        button.addEventListener('click', () => {
            this.tracker.advanceExplorationTurns(1);
        });

        container.appendChild(button);
        return button;
    }

    /**
     * Criar botao de avanco de ronda de combate
     */
    createCombatRoundButton(containerId) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.warn(`Container "${containerId}" nao encontrado`);
            return;
        }

        const button = document.createElement('button');
        button.className = 'btn btn-outline-danger btn-sm';

        const icon = document.createElement('i');
        icon.className = 'bi bi-skip-forward';
        button.appendChild(icon);

        button.appendChild(document.createTextNode(' +1'));

        button.title = 'Avançar Ronda';

        button.addEventListener('click', async () => {
            console.log('Botao de avancar ronda clicado');

            try {
                const response = await fetch(`/sessao/${this.tracker.sessionId}/tempo/combate/avancar`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });

                if (!response.ok) {
                    const error = await response.json();
                    console.error('Erro ao avancar ronda:', error);

                    // Mostrar alerta ao utilizador
                    if (error.error && error.error.includes('combate activo')) {
                        alert('Não há combate ativo. Inicie um combate primeiro.');
                    } else {
                        alert('Erro ao avançar ronda: ' + (error.error || 'Erro desconhecido'));
                    }
                    return;
                }

                const data = await response.json();
                console.log('Ronda avancada:', data);

                // Actualizar tracker
                await this.tracker.update();

                // Se houver callback global de atualizacao de combate, chamar
                if (window.combatState && typeof window.combatState.updateRound === 'function') {
                    window.combatState.updateRound(data.ronda_atual);
                }
            } catch (error) {
                console.error('Erro ao avancar ronda de combate:', error);
                alert('Erro de conexão ao avançar ronda');
            }
        });

        container.appendChild(button);
        console.log(`Botao de combate criado em "${containerId}"`);
        return button;
    }
}
