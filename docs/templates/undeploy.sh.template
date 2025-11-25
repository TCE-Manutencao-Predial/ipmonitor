#!/bin/bash
# ============================================================================
# Script de Undeploy - IP Monitor
# ============================================================================
# Remove completamente o projeto do servidor de produção.
# Configurações são carregadas de .env.deploy via config.sh
# ============================================================================

set -e  # Sair em caso de erro

# ----------------------------------------------------------------------------
# Carregar configurações centralizadas
# ----------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"

echo -e "${YELLOW}[UNDEPLOY]${NC} ====================================="
echo -e "${YELLOW}[UNDEPLOY]${NC} Removendo: ${PROJECT_NAME_DISPLAY}"
echo -e "${YELLOW}[UNDEPLOY]${NC} ====================================="

# ----------------------------------------------------------------------------
# Realizar o Undeploy
# ----------------------------------------------------------------------------

# Parar e desabilitar serviço
if systemctl is-active --quiet "$SERVICE_NAME"; then
    echo -e "${YELLOW}[UNDEPLOY]${NC} Parando serviço: $SERVICE_NAME"
    sudo systemctl stop "$SERVICE_NAME"
fi

if systemctl is-enabled --quiet "$SERVICE_NAME" 2>/dev/null; then
    echo -e "${YELLOW}[UNDEPLOY]${NC} Desabilitando serviço: $SERVICE_NAME"
    sudo systemctl disable "$SERVICE_NAME"
fi

# Remover arquivos de serviço systemd
if [ -f "$SERVICE_FILE" ]; then
    echo -e "${YELLOW}[UNDEPLOY]${NC} Removendo arquivo de serviço: $SERVICE_FILE"
    sudo rm "$SERVICE_FILE"
fi

if [ -f "/etc/systemd/system/${SERVICE_NAME}.service" ]; then
    echo -e "${YELLOW}[UNDEPLOY]${NC} Removendo link do serviço em /etc/systemd/system/"
    sudo rm "/etc/systemd/system/${SERVICE_NAME}.service"
fi

# Recarregar daemon
sudo systemctl daemon-reload

# Apagar frontend estático
if [ -d "$ROOT_FRONTEND" ]; then
    echo -e "${YELLOW}[UNDEPLOY]${NC} Removendo frontend: $ROOT_FRONTEND"
    sudo rm -r "$ROOT_FRONTEND"
fi

# Apagar backend
if [ -d "$ROOT_BACKEND" ]; then
    echo -e "${YELLOW}[UNDEPLOY]${NC} Removendo backend: $ROOT_BACKEND"
    sudo rm -r "$ROOT_BACKEND"
fi

echo -e "${YELLOW}[UNDEPLOY]${NC} ====================================="
echo -e "${YELLOW}[UNDEPLOY]${NC} Undeploy concluído!"
echo -e "${YELLOW}[UNDEPLOY]${NC} ====================================="
echo -e "${YELLOW}[UNDEPLOY]${NC} ATENÇÃO: Dados e logs NÃO foram removidos:"
echo -e "${YELLOW}[UNDEPLOY]${NC} - Dados: $ROOT_DATA"
echo -e "${YELLOW}[UNDEPLOY]${NC} - Logs:  $ROOT_LOGS"
echo -e "${YELLOW}[UNDEPLOY]${NC} Para remover dados, execute: sudo rm -r $ROOT_DATA"
echo -e "${YELLOW}[UNDEPLOY]${NC} Para remover logs, execute: sudo rm -r $ROOT_LOGS"