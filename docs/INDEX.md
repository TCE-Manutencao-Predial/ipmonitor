# Índice da Documentação - IP Monitor

## 📚 Documentação Principal

### 🚀 Quick Start
- **[README.md](../README.md)** - Início rápido e visão geral
- **[GUIA_RAPIDO_ENV_DEPLOY.md](GUIA_RAPIDO_ENV_DEPLOY.md)** - Guia rápido de configuração centralizada

### 📋 Planejamento e Arquitetura
- **[PLANO_PADRONIZACAO_SCRIPTS.md](PLANO_PADRONIZACAO_SCRIPTS.md)** - Planejamento completo da padronização de scripts
- **[REFATORACAO_ENV_DEPLOY.md](REFATORACAO_ENV_DEPLOY.md)** - Resumo da implementação da configuração centralizada
- **[CONFIGURACAO_CENTRALIZADA.md](CONFIGURACAO_CENTRALIZADA.md)** - Documentação técnica detalhada
- **[INVENTARIO_VARIAVEIS.md](INVENTARIO_VARIAVEIS.md)** - Inventário completo de variáveis
- **[RESUMO_PADRONIZACAO.md](RESUMO_PADRONIZACAO.md)** - Resumo executivo da padronização

### 🔧 Templates Reutilizáveis
- **[templates/README.md](templates/README.md)** - Guia de uso dos templates para outros submódulos
- **[templates/](templates/)** - Arquivos template para replicação

### 📂 Documentação Legada
- **[legacy/](legacy/)** - Documentação de versões anteriores e funcionalidades específicas

---

## 🎯 Por Onde Começar?

### Sou Novo no Projeto
1. Leia o **[README.md](../README.md)**
2. Siga o **[GUIA_RAPIDO_ENV_DEPLOY.md](GUIA_RAPIDO_ENV_DEPLOY.md)**

### Vou Fazer Deploy
1. Valide: `python tools/validate-config.py`
2. Leia o **[GUIA_RAPIDO_ENV_DEPLOY.md](GUIA_RAPIDO_ENV_DEPLOY.md)** seção "Deploy"
3. Execute: `make deploy`

### Vou Replicar para Outro Submódulo
1. Leia **[templates/README.md](templates/README.md)**
2. Use a checklist de padronização
3. Consulte **[PLANO_PADRONIZACAO_SCRIPTS.md](PLANO_PADRONIZACAO_SCRIPTS.md)** para detalhes técnicos

### Preciso Entender a Arquitetura
1. **[PLANO_PADRONIZACAO_SCRIPTS.md](PLANO_PADRONIZACAO_SCRIPTS.md)** - Decisões técnicas
2. **[CONFIGURACAO_CENTRALIZADA.md](CONFIGURACAO_CENTRALIZADA.md)** - Implementação
3. **[INVENTARIO_VARIAVEIS.md](INVENTARIO_VARIAVEIS.md)** - Variáveis disponíveis

---

## 📊 Organização dos Documentos

```
docs/
├── INDEX.md (este arquivo)           # Índice principal
│
├── 📘 Guias de Uso
│   ├── GUIA_RAPIDO_ENV_DEPLOY.md    # Referência rápida
│   └── CONFIGURACAO_CENTRALIZADA.md  # Guia completo
│
├── 📋 Planejamento
│   ├── PLANO_PADRONIZACAO_SCRIPTS.md
│   ├── REFATORACAO_ENV_DEPLOY.md
│   ├── RESUMO_PADRONIZACAO.md
│   └── INVENTARIO_VARIAVEIS.md
│
├── 🔧 Templates
│   └── templates/
│       ├── README.md                 # Guia de replicação
│       ├── *.template                # Arquivos reutilizáveis
│       └── ...
│
└── 📂 Legado
    └── legacy/
        ├── DEPLOY_FIX.md
        ├── MIGRACAO_DADOS.md
        └── ...
```

---

## 🔍 Índice por Tópico

### Configuração
- Configuração centralizada: [GUIA_RAPIDO_ENV_DEPLOY.md](GUIA_RAPIDO_ENV_DEPLOY.md)
- Variáveis disponíveis: [INVENTARIO_VARIAVEIS.md](INVENTARIO_VARIAVEIS.md)
- Hierarquia .env: [GUIA_RAPIDO_ENV_DEPLOY.md](GUIA_RAPIDO_ENV_DEPLOY.md#arquivos-principais)

### Deploy
- Scripts de deploy: [PLANO_PADRONIZACAO_SCRIPTS.md](PLANO_PADRONIZACAO_SCRIPTS.md)
- Processo de deploy: [GUIA_RAPIDO_ENV_DEPLOY.md](GUIA_RAPIDO_ENV_DEPLOY.md#deploy)
- Troubleshooting: [README.md](../README.md#troubleshooting)

### Desenvolvimento
- Setup local: [README.md](../README.md#desenvolvimento-local)
- Sobrescritas locais: [GUIA_RAPIDO_ENV_DEPLOY.md](GUIA_RAPIDO_ENV_DEPLOY.md#comandos-úteis)
- Validação: `python tools/validate-config.py`

### Replicação
- Templates: [templates/README.md](templates/README.md)
- Checklist: [templates/README.md](templates/README.md#checklist-de-padronização)
- Customização: [templates/README.md](templates/README.md#customizações-comuns)

---

## 📝 Glossário

| Termo | Descrição |
|-------|-----------|
| `.env.deploy` | Arquivo de configuração base (versionado) |
| `.env.local` | Sobrescritas locais (não versionado) |
| `config.sh` | Script que carrega configurações para bash |
| `settings.py` | Módulo Python que carrega configurações |
| `envsubst` | Ferramenta bash para substituição de variáveis |
| Submódulo | Microserviço dentro do zapdos-server |

---

## 🤝 Contribuições

Para adicionar ou atualizar documentação:

1. Edite o arquivo apropriado
2. Atualize este INDEX.md se necessário
3. Commit com mensagem descritiva
4. Se for melhoria geral, atualize os templates

---

**Mantido por**: TCE-GO Manutenção Predial  
**Última atualização**: 14/11/2025  
**Versão**: 2.0
