import os
from flask import Flask

# Configurar os caminhos explicitamente
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))

app = Flask(__name__, 
           template_folder=template_dir, 
           static_folder=static_dir,
           static_url_path='/static')

from app import routes

routes.start_background_service()