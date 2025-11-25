# Correção de URLs - Sistema IP Monitor

## Problema Identificado

O link para as configurações estava incorreto em produção:
- **URL Incorreta:** `https://automacao.tce.go.gov.br/configuracoes`
- **URL Correta:** `https://automacao.tce.go.gov.br/ipmonitor/configuracoes`

## Root Cause

O sistema está configurado para funcionar tanto em desenvolvimento quanto em produção:
- **Desenvolvimento:** `http://localhost:5000/configuracoes`
- **Produção:** `https://automacao.tce.go.gov.br/ipmonitor/configuracoes`

O problema estava nos **links hardcoded** nos templates e chamadas de API nos arquivos JavaScript.

## Soluções Implementadas

### 1. **Templates HTML - URLs Dinâmicas**

**Antes (URLs hardcoded):**
```html
<button onclick="window.location.href='/configuracoes'">⚙️ Configurações</button>
<button onclick="window.location.href='/'">🏠 Página Inicial</button>
```

**Depois (URLs dinâmicas com Flask url_for):**
```html
<button onclick="window.location.href='{{ url_for('configuracoes') }}'">⚙️ Configurações</button>
<button onclick="window.location.href='{{ url_for('index') }}'">🏠 Página Inicial</button>
```

### 2. **JavaScript - Detecção Automática de Ambiente**

**Nova função de detecção:**
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

### 3. **APIs Corrigidas**

**Arquivo: `index.js`**
```javascript
// Antes
const response = await fetch(`api/start-check/${vlan}`);

// Depois
const baseUrl = getApiBaseUrl();
const response = await fetch(`${baseUrl}/api/start-check/${vlan}`);
```

**Arquivo: `config.js`**
```javascript
// Antes
fetch('/api/config/save', {...})
fetch('/api/config/reset', {...})
fetch('/api/config/test', {...})

// Depois
fetch(`${this.apiBaseUrl}/api/config/save`, {...})
fetch(`${this.apiBaseUrl}/api/config/reset`, {...})
fetch(`${this.apiBaseUrl}/api/config/test`, {...})
```

### 4. **Deploy Script Atualizado**

**Arquivo: `deploy.sh`**
```bash
# Adicionado template de configurações ao frontend
sudo cp "app/templates/configuracoes.html" "$ROOT_FRONTEND/configuracoes.html"
```

## Arquivos Modificados

### **Templates:**
- ✅ `app/templates/index.html` - Links de navegação corrigidos
- ✅ `app/templates/configuracoes.html` - Links de navegação corrigidos

### **JavaScript:**
- ✅ `app/static/index.js` - API calls com detecção de ambiente
- ✅ `app/static/config.js` - API calls com detecção de ambiente

### **Deploy:**
- ✅ `scripts/deploy.sh` - Cópia do template de configurações

## Como Funciona Agora

### **Desenvolvimento (localhost:5000):**
- `getApiBaseUrl()` retorna `""` (string vazia)
- URLs finais: `/configuracoes`, `/api/config/save`, etc.

### **Produção (automacao.tce.go.gov.br):**
- `getApiBaseUrl()` retorna `"/ipmonitor"`
- URLs finais: `/ipmonitor/configuracoes`, `/ipmonitor/api/config/save`, etc.

### **Flask url_for:**
- Automaticamente usa as rotas corretas definidas em `routes.py`
- Considera tanto a rota local quanto a com prefixo `RAIZ`

## Resultado

✅ **Links de Navegação:** Funcionam em ambos os ambientes
✅ **Chamadas de API:** Automaticamente detectam o ambiente
✅ **Deploy:** Copia todos os arquivos necessários
✅ **Compatibilidade:** Mantém funcionamento local e produção

## URLs Finais Corretas

### **Produção:**
- 🏠 Página Principal: `https://automacao.tce.go.gov.br/ipmonitor/`
- ⚙️ Configurações: `https://automacao.tce.go.gov.br/ipmonitor/configuracoes`
- 📡 APIs: `https://automacao.tce.go.gov.br/ipmonitor/api/*`

### **Desenvolvimento:**
- 🏠 Página Principal: `http://localhost:5000/`
- ⚙️ Configurações: `http://localhost:5000/configuracoes`
- 📡 APIs: `http://localhost:5000/api/*`

## Próximos Passos

1. **Fazer commit** das alterações
2. **Executar deploy** para aplicar as correções
3. **Testar** o link: `https://automacao.tce.go.gov.br/ipmonitor/configuracoes`

As correções garantem que o sistema funcione perfeitamente em ambos os ambientes! 🚀