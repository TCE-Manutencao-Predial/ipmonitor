// Função para obter a base URL da API dependendo do ambiente
function getApiBaseUrl() {
    // Verifica se estamos em produção (domínio tce.go.gov.br) ou desenvolvimento
    if (window.location.hostname.includes('tce.go.gov.br')) {
        return '/ipmonitor';
    } else {
        return '';
    }
}

// Função assíncrona para buscar dados com base na VLAN selecionada
async function searchByVlan() {

    // Obtém o elemento do select com ID 'filtroVLAN'
    const vlanSelect = document.getElementById('filtroVLAN');

    // Obtém o valor selecionado no select e codifica-o para uso na URL
    const vlan = encodeURIComponent(vlanSelect.value);  
    
    // Atualiza o gateway dinamicamente
    updateGateway(vlan);
    
    // Atualiza as informações da VLAN
    updateVlanInfo(vlan);
    
    // Faz uma requisição para a API usando o valor da VLAN
    const baseUrl = getApiBaseUrl();
    const response = await fetch(`${baseUrl}/api/start-check/${vlan}`);

    // Obtém o elemento pela ID
    const mensagemPreliminar = document.getElementById('mensagem_preliminar');

    // Verifica se a requisição falhou
    if (response.status !== 200) {
        console.error('Falhou para obter os dados dos IPs');

        // Exibir texto de debugging:
        mensagemPreliminar.style.display = 'block';  

        // Altera o texto da mensagem
        mensagemPreliminar.innerHTML = 'Falha ao obter dados da API (código: ' + response.status + ').<br>Aguarde mais um pouco, por favor.';  // Substitua pelo texto que deseja exibir
        
        // Tenta buscar novamente a cada 5 segundos, caso tenha falhado
        // setInterval(searchByVlan, 5000);
        return;
    } else {
        // Esconder texto de debugging:
        mensagemPreliminar.style.display = 'none';  
        
        // Converte a resposta em JSON
        const data = await response.json();

        // Log para diagnóstico
        console.log('[INDEX.JS] Dados recebidos da API:', data.length, 'itens');
        const itemsComTipo = data.filter(item => item.tipo && item.tipo.trim() !== '');
        console.log('[INDEX.JS] Items com tipo:', itemsComTipo.length);
        if (itemsComTipo.length > 0) {
            console.log('[INDEX.JS] Exemplo com tipo:', itemsComTipo[0]);
        }

        // Obtém o corpo da tabela com os IPs
        const tbody = document.getElementById('ipTableBody');
        
        // Limpa a tabela antes de inserir novos elementos
        tbody.innerHTML = '';  

        // Obtém o container de cards
        const cardsContainer = document.getElementById('devices-container');
        
        // Limpa o container antes de inserir novos cards
        cardsContainer.innerHTML = '';

        // Verifica se há dados para exibir
        if (data.length === 0) {
            cardsContainer.innerHTML = '<div class="no-devices">📭 Nenhum dispositivo encontrado nesta VLAN</div>';
            return;
        }

        // Cria cards para cada dispositivo
        data.forEach(device => {
            const card = createDeviceCard(device, vlan);
            cardsContainer.appendChild(card);
        });

        // Mantém a lógica antiga da tabela (oculta) como fallback
        var QTD_COLUNAS = 4;

        // Percorre os dados recebidos e cria linhas para a tabela
        for (let i = 0; i < data.length; i += QTD_COLUNAS) {
            const row = document.createElement('tr');

            // Cria células para colunas de dados por linha
            for (let j = 0; j < QTD_COLUNAS; j++) {
                const descriptionCell = document.createElement('td');
                const tipoCell = document.createElement('td');
                const ipCell = document.createElement('td');
                const statusCell = document.createElement('td');
                const circle = document.createElement('span');

                // Verifica se há dados para a célula atual
                if (data[i + j]) {
                    const device = data[i + j];
                    
                    // Célula de descrição (sem ícone agora)
                    descriptionCell.textContent = device.descricao;
                    
                    // Célula de IP clicável com ícone de edição
                    ipCell.className = 'ip-cell';
                    ipCell.title = 'Clique para editar este dispositivo';
                    
                    const ipText = document.createElement('span');
                    ipText.className = 'ip-text';
                    ipText.textContent = device.ip;
                    
                    const editIcon = document.createElement('span');
                    editIcon.innerHTML = '✏️';
                    editIcon.className = 'edit-icon';
                    editIcon.title = 'Editar dispositivo';
                    
                    // Fazer toda a célula de IP clicável
                    ipCell.onclick = function() {
                        openEditModal(device.ip, device.descricao, device.tipo, vlan);
                    };
                    
                    ipCell.appendChild(ipText);
                    ipCell.appendChild(editIcon);
                    
                    tipoCell.textContent = device.tipo || '-';

                    // Verifica o status do dispositivo e aplica a classe correta
                    if (device.status === "on") {
                        circle.classList.add('circle', 'green'); // Aplica a classe 'green' para dispositivos online
                    } else if (device.status === "off") {
                        circle.classList.add('circle', 'red'); // Aplica a classe 'red' para dispositivos offline
                    }
                } else {
                    // Células vazias para manter estrutura da tabela
                    tipoCell.textContent = '';
                }

                // Aplica as classes corretas para cada coluna
                tipoCell.classList.add(`tipo_${String.fromCharCode(65 + j)}`);
                statusCell.classList.add(`status_${String.fromCharCode(65 + j)}`);

                // Adiciona o círculo de status à célula de status
                statusCell.appendChild(circle);
                
                // Adiciona as células à linha
                row.appendChild(descriptionCell);
                row.appendChild(tipoCell);
                row.appendChild(ipCell);
                row.appendChild(statusCell);
            }

            // Adiciona a linha à tabela
            tbody.appendChild(row);
        }
    }
}

// Função para atualizar o gateway baseado na VLAN selecionada
function updateGateway(vlan) {
    const gatewayElement = document.getElementById('gateway-value');
    if (gatewayElement) {
        gatewayElement.textContent = `172.17.${vlan}.254`;
    }
}

// Função para criar um card de dispositivo
function createDeviceCard(device, vlan) {
    // Criar elementos do card
    const card = document.createElement('div');
    card.className = `device-card ${device.status === 'on' ? 'online' : 'offline'}`;
    
    // Header do card
    const header = document.createElement('div');
    header.className = 'device-card-header';
    
    // Badge de status
    const statusBadge = document.createElement('div');
    statusBadge.className = `status-badge ${device.status === 'on' ? 'online' : 'offline'}`;
    statusBadge.innerHTML = `
        <span class="status-indicator"></span>
        <span>${device.status === 'on' ? 'Online' : 'Offline'}</span>
    `;
    
    // IP do dispositivo
    const ipElement = document.createElement('div');
    ipElement.className = 'device-ip';
    ipElement.textContent = device.ip;
    
    header.appendChild(statusBadge);
    header.appendChild(ipElement);
    
    // Corpo do card
    const body = document.createElement('div');
    body.className = 'device-card-body';
    
    // Descrição
    const description = document.createElement('div');
    description.className = 'device-description';
    description.textContent = device.descricao || 'Sem descrição';
    description.title = device.descricao; // Tooltip com texto completo
    
    // Tipo do dispositivo
    const typeElement = document.createElement('div');
    typeElement.className = 'device-type';
    typeElement.innerHTML = `
        <span class="device-type-icon">🏷️</span>
        <span>${device.tipo || 'Não definido'}</span>
    `;
    
    body.appendChild(description);
    body.appendChild(typeElement);
    
    // Footer do card
    const footer = document.createElement('div');
    footer.className = 'device-card-footer';
    
    // Botão de edição
    const editBtn = document.createElement('button');
    editBtn.className = 'card-edit-btn';
    editBtn.innerHTML = '✏️ Editar';
    editBtn.onclick = function(e) {
        e.stopPropagation(); // Evita propagação do clique
        openEditModal(device.ip, device.descricao, device.tipo, vlan);
    };
    
    footer.appendChild(editBtn);
    
    // Montar o card
    card.appendChild(header);
    card.appendChild(body);
    card.appendChild(footer);
    
    // Fazer o card inteiro clicável (exceto o botão)
    card.onclick = function(e) {
        if (e.target !== editBtn && !editBtn.contains(e.target)) {
            openEditModal(device.ip, device.descricao, device.tipo, vlan);
        }
    };
    
    return card;
}

// Função para mostrar informações da VLAN selecionada
function updateVlanInfo(vlan) {
    // Oculta todas as informações de VLAN
    const allVlanInfos = document.querySelectorAll('.vlan-info-card');
    allVlanInfos.forEach(card => {
        card.style.display = 'none';
    });
    
    // Mostra apenas a informação da VLAN selecionada (se existir)
    const selectedVlanInfo = document.getElementById(`vlan-${vlan}-info`);
    if (selectedVlanInfo) {
        selectedVlanInfo.style.display = 'block';
    }
}

// Quando a página carrega, define a VLAN inicial e inicia a busca
window.onload = function() {

    // Define o valor inicial do select 'filtroVLAN' para 85
    document.getElementById('filtroVLAN').value = '85';

    // Atualiza o gateway inicial
    updateGateway('85');
    
    // Atualiza as informações da VLAN inicial
    updateVlanInfo('85');

    // Inicia o processo de busca pela VLAN
    searchByVlan();

    // (Comentado) Adiciona o event listener para disparar a função quando o valor da VLAN mudar
    // document.getElementById('filtroVLAN').addEventListener('change', searchByVlan);
};

// Eu acho que isso não é mais necessário?
setInterval(searchByVlan, 20000);

// ====================================
// MODAL DE EDIÇÃO DE DISPOSITIVO
// ====================================

let currentEditDevice = null; // Armazena o dispositivo sendo editado

// Função para abrir o modal de edição
function openEditModal(ip, descricao, tipo, vlan) {
    const modal = document.getElementById('editModal');
    const ipInput = document.getElementById('edit-ip');
    const descricaoInput = document.getElementById('edit-descricao');
    const tipoInput = document.getElementById('edit-tipo');
    
    // Preencher os campos
    ipInput.value = ip;
    descricaoInput.value = descricao;
    tipoInput.value = tipo || '';
    
    // Armazenar informações do dispositivo atual
    currentEditDevice = { ip, vlan };
    
    // Carregar tipos de dispositivos disponíveis
    loadDeviceTypes(vlan);
    
    // Mostrar o modal
    modal.style.display = 'block';
    
    // Focar no campo descrição
    setTimeout(() => descricaoInput.focus(), 100);
}

// Função para fechar o modal
function closeEditModal() {
    const modal = document.getElementById('editModal');
    modal.style.display = 'none';
    currentEditDevice = null;
}

// Função para carregar tipos de dispositivos disponíveis
async function loadDeviceTypes(vlan) {
    try {
        const baseUrl = getApiBaseUrl();
        const response = await fetch(`${baseUrl}/api/device-types/${vlan}`);
        
        if (response.ok) {
            const data = await response.json();
            const datalist = document.getElementById('device-types');
            datalist.innerHTML = '';
            
            // Adicionar opções ao datalist
            if (data.types && data.types.length > 0) {
                data.types.forEach(type => {
                    const option = document.createElement('option');
                    option.value = type;
                    datalist.appendChild(option);
                });
            }
        }
    } catch (error) {
        console.error('Erro ao carregar tipos de dispositivos:', error);
    }
}

// Função para salvar as alterações do dispositivo
async function saveDevice() {
    if (!currentEditDevice) return;
    
    const descricao = document.getElementById('edit-descricao').value.trim();
    const tipo = document.getElementById('edit-tipo').value.trim();
    
    // Validação
    if (!descricao) {
        alert('⚠️ A descrição não pode estar vazia!');
        return;
    }
    
    const saveBtn = document.querySelector('.btn-save');
    saveBtn.disabled = true;
    saveBtn.textContent = '⏳ Salvando...';
    
    try {
        const baseUrl = getApiBaseUrl();
        const response = await fetch(
            `${baseUrl}/api/devices/${currentEditDevice.vlan}/${currentEditDevice.ip}`,
            {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    descricao: descricao,
                    tipo: tipo
                })
            }
        );
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            // Sucesso - fechar modal e atualizar tabela
            closeEditModal();
            alert('✅ Dispositivo atualizado com sucesso!');
            
            // Recarregar a tabela
            await searchByVlan();
        } else {
            alert('❌ Erro ao salvar: ' + (data.error || 'Erro desconhecido'));
        }
    } catch (error) {
        console.error('Erro ao salvar dispositivo:', error);
        alert('❌ Erro ao conectar com o servidor: ' + error.message);
    } finally {
        saveBtn.disabled = false;
        saveBtn.innerHTML = '💾 Salvar';
    }
}

// Fechar modal ao clicar no X
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('editModal');
    const closeBtn = document.querySelector('.close');
    
    if (closeBtn) {
        closeBtn.onclick = closeEditModal;
    }
    
    // Fechar modal ao clicar fora dele
    window.onclick = function(event) {
        if (event.target === modal) {
            closeEditModal();
        }
    };
    
    // Fechar modal com tecla ESC
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape' && modal.style.display === 'block') {
            closeEditModal();
        }
    });
    
    // Salvar com Enter (quando não estiver no campo de tipo com datalist aberto)
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Enter' && modal.style.display === 'block') {
            const activeElement = document.activeElement;
            if (activeElement.id !== 'edit-tipo') {
                saveDevice();
            }
        }
    });
});
