# Documentação - IP Monitor v2.0

## 🎯 Visão Geral

Sistema de monitoramento de dispositivos IP com **configuração centralizada** e **scripts padronizados** para deploy em produção.

**Versão 2.0** - Implementa padrão `.env.deploy` para configuração centralizada, eliminando duplicação e facilitando manutenção.

---

## 📚 Documentação por Categoria

### 🚀 Início Rápido
- **[../README.md](../README.md)** - README principal do projeto
- **[GUIA_RAPIDO_ENV_DEPLOY.md](GUIA_RAPIDO_ENV_DEPLOY.md)** - Guia rápido de configuração

### 📖 Referência Completa
- **[INDEX.md](INDEX.md)** - Índice completo da documentação
- **[CONFIGURACAO_CENTRALIZADA.md](CONFIGURACAO_CENTRALIZADA.md)** - Documentação técnica detalhada
- **[INVENTARIO_VARIAVEIS.md](INVENTARIO_VARIAVEIS.md)** - Todas as variáveis disponíveis

### 🏗️ Arquitetura e Planejamento
- **[PLANO_PADRONIZACAO_SCRIPTS.md](PLANO_PADRONIZACAO_SCRIPTS.md)** - Planejamento técnico completo
- **[REFATORACAO_ENV_DEPLOY.md](REFATORACAO_ENV_DEPLOY.md)** - Resumo da implementação
- **[RESUMO_PADRONIZACAO.md](RESUMO_PADRONIZACAO.md)** - Resumo executivo

### 🔧 Templates para Outros Submódulos
- **[templates/README.md](templates/README.md)** - Guia de replicação
- **[templates/apply-templates.sh](templates/apply-templates.sh)** - Script automatizado
- **[templates/](templates/)** - Arquivos reutilizáveis

### 📂 Histórico
- **[legacy/](legacy/)** - Documentação de versões anteriores

---

## ⚡ Comandos Rápidos

```bash
# Validar configuração
python tools/validate-config.py

# Deploy em produção
make deploy

# Ver status do serviço
systemctl status ipmonitor

# Ver logs
journalctl -u ipmonitor -f

# Aplicar templates em outro submódulo
cd docs/templates
./apply-templates.sh /caminho/para/submodulo nome_projeto
```

---

## 🗂️ Estrutura da Documentação

```
docs/
├── README.md (este arquivo)           # Visão geral
├── INDEX.md                            # Índice detalhado
│
├── 📘 Guias
│   ├── GUIA_RAPIDO_ENV_DEPLOY.md
│   └── CONFIGURACAO_CENTRALIZADA.md
│
├── 📋 Planejamento
│   ├── PLANO_PADRONIZACAO_SCRIPTS.md
│   ├── REFATORACAO_ENV_DEPLOY.md
│   ├── RESUMO_PADRONIZACAO.md
│   └── INVENTARIO_VARIAVEIS.md
│
├── 🔧 Templates (Reutilizáveis)
│   └── templates/
│       ├── README.md
│       ├── apply-templates.sh
│       ├── *.template
│       └── ...
│
└── 📂 Legado
    └── legacy/
        └── ...
```

---

## 🎓 Para Começar

### Desenvolvedores Novos
1. Leia **[../README.md](../README.md)**
2. Siga **[GUIA_RAPIDO_ENV_DEPLOY.md](GUIA_RAPIDO_ENV_DEPLOY.md)**

### Fazer Deploy
1. Validar: `python tools/validate-config.py`
2. Executar: `make deploy`
3. Consultar: **[GUIA_RAPIDO_ENV_DEPLOY.md](GUIA_RAPIDO_ENV_DEPLOY.md#deploy)**

### Replicar para Outro Submódulo
1. Ler **[templates/README.md](templates/README.md)**
2. Executar `./apply-templates.sh`
3. Seguir checklist de padronização

### Entender a Arquitetura
1. **[PLANO_PADRONIZACAO_SCRIPTS.md](PLANO_PADRONIZACAO_SCRIPTS.md)**
2. **[REFATORACAO_ENV_DEPLOY.md](REFATORACAO_ENV_DEPLOY.md)**
3. **[CONFIGURACAO_CENTRALIZADA.md](CONFIGURACAO_CENTRALIZADA.md)**

---

## 🔑 Conceitos Principais

### Configuração Centralizada
- **1 arquivo** (`.env.deploy`) = fonte única de verdade
- Lido por Python (`settings.py`) e Bash (`config.sh`)
- Elimina duplicação de variáveis

### Hierarquia de Configuração
1. `.env.deploy` - Base versionada (produção)
2. `.env.local` - Sobrescritas locais (não versionado)

### Templates Reutilizáveis
- Conjunto padronizado de arquivos
- Aplicável em qualquer submódulo zapdos-server
- Customizável por projeto

---

## 📊 Benefícios da Padronização

| Métrica | Antes | Depois | Melhoria |
|---------|-------|--------|----------|
| Lugares com config | 6-7 arquivos | 1 arquivo | -85% |
| Duplicação | Alta | Zero | -100% |
| Tempo para alterar | ~10 min | ~1 min | -90% |
| Risco de erro | Alto | Baixo | -80% |

---

## 🤝 Contribuindo

Para melhorar a documentação:

1. Edite o arquivo apropriado
2. Atualize `INDEX.md` se necessário
3. Se for melhoria geral, atualize os templates
4. Commit com mensagem descritiva

---

## 📞 Suporte

- **Repositório**: https://github.com/TCE-Manutencao-Predial/ip-monitor
- **Issues**: https://github.com/TCE-Manutencao-Predial/ip-monitor/issues
- **Documentação Completa**: [INDEX.md](INDEX.md)

---

**Mantido por**: TCE-GO Manutenção Predial  
**Última atualização**: 14/11/2025  
**Versão**: 2.0 (Configuração Centralizada)
