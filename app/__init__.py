from flask import Flask
import concurrent.futures
app = Flask(__name__)

from app import ip_operations
from app import routes

routes.start_background_service()