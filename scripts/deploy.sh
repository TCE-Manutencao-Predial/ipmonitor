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
ROOT_BACKEND=$ROOT_SOFTWARES"/"$PROJECT_NAME

GIT_REPO_NAME="ipmonitor"
GIT_REPO_LINK="https://github.com/wilsoncf/$GIT_REPO_NAME.git"

# Atualizar projeto do git
# ----------------------------

echo "[Deploy] Verificando atualizações do projeto..."
git pull


# Realizar o Deploy
# ----------------------------

# Copiar o frontend para o diretório reconhecido pelo apache.
echo "[Deploy] Instalando o Frontend..."
sudo rm -r $ROOT_FRONTEND   # Apaga os arquivos antigos
sudo mkdir -p $ROOT_FRONTEND
sudo cp "app/templates/index.html" $ROOT_FRONTEND"/index.html"
sudo cp -r "app/static" $ROOT_FRONTEND

# Se existir, dá um git pull para atualizar os conteudos
if [ -e $ROOT_BACKEND ]; then
    echo "[Deploy] Projeto antigo do backend encontrado, atualizando arquivos..."

    dir_atual=$(pwd)
    cd $ROOT_BACKEND
    git pull
    cd $dir_atual
    
else # Se não houver a pasta do Backend, a cria e clona o repositório para ela
    echo "[Deploy] Projeto do backend não encontrado, criando os arquivos..."

    # Cria a pasta dos softwares, caso não exista
    sudo mkdir -p $ROOT_SOFTWARES

    # Clona o repositório para o diretório dos softwares
    git clone $GIT_REPO_LINK
    sudo mv $GIT_REPO_NAME $ROOT_BACKEND
fi

# Antes de realizar o setup, altera as permissões de escrita dos arquivos do Backend para o usuário atual
sudo chown -R $(whoami) $ROOT_BACKEND

# Realiza o setup do projeto
dir_atual=$(pwd)
cd $ROOT_BACKEND
make setup
cd $dir_atual

# Copia o scadaweb.service para sua pasta
echo "Instalando o serviço..."
if [ -e "/usr/lib/systemd/system/$SERVICE_NAME" ]; then   # Antes de copiar, remove o arquivo anterior
    sudo rm "/usr/lib/systemd/system/$SERVICE_NAME"   
fi
sudo cp scripts/$SERVICE_NAME /usr/lib/systemd/system/$SERVICE_NAME

# Ativa o serviço
echo "Ativando o serviço..."
make service-reload
make service-restart