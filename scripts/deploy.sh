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

echo "[Deploy] Verificando atualizações do projeto no repositório git..."
git pull
echo "[Deploy] Atualizações do projeto concluídas."


# Realizar o Deploy
# ----------------------------

# Copiar o frontend para o diretório reconhecido pelo apache.
echo "[Deploy] Instalando o Frontend..."

if [ -e $ROOT_FRONTEND ]; then
    echo "[Deploy] Diretório do Frontend existente encontrado. Removendo arquivos antigos..."
    sudo rm -rv $ROOT_FRONTEND
fi

echo "[Deploy] Criando diretório do Frontend..."
sudo mkdir -pv $ROOT_FRONTEND

echo "[Deploy] Copiando arquivos HTML e estáticos para o diretório do Frontend..."
sudo cp -v "app/templates/index.html" "$ROOT_FRONTEND/index.html"
sudo cp -vr "app/static" "$ROOT_FRONTEND"

echo "[Deploy] Instalação do Frontend concluída."


# Verificar e atualizar o Backend
if [ -e $ROOT_BACKEND ]; then
    echo "[Deploy] Projeto antigo do Backend encontrado. Atualizando arquivos..."
    dir_atual=$(pwd)
    cd $ROOT_BACKEND
    git pull
    cd $dir_atual
    echo "[Deploy] Atualização do Backend concluída."
else
    echo "[Deploy] Diretório do Backend não encontrado. Criando novo repositório..."
    sudo mkdir -pv $ROOT_SOFTWARES
    git clone $GIT_REPO_LINK
    sudo mv -v $GIT_REPO_NAME $ROOT_BACKEND
    echo "[Deploy] Repositório do Backend clonado para: $ROOT_BACKEND"
fi

echo "[Deploy] Ajustando permissões do diretório do Backend..."
sudo chown -Rv $(whoami) $ROOT_BACKEND
echo "[Deploy] Permissões do Backend ajustadas."


# Configurar e preparar o Backend
echo "[Deploy] Configurando projeto do Backend..."
dir_atual=$(pwd)
cd $ROOT_BACKEND
make setup
cd $dir_atual
echo "[Deploy] Configuração do Backend concluída."


# Copiar e ativar o serviço
echo "[Deploy] Instalando o serviço..."

if [ -e "/usr/lib/systemd/system/$SERVICE_NAME" ]; then
    echo "[Deploy] Serviço existente encontrado. Removendo configuração antiga..."
    sudo rm -v "/usr/lib/systemd/system/$SERVICE_NAME"
fi

echo "[Deploy] Copiando novo arquivo de serviço..."
sudo cp -v scripts/$SERVICE_NAME /usr/lib/systemd/system/$SERVICE_NAME

echo "[Deploy] Reiniciando o serviço..."
make service-reload
make service-restart
echo "[Deploy] Serviço reiniciado com sucesso."
