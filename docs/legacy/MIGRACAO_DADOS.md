# Migração de Dados para Diretório Centralizado

## Resumo da Implementação

O sistema IP Monitor foi atualizado para armazenar todos os arquivos de dados no próprio diretório do backend: `/var/softwaresTCE/ipmonitor/`

## Arquivos Modificados

### 1. `app/migration.py`
Módulo que define o diretório de dados centralizado:
- **Constante `DATA_DIR`**: `/var/softwaresTCE/ipmonitor/`
- **Função `get_data_file_path()`**: Retorna o caminho completo para arquivos de dados
- **Função `ensure_data_directory()`**: Garante que o diretório existe
- **Função `migrate_data_files()`**: Mantida para compatibilidade (não faz migração automática)

**Arquivos armazenados:**
- `app_config.json` - Configurações do sistema
- `ip_devices.json` - Dispositivos cadastrados
- `ips_list.json` - Lista de IPs (formato antigo, se existir)

### 2. `scripts/deploy.sh`
**Nova função `migrate_data_files()`**: Migra arquivos de dados durante o deploy
- Copia `app_config.json`, `ip_devices.json`, `ips_list.json` do diretório de desenvolvimento para o backend
- Só copia se o arquivo não existir no destino
- Registra todas as operações no log

**Fluxo do deploy:**
1. Atualizar projeto local
2. Deploy frontend
3. Deploy backend
4. **Migrar arquivos de dados** ← NOVO
5. Deploy serviço

### 3. `app/__init__.py`
Chama funções de migração na inicialização (para desenvolvimento local):
```python
from app.migration import migrate_data_files, ensure_data_directory

ensure_data_directory()
migrate_data_files()
```

### 4. `app/config_manager.py`
Usa o diretório centralizado:
```python
from app.migration import get_data_file_path

def __init__(self, config_file='app_config.json'):
    self.config_file = get_data_file_path(config_file)
```

### 5. `app/device_manager.py`
Usa o diretório centralizado:
```python
from app.migration import get_data_file_path

def __init__(self, devices_file='ip_devices.json'):
    self.devices_file = get_data_file_path(devices_file)
```

## Como Funciona

### Em Produção (via deploy.sh)

1. Execute `make deploy` ou `./scripts/deploy.sh`
2. O script de deploy:
   - Atualiza o código no servidor
   - Copia arquivos JSON do projeto local para `/var/softwaresTCE/ipmonitor/`
   - Registra as operações no log
3. O aplicativo inicia e usa os arquivos em `/var/softwaresTCE/ipmonitor/`

### Em Desenvolvimento Local

1. Execute `flask run`
2. Os arquivos JSON ficam no diretório do projeto
3. O sistema funciona normalmente

## Estrutura de Diretórios

```
/var/softwaresTCE/ipmonitor/
├── app/
│   ├── __init__.py
│   ├── migration.py
│   ├── config_manager.py
│   ├── device_manager.py
│   └── ...
├── app_config.json        ← Dados aqui
├── ip_devices.json        ← Dados aqui
├── ips_list.json          ← Dados aqui (se existir)
└── ...
```

## Logs do Deploy

Durante o deploy, você verá:

```
[Deploy] Verificando migração de arquivos de dados...
[Deploy] Migrando arquivo de dados: app_config.json
[Deploy] Migrando arquivo de dados: ip_devices.json
[Deploy] Arquivo não encontrado localmente: ips_list.json
[Deploy] Verificação de migração concluída.
```

## Benefícios

✅ **Simplicidade** - Dados no mesmo diretório do código
✅ **Deploy Seguro** - Migração controlada pelo script
✅ **Compatibilidade** - Funciona em dev e produção
✅ **Sem Conflitos** - Git ignora arquivos JSON de dados

## Observações

- Os arquivos JSON de dados **não são versionados** no Git (`.gitignore`)
- A migração via deploy.sh **não sobrescreve** arquivos existentes
- Em produção, os dados ficam em `/var/softwaresTCE/ipmonitor/`
- Em desenvolvimento, os dados ficam na raiz do projeto local
