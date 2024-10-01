VENV_PYTHON=.venv/bin/python
VENV_PIP=.venv/bin/pip


# Cria a venv e instala as dependências
setup:
	python -m venv .venv
	# If linux
	./$(VENV_PIP) install -r requirements.txt
	./$(VENV_PIP) install .


# Executa o projeto
run:
	./.venv/bin/waitress-serve --host 127.0.0.1 --port 8000 ipmonitor:app


# Apaga a venv
clear_venv:
	@if [ -d ".venv" ]; then rm -r .venv; fi



# Configurações de Deploy
# ----------------------------

# Realiza o deploy
deploy:
	sudo chmod +x ./scripts/deploy.sh
	./scripts/deploy.sh

undeploy:
	sudo chmod +x ./scripts/undeploy.sh
	./scripts/undeploy.sh