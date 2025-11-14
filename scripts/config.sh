#!/bin/bash
# ============================================================================
# Configurações Centralizadas - IP Monitor
# ============================================================================
# Carrega variáveis do arquivo .env.deploy e calcula caminhos derivados.
# Este script deve ser incluído (source) por outros scripts de deploy.
# ============================================================================

set -e  # Sair em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ----------------------------------------------------------------------------
# Localizar e carregar .env.deploy
# ----------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="$PROJECT_ROOT/.env.deploy"

if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}[ERRO]${NC} Arquivo .env.deploy não encontrado em: $ENV_FILE"
    echo -e "${YELLOW}[DICA]${NC} Copie .env.deploy.template para .env.deploy e ajuste os valores."
    exit 1
fi

echo -e "${GREEN}[CONFIG]${NC} Carregando configurações de: $ENV_FILE"

# Carregar variáveis do .env.deploy
set -a  # Exportar todas as variáveis automaticamente
source "$ENV_FILE"
set +a

# ----------------------------------------------------------------------------
# Validar variáveis obrigatórias
# ----------------------------------------------------------------------------
REQUIRED_VARS=(
    "PROJECT_NAME"
    "SERVICE_NAME"
    "DOMAIN_BASE"
    "BACKEND_ROOT"
    "FRONTEND_ROOT"
    "DATA_ROOT"
    "LOGS_ROOT"
    "GIT_REPO_NAME"
    "GIT_REPO_OWNER"
)

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo -e "${RED}[ERRO]${NC} Variável obrigatória não definida: $var"
        exit 1
    fi
done

# ----------------------------------------------------------------------------
# Calcular caminhos derivados
# ----------------------------------------------------------------------------
export ROOT_BACKEND="${BACKEND_ROOT}/${PROJECT_NAME}"
export ROOT_FRONTEND="${FRONTEND_ROOT}/${PROJECT_NAME}"
export ROOT_DATA="${DATA_ROOT}/${PROJECT_NAME}"
export ROOT_LOGS="${LOGS_ROOT}/${PROJECT_NAME}"

# URL do repositório Git
export GIT_REPO_URL="https://github.com/${GIT_REPO_OWNER}/${GIT_REPO_NAME}.git"

# Caminho do arquivo de serviço systemd
export SERVICE_FILE="/usr/lib/systemd/system/${SERVICE_NAME}.service"

# ----------------------------------------------------------------------------
# Exibir configurações (apenas se DEBUG=1)
# ----------------------------------------------------------------------------
if [ "${DEBUG:-0}" = "1" ]; then
    echo -e "${GREEN}[CONFIG]${NC} Configurações carregadas:"
    echo "  PROJECT_NAME       = $PROJECT_NAME"
    echo "  SERVICE_NAME       = $SERVICE_NAME"
    echo "  DOMAIN_BASE        = $DOMAIN_BASE"
    echo "  ROOT_BACKEND       = $ROOT_BACKEND"
    echo "  ROOT_FRONTEND      = $ROOT_FRONTEND"
    echo "  ROOT_DATA          = $ROOT_DATA"
    echo "  ROOT_LOGS          = $ROOT_LOGS"
    echo "  GIT_REPO_URL       = $GIT_REPO_URL"
    echo "  SERVICE_FILE       = $SERVICE_FILE"
fi

echo -e "${GREEN}[CONFIG]${NC} Configurações validadas com sucesso!"
