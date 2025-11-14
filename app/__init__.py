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

app = Flask(__name__, 
           template_folder=template_dir, 
           static_folder=static_dir)

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