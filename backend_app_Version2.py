from flask import Flask
from backend.routes import register_routes

def create_app():
    app = Flask(__name__, static_folder="../web/build", static_url_path="/")
    register_routes(app)
    return app