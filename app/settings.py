"""
Configurações Centralizadas do IP Monitor
==========================================

Este arquivo centraliza TODAS as configurações e variáveis globais do projeto.
Objetivo: Padronizar e facilitar migração futura, SEM quebrar código existente.

IMPORTANTE: Este arquivo é APENAS para centralização de configurações.
O código existente continua funcionando normalmente.

Data de criação: 2025-11-14
Versão: 1.0.0
"""

import os
import platform


# ============================================================================
# SEÇÃO 1: IDENTIFICAÇÃO DO PROJETO
# ============================================================================
# Estas variáveis definem a identidade única do projeto no ecossistema Zapdos

PROJECT_NAME = "ip-monitor"           # Nome do projeto (kebab-case) - usado para repositório git
PROJECT_NAME_SERVICE = "ipmonitor"    # Nome usado para systemd service (sem hífen)
PROJECT_NAME_DISPLAY = "IP Monitor"   # Nome para exibição em interfaces

MODULE_NAME = "config"                # Nome do módulo Python principal (para WSGI)
PORT_DEFAULT = 8000                   # Porta padrão para desenvolvimento local


# ============================================================================
# SEÇÃO 2: ROTAS E URLs
# ============================================================================
# Define como o serviço é acessado via web

# Prefixo das rotas (usado em produção com proxy reverso)
ROUTES_PREFIX = "/ipmonitor"          # ATUAL: mantido por compatibilidade
ROUTES_PREFIX_CANONICAL = f"/{PROJECT_NAME_SERVICE}"  # FUTURO: padronizado

# Domínio base do sistema
DOMAIN_BASE = "automacao.tce.go.gov.br"

# URLs completas
BASE_URL_PRODUCTION = f"https://{DOMAIN_BASE}{ROUTES_PREFIX}"
API_BASE_URL_PRODUCTION = f"{BASE_URL_PRODUCTION}/api"


# ============================================================================
# SEÇÃO 3: ESTRUTURA DE PASTAS - PRODUÇÃO (Linux)
# ============================================================================
# Organização padronizada de diretórios no servidor de produção

# Raiz dos softwares TCE
BACKEND_ROOT = "/var/softwaresTCE"
FRONTEND_ROOT = f"/var/www/{DOMAIN_BASE}"

# Caminhos específicos deste projeto - ESTRUTURA ATUAL (mantida por compatibilidade)
PROJECT_BACKEND_CURRENT = os.path.join(BACKEND_ROOT, PROJECT_NAME_SERVICE)
PROJECT_FRONTEND_CURRENT = os.path.join(FRONTEND_ROOT, PROJECT_NAME_SERVICE)
PROJECT_DATA_CURRENT = os.path.join(BACKEND_ROOT, "dados", PROJECT_NAME_SERVICE)

# Caminhos específicos deste projeto - ESTRUTURA PADRONIZADA (futura migração)
PROJECT_ROOT_STANDARD = os.path.join(BACKEND_ROOT, PROJECT_NAME)
PROJECT_LOGS_STANDARD = os.path.join(PROJECT_ROOT_STANDARD, "logs")
PROJECT_DATA_STANDARD = os.path.join(PROJECT_ROOT_STANDARD, "data")
PROJECT_STATIC_STANDARD = os.path.join(PROJECT_ROOT_STANDARD, "static")


# ============================================================================
# SEÇÃO 4: ESTRUTURA DE PASTAS - DESENVOLVIMENTO (Windows/Mac/Linux Local)
# ============================================================================
# Caminhos para ambiente de desenvolvimento local

if platform.system() == "Linux":
    # Em produção, usa os caminhos padrão do servidor
    PROJECT_BACKEND = PROJECT_BACKEND_CURRENT
    PROJECT_FRONTEND = PROJECT_FRONTEND_CURRENT
    PROJECT_DATA = PROJECT_DATA_CURRENT
    PROJECT_LOGS = os.path.join(BACKEND_ROOT, "logs", PROJECT_NAME_SERVICE)
    PROJECT_STATIC = os.path.join(PROJECT_BACKEND, "app", "static")
else:
    # Desenvolvimento local - usa diretório relativo ao projeto
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    PROJECT_BACKEND = BASE_DIR
    PROJECT_FRONTEND = os.path.join(BASE_DIR, "app", "templates")
    PROJECT_DATA = os.path.join(BASE_DIR, "data")
    PROJECT_LOGS = os.path.join(BASE_DIR, "logs")
    PROJECT_STATIC = os.path.join(BASE_DIR, "app", "static")


# ============================================================================
# SEÇÃO 5: ARQUIVOS DE DADOS
# ============================================================================
# Localização de arquivos JSON e bancos de dados

# Arquivos de configuração
APP_CONFIG_FILE = "app_config.json"
APP_CONFIG_PATH = os.path.join(PROJECT_DATA, APP_CONFIG_FILE)

# Arquivos de dados
DEVICES_FILE = "ip_devices.json"
DEVICES_PATH = os.path.join(PROJECT_DATA, DEVICES_FILE)

IPS_LIST_FILE = "ips_list.json"
IPS_LIST_PATH = os.path.join(PROJECT_DATA, IPS_LIST_FILE)


# ============================================================================
# SEÇÃO 6: CONFIGURAÇÕES DO SYSTEMD SERVICE
# ============================================================================
# Configurações para o serviço systemd no servidor

SERVICE_NAME = PROJECT_NAME_SERVICE
SERVICE_FILE = f"{SERVICE_NAME}.service"
SERVICE_DESCRIPTION = "TCE IP Monitor - Sistema de Monitoramento de Dispositivos de Rede"


# ============================================================================
# SEÇÃO 7: CONFIGURAÇÕES DO GIT
# ============================================================================
# Informações do repositório

GIT_REPO_NAME = PROJECT_NAME           # Nome do repositório (kebab-case)
GIT_REPO_OWNER = "TCE-Manutencao-Predial"
GIT_REPO_URL = f"https://github.com/{GIT_REPO_OWNER}/{GIT_REPO_NAME}.git"


# ============================================================================
# SEÇÃO 8: CONFIGURAÇÕES DE REDE E MONITORAMENTO
# ============================================================================
# Parâmetros técnicos do sistema de monitoramento

# VLANs monitoradas
VLANS = {
    70: "Câmeras",
    80: "Alarme",
    85: "Automação Ethernet",
    86: "Automação WiFi",
    200: "Telefonia IP Fixa",
    204: "Telefonia IP Móvel"
}

# Base de rede para cada VLAN
NETWORK_BASE = "172.17.{vlan}."

# Configurações padrão de ping
PING_TIMEOUT_DEFAULT = 2
MAX_CONCURRENT_PINGS_DEFAULT = 3
RETRY_ATTEMPTS_DEFAULT = 2


# ============================================================================
# SEÇÃO 9: FUNÇÕES UTILITÁRIAS
# ============================================================================

def ensure_directories():
    """
    Garante que todos os diretórios necessários existem.
    Esta função deve ser chamada na inicialização da aplicação.
    """
    directories = [
        PROJECT_DATA,
        PROJECT_LOGS,
        PROJECT_STATIC
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            

def get_environment():
    """
    Retorna o ambiente atual (production ou development).
    """
    return "production" if platform.system() == "Linux" else "development"


def get_routes_prefix():
    """
    Retorna o prefixo de rotas apropriado para o ambiente.
    Em produção retorna '/ipmonitor', em desenvolvimento retorna ''.
    """
    return ROUTES_PREFIX if get_environment() == "production" else ""


def get_api_base_url():
    """
    Retorna a URL base da API para o ambiente atual.
    """
    if get_environment() == "production":
        return f"{ROUTES_PREFIX}/api"
    else:
        return "/api"


# ============================================================================
# SEÇÃO 10: CONFIGURAÇÕES DE LOGGING
# ============================================================================

LOG_FILE = os.path.join(PROJECT_LOGS, "app.log")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5


# ============================================================================
# SEÇÃO 11: COMPATIBILIDADE COM CÓDIGO EXISTENTE
# ============================================================================
# Aliases para manter compatibilidade com variáveis usadas no código atual

# Para deploy.sh
ROOT_FRONTEND = PROJECT_FRONTEND
ROOT_BACKEND = PROJECT_BACKEND
ROOT_DATA = PROJECT_DATA
ROOT_SOFTWARES = BACKEND_ROOT

# Para routes.py
RAIZ = ROUTES_PREFIX

# Para config_manager.py (já usa get_data_file_path)
# Sem mudanças necessárias


# ============================================================================
# INFORMAÇÕES DO ARQUIVO
# ============================================================================

__version__ = "1.0.0"
__author__ = "TCE Manutenção Predial"
__date__ = "2025-11-14"
__description__ = "Configurações centralizadas do IP Monitor"


# ============================================================================
# EXEMPLO DE USO
# ============================================================================
"""
# No código Python, importe as configurações:
from app.settings import (
    PROJECT_NAME,
    ROUTES_PREFIX,
    PROJECT_DATA,
    ensure_directories
)

# Garanta que os diretórios existem:
ensure_directories()

# Use as constantes:
print(f"Projeto: {PROJECT_NAME}")
print(f"Dados em: {PROJECT_DATA}")
"""
