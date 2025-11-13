
# Monitor IP

Sistema de monitoramento de dispositivos IP por VLAN com gerenciamento de configurações.

## Estrutura de Dados

O sistema armazena todos os dados em um diretório separado do código:

**Código:** `/var/softwaresTCE/ipmonitor/`  
**Dados:** `/var/softwaresTCE/dados/ipmonitor/`

**Arquivos de dados:**
- `app_config.json` - Configurações do sistema
- `ip_devices.json` - Dispositivos cadastrados por VLAN

A migração é feita automaticamente pelo script de deploy.

## Desenvolvimento Local

Para rodar essa aplicação Flask primeiro criar uma venv:

```bash
python -m venv .venv
```
Depois ativar a venv:

```bash
.venv\Scripts\activate
```

Depois instalar as dependências:

```bash
pip install -r requirements.txt 
```

Por fim rodar o Flask:

```bash
Flask run
```

## Deploy em Produção

O script de deploy cuida automaticamente da migração de arquivos de dados:

```bash
make deploy
```

O sistema usará:
- Código em `/var/softwaresTCE/ipmonitor/`
- Dados em `/var/softwaresTCE/dados/ipmonitor/`

:D
