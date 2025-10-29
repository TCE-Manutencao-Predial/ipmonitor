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
	./.venv/bin/waitress-serve --host 0.0.0.0 --port 5000 config:app


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

# Configurações do Servico
# ----------------------------
SERVICE_NAME=ipmonitor

service-reload:
	sudo systemctl daemon-reload

service-restart:
	sudo setenforce 0
	sudo systemctl restart $(SERVICE_NAME)
	sudo setenforce 1

service-status:
	sudo systemctl status $(SERVICE_NAME)
