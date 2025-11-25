#!/bin/bash
# ============================================================================
# Script de Deploy - IP Monitor
# ============================================================================
# Este script realiza o deploy completo do projeto em produção.
# Configurações são carregadas de .env.deploy via config.sh
# ============================================================================

set -e  # Sair em caso de erro

# ----------------------------------------------------------------------------
# Carregar configurações centralizadas
# ----------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"

echo -e "${GREEN}[DEPLOY]${NC} Iniciando deploy do ${PROJECT_NAME_DISPLAY}..."

# ----------------------------------------------------------------------------
# Atualizar projeto do git
# ----------------------------------------------------------------------------

atualizar_projeto_local() {
    echo -e "${GREEN}[DEPLOY]${NC} Verificando atualizações do projeto no repositório git..."
    echo -e "${YELLOW}[DEPLOY]${NC} Descartando alterações locais para evitar conflitos..."
    
    # Verificar e mudar para a branch main se necessário
    current_branch=$(git branch --show-current)
    if [ "$current_branch" != "main" ]; then
        echo -e "${YELLOW}[DEPLOY]${NC} Mudando para a branch main..."
        git checkout main
    fi
    
    # Descartar todas as alterações locais não commitadas
    git reset --hard HEAD
    
    # Limpar arquivos não rastreados
    git clean -fd
    
    # Atualizar com a versão remota
    echo -e "${GREEN}[DEPLOY]${NC} Fazendo pull da versão remota..."
    git pull origin main
    
    echo -e "${GREEN}[DEPLOY]${NC} Projeto atualizado com sucesso!"
}

# ----------------------------------------------------------------------------
# Deploy Frontend
# ----------------------------------------------------------------------------

deploy_frontend() {
    echo -e "${GREEN}[DEPLOY]${NC} Iniciando instalação do Frontend..."

    if [ -e "$ROOT_FRONTEND" ]; then
        sudo rm -r "$ROOT_FRONTEND"
    fi

    sudo mkdir -p "$ROOT_FRONTEND"
    sudo cp "app/templates/index.html" "$ROOT_FRONTEND/index.html"
    sudo cp "app/templates/configuracoes.html" "$ROOT_FRONTEND/configuracoes.html"
    sudo cp "app/templates/dispositivos.html" "$ROOT_FRONTEND/dispositivos.html"
    sudo cp -r "app/static" "$ROOT_FRONTEND"

    echo -e "${GREEN}[DEPLOY]${NC} Frontend instalado em: $ROOT_FRONTEND"
}

# ----------------------------------------------------------------------------
# Deploy Backend
# ----------------------------------------------------------------------------

migrate_data_files() {
    echo -e "${GREEN}[DEPLOY]${NC} Verificando migração de arquivos de dados..."
    
    # Criar diretório de dados se não existir
    if [ ! -d "$ROOT_DATA" ]; then
        echo -e "${GREEN}[DEPLOY]${NC} Criando diretório de dados: $ROOT_DATA"
        sudo mkdir -p "$ROOT_DATA"
        sudo chown $(whoami) "$ROOT_DATA"
    fi
    
    # Criar diretório de logs se não existir
    if [ ! -d "$ROOT_LOGS" ]; then
        echo -e "${GREEN}[DEPLOY]${NC} Criando diretório de logs: $ROOT_LOGS"
        sudo mkdir -p "$ROOT_LOGS"
        sudo chown $(whoami) "$ROOT_LOGS"
    fi
    
    # Arquivos de dados que devem estar no diretório de dados
    DATA_FILES=("app_config.json" "ip_devices.json" "ips_list.json")
    
    for file in "${DATA_FILES[@]}"; do
        # Caminho do arquivo no backend (localização antiga)
        backend_file="$ROOT_BACKEND/$file"
        # Caminho de destino no diretório de dados (localização correta)
        data_file="$ROOT_DATA/$file"
        
        # Se o arquivo existe no backend e não existe no diretório de dados, mover
        if [ -f "$backend_file" ] && [ ! -f "$data_file" ]; then
            echo -e "${YELLOW}[DEPLOY]${NC} Movendo arquivo de dados: $file"
            sudo mv "$backend_file" "$data_file"
            sudo chown $(whoami) "$data_file"
        elif [ -f "$data_file" ]; then
            echo -e "${GREEN}[DEPLOY]${NC} Arquivo de dados já existe: $file"
            # Remover do backend se ainda existir
            if [ -f "$backend_file" ]; then
                echo -e "${YELLOW}[DEPLOY]${NC} Removendo arquivo duplicado do backend: $file"
                sudo rm "$backend_file"
            fi
        else
            echo -e "${YELLOW}[DEPLOY]${NC} Arquivo de dados não encontrado: $file"
        fi
    done
    
    echo -e "${GREEN}[DEPLOY]${NC} Migração concluída. Dados em: $ROOT_DATA"
}

deploy_backend() {
    echo -e "${GREEN}[DEPLOY]${NC} Iniciando instalação do Backend..."

    if [ -e "$ROOT_BACKEND" ]; then
        echo -e "${YELLOW}[DEPLOY]${NC} Atualizando projeto existente..."
        dir_atual=$(pwd)
        cd "$ROOT_BACKEND"
        
        # Verificar e mudar para a branch main se necessário
        backend_branch=$(git branch --show-current)
        if [ "$backend_branch" != "main" ]; then
            echo -e "${YELLOW}[DEPLOY]${NC} Mudando backend para a branch main..."
            git checkout main
        fi
        
        # Descartar alterações locais no backend também
        echo -e "${YELLOW}[DEPLOY]${NC} Descartando alterações locais no backend..."
        git reset --hard HEAD
        git clean -fd
        git pull origin main
        
        cd "$dir_atual"
    else
        echo -e "${GREEN}[DEPLOY]${NC} Clonando novo repositório..."
        sudo mkdir -p "$BACKEND_ROOT"
        git clone "$GIT_REPO_URL"
        sudo mv "$GIT_REPO_NAME" "$ROOT_BACKEND"
    fi

    sudo chown -R $(whoami) "$ROOT_BACKEND"

    echo -e "${GREEN}[DEPLOY]${NC} Configurando projeto..."
    dir_atual=$(pwd)
    cd "$ROOT_BACKEND"
    make setup
    cd "$dir_atual"

    # Tornar scripts executáveis
    [ ! -x "$ROOT_BACKEND/scripts/deploy.sh" ] && sudo chmod +x "$ROOT_BACKEND/scripts/deploy.sh"
    [ ! -x "$ROOT_BACKEND/scripts/run.sh" ] && sudo chmod +x "$ROOT_BACKEND/scripts/run.sh"
    [ ! -x "$ROOT_BACKEND/scripts/config.sh" ] && sudo chmod +x "$ROOT_BACKEND/scripts/config.sh"

    echo -e "${GREEN}[DEPLOY]${NC} Backend instalado em: $ROOT_BACKEND"
}

# ----------------------------------------------------------------------------
# Deploy Serviço Systemd
# ----------------------------------------------------------------------------

deploy_servico() {
    echo -e "${GREEN}[DEPLOY]${NC} Configurando serviço systemd..."

    # Gerar arquivo .service a partir do template
    if [ -f "scripts/generate-service.sh" ]; then
        echo -e "${GREEN}[DEPLOY]${NC} Gerando arquivo de serviço a partir do template..."
        bash scripts/generate-service.sh
    fi

    # Copiar arquivo de serviço para systemd
    if [ -f "scripts/${SERVICE_NAME}.service" ]; then
        sudo cp "scripts/${SERVICE_NAME}.service" "$SERVICE_FILE"
        echo -e "${GREEN}[DEPLOY]${NC} Arquivo de serviço copiado para: $SERVICE_FILE"
    else
        echo -e "${RED}[ERRO]${NC} Arquivo de serviço não encontrado: scripts/${SERVICE_NAME}.service"
        exit 1
    fi

    # Recarregar daemon e reiniciar serviço
    make service-reload
    make service-restart
    
    echo -e "${GREEN}[DEPLOY]${NC} Serviço configurado: $SERVICE_NAME"
}

# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

main() {
    echo -e "${GREEN}[DEPLOY]${NC} ===================================="
    echo -e "${GREEN}[DEPLOY]${NC} Deploy: ${PROJECT_NAME_DISPLAY}"
    echo -e "${GREEN}[DEPLOY]${NC} ===================================="
    
    atualizar_projeto_local
    deploy_frontend
    deploy_backend
    migrate_data_files
    deploy_servico
    
    echo -e "${GREEN}[DEPLOY]${NC} ===================================="
    echo -e "${GREEN}[DEPLOY]${NC} Deploy concluído com sucesso!"
    echo -e "${GREEN}[DEPLOY]${NC} ===================================="
    echo -e "${GREEN}[DEPLOY]${NC} Backend:  $ROOT_BACKEND"
    echo -e "${GREEN}[DEPLOY]${NC} Frontend: $ROOT_FRONTEND"
    echo -e "${GREEN}[DEPLOY]${NC} Dados:    $ROOT_DATA"
    echo -e "${GREEN}[DEPLOY]${NC} Logs:     $ROOT_LOGS"
    echo -e "${GREEN}[DEPLOY]${NC} Serviço:  $SERVICE_NAME"
}

main
