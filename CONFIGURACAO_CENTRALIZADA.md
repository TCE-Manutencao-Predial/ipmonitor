# Sistema de Configuração Padronizada - IP Monitor

## 📋 Visão Geral

Este documento descreve o novo sistema de configuração centralizada do **IP Monitor**, criado para:

✅ **Centralizar** todas as variáveis globais em um único local  
✅ **Padronizar** nomenclaturas e estruturas de pastas  
✅ **Facilitar** manutenção e migração futura  
✅ **Manter** compatibilidade total com código existente  

**IMPORTANTE:** Esta é uma camada de configuração **não-invasiva**. O código atual continua funcionando normalmente.

## 📁 Estrutura de Arquivos

```
ip-monitor/
├── app/
│   ├── settings.py          ← 🆕 NOVO: Configurações centralizadas
│   ├── __init__.py          ← Mantido (sem alterações)
│   ├── routes.py            ← Mantido (sem alterações)
│   ├── config_manager.py    ← Mantido (sem alterações)
│   └── ...
├── scripts/
│   └── deploy.sh            ← Mantido (sem alterações)
├── config.py                ← Mantido (sem alterações)
└── makefile                 ← Mantido (sem alterações)
```

## 🎯 Objetivo

### Antes (Situação Atual)
- Variáveis espalhadas em múltiplos arquivos
- Hardcoding de URLs e caminhos
- Inconsistências entre ambientes
- Difícil manutenção

### Depois (Com settings.py)
- **Uma única fonte de verdade** para configurações
- Fácil localização de variáveis
- Preparado para migração futura
- Código atual **NÃO é afetado**

## 📊 Mapeamento de Variáveis

### Variáveis Centralizadas em `app/settings.py`

#### 1. Identificação do Projeto
```python
PROJECT_NAME = "ip-monitor"           # Nome canônico (kebab-case)
PROJECT_NAME_SERVICE = "ipmonitor"    # Nome usado atualmente
PROJECT_NAME_DISPLAY = "IP Monitor"   # Nome para exibição
```

#### 2. Rotas e URLs
```python
ROUTES_PREFIX = "/ipmonitor"          # Atual (mantido)
DOMAIN_BASE = "automacao.tce.go.gov.br"
BASE_URL_PRODUCTION = "https://automacao.tce.go.gov.br/ipmonitor"
```

#### 3. Caminhos de Diretórios
```python
# Produção (Linux)
BACKEND_ROOT = "/var/softwaresTCE"
PROJECT_BACKEND = "/var/softwaresTCE/ipmonitor"
PROJECT_DATA = "/var/softwaresTCE/dados/ipmonitor"
PROJECT_LOGS = "/var/softwaresTCE/logs/ipmonitor"

# Desenvolvimento (Windows/Mac)
# Automaticamente ajustado para usar caminhos relativos
```

#### 4. Arquivos de Dados
```python
APP_CONFIG_PATH = "{PROJECT_DATA}/app_config.json"
DEVICES_PATH = "{PROJECT_DATA}/ip_devices.json"
IPS_LIST_PATH = "{PROJECT_DATA}/ips_list.json"
```

#### 5. Git
```python
GIT_REPO_NAME = "ip-monitor"
GIT_REPO_OWNER = "TCE-Manutencao-Predial"
GIT_REPO_URL = "https://github.com/TCE-Manutencao-Predial/ip-monitor.git"
```

## 🔍 Onde Estão as Variáveis Atualmente

### Python (routes.py)
```python
# ATUAL (linha 16)
RAIZ = '/ipmonitor'

# DISPONÍVEL EM settings.py
from app.settings import ROUTES_PREFIX
```

### Shell Scripts (deploy.sh)
```bash
# ATUAL (linhas 10-17)
PROJECT_NAME="ipmonitor"
ROOT_FRONTEND=/var/www/automacao.tce.go.gov.br/$PROJECT_NAME
ROOT_BACKEND=/var/softwaresTCE/$PROJECT_NAME
ROOT_DATA=/var/softwaresTCE/dados/$PROJECT_NAME

# EQUIVALENTE EM settings.py (para referência)
# PROJECT_NAME_SERVICE = "ipmonitor"
# PROJECT_FRONTEND = "/var/www/automacao.tce.go.gov.br/ipmonitor"
# PROJECT_BACKEND = "/var/softwaresTCE/ipmonitor"
# PROJECT_DATA = "/var/softwaresTCE/dados/ipmonitor"
```

### JavaScript (index.js, config.js, devices.js)
```javascript
// ATUAL (múltiplos arquivos)
function getApiBaseUrl() {
    if (window.location.hostname.includes('tce.go.gov.br')) {
        return '/ipmonitor';
    } else {
        return '';
    }
}

// FUTURO: Pode ser injetado via template Jinja2
// {{ settings.ROUTES_PREFIX }}
```

### HTML Templates
```html
<!-- ATUAL (múltiplos templates) -->
<script>
    function getStaticUrl() {
        return path.includes('/ipmonitor/') ? '/ipmonitor/static/' : '/static/';
    }
</script>

<!-- FUTURO: Pode usar variáveis do settings.py -->
```

## 🚀 Como Usar (Migração Gradual Opcional)

### Opção 1: Continuar Como Está
**Nada muda!** O código atual continua funcionando normalmente.

### Opção 2: Usar settings.py em Novos Códigos
```python
# Em vez de hardcoding:
RAIZ = '/ipmonitor'

# Use o settings:
from app.settings import ROUTES_PREFIX
```

### Opção 3: Migração Gradual (Quando Decidir)
1. Importar settings nos módulos Python
2. Substituir hardcoded por variáveis do settings
3. Testar cada alteração isoladamente
4. Commit incremental

## 📝 Funções Utilitárias Disponíveis

```python
from app.settings import (
    ensure_directories,    # Cria diretórios necessários
    get_environment,       # Retorna 'production' ou 'development'
    get_routes_prefix,     # Retorna prefixo conforme ambiente
    get_api_base_url      # Retorna URL da API conforme ambiente
)

# Exemplo de uso
ensure_directories()  # Garante que pastas existem
env = get_environment()  # 'production' ou 'development'
prefix = get_routes_prefix()  # '/ipmonitor' ou ''
```

## ✅ Garantias de Segurança

### O que NÃO foi alterado:
- ✅ `app/__init__.py` - sem alterações
- ✅ `app/routes.py` - sem alterações  
- ✅ `app/config_manager.py` - sem alterações
- ✅ `scripts/deploy.sh` - sem alterações
- ✅ `makefile` - sem alterações
- ✅ Templates HTML - sem alterações
- ✅ Arquivos JavaScript - sem alterações

### O que foi criado:
- ✅ `app/settings.py` - arquivo NOVO (não afeta código existente)
- ✅ Esta documentação

## 🎓 Benefícios

1. **Documentação Viva**: `settings.py` documenta todas as configurações
2. **Fonte Única**: Fácil encontrar onde cada variável está definida
3. **Migração Segura**: Permite mudanças graduais sem riscos
4. **Padronização**: Base para padronizar outros submódulos
5. **Retrocompatível**: Código atual funciona sem modificações

## 📋 Próximos Passos (Opcional e Gradual)

Quando decidir migrar (SEM PRESSA):

### Fase 1: Validação (Atual)
- [x] Criar `settings.py`
- [x] Documentar variáveis
- [ ] Testar importação do settings
- [ ] Validar que nada quebrou

### Fase 2: Uso Pontual (Futuro)
- [ ] Importar settings em 1-2 arquivos
- [ ] Substituir hardcoded por variáveis
- [ ] Testar funcionamento
- [ ] Commit e validação

### Fase 3: Migração Completa (Futuro Distante)
- [ ] Migrar todos os arquivos Python
- [ ] Atualizar templates HTML/JS
- [ ] Atualizar scripts shell
- [ ] Documentação final

## 🔗 Relação com Outros Submódulos

Este mesmo padrão pode ser replicado para:
- `helpdesk-monitor`
- `analise-processos`
- `checklist-predial`
- Todos os outros submódulos

Cada um terá seu próprio `app/settings.py` com variáveis específicas.

## 📞 Suporte

Em caso de dúvidas ou problemas:
1. Verifique se `settings.py` está causando algum erro
2. Se sim, pode deletar temporariamente (não afeta o código)
3. Consulte esta documentação
4. Teste gradualmente

---

**Data:** 14 de novembro de 2025  
**Versão:** 1.0.0  
**Status:** Implementado (Não-invasivo)  
**Risco:** Nenhum (código atual não modificado)
