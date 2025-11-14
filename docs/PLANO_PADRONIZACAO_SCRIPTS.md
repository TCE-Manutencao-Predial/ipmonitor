# Plano de Padronização: Scripts de Deploy e Settings.py

## 📋 Análise da Situação Atual

### 🔴 Problemas Identificados

#### 1. **Duplicação de Configurações**
Atualmente as mesmas variáveis existem em **múltiplos lugares**:

| Variável | settings.py | deploy.sh | undeploy.sh | run.sh | .service | makefile |
|----------|-------------|-----------|-------------|--------|----------|----------|
| PROJECT_NAME | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| SERVICE_NAME | ✅ | ✅ | ✅ | ❌ | Hardcoded | ✅ |
| ROOT_BACKEND | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| ROOT_FRONTEND | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| ROOT_DATA | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| GIT_REPO_NAME | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| DOMAIN_BASE | ✅ | Hardcoded | Hardcoded | ❌ | ❌ | ❌ |

**Resultado**: 6-7 lugares com valores hardcoded que podem ficar dessincronizados.

#### 2. **Inconsistências Entre Submódulos**

**ip-monitor** (atual):
```bash
# deploy.sh (linhas 10-17)
PROJECT_NAME="ipmonitor"
ROOT_FRONTEND=/var/www/automacao.tce.go.gov.br/$PROJECT_NAME
ROOT_BACKEND=/var/softwaresTCE/$PROJECT_NAME
ROOT_DATA=/var/softwaresTCE/dados/$PROJECT_NAME
```

**helpdesk-monitor** (tem config.sh separado):
```bash
# config.sh
PROJECT_NAME="helpdesk_monitor"
DATA_FOLDER_NAME="helpdeskmonitor"  # ← Variável adicional
LOGS_PATH=/var/softwaresTCE/logs/$PROJECT_NAME
DADOS_PATH=/var/softwaresTCE/dados/$DATA_FOLDER_NAME
```

#### 3. **Acesso Unidirecional**
- ✅ Python pode importar de `settings.py`
- ❌ Bash scripts **NÃO** podem importar Python
- ❌ Systemd service **NÃO** pode usar Python

---

## 🎯 Soluções Possíveis

### **Opção A: Arquivo de Configuração Compartilhado (ENV/INI)**

Criar um arquivo intermediário que **ambos** possam ler.

#### Estrutura Proposta:
```
ip-monitor/
├── app/
│   └── settings.py          ← Lê de .env
├── scripts/
│   ├── deploy.sh            ← Lê de .env
│   └── config.sh            ← Source .env
├── .env.deploy              ← 🆕 FONTE ÚNICA
└── .env.deploy.template     ← Template para novos deploys
```

#### `.env.deploy` (Exemplo)
```bash
# Configurações de Deploy - IP Monitor
# IMPORTANTE: Este arquivo é a fonte única de verdade para deploy

# Identificação
PROJECT_NAME=ipmonitor
PROJECT_NAME_DISPLAY="IP Monitor"
SERVICE_NAME=ipmonitor

# Git
GIT_REPO_NAME=ip-monitor
GIT_REPO_OWNER=TCE-Manutencao-Predial

# Domínio
DOMAIN_BASE=automacao.tce.go.gov.br

# Caminhos Base
BACKEND_ROOT=/var/softwaresTCE
FRONTEND_ROOT=/var/www/automacao.tce.go.gov.br

# Caminhos Derivados (calculados em scripts)
# ROOT_BACKEND=${BACKEND_ROOT}/${PROJECT_NAME}
# ROOT_FRONTEND=${FRONTEND_ROOT}/${PROJECT_NAME}
# ROOT_DATA=${BACKEND_ROOT}/dados/${PROJECT_NAME}
# ROOT_LOGS=${BACKEND_ROOT}/logs/${PROJECT_NAME}

# Porta
PORT=8000

# Opções
AUTO_ENABLE_SERVICE=true
```

#### `app/settings.py` (Modificado)
```python
import os
from pathlib import Path
from dotenv import load_dotenv

# Carregar .env.deploy se existir (produção)
env_file = Path(__file__).parent.parent / '.env.deploy'
if env_file.exists():
    load_dotenv(env_file)

# Valores com fallback
PROJECT_NAME = os.getenv('PROJECT_NAME', 'ip-monitor')
PROJECT_NAME_SERVICE = os.getenv('PROJECT_NAME', 'ipmonitor')
DOMAIN_BASE = os.getenv('DOMAIN_BASE', 'automacao.tce.go.gov.br')
# ...
```

#### `scripts/config.sh` (Novo - substitui variáveis em deploy.sh)
```bash
#!/bin/bash

# Carregar configurações do .env.deploy
if [ -f "../.env.deploy" ]; then
    source "../.env.deploy"
else
    echo "ERRO: Arquivo .env.deploy não encontrado!"
    exit 1
fi

# Calcular caminhos derivados
ROOT_BACKEND="${BACKEND_ROOT}/${PROJECT_NAME}"
ROOT_FRONTEND="${FRONTEND_ROOT}/${PROJECT_NAME}"
ROOT_DATA="${BACKEND_ROOT}/dados/${PROJECT_NAME}"
ROOT_LOGS="${BACKEND_ROOT}/logs/${PROJECT_NAME}"

GIT_REPO_LINK="https://github.com/${GIT_REPO_OWNER}/${GIT_REPO_NAME}.git"

# Exportar para uso em outros scripts
export PROJECT_NAME SERVICE_NAME
export ROOT_BACKEND ROOT_FRONTEND ROOT_DATA ROOT_LOGS
export GIT_REPO_LINK
```

#### `scripts/deploy.sh` (Modificado)
```bash
#!/bin/bash

# Carregar configurações centralizadas
source "$(dirname "$0")/config.sh"

# Agora todas as variáveis estão disponíveis
deploy_frontend() {
    echo "[Deploy] Instalando Frontend em: $ROOT_FRONTEND"
    sudo mkdir -p "$ROOT_FRONTEND"
    # ...
}
```

#### `scripts/ipmonitor.service.template` (Template)
```ini
[Unit]
Description={{PROJECT_NAME_DISPLAY}} API

[Service]
User=root
WorkingDirectory={{ROOT_BACKEND}}
ExecStart={{ROOT_BACKEND}}/scripts/run.sh
Restart=always
RestartSec=9

[Install]
WantedBy=multi-user.target
```

**Deploy gera .service real**:
```bash
# Em deploy.sh
envsubst < scripts/ipmonitor.service.template > /tmp/ipmonitor.service
sudo cp /tmp/ipmonitor.service /usr/lib/systemd/system/
```

---

### **Opção B: Python Gera Configurações para Bash**

Python `settings.py` é a fonte única. Scripts bash leem arquivo gerado.

#### Estrutura:
```
ip-monitor/
├── app/
│   └── settings.py           ← Fonte única
├── scripts/
│   ├── .config.generated.sh  ← 🆕 Gerado por Python
│   └── deploy.sh             ← Lê .config.generated.sh
└── tools/
    └── generate_config.py    ← 🆕 Gera config para bash
```

#### `tools/generate_config.py`
```python
#!/usr/bin/env python3
"""Gera arquivo de configuração bash a partir do settings.py"""

from app import settings
from pathlib import Path

def generate_bash_config():
    config_content = f"""#!/bin/bash
# ARQUIVO GERADO AUTOMATICAMENTE - NÃO EDITE
# Gerado a partir de app/settings.py

PROJECT_NAME="{settings.PROJECT_NAME_SERVICE}"
SERVICE_NAME="{settings.SERVICE_NAME}"
DOMAIN_BASE="{settings.DOMAIN_BASE}"
ROOT_BACKEND="{settings.PROJECT_BACKEND}"
ROOT_FRONTEND="{settings.PROJECT_FRONTEND}"
ROOT_DATA="{settings.PROJECT_DATA}"
ROOT_LOGS="{settings.PROJECT_LOGS}"
GIT_REPO_NAME="{settings.GIT_REPO_NAME}"
GIT_REPO_URL="{settings.GIT_REPO_URL}"
PORT="{settings.PORT_DEFAULT}"
"""
    
    output_file = Path(__file__).parent.parent / 'scripts' / '.config.generated.sh'
    output_file.write_text(config_content)
    print(f"✅ Configuração gerada: {output_file}")

if __name__ == '__main__':
    generate_bash_config()
```

#### Uso em Makefile:
```makefile
deploy:
	python tools/generate_config.py  # Gera config.sh antes
	sudo chmod +x ./scripts/deploy.sh
	./scripts/deploy.sh
```

---

### **Opção C: JSON Compartilhado**

Arquivo JSON que ambos leem (Python nativo, bash com `jq`).

#### `.deploy-config.json`
```json
{
  "project": {
    "name": "ipmonitor",
    "display_name": "IP Monitor",
    "service_name": "ipmonitor"
  },
  "git": {
    "repo_name": "ip-monitor",
    "repo_owner": "TCE-Manutencao-Predial"
  },
  "paths": {
    "domain": "automacao.tce.go.gov.br",
    "backend_root": "/var/softwaresTCE",
    "frontend_root": "/var/www/automacao.tce.go.gov.br"
  },
  "port": 8000
}
```

#### Python lê JSON:
```python
import json
from pathlib import Path

config_file = Path(__file__).parent.parent / '.deploy-config.json'
with open(config_file) as f:
    DEPLOY_CONFIG = json.load(f)

PROJECT_NAME = DEPLOY_CONFIG['project']['name']
```

#### Bash lê JSON (requer `jq`):
```bash
CONFIG_FILE="../.deploy-config.json"
PROJECT_NAME=$(jq -r '.project.name' "$CONFIG_FILE")
```

**❌ Desvantagem**: Requer `jq` instalado no servidor.

---

## 🏆 Recomendação: **Opção A (Arquivo .env Compartilhado)**

### ✅ Vantagens

1. **Fonte Única de Verdade**: Um arquivo, múltiplos consumidores
2. **Sem Dependências**: Bash nativo lê `.env`, Python usa `python-dotenv`
3. **Padrão da Indústria**: `.env` é amplamente usado (12-factor app)
4. **Fácil Edição**: Arquivo texto simples
5. **Versionável**: Pode ter `.env.template` no git, `.env.deploy` local
6. **Compatível com Docker**: Se migrar para containers, já está pronto
7. **Auditável**: Um lugar para revisar configurações

### ⚙️ Implementação Gradual

#### **Fase 1: Criar Estrutura** (Sem quebrar nada)
```bash
# Criar arquivos novos
.env.deploy.template    # Template versionado
.env.deploy             # Local (não versionado)
scripts/config.sh       # Source .env.deploy
```

#### **Fase 2: Migrar settings.py**
```python
# settings.py passa a ler de .env.deploy
from dotenv import load_dotenv
load_dotenv('.env.deploy')
```

#### **Fase 3: Migrar Scripts**
```bash
# deploy.sh, undeploy.sh, run.sh
source "$(dirname "$0")/config.sh"
# Remove variáveis hardcoded
```

#### **Fase 4: Template do .service**
```bash
# Gerar .service dinamicamente
envsubst < ipmonitor.service.template > ipmonitor.service
```

---

## 📊 Comparação de Opções

| Critério | Opção A (.env) | Opção B (Python→Bash) | Opção C (JSON) |
|----------|----------------|----------------------|----------------|
| **Fonte Única** | ✅ | ✅ | ✅ |
| **Sem Dependências** | ✅ | ✅ | ❌ (precisa jq) |
| **Edição Manual** | ✅ Fácil | ❌ Regenera | ✅ Fácil |
| **Padrão** | ✅ 12-factor | ⚠️ Custom | ⚠️ Menos comum |
| **Docker-ready** | ✅ | ❌ | ⚠️ |
| **Auditável** | ✅ | ⚠️ (2 arquivos) | ✅ |
| **Manutenção** | ✅ Simples | ⚠️ Intermediário | ⚠️ Intermediário |

---

## 🗺️ Estrutura Final Proposta

```
ip-monitor/
├── .env.deploy.template         # 🆕 Template versionado
├── .env.deploy                  # 🆕 Configuração local (gitignore)
├── .gitignore                   # Adicionar .env.deploy
├── requirements.txt             # Adicionar python-dotenv
│
├── app/
│   ├── settings.py              # ✏️ Modificado - lê .env.deploy
│   └── __init__.py              # ✏️ Modificado - usa settings
│
├── scripts/
│   ├── config.sh                # 🆕 Fonte configurações bash
│   ├── deploy.sh                # ✏️ Modificado - usa config.sh
│   ├── undeploy.sh              # ✏️ Modificado - usa config.sh
│   ├── run.sh                   # ✏️ Modificado - usa config.sh
│   ├── ipmonitor.service.template # 🆕 Template systemd
│   └── generate-service.sh      # 🆕 Gera .service final
│
└── tools/                       # 🆕 Ferramentas auxiliares
    └── validate-config.py       # 🆕 Valida .env.deploy
```

---

## 📝 Exemplo de Migração (ip-monitor)

### Antes:
```bash
# deploy.sh (linha 10)
PROJECT_NAME="ipmonitor"
ROOT_FRONTEND=/var/www/automacao.tce.go.gov.br/$PROJECT_NAME
```

### Depois:
```bash
# config.sh
source "../.env.deploy"
ROOT_FRONTEND="${FRONTEND_ROOT}/${PROJECT_NAME}"

# deploy.sh (linha 10)
source "$(dirname "$0")/config.sh"
# Variáveis já disponíveis: $PROJECT_NAME, $ROOT_FRONTEND
```

---

## 🎯 Benefícios Esperados

1. **Manutenibilidade**: Alterar URL = 1 lugar (`.env.deploy`)
2. **Consistência**: Python e Bash sempre sincronizados
3. **Escalabilidade**: Fácil adicionar novos submódulos
4. **Documentação**: `.env.template` documenta configurações
5. **Segurança**: `.env.deploy` pode conter secrets (não versionado)
6. **Validação**: Script pode validar configurações antes do deploy
7. **Migração**: Compatível com Docker Compose futuramente

---

## ⚠️ Riscos e Mitigações

| Risco | Mitigação |
|-------|-----------|
| `.env.deploy` perdido | Manter `.env.template` versionado |
| Bash não lê .env | Criar `config.sh` que valida e carrega |
| Python sem dotenv | Adicionar `python-dotenv` ao requirements.txt |
| Service hardcoded | Gerar dinamicamente com `envsubst` |
| Múltiplos ambientes | `.env.deploy.dev`, `.env.deploy.prod` |

---

## 🚀 Próximos Passos Sugeridos

1. **Aprovação**: Revisar e aprovar este plano
2. **Protótipo**: Implementar Opção A no `ip-monitor`
3. **Teste**: Validar deploy em ambiente de testes
4. **Template**: Criar templates reutilizáveis
5. **Documentação**: Documentar processo
6. **Replicação**: Aplicar em outros submódulos

---

**Data**: 14 de novembro de 2025  
**Submódulo**: ip-monitor  
**Status**: 📋 Planejamento Completo  
**Recomendação**: Opção A (Arquivo .env Compartilhado)
