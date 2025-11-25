# Templates de Padronização - Zapdos Server

Este diretório contém templates reutilizáveis para padronização de todos os submódulos do zapdos-server.

## 📁 Estrutura

```
templates/
├── README.md                    # Este arquivo
├── env.deploy.template          # Template .env.deploy genérico
├── config.sh.template           # Template scripts/config.sh
├── deploy.sh.template           # Template scripts/deploy.sh
├── undeploy.sh.template         # Template scripts/undeploy.sh
├── run.sh.template              # Template scripts/run.sh
├── service.template             # Template systemd .service
├── generate-service.sh.template # Template gerador de .service
├── validate-config.py.template  # Template validador Python
└── gitignore.template           # Template .gitignore
```

## 🎯 Como Usar

### Para Aplicar em um Novo Submódulo

1. **Copiar templates**:
```bash
cd /caminho/para/submodulo
mkdir -p scripts tools docs

# Copiar e renomear templates
cp /caminho/templates/env.deploy.template .env.deploy.template
cp /caminho/templates/env.deploy.template .env.deploy
cp /caminho/templates/config.sh.template scripts/config.sh
cp /caminho/templates/deploy.sh.template scripts/deploy.sh
# ... etc
```

2. **Personalizar variáveis** em `.env.deploy`:
```bash
# Substituir valores específicos do submódulo
PROJECT_NAME=nome-do-projeto
SERVICE_NAME=nomedoprojeto
ROUTES_PREFIX=/nomedoprojeto
PORT=8001  # Porta única
```

3. **Ajustar scripts** se necessário:
- Funções específicas de deploy
- Dependências especiais
- Estrutura de pastas diferente

4. **Validar**:
```bash
python tools/validate-config.py
```

## 🔄 Variáveis a Personalizar

Em **cada novo submódulo**, altere:

| Variável | Exemplo ip-monitor | Seu Submódulo |
|----------|-------------------|---------------|
| `PROJECT_NAME` | `ipmonitor` | `seuservico` |
| `PROJECT_NAME_DISPLAY` | `"IP Monitor"` | `"Seu Serviço"` |
| `PROJECT_NAME_GIT` | `ip-monitor` | `seu-servico` |
| `SERVICE_NAME` | `ipmonitor` | `seuservico` |
| `ROUTES_PREFIX` | `/ipmonitor` | `/seuservico` |
| `PORT` | `8000` | `8001` (única) |
| `GIT_REPO_NAME` | `ip-monitor` | `seu-servico` |

## 📝 Checklist de Padronização

- [ ] Copiar `.env.deploy.template` e `.env.deploy`
- [ ] Personalizar variáveis no `.env.deploy`
- [ ] Copiar `scripts/config.sh`
- [ ] Copiar `scripts/deploy.sh`
- [ ] Copiar `scripts/undeploy.sh`
- [ ] Copiar `scripts/run.sh`
- [ ] Copiar `scripts/generate-service.sh`
- [ ] Criar `scripts/<service>.service.template`
- [ ] Copiar `tools/validate-config.py`
- [ ] Atualizar `.gitignore`
- [ ] Atualizar `app/settings.py` para ler `.env.deploy`
- [ ] Adicionar `python-dotenv` ao `requirements.txt`
- [ ] Atualizar `README.md`
- [ ] Testar: `python tools/validate-config.py`
- [ ] Testar deploy: `make deploy` (em ambiente de testes)

## 🎨 Customizações Comuns

### Adicionar Variáveis Específicas

Em `.env.deploy`:
```bash
# Variáveis padrão (não mexer)
PROJECT_NAME=meuservico
...

# Variáveis específicas deste submódulo
DATABASE_URL=postgresql://...
REDIS_HOST=localhost
CUSTOM_PATH=/var/data/custom
```

### Funções Adicionais no Deploy

Em `scripts/deploy.sh`:
```bash
# Após as funções padrão
deploy_database() {
    echo -e "${GREEN}[DEPLOY]${NC} Configurando banco de dados..."
    # Lógica específica
}

# Adicionar ao main()
main() {
    ...
    deploy_backend
    deploy_database  # ← Nova função
    deploy_servico
    ...
}
```

## 📚 Documentação de Referência

- **ip-monitor** - Submódulo de referência (primeiro implementado)
  - `ip-monitor/docs/GUIA_RAPIDO_ENV_DEPLOY.md`
  - `ip-monitor/docs/PLANO_PADRONIZACAO_SCRIPTS.md`
  - `ip-monitor/docs/REFATORACAO_ENV_DEPLOY.md`

## 🤝 Contribuindo

Ao melhorar a padronização em um submódulo:

1. Teste as melhorias no submódulo
2. Atualize os templates neste diretório
3. Documente as mudanças
4. Compartilhe com a equipe

## ⚠️ Importante

- **Não commit** `.env.local` (configurações pessoais)
- **Sempre versione** `.env.deploy` (valores padrão de produção)
- **Valide antes do deploy** com `validate-config.py`
- **Mantenha portas únicas** para cada submódulo

---

**Mantido por**: TCE-GO Manutenção Predial  
**Última atualização**: 14/11/2025  
**Baseado em**: ip-monitor v2.0
