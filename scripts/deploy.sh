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


# Realizar o Deploy
# ----------------------------

# Copiar o frontend para o diretório reconhecido pelo apache.
sudo mkdir -p $ROOT_FRONTEND
sudo cp "ipmonitor/templates/index.html" $ROOT_FRONTEND"/index.html"
sudo cp -r "ipmonitor/static" $ROOT_FRONTEND"/static"

# Baixar uma cópia do repositório e mover para o diretório do backend
sudo mkdir -p $ROOT_SOFTWARES
git clone $GIT_REPO_LINK
sudo mv $GIT_REPO_NAME $ROOT_BACKEND

# Copiar o ipmonitor.service para sua pasta
sudo cp scripts/$SERVICE_NAME /usr/lib/systemd/system/$SERVICE_NAME

# Realizar o setup no projeto
cd $ROOT_BACKEND
make setup