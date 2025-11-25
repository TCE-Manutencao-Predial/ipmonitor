#!/bin/bash
# ============================================================================
# Script de Replicação de Padronização
# ============================================================================
# Aplica os templates de padronização em um novo submódulo zapdos-server.
# 
# Uso: ./apply-templates.sh /caminho/para/submodulo NOME_PROJETO
# 
# Exemplo: ./apply-templates.sh ~/helpdesk-monitor helpdesk_monitor
# ============================================================================

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Validar argumentos
if [ $# -lt 2 ]; then
    echo -e "${RED}[ERRO]${NC} Uso: $0 /caminho/para/submodulo NOME_PROJETO"
    echo -e "${YELLOW}[EXEMPLO]${NC} $0 ~/helpdesk-monitor helpdesk_monitor"
    exit 1
fi

TARGET_DIR="$1"
PROJECT_NAME="$2"
TEMPLATE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Validar diretório de destino
if [ ! -d "$TARGET_DIR" ]; then
    echo -e "${RED}[ERRO]${NC} Diretório não encontrado: $TARGET_DIR"
    exit 1
fi

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         Aplicador de Templates - Zapdos Server            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}[INFO]${NC} Diretório destino: $TARGET_DIR"
echo -e "${GREEN}[INFO]${NC} Nome do projeto: $PROJECT_NAME"
echo ""

# Criar diretórios necessários
echo -e "${GREEN}[1/5]${NC} Criando estrutura de diretórios..."
mkdir -p "$TARGET_DIR/scripts"
mkdir -p "$TARGET_DIR/tools"
mkdir -p "$TARGET_DIR/docs"

# Copiar templates
echo -e "${GREEN}[2/5]${NC} Copiando templates..."

cp "$TEMPLATE_DIR/env.deploy.template" "$TARGET_DIR/.env.deploy.template"
cp "$TEMPLATE_DIR/env.deploy.template" "$TARGET_DIR/.env.deploy"
cp "$TEMPLATE_DIR/config.sh.template" "$TARGET_DIR/scripts/config.sh"
cp "$TEMPLATE_DIR/deploy.sh.template" "$TARGET_DIR/scripts/deploy.sh"
cp "$TEMPLATE_DIR/undeploy.sh.template" "$TARGET_DIR/scripts/undeploy.sh"
cp "$TEMPLATE_DIR/run.sh.template" "$TARGET_DIR/scripts/run.sh"
cp "$TEMPLATE_DIR/generate-service.sh.template" "$TARGET_DIR/scripts/generate-service.sh"
cp "$TEMPLATE_DIR/service.template" "$TARGET_DIR/scripts/${PROJECT_NAME}.service.template"
cp "$TEMPLATE_DIR/validate-config.py.template" "$TARGET_DIR/tools/validate-config.py"

# Atualizar .gitignore se existir
if [ -f "$TARGET_DIR/.gitignore" ]; then
    echo -e "${GREEN}[3/5]${NC} Atualizando .gitignore..."
    
    # Adicionar linhas se não existirem
    grep -q ".env.local" "$TARGET_DIR/.gitignore" || cat >> "$TARGET_DIR/.gitignore" << 'EOF'

# Configurações locais
.env.local
.env.*.local

# Arquivos gerados
scripts/.config.generated.sh
scripts/*.service
EOF
else
    cp "$TEMPLATE_DIR/gitignore.template" "$TARGET_DIR/.gitignore"
fi

# Tornar scripts executáveis
echo -e "${GREEN}[4/5]${NC} Tornando scripts executáveis..."
chmod +x "$TARGET_DIR/scripts/config.sh"
chmod +x "$TARGET_DIR/scripts/deploy.sh"
chmod +x "$TARGET_DIR/scripts/undeploy.sh"
chmod +x "$TARGET_DIR/scripts/run.sh"
chmod +x "$TARGET_DIR/scripts/generate-service.sh"
chmod +x "$TARGET_DIR/tools/validate-config.py"

# Personalizar .env.deploy (interativo)
echo -e "${GREEN}[5/5]${NC} Personalizando .env.deploy..."
echo ""
echo -e "${YELLOW}[INPUT]${NC} Digite as informações do projeto:"
echo ""

read -p "Nome do projeto (kebab-case) [${PROJECT_NAME}]: " input_name
PROJECT_NAME_INPUT="${input_name:-$PROJECT_NAME}"

read -p "Nome para exibição [IP Monitor]: " display_name
DISPLAY_NAME="${display_name:-Novo Serviço}"

read -p "Prefixo de rotas [/${PROJECT_NAME}]: " routes_prefix
ROUTES_PREFIX="${routes_prefix:-/${PROJECT_NAME}}"

read -p "Porta [8000]: " port
PORT="${port:-8000}"

# Aplicar substituições no .env.deploy
sed -i "s/PROJECT_NAME=ipmonitor/PROJECT_NAME=${PROJECT_NAME_INPUT}/" "$TARGET_DIR/.env.deploy"
sed -i "s/PROJECT_NAME_DISPLAY=\"IP Monitor\"/PROJECT_NAME_DISPLAY=\"${DISPLAY_NAME}\"/" "$TARGET_DIR/.env.deploy"
sed -i "s/SERVICE_NAME=ipmonitor/SERVICE_NAME=${PROJECT_NAME_INPUT}/" "$TARGET_DIR/.env.deploy"
sed -i "s|ROUTES_PREFIX=/ipmonitor|ROUTES_PREFIX=${ROUTES_PREFIX}|" "$TARGET_DIR/.env.deploy"
sed -i "s/PORT=8000/PORT=${PORT}/" "$TARGET_DIR/.env.deploy"

echo ""
echo -e "${GREEN}✅ Templates aplicados com sucesso!${NC}"
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                   Próximos Passos                          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}1.${NC} Revisar configurações:"
echo -e "   ${BLUE}nano $TARGET_DIR/.env.deploy${NC}"
echo ""
echo -e "${YELLOW}2.${NC} Atualizar app/settings.py para usar .env.deploy"
echo -e "   ${BLUE}# Adicionar: from dotenv import load_dotenv${NC}"
echo ""
echo -e "${YELLOW}3.${NC} Adicionar python-dotenv ao requirements.txt"
echo -e "   ${BLUE}echo 'python-dotenv==1.0.0' >> $TARGET_DIR/requirements.txt${NC}"
echo ""
echo -e "${YELLOW}4.${NC} Validar configuração:"
echo -e "   ${BLUE}cd $TARGET_DIR && python tools/validate-config.py${NC}"
echo ""
echo -e "${YELLOW}5.${NC} Testar deploy em ambiente de testes"
echo ""
echo -e "${GREEN}Documentação completa:${NC} $TEMPLATE_DIR/README.md"
echo ""
