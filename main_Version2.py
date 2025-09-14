import argparse
import os

from scripts.wsl_agent_tools import WSLAgentTools


class WSLAgent:
    """WSL agent mode: simulate user actions, file/app automation, etc."""

    def __init__(self):
        print("[OpenManus] WSLAgent initialized. Ready to simulate user actions.")
        self.tools = WSLAgentTools()

    def run(self):
        print("[OpenManus] (WSLAgent) Simulating Manus-like agent mode in WSL...")
        while True:
            print("\nChoose an action:")
            print("1. Open file manager (Linux)")
            print("2. Open a URL (Linux)")
            print("3. Run a shell command (Linux)")
            print("4. List files in home directory (Linux)")
            print("5. Open Windows Explorer")
            print("6. Transfer file from WSL to Windows Desktop")
            print("7. Transfer file from Windows to WSL home")
            print("8. Show WSL/Windows usernames")
            print("9. Shutdown WSL")
            print("10. Reboot WSL")
            print("0. Exit agent mode")
            choice = input("Enter choice [0-10]: ").strip()
            if choice == "1":
                path = input("Enter path (leave blank for home): ").strip() or None
                self.tools.open_file_manager(path)
            elif choice == "2":
                url = input("Enter URL: ").strip()
                self.tools.open_url(url)
            elif choice == "3":
                cmd = input("Enter shell command: ").strip()
                self.tools.run_command(cmd)
            elif choice == "4":
                self.tools.list_home_files()
            elif choice == "5":
                path = input("Enter path (leave blank for home): ").strip() or None
                self.tools.open_windows_explorer(path)
            elif choice == "6":
                wsl_path = input("Enter WSL file path to copy: ").strip()
                win_dest = (
                    input(
                        "Enter Windows destination (leave blank for Desktop): "
                    ).strip()
                    or None
                )
                self.tools.transfer_file_to_windows(wsl_path, win_dest)
            elif choice == "7":
                win_path = input("Enter Windows file path to copy: ").strip()
                wsl_dest = (
                    input("Enter WSL destination (leave blank for home): ").strip()
                    or None
                )
                self.tools.transfer_file_to_wsl(win_path, wsl_dest)
            elif choice == "8":
                self.tools.show_usernames()
            elif choice == "9":
                self.tools.shutdown_wsl()
            elif choice == "10":
                self.tools.reboot_wsl()
            elif choice == "0":
                print("[OpenManus] Exiting WSL agent mode.")
                break
            else:
                print("Invalid choice. Please try again.")


try:
    from app import create_app
except ImportError:
    from backend_app_Version2 import create_app  # fallback if app is not found

try:
    from key_loader import inject_keys_env, load_keys
except ImportError:
    from .key_loader import inject_keys_env, load_keys


def detect_wsl():
    return "WSL_DISTRO_NAME" in os.environ


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="OpenManus: Modular AI agent framework"
    )
    parser.add_argument("--web", action="store_true", help="Run the advanced Web GUI")
    parser.add_argument(
        "--agent",
        action="store_true",
        help="Run in agent mode (Manus simulation, WSL supported)",
    )
    args = parser.parse_args()

    # Load API keys
    try:
        keys = load_keys()
        inject_keys_env(keys)
    except Exception as e:
        print(f"[OpenManus] Warning: Failed to load/inject API keys: {e}")

    if detect_wsl():
        print("[OpenManus] Detected WSL environment.")

    if args.agent and detect_wsl():
        agent = WSLAgent()
        agent.run()
    elif args.web:
        app = create_app()
        app.run(host="127.0.0.1", port=7860)
    else:
        # CLI fallback
        try:
            from cli.entrypoint import run_cli
        except ImportError:
            from .cli.entrypoint import run_cli
        run_cli()
