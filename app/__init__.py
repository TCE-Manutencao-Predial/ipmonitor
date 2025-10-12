import os
from flask import Flask

app = Flask(__name__)

from app import routes

routes.start_background_service()