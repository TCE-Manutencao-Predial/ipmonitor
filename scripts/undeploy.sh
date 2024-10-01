#!/bin/bash

# Parâmetros de Undeploy
# ----------------------------

PROJECT_NAME="ipmonitor"
SERVICE_NAME="ipmonitor.service"

ROOT_FRONTEND=/var/www/automacao.tce.go.gov.br/$PROJECT_NAME

ROOT_SOFTWARES=/var/softwaresTCE
ROOT_BACKEND=$ROOT_SOFTWARES"/"$PROJECT_NAME


# Realizar o Undeploy
# ----------------------------

# Apagar frontend estático do diretório /var/www
sudo rm -r $ROOT_FRONTEND

# Apagar backend da pasta /var/softwaresTCE
sudo rm -r $ROOT_BACKEND

# Remover o serviço criado e os seus links
sudo rm /etc/systemd/system/$SERVICE_NAME
sudo rm /usr/lib/systemd/system/$SERVICE_NAME