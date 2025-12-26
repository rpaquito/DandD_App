/**
 * MapGrid - Interactive tactical map with drag-and-drop entity positioning
 *
 * Features:
 * - HTML5 Canvas grid rendering
 * - Drag-and-drop entity movement with snap-to-grid
 * - Entity type filters (players/NPCs/monsters)
 * - Background image support
 * - Hover and selection states
 */

class MapGrid {
    constructor(canvasId, config) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) {
            console.error(`Canvas com id "${canvasId}" nao encontrado`);
            return;
        }

        this.ctx = this.canvas.getContext('2d');

        // Configuracao do mapa
        this.config = {
            gridWidth: config.gridWidth || 20,
            gridHeight: config.gridHeight || 20,
            squareSizeMeters: config.squareSizeMeters || 1.5,
            backgroundImage: config.backgroundImage || null,
            cellSize: config.cellSize || 40  // Pixels por quadrado
        };

        // Calcular dimensoes do canvas
        const width = this.config.gridWidth * this.config.cellSize;
        const height = this.config.gridHeight * this.config.cellSize;

        // Configurar dimensoes do canvas (previne esticamento por CSS)
        this.canvas.width = width;
        this.canvas.height = height;
        this.canvas.style.width = width + 'px';
        this.canvas.style.height = height + 'px';

        // Ajustar para displays de alta resolucao (Retina)
        const dpr = window.devicePixelRatio || 1;
        if (dpr > 1) {
            this.canvas.width = width * dpr;
            this.canvas.height = height * dpr;
            this.canvas.style.width = width + 'px';
            this.canvas.style.height = height + 'px';
            this.ctx.scale(dpr, dpr);
        }

        // Entidades no mapa
        this.entities = [];

        // Estado de interaccao
        this.selectedEntity = null;
        this.hoveredEntity = null;
        this.isDragging = false;
        this.dragOffset = { x: 0, y: 0 };

        // Filtros de visibilidade
        this.filters = {
            showPlayers: true,
            showNPCs: true,
            showMonsters: true
        };

        // Callbacks
        this.onEntityMoved = null;  // Callback quando entidade e movida
        this.onEntitySelected = null;  // Callback quando entidade e seleccionada

        // Participante activo (para highlighting)
        this.activeParticipantId = null;

        // Imagem de fundo
        this.backgroundImg = null;
        if (this.config.backgroundImage && this.config.backgroundImage !== 'null') {
            this.loadBackgroundImage(this.config.backgroundImage);
        }

        // Event listeners
        this.setupEventListeners();

        // Render inicial
        this.render();
    }

    /**
     * Carregar imagem de fundo
     */
    loadBackgroundImage(url) {
        this.backgroundImg = new Image();
        this.backgroundImg.onload = () => {
            this.render();
        };
        this.backgroundImg.onerror = () => {
            console.warn(`Falha ao carregar imagem de fundo: ${url}`);
            this.backgroundImg = null;
        };
        this.backgroundImg.src = url;
    }

    /**
     * Configurar event listeners
     */
    setupEventListeners() {
        this.canvas.addEventListener('mousedown', this.handleMouseDown.bind(this));
        this.canvas.addEventListener('mousemove', this.handleMouseMove.bind(this));
        this.canvas.addEventListener('mouseup', this.handleMouseUp.bind(this));
        this.canvas.addEventListener('mouseleave', this.handleMouseLeave.bind(this));

        // Touch events para mobile
        this.canvas.addEventListener('touchstart', this.handleTouchStart.bind(this));
        this.canvas.addEventListener('touchmove', this.handleTouchMove.bind(this));
        this.canvas.addEventListener('touchend', this.handleTouchEnd.bind(this));
    }

    /**
     * Carregar entidades no mapa
     */
    loadEntities(entities) {
        this.entities = entities || [];
        this.render();
    }

    /**
     * Actualizar entidade especifica
     */
    updateEntity(entityId, updates) {
        const entity = this.entities.find(e => e.entity_id === entityId);
        if (entity) {
            Object.assign(entity, updates);
            this.render();
        }
    }

    /**
     * Adicionar nova entidade
     */
    addEntity(entity) {
        this.entities.push(entity);
        this.render();
    }

    /**
     * Remover entidade
     */
    removeEntity(entityId) {
        this.entities = this.entities.filter(e => e.entity_id !== entityId);
        if (this.selectedEntity && this.selectedEntity.entity_id === entityId) {
            this.selectedEntity = null;
        }
        this.render();
    }

    /**
     * Definir filtro de visibilidade
     */
    setFilter(filterName, value) {
        if (this.filters.hasOwnProperty(filterName)) {
            this.filters[filterName] = value;
            this.render();
        }
    }

    /**
     * Verificar se entidade deve ser visivel
     */
    isEntityVisible(entity) {
        if (!entity.visivel) return false;

        switch (entity.entity_type) {
            case 'jogador':
                return this.filters.showPlayers;
            case 'npc':
                return this.filters.showNPCs;
            case 'monstro':
                return this.filters.showMonsters;
            default:
                return true;
        }
    }

    /**
     * Renderizar mapa completo
     */
    render() {
        // Limpar canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Desenhar imagem de fundo
        if (this.backgroundImg && this.backgroundImg.complete) {
            this.ctx.drawImage(this.backgroundImg, 0, 0, this.canvas.width, this.canvas.height);
        }

        // Desenhar grelha
        this.drawGrid();

        // Desenhar entidades
        this.entities.forEach(entity => {
            if (this.isEntityVisible(entity)) {
                this.drawEntity(entity);
            }
        });

        // Desenhar entidade seleccionada por cima
        if (this.selectedEntity && this.isEntityVisible(this.selectedEntity)) {
            this.drawEntityHighlight(this.selectedEntity, '#ffff00', 3);
        }

        // Desenhar participante activo (turno actual)
        if (this.activeParticipantId) {
            const activeEntity = this.entities.find(e => e.entity_id === this.activeParticipantId);
            if (activeEntity && this.isEntityVisible(activeEntity) && activeEntity !== this.selectedEntity) {
                this.drawEntityHighlight(activeEntity, '#00ff00', 3);
                this.drawEntityPulse(activeEntity);
            }
        }

        // Desenhar entidade sob hover
        if (this.hoveredEntity && this.hoveredEntity !== this.selectedEntity && this.isEntityVisible(this.hoveredEntity)) {
            this.drawEntityHighlight(this.hoveredEntity, '#ffffff', 2);
        }

        // Desenhar tooltip para entidade sob hover
        if (this.hoveredEntity && this.isEntityVisible(this.hoveredEntity)) {
            this.drawTooltip(this.hoveredEntity);
        }
    }

    /**
     * Desenhar grelha
     */
    drawGrid() {
        const cellSize = this.config.cellSize;

        this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
        this.ctx.lineWidth = 1;

        // Linhas verticais
        // Adicionar 0.5 para alinhar perfeitamente com pixels (evita blur)
        for (let x = 0; x <= this.config.gridWidth; x++) {
            const posX = Math.floor(x * cellSize) + 0.5;
            this.ctx.beginPath();
            this.ctx.moveTo(posX, 0);
            this.ctx.lineTo(posX, this.canvas.height);
            this.ctx.stroke();
        }

        // Linhas horizontais
        for (let y = 0; y <= this.config.gridHeight; y++) {
            const posY = Math.floor(y * cellSize) + 0.5;
            this.ctx.beginPath();
            this.ctx.moveTo(0, posY);
            this.ctx.lineTo(this.canvas.width, posY);
            this.ctx.stroke();
        }
    }

    /**
     * Desenhar entidade
     */
    drawEntity(entity) {
        const cellSize = this.config.cellSize;
        const centerX = entity.grid_x * cellSize + cellSize / 2;
        const centerY = entity.grid_y * cellSize + cellSize / 2;
        const radius = cellSize * 0.35;

        // Desenhar circulo (token)
        this.ctx.fillStyle = entity.token_cor || '#ffffff';
        this.ctx.beginPath();
        this.ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
        this.ctx.fill();

        // Borda do token
        this.ctx.strokeStyle = '#000000';
        this.ctx.lineWidth = 2;
        this.ctx.stroke();

        // Icone (usar primeira letra do tipo se nao tiver icone)
        this.ctx.fillStyle = '#000000';
        this.ctx.font = 'bold 16px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';

        let iconText = '?';
        if (entity.entity_type === 'jogador') iconText = 'J';
        else if (entity.entity_type === 'npc') iconText = 'N';
        else if (entity.entity_type === 'monstro') iconText = 'M';

        this.ctx.fillText(iconText, centerX, centerY);

        // Nome da entidade abaixo do token
        this.ctx.fillStyle = '#ffffff';
        this.ctx.font = '10px Arial';
        const entityName = this.getEntityDisplayName(entity);
        this.ctx.fillText(entityName, centerX, centerY + radius + 12);
    }

    /**
     * Desenhar highlight em volta da entidade
     */
    drawEntityHighlight(entity, color, lineWidth) {
        const cellSize = this.config.cellSize;
        const centerX = entity.grid_x * cellSize + cellSize / 2;
        const centerY = entity.grid_y * cellSize + cellSize / 2;
        const radius = cellSize * 0.4;

        this.ctx.strokeStyle = color;
        this.ctx.lineWidth = lineWidth;
        this.ctx.beginPath();
        this.ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
        this.ctx.stroke();
    }

    /**
     * Desenhar efeito de pulso no participante activo
     */
    drawEntityPulse(entity) {
        const cellSize = this.config.cellSize;
        const centerX = entity.grid_x * cellSize + cellSize / 2;
        const centerY = entity.grid_y * cellSize + cellSize / 2;
        const baseRadius = cellSize * 0.4;

        // Criar pulso animado
        const time = Date.now() / 1000;
        const pulseRadius = baseRadius + Math.sin(time * 3) * 5;

        this.ctx.strokeStyle = 'rgba(0, 255, 0, 0.5)';
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();
        this.ctx.arc(centerX, centerY, pulseRadius, 0, Math.PI * 2);
        this.ctx.stroke();

        // Continuar animacao
        if (this.activeParticipantId) {
            requestAnimationFrame(() => this.render());
        }
    }

    /**
     * Desenhar tooltip com informacoes da entidade
     */
    drawTooltip(entity) {
        const cellSize = this.config.cellSize;
        const centerX = entity.grid_x * cellSize + cellSize / 2;
        const centerY = entity.grid_y * cellSize + cellSize / 2;

        // Obter informacoes da entidade (se disponiveis)
        const nome = entity.nome || this.getEntityDisplayName(entity);
        const ac = entity.ac ? `AC: ${entity.ac}` : '';
        const hp = entity.hp_atual !== undefined ? `HP: ${entity.hp_atual}/${entity.hp_max || entity.hp_atual}` : '';

        // Construir texto do tooltip
        const lines = [nome];
        if (ac) lines.push(ac);
        if (hp) lines.push(hp);

        // Configurar estilo
        this.ctx.font = '12px Arial';
        const padding = 6;
        const lineHeight = 14;

        // Calcular dimensoes do tooltip
        const maxWidth = Math.max(...lines.map(line => this.ctx.measureText(line).width));
        const boxWidth = maxWidth + padding * 2;
        const boxHeight = lines.length * lineHeight + padding * 2;

        // Posicao do tooltip (acima da entidade)
        let tooltipX = centerX - boxWidth / 2;
        let tooltipY = centerY - cellSize * 0.6 - boxHeight - 5;

        // Ajustar se sair do canvas
        if (tooltipY < 0) tooltipY = centerY + cellSize * 0.6 + 5;
        if (tooltipX < 0) tooltipX = 0;
        if (tooltipX + boxWidth > this.canvas.width) tooltipX = this.canvas.width - boxWidth;

        // Desenhar fundo do tooltip
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.85)';
        this.ctx.fillRect(tooltipX, tooltipY, boxWidth, boxHeight);

        // Desenhar borda
        this.ctx.strokeStyle = '#ffffff';
        this.ctx.lineWidth = 1;
        this.ctx.strokeRect(tooltipX, tooltipY, boxWidth, boxHeight);

        // Desenhar texto
        this.ctx.fillStyle = '#ffffff';
        this.ctx.textAlign = 'left';
        this.ctx.textBaseline = 'top';
        lines.forEach((line, index) => {
            this.ctx.fillText(line, tooltipX + padding, tooltipY + padding + index * lineHeight);
        });
    }

    /**
     * Definir participante activo (turno actual)
     */
    setActiveParticipant(participantId) {
        this.activeParticipantId = participantId;
        this.render();
    }

    /**
     * Obter nome de exibicao da entidade
     */
    getEntityDisplayName(entity) {
        // Extrair nome do entity_id (ex: "player_1" -> "P1", "monster_goblin_0" -> "Goblin")
        const parts = entity.entity_id.split('_');
        if (parts[0] === 'player') {
            return `J${parts[1]}`;
        } else if (parts[0] === 'npc') {
            return parts[1].substring(0, 6);
        } else if (parts[0] === 'monster') {
            return parts[1].substring(0, 6);
        }
        return entity.entity_id.substring(0, 6);
    }

    /**
     * Converter coordenadas do canvas para coordenadas da grelha
     */
    canvasToGrid(canvasX, canvasY) {
        const rect = this.canvas.getBoundingClientRect();
        const scaleX = this.canvas.width / rect.width;
        const scaleY = this.canvas.height / rect.height;

        const x = Math.floor((canvasX - rect.left) * scaleX / this.config.cellSize);
        const y = Math.floor((canvasY - rect.top) * scaleY / this.config.cellSize);

        return { x, y };
    }

    /**
     * Obter entidade nas coordenadas do canvas
     */
    getEntityAtCanvasPos(canvasX, canvasY) {
        const gridPos = this.canvasToGrid(canvasX, canvasY);

        // Procurar entidades nesta celula
        for (let i = this.entities.length - 1; i >= 0; i--) {
            const entity = this.entities[i];
            if (entity.grid_x === gridPos.x && entity.grid_y === gridPos.y && this.isEntityVisible(entity)) {
                return entity;
            }
        }

        return null;
    }

    /**
     * Mouse down handler
     */
    handleMouseDown(e) {
        const entity = this.getEntityAtCanvasPos(e.clientX, e.clientY);

        if (entity) {
            this.selectedEntity = entity;
            this.isDragging = true;

            const gridPos = this.canvasToGrid(e.clientX, e.clientY);
            this.dragOffset = {
                x: entity.grid_x - gridPos.x,
                y: entity.grid_y - gridPos.y
            };

            if (this.onEntitySelected) {
                this.onEntitySelected(entity);
            }

            this.render();
        }
    }

    /**
     * Mouse move handler
     */
    handleMouseMove(e) {
        if (this.isDragging && this.selectedEntity) {
            const gridPos = this.canvasToGrid(e.clientX, e.clientY);
            const newX = Math.max(0, Math.min(this.config.gridWidth - 1, gridPos.x + this.dragOffset.x));
            const newY = Math.max(0, Math.min(this.config.gridHeight - 1, gridPos.y + this.dragOffset.y));

            this.selectedEntity.grid_x = newX;
            this.selectedEntity.grid_y = newY;

            this.render();
        } else {
            // Actualizar hover
            const hoveredEntity = this.getEntityAtCanvasPos(e.clientX, e.clientY);
            if (hoveredEntity !== this.hoveredEntity) {
                this.hoveredEntity = hoveredEntity;
                this.canvas.style.cursor = hoveredEntity ? 'pointer' : 'default';
                this.render();
            }
        }
    }

    /**
     * Mouse up handler
     */
    handleMouseUp(e) {
        if (this.isDragging && this.selectedEntity) {
            this.isDragging = false;

            // Callback para sincronizar com servidor
            if (this.onEntityMoved) {
                this.onEntityMoved(this.selectedEntity);
            }
        }
    }

    /**
     * Mouse leave handler
     */
    handleMouseLeave(e) {
        if (this.isDragging) {
            this.isDragging = false;
        }
        this.hoveredEntity = null;
        this.canvas.style.cursor = 'default';
        this.render();
    }

    /**
     * Touch start handler
     */
    handleTouchStart(e) {
        e.preventDefault();
        if (e.touches.length === 1) {
            const touch = e.touches[0];
            this.handleMouseDown({ clientX: touch.clientX, clientY: touch.clientY });
        }
    }

    /**
     * Touch move handler
     */
    handleTouchMove(e) {
        e.preventDefault();
        if (e.touches.length === 1) {
            const touch = e.touches[0];
            this.handleMouseMove({ clientX: touch.clientX, clientY: touch.clientY });
        }
    }

    /**
     * Touch end handler
     */
    handleTouchEnd(e) {
        e.preventDefault();
        this.handleMouseUp({});
    }

    /**
     * Limpar seleccao
     */
    clearSelection() {
        this.selectedEntity = null;
        this.render();
    }

    /**
     * Obter entidades numa posicao especifica
     */
    getEntitiesAt(gridX, gridY) {
        return this.entities.filter(e => e.grid_x === gridX && e.grid_y === gridY && this.isEntityVisible(e));
    }

    /**
     * Redimensionar canvas (util para responsividade)
     */
    resize(newCellSize) {
        this.config.cellSize = newCellSize;
        this.canvas.width = this.config.gridWidth * this.config.cellSize;
        this.canvas.height = this.config.gridHeight * this.config.cellSize;
        this.render();
    }
}
