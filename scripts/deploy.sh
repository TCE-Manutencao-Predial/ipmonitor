#!/bin/bash

# Atenção:
# Este Script deve ser executado na raiz do projeto
# Ou pela makefile através do "make deploy"

# Parâmetros de Deploy
# ----------------------------

PROJECT_NAME="ipmonitor"
SERVICE_NAME="ipmonitor.service"

ROOT_FRONTEND=/var/www/automacao.tce.go.gov.br/$PROJECT_NAME
ROOT_SOFTWARES=/var/softwaresTCE
ROOT_BACKEND="$ROOT_SOFTWARES/$PROJECT_NAME"
ROOT_DATA="$ROOT_SOFTWARES/dados/$PROJECT_NAME"

GIT_REPO_NAME="ip-monitor"
GIT_REPO_LINK="https://github.com/TCE-Manutencao-Predial/$GIT_REPO_NAME.git"

# Atualizar projeto do git
# ----------------------------

atualizar_projeto_local() {
    echo "[Deploy] Verificando atualizações do projeto no repositório git..."
    echo "[Deploy] Descartando alterações locais para evitar conflitos..."
    
    # Verificar e mudar para a branch main se necessário
    current_branch=$(git branch --show-current)
    if [ "$current_branch" != "main" ]; then
        echo "[Deploy] Mudando para a branch main..."
        git checkout main
    fi
    
    # Descartar todas as alterações locais não commitadas
    git reset --hard HEAD
    
    # Limpar arquivos não rastreados
    git clean -fd
    
    # Atualizar com a versão remota
    echo "[Deploy] Fazendo pull da versão remota..."
    git pull origin main
    
    echo "[Deploy] Projeto atualizado com sucesso!"
}

# Deploy Frontend
# ----------------------------

deploy_frontend() {
    echo "[Deploy] Iniciando instalação do Frontend..."

    if [ -e $ROOT_FRONTEND ]; then
        sudo rm -r $ROOT_FRONTEND
    fi

    sudo mkdir -p $ROOT_FRONTEND
    sudo cp "app/templates/index.html" "$ROOT_FRONTEND/index.html"
    sudo cp "app/templates/configuracoes.html" "$ROOT_FRONTEND/configuracoes.html"
    sudo cp -r "app/static" "$ROOT_FRONTEND"

    echo "[Deploy] Instalação do Frontend concluída."
}

# Deploy Backend
# ----------------------------

migrate_data_files() {
    echo "[Deploy] Verificando migração de arquivos de dados..."
    
    # Criar diretório de dados se não existir
    if [ ! -d "$ROOT_DATA" ]; then
        echo "[Deploy] Criando diretório de dados: $ROOT_DATA"
        sudo mkdir -p "$ROOT_DATA"
        sudo chown $(whoami) "$ROOT_DATA"
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
            echo "[Deploy] Movendo arquivo de dados do backend para diretório de dados: $file"
            sudo mv "$backend_file" "$data_file"
            sudo chown $(whoami) "$data_file"
        elif [ -f "$data_file" ]; then
            echo "[Deploy] Arquivo de dados já existe no local correto: $file"
            # Remover do backend se ainda existir
            if [ -f "$backend_file" ]; then
                echo "[Deploy] Removendo arquivo duplicado do backend: $file"
                sudo rm "$backend_file"
            fi
        else
            echo "[Deploy] Arquivo de dados não encontrado: $file"
        fi
    done
    
    echo "[Deploy] Verificação de migração concluída."
    echo "[Deploy] Diretório de dados: $ROOT_DATA"
}

deploy_backend() {
    echo "[Deploy] Iniciando instalação do Backend..."

    if [ -e $ROOT_BACKEND ]; then
        echo "[Deploy] Atualizando projeto existente..."
        dir_atual=$(pwd)
        cd $ROOT_BACKEND
        
        # Verificar e mudar para a branch main se necessário
        backend_branch=$(git branch --show-current)
        if [ "$backend_branch" != "main" ]; then
            echo "[Deploy] Mudando backend para a branch main..."
            git checkout main
        fi
        
        # Descartar alterações locais no backend também
        echo "[Deploy] Descartando alterações locais no backend..."
        git reset --hard HEAD
        git clean -fd
        git pull origin main
        
        cd $dir_atual
    else
        echo "[Deploy] Clonando novo repositório..."
        sudo mkdir -p $ROOT_SOFTWARES
        git clone $GIT_REPO_LINK
        sudo mv $GIT_REPO_NAME $ROOT_BACKEND
    fi

    sudo chown -R $(whoami) $ROOT_BACKEND

    echo "[Deploy] Configurando projeto..."
    dir_atual=$(pwd)
    cd $ROOT_BACKEND
    make setup
    cd $dir_atual

    [ ! -x "$ROOT_BACKEND/scripts/deploy.sh" ] && sudo chmod +x "$ROOT_BACKEND/scripts/deploy.sh"
    [ ! -x "$ROOT_BACKEND/scripts/run.sh" ] && sudo chmod +x "$ROOT_BACKEND/scripts/run.sh"
    [ ! -x "$ROOT_BACKEND/scripts/config.sh" ] && sudo chmod +x "$ROOT_BACKEND/scripts/config.sh"

    echo "[Deploy] Backend configurado com sucesso."
}

# Deploy Serviço
# ----------------------------

deploy_servico() {
    echo "[Deploy] Configurando serviço..."

    if [ -e "/usr/lib/systemd/system/$SERVICE_NAME" ]; then
        sudo rm "/usr/lib/systemd/system/$SERVICE_NAME"
    fi

    sudo cp scripts/$SERVICE_NAME /usr/lib/systemd/system/$SERVICE_NAME

    make service-reload
    make service-restart
    echo "[Deploy] Serviço configurado com sucesso."
}

# Main
# ----------------------------

main() {
    echo "[Deploy] Iniciando processo de Deploy..."
    atualizar_projeto_local
    deploy_frontend
    deploy_backend
    migrate_data_files
    deploy_servico
    echo "[Deploy] Processo de Deploy concluído com sucesso!"
}

main
