# Deploy Script - Correções para Conflitos Git

## Problema Resolvido

O erro estava ocorrendo porque o script de deploy tentava fazer `git pull` quando havia alterações locais não commitadas, causando conflitos de merge:

```
error: Your local changes to the following files would be overwritten by merge:
	scripts/deploy.sh
Please commit your changes or stash them before you merge.
Aborting
```

## Soluções Implementadas

### 1. **Atualização Forçada do Projeto Local**

**Antes:**
```bash
atualizar_projeto_local() {
    echo "[Deploy] Verificando atualizações do projeto..."
    git pull
}
```

**Depois:**
```bash
atualizar_projeto_local() {
    echo "[Deploy] Verificando atualizações do projeto no repositório git..."
    echo "[Deploy] Descartando alterações locais para evitar conflitos..."
    
    # Verificar e mudar para a branch main se necessário
    current_branch=$(git branch --show-current)
    if [ "$current_branch" != "main" ]; then
        echo "[Deploy] Mudando para a branch main..."
        git checkout main
    fi
    
    # Descartar todas as alterações locais não commitadas
    git reset --hard HEAD
    
    # Limpar arquivos não rastreados
    git clean -fd
    
    # Atualizar com a versão remota
    echo "[Deploy] Fazendo pull da versão remota..."
    git pull origin main
    
    echo "[Deploy] Projeto atualizado com sucesso!"
}
```

### 2. **Atualização Forçada do Backend**

**Antes:**
```bash
cd $ROOT_BACKEND
git pull
cd $dir_atual
```

**Depois:**
```bash
cd $ROOT_BACKEND

# Verificar e mudar para a branch main se necessário
backend_branch=$(git branch --show-current)
if [ "$backend_branch" != "main" ]; then
    echo "[Deploy] Mudando backend para a branch main..."
    git checkout main
fi

# Descartar alterações locais no backend também
echo "[Deploy] Descartando alterações locais no backend..."
git reset --hard HEAD
git clean -fd
git pull origin main

cd $dir_atual
```

## Comandos Git Utilizados

### `git reset --hard HEAD`
- **Função:** Descarta todas as alterações não commitadas
- **Impacto:** Remove modificações em arquivos rastreados
- **Seguro:** Sim, pois o deploy só deve usar a versão remota

### `git clean -fd`
- **Função:** Remove arquivos e diretórios não rastreados
- **Parâmetros:** 
  - `-f`: Force (forçar)
  - `-d`: Directories (incluir diretórios)
- **Seguro:** Sim, remove apenas arquivos não versionados

### `git checkout main`
- **Função:** Garante que estamos na branch correta
- **Necessário:** Caso o repositório esteja em outra branch

### `git pull origin main`
- **Função:** Atualiza com a versão remota da branch main
- **Específico:** Puxa especificamente da origin/main

## Benefícios das Alterações

### ✅ **Resolução de Conflitos**
- Elimina erros de merge durante o deploy
- Garante que sempre usa a versão mais recente do repositório

### ✅ **Deploy Confiável**
- Processo determinístico
- Não depende do estado local do repositório

### ✅ **Limpeza Automática**
- Remove arquivos temporários e alterações não desejadas
- Ambiente limpo para cada deploy

### ✅ **Mensagens Informativas**
- Logs claros sobre o que está acontecendo
- Facilita debugging se necessário

## Comportamento Esperado

Agora o deploy irá:

1. **Verificar a branch atual** e mudar para `main` se necessário
2. **Descartar todas as alterações locais** sem perguntar
3. **Limpar arquivos não rastreados** automaticamente
4. **Fazer pull da versão remota** sem conflitos
5. **Repetir o processo no backend** de produção

## Segurança

⚠️ **IMPORTANTE:** Este script agora **descarta alterações locais permanentemente**. 

- ✅ **Seguro para deploy:** O objetivo é usar apenas a versão remota
- ✅ **Automático:** Não requer intervenção manual
- ⚠️ **Destrutivo:** Alterações locais não commitadas serão perdidas

## Execução

O script pode ser executado normalmente:

```bash
# Via makefile
make deploy

# Ou diretamente
./scripts/deploy.sh
```

Agora o deploy funcionará sem erros de conflitos git! 🚀