import os
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

# Configurar os caminhos explicitamente
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))

app = Flask(__name__, 
           template_folder=template_dir, 
           static_folder=static_dir)

# Configurar middleware para proxy reverso (Apache)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

from app import routes

routes.start_background_service()