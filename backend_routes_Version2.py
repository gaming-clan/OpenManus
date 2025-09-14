import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from flask import jsonify, request, send_from_directory

try:
    from backend.agent_controller import get_logs, handle_agent, handle_chat
except ImportError:
    from backend_agent_controller import get_logs, handle_agent, handle_chat


try:
    from key_loader import load_keys, save_keys
except ImportError:
    from .key_loader import load_keys, save_keys


def register_routes(app):
    @app.route("/api/chat", methods=["POST"])
    def chat():
        data = request.get_json()
        return jsonify(handle_chat(data))

    @app.route("/api/agent", methods=["POST"])
    def agent():
        data = request.get_json()
        return jsonify(handle_agent(data))

    @app.route("/api/agent/logs", methods=["GET"])
    def logs():
        return jsonify(get_logs())

    @app.route("/api/keys", methods=["GET", "POST"])
    def keys():
        if request.method == "GET":
            return jsonify(load_keys())
        else:
            keys = request.get_json()
            save_keys(keys)
            return jsonify({"status": "ok"})

    # Serve frontend
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve(path):
        file_path = os.path.join(app.static_folder, path)
        if path != "" and os.path.exists(file_path):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, "index.html")
