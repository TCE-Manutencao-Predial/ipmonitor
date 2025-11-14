
# IP Monitor

Sistema de monitoramento de dispositivos IP por VLAN com gerenciamento de configurações.

## ✨ Novidade: Configuração Centralizada

A partir da **versão 2.0**, todas as configurações são gerenciadas via arquivo `.env.deploy`:

- ✅ **1 lugar** para alterar configurações
- ✅ **Zero duplicação** entre Python e Bash
- ✅ **Validação automática** antes do deploy
- ✅ **Padrão da indústria** (12-factor app)

**Documentação completa**: [`docs/GUIA_RAPIDO_ENV_DEPLOY.md`](docs/GUIA_RAPIDO_ENV_DEPLOY.md)

---

## 📋 Quick Start

### Validar Configuração
```bash
python tools/validate-config.py
```

### Desenvolvimento Local
```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar (Windows)
.venv\Scripts\activate

# Ativar (Linux)
source .venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Rodar aplicação
flask run
# ou
make run
```

### Deploy em Produção
```bash
make deploy
```

---

## 📁 Estrutura de Dados

O sistema separa código de dados:

| Tipo | Caminho Produção | Caminho Desenvolvimento |
|------|------------------|-------------------------|
| **Código (Backend)** | `/var/softwaresTCE/ipmonitor/` | `./` (raiz do projeto) |
| **Código (Frontend)** | `/var/www/automacao.tce.go.gov.br/ipmonitor/` | `./app/templates/` |
| **Dados** | `/var/softwaresTCE/dados/ipmonitor/` | `./data/` |
| **Logs** | `/var/softwaresTCE/logs/ipmonitor/` | `./logs/` |

### Arquivos de Dados
- `app_config.json` - Configurações do sistema (VLANs, intervalos de ping, etc.)
- `ip_devices.json` - Dispositivos cadastrados por VLAN
- `ips_list.json` - Lista de IPs para monitoramento

**Nota**: A migração de dados é feita automaticamente pelo script de deploy.

---

## ⚙️ Configuração

### Arquivo Principal: `.env.deploy`

```bash
# Copiar template (primeira vez)
cp .env.deploy.template .env.deploy

# Editar se necessário
nano .env.deploy

# Validar
python tools/validate-config.py
```

### Principais Configurações

```bash
# Identificação
PROJECT_NAME=ipmonitor
SERVICE_NAME=ipmonitor

# Rede
DOMAIN_BASE=automacao.tce.go.gov.br
ROUTES_PREFIX=/ipmonitor
PORT=8000

# Caminhos (Linux/Produção)
BACKEND_ROOT=/var/softwaresTCE
DATA_ROOT=/var/softwaresTCE/dados
LOGS_ROOT=/var/softwaresTCE/logs
```

**Mais detalhes**: [`docs/GUIA_RAPIDO_ENV_DEPLOY.md`](docs/GUIA_RAPIDO_ENV_DEPLOY.md)

---

## 🚀 Deploy

### Validar antes do deploy
```bash
python tools/validate-config.py
```

### Executar deploy
```bash
make deploy
```

O deploy executará automaticamente:
1. ✅ Atualização do código (git pull)
2. ✅ Instalação do frontend em `/var/www/`
3. ✅ Instalação do backend em `/var/softwaresTCE/`
4. ✅ Migração de dados para `/var/softwaresTCE/dados/`
5. ✅ Geração do arquivo `.service` do systemd
6. ✅ Configuração e reinício do serviço

### Verificar status
```bash
# Status do serviço
sudo systemctl status ipmonitor

# Logs em tempo real
journalctl -u ipmonitor -f

# Última execução
journalctl -u ipmonitor -n 50
```

---

## 📚 Documentação

| Documento | Descrição |
|-----------|-----------|
| [GUIA_RAPIDO_ENV_DEPLOY.md](docs/GUIA_RAPIDO_ENV_DEPLOY.md) | Guia rápido de configuração |
| [REFATORACAO_ENV_DEPLOY.md](docs/REFATORACAO_ENV_DEPLOY.md) | Detalhes da implementação |
| [PLANO_PADRONIZACAO_SCRIPTS.md](docs/PLANO_PADRONIZACAO_SCRIPTS.md) | Planejamento técnico |
| [CONFIGURACAO_CENTRALIZADA.md](docs/CONFIGURACAO_CENTRALIZADA.md) | Documentação completa |

---

## 🛠️ Comandos Úteis

### Desenvolvimento
```bash
make setup          # Instalar dependências
make run            # Rodar aplicação
make test           # Executar testes (se houver)
```

### Produção
```bash
make deploy         # Deploy completo
make service-start  # Iniciar serviço
make service-stop   # Parar serviço
make service-restart # Reiniciar serviço
make service-status # Status do serviço
```

### Manutenção
```bash
# Validar configuração
python tools/validate-config.py

# Gerar arquivo .service
bash scripts/generate-service.sh

# Verificar logs
journalctl -u ipmonitor -f
```

---

## 🔧 Troubleshooting

### Serviço não inicia
```bash
# Ver logs de erro
journalctl -u ipmonitor -n 100

# Verificar arquivo .service
cat /usr/lib/systemd/system/ipmonitor.service

# Recarregar daemon
sudo systemctl daemon-reload
sudo systemctl restart ipmonitor
```

### Configuração inválida
```bash
# Validar
python tools/validate-config.py

# Verificar se .env.deploy existe
ls -la .env.deploy

# Comparar com template
diff .env.deploy .env.deploy.template
```

### Dados não aparecem
```bash
# Verificar diretório de dados
ls -la /var/softwaresTCE/dados/ipmonitor/

# Verificar permissões
sudo chown -R $(whoami) /var/softwaresTCE/dados/ipmonitor/
```

---

## 🏗️ Arquitetura

```
ip-monitor/
├── .env.deploy              # Configuração principal (não versionado)
├── .env.deploy.template     # Template de configuração
│
├── app/                     # Código da aplicação
│   ├── __init__.py         # Inicialização Flask
│   ├── settings.py         # Configurações (lê .env.deploy)
│   ├── routes.py           # Rotas da API
│   ├── models/             # Modelos de dados
│   ├── static/             # CSS, JS, imagens
│   └── templates/          # HTML (Jinja2)
│
├── scripts/                 # Scripts de deploy/manutenção
│   ├── config.sh           # Carrega .env.deploy
│   ├── deploy.sh           # Deploy em produção
│   ├── undeploy.sh         # Remove instalação
│   ├── run.sh              # Executa aplicação
│   ├── generate-service.sh # Gera arquivo systemd
│   └── *.service.template  # Template systemd
│
├── tools/                   # Ferramentas auxiliares
│   └── validate-config.py  # Valida configuração
│
├── docs/                    # Documentação
│   └── *.md                # Guias e planejamento
│
└── data/                    # Dados (desenvolvimento)
    ├── app_config.json     # Configurações da aplicação
    ├── ip_devices.json     # Dispositivos cadastrados
    └── ips_list.json       # Lista de IPs
```

---

## 📝 Licença

Tribunal de Contas do Estado de Goiás - TCE-GO  
Diretoria de Tecnologia da Informação  
Gerência de Manutenção Predial

---

## 👥 Contato

**Repositório**: https://github.com/TCE-Manutencao-Predial/ip-monitor  
**Documentação**: [docs/](docs/)  
**Issues**: https://github.com/TCE-Manutencao-Predial/ip-monitor/issues
