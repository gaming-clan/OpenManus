import os
import argparse
from backend.app import create_app
from utils.key_loader import load_keys, inject_keys_env

def detect_wsl():
    return "WSL_DISTRO_NAME" in os.environ

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OpenManus: Modular AI agent framework")
    parser.add_argument("--web", action="store_true", help="Run the advanced Web GUI")
    args = parser.parse_args()

    # Load API keys
    keys = load_keys()
    inject_keys_env(keys)

    if detect_wsl():
        print("[OpenManus] Detected WSL environment.")

    if args.web:
        app = create_app()
        app.run(host="127.0.0.1", port=7860)
    else:
        # CLI fallback
        from cli.entrypoint import run_cli
        run_cli()