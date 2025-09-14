from flask import Flask

try:
    from app.backend.routes import register_routes
except ImportError:
    from backend_routes_Version2 import register_routes


def create_app():
    app = Flask(__name__, static_folder="web", static_url_path="/")
    register_routes(app)
    return app
