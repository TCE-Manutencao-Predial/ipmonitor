#!/bin/bash
# ============================================================================
# Gerador de Arquivo de Serviço Systemd - IP Monitor
# ============================================================================
# Gera o arquivo .service a partir do template, substituindo variáveis.
# Usa envsubst para substituir placeholders do template.
# ============================================================================

set -e  # Sair em caso de erro

# ----------------------------------------------------------------------------
# Carregar configurações centralizadas
# ----------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"

# ----------------------------------------------------------------------------
# Gerar arquivo de serviço
# ----------------------------------------------------------------------------
TEMPLATE_FILE="$SCRIPT_DIR/${SERVICE_NAME}.service.template"
OUTPUT_FILE="$SCRIPT_DIR/${SERVICE_NAME}.service"

if [ ! -f "$TEMPLATE_FILE" ]; then
    echo -e "${RED}[ERRO]${NC} Template não encontrado: $TEMPLATE_FILE"
    exit 1
fi

echo -e "${GREEN}[GEN-SERVICE]${NC} Gerando arquivo de serviço..."
echo -e "${GREEN}[GEN-SERVICE]${NC} Template: $TEMPLATE_FILE"
echo -e "${GREEN}[GEN-SERVICE]${NC} Output:   $OUTPUT_FILE"

# Exportar variáveis para envsubst (todas já estão exportadas pelo config.sh)
# Mas garantir que estejam disponíveis
export PROJECT_NAME_DISPLAY
export ROOT_BACKEND
export SERVICE_NAME

# Debug: mostrar valores
if [ "${DEBUG:-0}" = "1" ]; then
    echo -e "${YELLOW}[DEBUG]${NC} PROJECT_NAME_DISPLAY=$PROJECT_NAME_DISPLAY"
    echo -e "${YELLOW}[DEBUG]${NC} ROOT_BACKEND=$ROOT_BACKEND"
fi

# Substituir variáveis no template usando envsubst
# Lista explícita de variáveis para evitar substituir outras
envsubst '${PROJECT_NAME_DISPLAY} ${ROOT_BACKEND}' < "$TEMPLATE_FILE" > "$OUTPUT_FILE"

echo -e "${GREEN}[GEN-SERVICE]${NC} Arquivo gerado com sucesso!"
echo -e "${GREEN}[GEN-SERVICE]${NC} Conteúdo:"
echo -e "${YELLOW}$(cat "$OUTPUT_FILE")${NC}"
