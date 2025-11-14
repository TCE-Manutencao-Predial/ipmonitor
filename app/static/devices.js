// JavaScript para a página de dispositivos
class DeviceManager {
    constructor() {
        console.log('[DeviceManager] Construtor iniciado');
        this.currentVlan = '';
        this.devices = [];
        this.deviceTypes = {};
        this.filteredDevices = [];
        this.editingDevice = null;
        this.apiBasePath = this.getApiBasePath();
        
        console.log('[DeviceManager] API Base Path:', this.apiBasePath);
        this.init();
        console.log('[DeviceManager] Construtor concluído');
    }
    
    getApiBasePath() {
        const path = window.location.pathname;
        // Usa APP_CONFIG injetado do settings.py via template
        return path.includes(APP_CONFIG.routesPrefix + '/') ? APP_CONFIG.routesPrefix + '/api' : '/api';
    }
    
    init() {
        console.log('[DeviceManager] Iniciando setup...');
        this.setupEventListeners();
        this.loadInitialData();
    }
    
    setupEventListeners() {
        console.log('[DeviceManager] Configurando event listeners...');
        
        // Seletor de VLAN
        const vlanSelect = document.getElementById('vlan-select');
        console.log('[DeviceManager] VLAN Select encontrado:', !!vlanSelect);
        if (vlanSelect) {
            vlanSelect.addEventListener('change', (e) => {
                console.log('[DeviceManager] VLAN selecionada:', e.target.value);
                this.loadVlanData(e.target.value);
            });
        }
        
        // Botões de ação
        const addBtn = document.getElementById('add-device-btn');
        const manageBtn = document.getElementById('manage-types-btn');
        const refreshBtn = document.getElementById('refresh-btn');
        
        console.log('[DeviceManager] Botões encontrados - Add:', !!addBtn, 'Manage:', !!manageBtn, 'Refresh:', !!refreshBtn);
        
        addBtn?.addEventListener('click', () => {
            console.log('[DeviceManager] Botão Adicionar clicado');
            this.openAddDeviceModal();
        });
        
        manageBtn?.addEventListener('click', () => {
            console.log('[DeviceManager] Botão Gerenciar Tipos clicado');
            this.openManageTypesModal();
        });
        
        refreshBtn?.addEventListener('click', () => {
            console.log('[DeviceManager] Botão Refresh clicado');
            this.refreshCurrentVlan();
        });
        
        // Filtro de pesquisa
        document.getElementById('search-filter')?.addEventListener('input', (e) => {
            this.filterDevices(e.target.value);
        });
        
        // Modais - botões de fechar
        document.querySelectorAll('.close').forEach(closeBtn => {
            closeBtn.addEventListener('click', () => {
                this.closeModals();
            });
        });
        
        // Modais - clique no fundo
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModals();
                }
            });
        });
        
        // Formulário de dispositivo
        document.getElementById('device-form')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveDevice();
        });
        
        // Gerenciamento de tipos
        document.getElementById('new-type-form')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.addNewType();
        });
        
        // Tipo personalizado
        document.getElementById('tipo-select')?.addEventListener('change', (e) => {
            this.handleTipoSelection(e.target.value);
        });
    }
    
    async loadInitialData() {
        try {
            // Carregar dados iniciais se necessário
            const vlanSelect = document.getElementById('vlan-select');
            if (vlanSelect && vlanSelect.value) {
                await this.loadVlanData(vlanSelect.value);
            }
        } catch (error) {
            console.error('Erro ao carregar dados iniciais:', error);
            this.showStatus('Erro ao carregar dados iniciais', 'error');
        }
    }
    
    async loadVlanData(vlan) {
        if (!vlan) {
            this.clearDevicesTable();
            return;
        }
        
        this.currentVlan = vlan;
        this.showLoading(true);
        
        try {
            // Carregar dispositivos da VLAN
            const devicesResponse = await fetch(`${this.apiBasePath}/devices/${vlan}`);
            if (!devicesResponse.ok) {
                throw new Error(`Erro ao carregar dispositivos: ${devicesResponse.status}`);
            }
            const devicesData = await devicesResponse.json();
            this.devices = devicesData.devices || [];
            
            // Carregar tipos de dispositivos da VLAN
            const typesResponse = await fetch(`${this.apiBasePath}/device-types/${vlan}`);
            if (!typesResponse.ok) {
                throw new Error(`Erro ao carregar tipos: ${typesResponse.status}`);
            }
            const typesData = await typesResponse.json();
            this.deviceTypes = typesData.types || [];
            
            this.renderDevicesTable();
            this.showStatus(`${this.devices.length} dispositivos carregados para VLAN ${vlan}`, 'success');
            
        } catch (error) {
            console.error('Erro ao carregar dados da VLAN:', error);
            this.showStatus(`Erro ao carregar dados da VLAN ${vlan}`, 'error');
            this.clearDevicesTable();
        } finally {
            this.showLoading(false);
        }
    }
    
    renderDevicesTable() {
        const tbody = document.querySelector('#devices-table tbody');
        if (!tbody) return;
        
        this.filteredDevices = [...this.devices];
        this.updateTable();
    }
    
    updateTable() {
        const tbody = document.querySelector('#devices-table tbody');
        if (!tbody) return;
        
        if (this.filteredDevices.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" style="text-align: center; padding: 40px; color: #6c757d;">
                        ${this.devices.length === 0 ? 'Nenhum dispositivo cadastrado nesta VLAN' : 'Nenhum dispositivo corresponde ao filtro'}
                    </td>
                </tr>
            `;
            return;
        }
        
        tbody.innerHTML = this.filteredDevices.map(device => `
            <tr>
                <td class="ip-cell">${device.ip}</td>
                <td>${device.descricao || '-'}</td>
                <td class="tipo-cell">${device.tipo || '-'}</td>
                <td class="updated-cell">${this.formatDate(device.updated_at)}</td>
                <td class="actions-cell">
                    <button class="btn-edit" data-ip="${device.ip}" data-action="edit">
                        ✏️ Editar
                    </button>
                    <button class="btn-danger" data-ip="${device.ip}" data-action="delete">
                        🗑️ Excluir
                    </button>
                </td>
            </tr>
        `).join('');
        
        // Adicionar event listeners para os botões criados dinamicamente
        tbody.querySelectorAll('button[data-action="edit"]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                // Garante que pegamos o botão, não o conteúdo interno (emoji/texto)
                const button = e.currentTarget;
                const ip = button.getAttribute('data-ip');
                console.log('[DeviceManager] Botão Editar clicado - IP:', ip);
                this.editDevice(ip);
            });
        });
        
        tbody.querySelectorAll('button[data-action="delete"]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                // Garante que pegamos o botão, não o conteúdo interno (emoji/texto)
                const button = e.currentTarget;
                const ip = button.getAttribute('data-ip');
                console.log('[DeviceManager] Botão Excluir clicado - IP:', ip);
                this.deleteDevice(ip);
            });
        });
    }
    
    filterDevices(searchTerm) {
        if (!searchTerm.trim()) {
            this.filteredDevices = [...this.devices];
        } else {
            const term = searchTerm.toLowerCase();
            this.filteredDevices = this.devices.filter(device => 
                device.ip.toLowerCase().includes(term) ||
                (device.descricao || '').toLowerCase().includes(term) ||
                (device.tipo || '').toLowerCase().includes(term)
            );
        }
        this.updateTable();
    }
    
    openAddDeviceModal() {
        if (!this.currentVlan) {
            this.showStatus('Selecione uma VLAN primeiro', 'error');
            return;
        }
        
        this.editingDevice = null;
        this.setupDeviceForm();
        document.getElementById('device-modal').style.display = 'flex';
    }
    
    editDevice(ip) {
        this.editingDevice = this.devices.find(device => device.ip === ip);
        if (!this.editingDevice) {
            this.showStatus('Dispositivo não encontrado', 'error');
            return;
        }
        
        this.setupDeviceForm(this.editingDevice);
        document.getElementById('device-modal').style.display = 'flex';
    }
    
    setupDeviceForm(device = null) {
        const form = document.getElementById('device-form');
        const title = document.querySelector('#device-modal .modal-header h3');
        
        if (device) {
            title.textContent = 'Editar Dispositivo';
            document.getElementById('device-ip').value = device.ip;
            document.getElementById('device-description').value = device.descricao || '';
            
            // Configurar seleção de tipo
            this.populateTipoSelect();
            const tipoSelect = document.getElementById('tipo-select');
            const tipoCustom = document.getElementById('tipo-custom');
            
            if (device.tipo && this.deviceTypes.includes(device.tipo)) {
                tipoSelect.value = device.tipo;
                tipoCustom.style.display = 'none';
                tipoCustom.value = '';
            } else if (device.tipo) {
                tipoSelect.value = '__custom__';
                tipoCustom.style.display = 'block';
                tipoCustom.value = device.tipo;
            } else {
                tipoSelect.value = '';
                tipoCustom.style.display = 'none';
                tipoCustom.value = '';
            }
            
            document.getElementById('device-ip').readOnly = true;
        } else {
            title.textContent = 'Adicionar Dispositivo';
            form.reset();
            this.populateTipoSelect();
            document.getElementById('device-ip').readOnly = false;
            document.getElementById('tipo-custom').style.display = 'none';
        }
    }
    
    populateTipoSelect() {
        const tipoSelect = document.getElementById('tipo-select');
        if (!tipoSelect) return;
        
        // Limpar opções existentes (exceto as padrões)
        tipoSelect.innerHTML = `
            <option value="">Selecione um tipo</option>
            <option value="__custom__">Novo tipo...</option>
        `;
        
        // Adicionar tipos existentes
        this.deviceTypes.forEach(tipo => {
            const option = document.createElement('option');
            option.value = tipo;
            option.textContent = tipo;
            tipoSelect.appendChild(option);
        });
    }
    
    handleTipoSelection(value) {
        const tipoCustom = document.getElementById('tipo-custom');
        if (value === '__custom__') {
            tipoCustom.style.display = 'block';
            tipoCustom.focus();
        } else {
            tipoCustom.style.display = 'none';
            tipoCustom.value = '';
        }
    }
    
    async saveDevice() {
        const ip = document.getElementById('device-ip').value.trim();
        const description = document.getElementById('device-description').value.trim();
        const tipoSelect = document.getElementById('tipo-select').value;
        const tipoCustom = document.getElementById('tipo-custom').value.trim();
        
        // Validações
        if (!ip) {
            this.showStatus('IP é obrigatório', 'error');
            return;
        }
        
        if (!this.isValidIP(ip)) {
            this.showStatus('IP inválido', 'error');
            return;
        }
        
        // Determinar tipo final
        let finalTipo = '';
        if (tipoSelect === '__custom__') {
            if (!tipoCustom) {
                this.showStatus('Digite o novo tipo', 'error');
                return;
            }
            finalTipo = tipoCustom;
        } else if (tipoSelect) {
            finalTipo = tipoSelect;
        }
        
        const deviceData = {
            ip: ip,
            descricao: description,
            tipo: finalTipo
        };
        
        try {
            const method = this.editingDevice ? 'PUT' : 'POST';
            const response = await fetch(`${this.apiBasePath}/devices/${this.currentVlan}`, {
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(deviceData)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `Erro ${response.status}`);
            }
            
            const result = await response.json();
            
            // Se foi um tipo novo, adicionar à lista de tipos
            if (finalTipo && !this.deviceTypes.includes(finalTipo)) {
                this.deviceTypes.push(finalTipo);
            }
            
            this.closeModals();
            await this.loadVlanData(this.currentVlan);
            
            const action = this.editingDevice ? 'atualizado' : 'adicionado';
            this.showStatus(`Dispositivo ${ip} ${action} com sucesso`, 'success');
            
        } catch (error) {
            console.error('Erro ao salvar dispositivo:', error);
            this.showStatus(`Erro ao salvar dispositivo: ${error.message}`, 'error');
        }
    }
    
    async deleteDevice(ip) {
        if (!confirm(`Tem certeza que deseja excluir o dispositivo ${ip}?`)) {
            return;
        }
        
        try {
            const response = await fetch(`${this.apiBasePath}/devices/${this.currentVlan}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ ip: ip })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `Erro ${response.status}`);
            }
            
            await this.loadVlanData(this.currentVlan);
            this.showStatus(`Dispositivo ${ip} excluído com sucesso`, 'success');
            
        } catch (error) {
            console.error('Erro ao excluir dispositivo:', error);
            this.showStatus(`Erro ao excluir dispositivo: ${error.message}`, 'error');
        }
    }
    
    openManageTypesModal() {
        if (!this.currentVlan) {
            this.showStatus('Selecione uma VLAN primeiro', 'error');
            return;
        }
        
        this.populateTypesModal();
        document.getElementById('types-modal').style.display = 'flex';
    }
    
    populateTypesModal() {
        const typesList = document.getElementById('types-list');
        if (!typesList) return;
        
        if (this.deviceTypes.length === 0) {
            typesList.innerHTML = '<p style="color: #6c757d; text-align: center; padding: 20px;">Nenhum tipo configurado para esta VLAN</p>';
            return;
        }
        
        // Verificar quais tipos estão em uso
        const usedTypes = new Set(this.devices.map(device => device.tipo).filter(tipo => tipo));
        
        typesList.innerHTML = this.deviceTypes.map(tipo => {
            const isUsed = usedTypes.has(tipo);
            const tagClass = isUsed ? 'type-tag used' : 'type-tag configured';
            const title = isUsed ? 'Tipo em uso' : 'Tipo configurado';
            
            return `
                <div class="${tagClass}" title="${title}">
                    ${tipo}
                    <span class="type-remove" data-type="${tipo}" title="Remover tipo">×</span>
                </div>
            `;
        }).join('');
        
        // Adicionar event listeners para os botões de remover tipo
        typesList.querySelectorAll('.type-remove').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation(); // Evita propagação do evento
                const tipo = e.currentTarget.getAttribute('data-type');
                console.log('[DeviceManager] Removendo tipo:', tipo);
                this.removeType(tipo);
            });
        });
    }
    
    async addNewType() {
        const input = document.getElementById('new-type-input');
        const newType = input.value.trim();
        
        if (!newType) {
            this.showStatus('Digite o nome do tipo', 'error');
            return;
        }
        
        if (this.deviceTypes.includes(newType)) {
            this.showStatus('Este tipo já existe', 'error');
            return;
        }
        
        try {
            const response = await fetch(`${this.apiBasePath}/device-types/${this.currentVlan}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ type: newType })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `Erro ${response.status}`);
            }
            
            this.deviceTypes.push(newType);
            input.value = '';
            this.populateTypesModal();
            this.showStatus(`Tipo "${newType}" adicionado com sucesso`, 'success');
            
        } catch (error) {
            console.error('Erro ao adicionar tipo:', error);
            this.showStatus(`Erro ao adicionar tipo: ${error.message}`, 'error');
        }
    }
    
    async removeType(tipo) {
        // Verificar se o tipo está em uso
        const isUsed = this.devices.some(device => device.tipo === tipo);
        
        if (isUsed) {
            if (!confirm(`O tipo "${tipo}" está em uso por dispositivos. Tem certeza que deseja removê-lo? Os dispositivos ficarão sem tipo.`)) {
                return;
            }
        } else {
            if (!confirm(`Tem certeza que deseja remover o tipo "${tipo}"?`)) {
                return;
            }
        }
        
        try {
            const response = await fetch(`${this.apiBasePath}/device-types/${this.currentVlan}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ type: tipo })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `Erro ${response.status}`);
            }
            
            this.deviceTypes = this.deviceTypes.filter(t => t !== tipo);
            this.populateTypesModal();
            
            // Recarregar dispositivos se o tipo removido estava em uso
            if (isUsed) {
                await this.loadVlanData(this.currentVlan);
            }
            
            this.showStatus(`Tipo "${tipo}" removido com sucesso`, 'success');
            
        } catch (error) {
            console.error('Erro ao remover tipo:', error);
            this.showStatus(`Erro ao remover tipo: ${error.message}`, 'error');
        }
    }
    
    refreshCurrentVlan() {
        if (this.currentVlan) {
            this.loadVlanData(this.currentVlan);
        }
    }
    
    closeModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.style.display = 'none';
        });
    }
    
    clearDevicesTable() {
        const tbody = document.querySelector('#devices-table tbody');
        if (tbody) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" style="text-align: center; padding: 40px; color: #6c757d;">
                        Selecione uma VLAN para ver os dispositivos
                    </td>
                </tr>
            `;
        }
        this.devices = [];
        this.deviceTypes = [];
        this.filteredDevices = [];
    }
    
    showLoading(show) {
        const loadingDiv = document.getElementById('loading');
        const tableContainer = document.querySelector('.table-container');
        
        if (show) {
            if (loadingDiv) loadingDiv.style.display = 'flex';
            if (tableContainer) tableContainer.style.display = 'none';
        } else {
            if (loadingDiv) loadingDiv.style.display = 'none';
            if (tableContainer) tableContainer.style.display = 'block';
        }
    }
    
    showStatus(message, type = 'info') {
        const statusDiv = document.getElementById('status-message');
        if (!statusDiv) return;
        
        statusDiv.textContent = message;
        statusDiv.className = type;
        statusDiv.style.display = 'block';
        
        // Auto-hide após 5 segundos
        setTimeout(() => {
            statusDiv.style.display = 'none';
        }, 5000);
    }
    
    isValidIP(ip) {
        const ipRegex = /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
        return ipRegex.test(ip);
    }
    
    formatDate(dateString) {
        if (!dateString) return '-';
        
        try {
            const date = new Date(dateString);
            return date.toLocaleString('pt-BR', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        } catch (error) {
            return dateString;
        }
    }
}

// Inicializar o gerenciador quando a página carregar
let deviceManager;

function initializeDeviceManager() {
    if (!deviceManager) {
        console.log('[DEVICES.JS] Inicializando DeviceManager...');
        deviceManager = new DeviceManager();
        console.log('[DEVICES.JS] DeviceManager inicializado:', deviceManager);
        
        // Disponibilizar globalmente para debug
        window.deviceManager = deviceManager;
    }
}

document.addEventListener('DOMContentLoaded', initializeDeviceManager);

// Fallback caso o DOMContentLoaded já tenha disparado
if (document.readyState === 'loading') {
    console.log('[DEVICES.JS] Documento ainda carregando, aguardando DOMContentLoaded');
} else {
    console.log('[DEVICES.JS] Documento já carregado, inicializando imediatamente');
    initializeDeviceManager();
}

// Prevenir fechamento acidental dos modais ao clicar nos inputs
document.addEventListener('click', function(e) {
    if (e.target.closest('.modal-content')) {
        e.stopPropagation();
    }
});

// Atalhos de teclado
document.addEventListener('keydown', function(e) {
    // ESC para fechar modais
    if (e.key === 'Escape') {
        deviceManager?.closeModals();
    }
    
    // Ctrl+F para focar no campo de pesquisa
    if (e.ctrlKey && e.key === 'f') {
        e.preventDefault();
        const searchInput = document.getElementById('search-filter');
        if (searchInput) {
            searchInput.focus();
            searchInput.select();
        }
    }
});