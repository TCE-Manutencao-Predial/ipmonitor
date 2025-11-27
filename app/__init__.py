import os
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

# Executar migração de dados na inicialização
from app.migration import migrate_data_files, ensure_data_directory

# Garantir que o diretório de dados existe e migrar arquivos se necessário
ensure_data_directory()
migrate_data_files()

# Configurar os caminhos explicitamente
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))

# Obter ROUTES_PREFIX do ambiente (.env.deploy)
from dotenv import load_dotenv
from pathlib import Path
import platform

BASE_DIR = Path(__file__).parent.parent
env_file_deploy = BASE_DIR / '.env.deploy'
if env_file_deploy.exists():
    load_dotenv(env_file_deploy)

# Definir ROUTES_PREFIX baseado no ambiente
# Em produção (Linux): usa /ipmonitor
# Em desenvolvimento (Windows/Mac): usa '' (vazio) para servir na raiz
if platform.system() == "Linux":
    ROUTES_PREFIX = os.getenv('ROUTES_PREFIX', '/ipmonitor')
    STATIC_URL_PATH = f'{ROUTES_PREFIX}/static'
else:
    ROUTES_PREFIX = ''
    STATIC_URL_PATH = '/static'

app = Flask(__name__,
           template_folder=template_dir,
           static_folder=static_dir,
           static_url_path=STATIC_URL_PATH)

# Configurar middleware para proxy reverso (Apache)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Injetar configurações centralizadas nos templates
from app import settings

@app.context_processor
def inject_settings():
    """Disponibiliza configurações do settings.py em todos os templates"""
    return {
        'ROUTES_PREFIX': settings.ROUTES_PREFIX,
        'DOMAIN_BASE': settings.DOMAIN_BASE,
        'PROJECT_NAME': settings.PROJECT_NAME,
        'BASE_URL': settings.BASE_URL_PRODUCTION,
        'NETWORK_BASE': settings.NETWORK_BASE
    }

from app import routes

routes.start_background_service()