# Guia Rápido: Configuração Centralizada

## 🎯 Conceito

**1 arquivo** = **1 fonte de verdade** para TODAS as configurações de deploy.

```
.env.deploy  ←  Python lê     (settings.py)
             ←  Bash lê       (config.sh)
             ←  Systemd usa   (.service.template)
```

---

## 📁 Arquivos Principais

| Arquivo | Descrição | Versionado? |
|---------|-----------|-------------|
| `.env.deploy.template` | Template de configuração | ✅ Sim |
| `.env.deploy` | Configuração padrão de produção | ✅ Sim |
| `.env.local` | Sobrescritas locais (opcional) | ❌ Não (gitignore) |
| `.env.local.example` | Exemplo de configurações locais | ✅ Sim |
| `scripts/config.sh` | Carrega .env para bash | ✅ Sim |
| `tools/validate-config.py` | Valida configurações | ✅ Sim |

---

## ⚙️ Variáveis Disponíveis

### Identificação
```bash
PROJECT_NAME=ipmonitor           # Nome do projeto (sem hífen)
PROJECT_NAME_DISPLAY=IP Monitor  # Nome para exibição
PROJECT_NAME_GIT=ip-monitor      # Nome do repositório git
SERVICE_NAME=ipmonitor           # Nome do serviço systemd
```

### Git
```bash
GIT_REPO_NAME=ip-monitor
GIT_REPO_OWNER=TCE-Manutencao-Predial
```

### Rede
```bash
DOMAIN_BASE=automacao.tce.go.gov.br
ROUTES_PREFIX=/ipmonitor
NETWORK_BASE=172.17.{vlan}.
PORT=8000
```

### Caminhos Base (Linux)
```bash
BACKEND_ROOT=/var/softwaresTCE
FRONTEND_ROOT=/var/www/automacao.tce.go.gov.br
DATA_ROOT=/var/softwaresTCE/dados
LOGS_ROOT=/var/softwaresTCE/logs
```

### Caminhos Derivados (Calculados Automaticamente)
```bash
# Em config.sh:
ROOT_BACKEND=${BACKEND_ROOT}/${PROJECT_NAME}
ROOT_FRONTEND=${FRONTEND_ROOT}/${PROJECT_NAME}
ROOT_DATA=${DATA_ROOT}/${PROJECT_NAME}
ROOT_LOGS=${LOGS_ROOT}/${PROJECT_NAME}
```

---

## 🚀 Uso em Python

### settings.py
```python
from dotenv import load_dotenv
import os

# Carregar .env.deploy
load_dotenv('.env.deploy')

# Usar variáveis
PROJECT_NAME = os.getenv('PROJECT_NAME', 'ipmonitor')
DOMAIN_BASE = os.getenv('DOMAIN_BASE', 'automacao.tce.go.gov.br')
PORT = int(os.getenv('PORT', '8000'))
```

### Em qualquer módulo
```python
from app.settings import PROJECT_NAME, DOMAIN_BASE, ROUTES_PREFIX

print(f"Projeto: {PROJECT_NAME}")
print(f"URL: https://{DOMAIN_BASE}{ROUTES_PREFIX}")
```

---

## 🐚 Uso em Bash

### Em scripts de deploy
```bash
#!/bin/bash

# Carregar configurações
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"

# Usar variáveis
echo "Deploy em: $ROOT_BACKEND"
sudo mkdir -p "$ROOT_FRONTEND"
git clone "$GIT_REPO_URL"
```

### Variáveis disponíveis automaticamente
Depois de `source config.sh`:
- `$PROJECT_NAME`
- `$SERVICE_NAME`
- `$ROOT_BACKEND`
- `$ROOT_FRONTEND`
- `$ROOT_DATA`
- `$ROOT_LOGS`
- `$GIT_REPO_URL`
- `$SERVICE_FILE`

---

## 🔧 Comandos Úteis

### Validar configuração
```bash
python tools/validate-config.py
python tools/validate-config.py --verbose  # Mais detalhes
```

### Sobrescrever configurações localmente (desenvolvimento)
```bash
# Copiar exemplo
cp .env.local.example .env.local

# Editar apenas as variáveis que deseja sobrescrever
nano .env.local

# Exemplo: alterar porta
echo "PORT=9000" >> .env.local

# .env.local sobrescreve .env.deploy sem modificá-lo
```

### Testar carregamento Python
```bash
python -c "from app.settings import *; print(f'Projeto: {PROJECT_NAME}')"
```

### Testar carregamento Bash
```bash
source scripts/config.sh && echo "Backend: $ROOT_BACKEND"
```

### Gerar arquivo .service
```bash
bash scripts/generate-service.sh
cat scripts/ipmonitor.service  # Ver resultado
```

---

## 📝 Exemplo: Alterar Domínio

### ❌ ANTES (múltiplos lugares)
```bash
# settings.py
DOMAIN_BASE = "automacao.tce.go.gov.br"

# deploy.sh
ROOT_FRONTEND=/var/www/automacao.tce.go.gov.br/$PROJECT_NAME

# index.html
const BASE_URL = "https://automacao.tce.go.gov.br/ipmonitor"
```

### ✅ AGORA (1 lugar)
```bash
# .env.deploy
DOMAIN_BASE=novo-dominio.tce.go.gov.br
```

Pronto! Tudo atualizado automaticamente.

---

## 🛠️ Tarefas Comuns

### Alterar porta
```bash
# .env.deploy
PORT=9000
```

### Alterar prefixo de rotas
```bash
# .env.deploy
ROUTES_PREFIX=/novo-prefixo
```

### Alterar diretório de dados
```bash
# .env.deploy
DATA_ROOT=/mnt/storage/dados
```

### Adicionar nova variável

1. **Adicionar em `.env.deploy`**:
```bash
NOVA_VARIAVEL=valor
```

2. **Usar em Python** (settings.py):
```python
NOVA_VARIAVEL = os.getenv('NOVA_VARIAVEL', 'default')
```

3. **Usar em Bash** (automático):
```bash
source scripts/config.sh
echo $NOVA_VARIAVEL
```

---

## ⚠️ Boas Práticas

### ✅ FAZER
- Sempre validar antes do deploy: `python tools/validate-config.py`
- Usar `.env.local` para configurações temporárias de desenvolvimento
- Manter `.env.deploy` com valores padrão de produção
- Documentar novas variáveis no `.env.deploy.template`
- Usar nomes descritivos: `DATABASE_URL` não `DB`

### ❌ NÃO FAZER
- Modificar `.env.deploy` para testes locais (use `.env.local`)
- Commitar `.env.local` no git (contém configurações pessoais)
- Hardcoding de valores em scripts
- Duplicar variáveis em múltiplos lugares
- Usar nomes genéricos: `VAR1`, `CONFIG`

---

## 🐛 Troubleshooting

### Erro: "Arquivo .env.deploy não encontrado"
```bash
# Copiar template
cp .env.deploy.template .env.deploy
```

### Erro: "Variável não definida"
```bash
# Validar configuração
python tools/validate-config.py

# Ver o que foi carregado
source scripts/config.sh
env | grep PROJECT
```

### Python não carrega .env
```bash
# Instalar dependência
pip install python-dotenv

# Verificar se arquivo existe
ls -la .env.deploy
```

### Bash não exporta variáveis
```bash
# Usar source, não bash
source scripts/config.sh  # ✅ Correto
bash scripts/config.sh    # ❌ Errado (cria subshell)
```

---

## 📚 Referências

- **12-factor App**: https://12factor.net/config
- **Python dotenv**: https://pypi.org/project/python-dotenv/
- **Bash source**: `man bash` (procurar "source")
- **envsubst**: `man envsubst`

---

## ✨ Dica Pro

Use o validador sempre antes do deploy:

```bash
# Criar alias no ~/.bashrc
alias validate-ip="cd ~/ip-monitor && python tools/validate-config.py"

# Usar
validate-ip
```

---

**Mantido por**: TCE-GO Manutenção Predial  
**Última atualização**: 14/11/2025
