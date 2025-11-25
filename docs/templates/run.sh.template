#!/bin/bash
# ============================================================================
# Script de Execução - IP Monitor
# ============================================================================
# Inicia o serviço Flask em produção.
# Configurações são carregadas de .env.deploy via config.sh
# ============================================================================

set -e  # Sair em caso de erro

# ----------------------------------------------------------------------------
# Carregar configurações centralizadas
# ----------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"

# ----------------------------------------------------------------------------
# Executar aplicação
# ----------------------------------------------------------------------------
echo -e "${GREEN}[RUN]${NC} Iniciando ${PROJECT_NAME_DISPLAY}..."
echo -e "${GREEN}[RUN]${NC} Diretório: $ROOT_BACKEND"

cd "$ROOT_BACKEND"
make run