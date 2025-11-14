# Inventário Completo de Variáveis - IP Monitor

## 📊 Mapeamento Detalhado de Todas as Variáveis

Este documento mapeia **TODAS** as variáveis, URLs e configurações encontradas no submódulo `ip-monitor`.

---

## 1. Python - `app/routes.py`

### Linha 16
```python
RAIZ = '/ipmonitor'
```
**Uso**: Prefixo de todas as rotas da API  
**Centralizado em**: `settings.ROUTES_PREFIX`  
**Ocorrências**: 22 vezes no arquivo

### Exemplos de uso:
```python
@app.route(RAIZ + '/')                              # Linha 45
@app.route(RAIZ + '/configuracoes')                 # Linha 51
@app.route(RAIZ + '/dispositivos')                  # Linha 57
@app.route(RAIZ + '/api/ip-status')                 # Linha 63
@app.route(RAIZ + '/api/start-check/<vlan>')        # Linha 69
@app.route(RAIZ + '/api/config/save')               # Linha 95
```

---

## 2. Shell Scripts - `scripts/deploy.sh`

### Linhas 10-20
```bash
PROJECT_NAME="ipmonitor"
SERVICE_NAME="ipmonitor.service"

ROOT_FRONTEND=/var/www/automacao.tce.go.gov.br/$PROJECT_NAME
ROOT_SOFTWARES=/var/softwaresTCE
ROOT_BACKEND="$ROOT_SOFTWARES/$PROJECT_NAME"
ROOT_DATA="$ROOT_SOFTWARES/dados/$PROJECT_NAME"

GIT_REPO_NAME="ip-monitor"
GIT_REPO_LINK="https://github.com/TCE-Manutencao-Predial/$GIT_REPO_NAME.git"
```

**Mapeamento para settings.py**:
```python
PROJECT_NAME_SERVICE = "ipmonitor"
SERVICE_NAME = "ipmonitor"
PROJECT_FRONTEND = "/var/www/automacao.tce.go.gov.br/ipmonitor"
BACKEND_ROOT = "/var/softwaresTCE"
PROJECT_BACKEND = "/var/softwaresTCE/ipmonitor"
PROJECT_DATA = "/var/softwaresTCE/dados/ipmonitor"
GIT_REPO_NAME = "ip-monitor"
GIT_REPO_URL = "https://github.com/TCE-Manutencao-Predial/ip-monitor.git"
```

---

## 3. JavaScript - `app/static/index.js`

### Linhas 1-8
```javascript
// Função para obter a base URL da API dependendo do ambiente
function getApiBaseUrl() {
    // Verifica se estamos em produção (domínio tce.go.gov.br) ou desenvolvimento
    if (window.location.hostname.includes('tce.go.gov.br')) {
        return '/ipmonitor';
    } else {
        return '';
    }
}
```

**Hardcoded**:
- String: `/ipmonitor`
- String: `tce.go.gov.br`

**Centralizado em**:
```python
ROUTES_PREFIX = "/ipmonitor"
DOMAIN_BASE = "automacao.tce.go.gov.br"
```

**Ocorrências no arquivo**: `getApiBaseUrl()` é chamada 15+ vezes

---

## 4. JavaScript - `app/static/config.js`

### Linhas 1-8 (Idêntico ao index.js)
```javascript
function getApiBaseUrl() {
    if (window.location.hostname.includes('tce.go.gov.br')) {
        return '/ipmonitor';
    } else {
        return '';
    }
}
```

**Uso**: 10+ chamadas no arquivo

---

## 5. JavaScript - `app/static/devices.js`

### Linhas 19-25
```javascript
getApiBaseUrl() {
    const path = window.location.pathname;
    return path.includes('/ipmonitor/') ? '/ipmonitor/api' : '/api';
}
```

**Hardcoded**:
- String: `/ipmonitor/`
- String: `/ipmonitor/api`

**Centralizado em**:
```python
ROUTES_PREFIX = "/ipmonitor"
API_BASE_URL_PRODUCTION = "https://automacao.tce.go.gov.br/ipmonitor/api"
```

---

## 6. HTML Template - `app/templates/index.html`

### Linhas 10-14
```javascript
function getStaticUrl() {
    const path = window.location.pathname;
    return path.includes('/ipmonitor/') ? '/ipmonitor/static/' : '/static/';
}
```

### Linhas 27-31
```javascript
function getBaseUrl() {
    const path = window.location.pathname;
    return path.includes('/ipmonitor/') ? '/ipmonitor/' : '/';
}
```

**Hardcoded**: `/ipmonitor/`, `/ipmonitor/static/`

---

## 7. HTML Template - `app/templates/dispositivos.html`

### Linha 215-216
```javascript
const isProduction = hostname.includes('automacao.tce.go.gov.br');
return isProduction ? '/ipmonitor' : '';
```

**Hardcoded**:
- String: `automacao.tce.go.gov.br`
- String: `/ipmonitor`

**Centralizado em**:
```python
DOMAIN_BASE = "automacao.tce.go.gov.br"
ROUTES_PREFIX = "/ipmonitor"
```

---

## 8. HTML Template - `app/templates/configuracoes.html`

### Linha 333-334
```javascript
const isProduction = hostname.includes('automacao.tce.go.gov.br');
return isProduction ? '/ipmonitor' : '';
```

**Idêntico ao dispositivos.html**

---

## 9. Makefile

### Linhas 1-42
```makefile
# Sem variáveis de projeto explícitas
# Usa apenas SERVICE_NAME para systemd

SERVICE_NAME=ipmonitor
```

**Centralizado em**:
```python
SERVICE_NAME = "ipmonitor"
```

---

## 10. Python - `app/config_manager.py`

### Linha 5
```python
from app.migration import get_data_file_path
```

**Usa função utilitária** que já gerencia os caminhos corretamente.

### Linha 12
```python
config_file = get_data_file_path(config_file)
```

**Não requer alteração** - já usa abstração de caminho.

---

## 📋 Resumo de Ocorrências

| String Hardcoded | Arquivos | Ocorrências Totais | Centralizado em settings.py |
|------------------|----------|--------------------|-----------------------------|
| `/ipmonitor` | 7 | 50+ | `ROUTES_PREFIX` |
| `automacao.tce.go.gov.br` | 2 | 4 | `DOMAIN_BASE` |
| `tce.go.gov.br` | 2 | 2 | `DOMAIN_BASE` |
| `/var/softwaresTCE` | 1 | 3 | `BACKEND_ROOT` |
| `ipmonitor` (nome) | 3 | 10+ | `PROJECT_NAME_SERVICE` |
| `ip-monitor` (repo) | 1 | 1 | `GIT_REPO_NAME` |

---

## 🎯 Arquivos com URLs Hardcoded

### Alta Prioridade (Mais Ocorrências)
1. ✅ `app/static/index.js` - 15+ ocorrências
2. ✅ `app/static/config.js` - 10+ ocorrências
3. ✅ `app/routes.py` - 22 ocorrências

### Média Prioridade
4. ✅ `app/static/devices.js` - 5+ ocorrências
5. ✅ `app/templates/index.html` - 4 ocorrências
6. ✅ `app/templates/dispositivos.html` - 2 ocorrências
7. ✅ `app/templates/configuracoes.html` - 2 ocorrências

### Baixa Prioridade
8. ✅ `scripts/deploy.sh` - 6 variáveis
9. ✅ `makefile` - 1 variável

---

## 🔄 Migração Futura (Quando Decidir)

### Opção A: Injeção via Jinja2 nos Templates
```html
<!-- Em vez de hardcoded: -->
<script>
    const BASE_URL = '/ipmonitor';
</script>

<!-- Usar variável do Flask: -->
<script>
    const BASE_URL = '{{ settings.ROUTES_PREFIX }}';
</script>
```

### Opção B: Arquivo config.js Gerado
```javascript
// Gerar arquivo config.js dinamicamente via Flask:
// /static/config.js (gerado)
const APP_CONFIG = {
    routesPrefix: '{{ settings.ROUTES_PREFIX }}',
    domainBase: '{{ settings.DOMAIN_BASE }}',
    apiBaseUrl: '{{ settings.API_BASE_URL_PRODUCTION }}'
};
```

### Opção C: Importação Direta em Python
```python
# Em routes.py:
from app.settings import ROUTES_PREFIX

# Em vez de:
RAIZ = '/ipmonitor'

# Usar:
RAIZ = ROUTES_PREFIX
```

---

## ✅ Status Atual

- ✅ Todas as variáveis mapeadas
- ✅ Todas as URLs identificadas
- ✅ Centralização em settings.py concluída
- ✅ Documentação completa
- ✅ Zero alterações no código (mantém compatibilidade)

---

**Data**: 14 de novembro de 2025  
**Submódulo**: ip-monitor  
**Total de Variáveis Mapeadas**: 50+  
**Arquivos Analisados**: 10  
**Status**: ✅ Inventário Completo
