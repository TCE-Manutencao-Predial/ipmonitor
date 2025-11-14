#!/usr/bin/env python3
"""
Validador de Configuração - IP Monitor
========================================

Valida o arquivo .env.deploy e exibe as configurações que serão usadas.
Útil para verificar se todas as variáveis estão corretas antes do deploy.

Uso:
    python tools/validate-config.py
    python tools/validate-config.py --verbose
"""

import sys
import os
from pathlib import Path

# Adicionar diretório raiz ao path para importar settings
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from app import settings
except ImportError as e:
    print(f"❌ ERRO: Não foi possível importar settings.py")
    print(f"   {e}")
    sys.exit(1)


def print_header(text):
    """Imprime cabeçalho formatado"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)


def print_section(title, items):
    """Imprime seção com itens"""
    print(f"\n{title}:")
    print("-" * 80)
    for key, value in items.items():
        print(f"  {key:30} = {value}")


def validate_paths(paths):
    """Valida se os caminhos existem (apenas em produção Linux)"""
    if settings.get_environment() != "production":
        print("\n⚠️  Validação de caminhos pulada (ambiente de desenvolvimento)")
        return True
    
    print("\n🔍 Validando caminhos de produção...")
    all_valid = True
    
    for name, path in paths.items():
        if os.path.exists(path):
            print(f"  ✅ {name}: {path}")
        else:
            print(f"  ❌ {name}: {path} (NÃO EXISTE)")
            all_valid = False
    
    return all_valid


def main():
    """Função principal"""
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    
    print_header("VALIDADOR DE CONFIGURAÇÃO - IP MONITOR")
    
    # Informações do ambiente
    env_info = {
        "Ambiente": settings.get_environment(),
        "Sistema": settings.platform.system(),
        "Arquivo .env": ".env.deploy" if (Path(__file__).parent.parent / '.env.deploy').exists() else "NÃO ENCONTRADO"
    }
    print_section("📋 Ambiente", env_info)
    
    # Identificação do projeto
    project_info = {
        "Nome do Projeto": settings.PROJECT_NAME,
        "Nome para Exibição": settings.PROJECT_NAME_DISPLAY,
        "Nome Git": settings.PROJECT_NAME_GIT,
        "Nome do Serviço": settings.SERVICE_NAME,
        "Porta Padrão": settings.PORT_DEFAULT
    }
    print_section("🏷️  Identificação", project_info)
    
    # Rotas e URLs
    routes_info = {
        "Domínio Base": settings.DOMAIN_BASE,
        "Prefixo de Rotas": settings.ROUTES_PREFIX,
        "URL de Produção": settings.BASE_URL_PRODUCTION,
        "URL da API": settings.API_BASE_URL_PRODUCTION
    }
    print_section("🌐 Rotas e URLs", routes_info)
    
    # Git
    git_info = {
        "Repositório": settings.GIT_REPO_NAME,
        "Proprietário": settings.GIT_REPO_OWNER,
        "URL": settings.GIT_REPO_URL
    }
    print_section("📦 Repositório Git", git_info)
    
    # Caminhos de produção
    if settings.get_environment() == "production":
        paths_info = {
            "Backend": settings.PROJECT_BACKEND,
            "Frontend": settings.PROJECT_FRONTEND,
            "Dados": settings.PROJECT_DATA,
            "Logs": settings.PROJECT_LOGS,
            "Estáticos": settings.PROJECT_STATIC
        }
    else:
        paths_info = {
            "Backend (dev)": settings.PROJECT_BACKEND,
            "Frontend (dev)": settings.PROJECT_FRONTEND,
            "Dados (dev)": settings.PROJECT_DATA,
            "Logs (dev)": settings.PROJECT_LOGS,
            "Estáticos (dev)": settings.PROJECT_STATIC,
            "---": "---",
            "Backend (deploy)": settings.PROJECT_BACKEND_DEPLOY,
            "Frontend (deploy)": settings.PROJECT_FRONTEND_DEPLOY,
            "Dados (deploy)": settings.PROJECT_DATA_DEPLOY,
            "Logs (deploy)": settings.PROJECT_LOGS_DEPLOY
        }
    
    print_section("📁 Caminhos", paths_info)
    
    # Rede
    network_info = {
        "Base de Rede": settings.NETWORK_BASE,
        "VLANs": f"{len(settings.VLANS)} configuradas"
    }
    
    if verbose:
        for vlan, desc in settings.VLANS.items():
            network_info[f"  VLAN {vlan}"] = desc
    
    print_section("🌐 Rede", network_info)
    
    # Systemd Service
    service_info = {
        "Nome do Serviço": settings.SERVICE_NAME,
        "Arquivo": settings.SERVICE_FILE,
        "Caminho": settings.SERVICE_PATH,
        "Descrição": settings.SERVICE_DESCRIPTION
    }
    print_section("⚙️  Systemd Service", service_info)
    
    # Validação de caminhos
    if settings.get_environment() == "production":
        paths_to_validate = {
            "Backend": settings.PROJECT_BACKEND,
            "Dados": settings.PROJECT_DATA,
            "Logs": settings.PROJECT_LOGS
        }
        paths_valid = validate_paths(paths_to_validate)
    else:
        paths_valid = True
    
    # Resumo
    print_header("RESUMO DA VALIDAÇÃO")
    
    if paths_valid:
        print("\n✅ Configuração válida!")
        print("\n💡 Próximos passos:")
        print("   1. Revise as configurações acima")
        print("   2. Execute 'make deploy' para fazer o deploy")
        print("   3. Verifique os logs com 'journalctl -u ipmonitor -f'")
        return 0
    else:
        print("\n❌ Configuração com problemas!")
        print("\n⚠️  Corrija os caminhos antes de fazer o deploy.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
