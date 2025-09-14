import os
import subprocess
from typing import Optional


class WSLAgentTools:
    """
    Utility class for WSLAgent to perform user-like actions in WSL.
    Extend this with more methods as needed.
    """

    def open_windows_explorer(self, path: Optional[str] = None):
        """Open Windows Explorer at the given path from WSL (if possible)."""
        path = path or os.path.expanduser("~")
        # Convert WSL path to Windows path
        try:
            win_path = subprocess.check_output(
                ["wslpath", "-w", path], text=True
            ).strip()
            subprocess.Popen(["explorer.exe", win_path])
            print(f"[WSLAgent] Opened Windows Explorer at: {win_path}")
        except Exception as e:
            print(f"[WSLAgent] Failed to open Windows Explorer: {e}")

    def transfer_file_to_windows(self, wsl_path: str, win_dest: Optional[str] = None):
        """Copy a file from WSL to Windows user's Desktop (or specified path)."""
        try:
            win_user = os.environ.get("WINUSER") or "Administrator"
            if not win_dest:
                win_dest = f"/mnt/c/Users/{win_user}/Desktop/"
            win_path = subprocess.check_output(
                ["wslpath", "-w", win_dest], text=True
            ).strip()
            subprocess.run(["cp", wsl_path, win_dest], check=True)
            print(f"[WSLAgent] Copied {wsl_path} to Windows: {win_path}")
        except Exception as e:
            print(f"[WSLAgent] Failed to copy file to Windows: {e}")

    def transfer_file_to_wsl(self, win_path: str, wsl_dest: Optional[str] = None):
        """Copy a file from Windows to WSL home (or specified path)."""
        try:
            if not wsl_dest:
                wsl_dest = os.path.expanduser("~")
            # Convert Windows path to WSL path
            wsl_path = subprocess.check_output(["wslpath", win_path], text=True).strip()
            subprocess.run(["cp", wsl_path, wsl_dest], check=True)
            print(f"[WSLAgent] Copied {win_path} to WSL: {wsl_dest}")
        except Exception as e:
            print(f"[WSLAgent] Failed to copy file to WSL: {e}")

    def show_usernames(self):
        """Show WSL and Windows usernames."""
        try:
            wsl_user = os.environ.get("USER") or os.environ.get("LOGNAME")
            win_user = os.environ.get("WINUSER") or "Administrator"
            print(
                f"[WSLAgent] WSL username: {wsl_user}\n[WSLAgent] Windows username: {win_user}"
            )
        except Exception as e:
            print(f"[WSLAgent] Failed to get usernames: {e}")

    def shutdown_wsl(self):
        """Shutdown the WSL instance."""
        try:
            print("[WSLAgent] Shutting down WSL...")
            subprocess.Popen(["wsl.exe", "--shutdown"])
        except Exception as e:
            print(f"[WSLAgent] Failed to shutdown WSL: {e}")

    def reboot_wsl(self):
        """Reboot the WSL instance (shutdown and restart)."""
        try:
            print("[WSLAgent] Rebooting WSL...")
            subprocess.Popen(["wsl.exe", "--shutdown"])
            print("[WSLAgent] Please restart WSL manually.")
        except Exception as e:
            print(f"[WSLAgent] Failed to reboot WSL: {e}")

    def open_file_manager(self, path: Optional[str] = None):
        """Open the default file manager at the given path (Linux/WSL)."""
        path = path or os.path.expanduser("~")
        try:
            subprocess.Popen(["xdg-open", path])
            print(f"[WSLAgent] Opened file manager at: {path}")
        except Exception as e:
            print(f"[WSLAgent] Failed to open file manager: {e}")

    def open_url(self, url: str):
        """Open a URL in the default browser."""
        try:
            subprocess.Popen(["xdg-open", url])
            print(f"[WSLAgent] Opened URL: {url}")
        except Exception as e:
            print(f"[WSLAgent] Failed to open URL: {e}")

    def run_command(self, command: str):
        """Run a shell command as the user."""
        try:
            result = subprocess.run(
                command, shell=True, check=True, capture_output=True, text=True
            )
            print(f"[WSLAgent] Command output:\n{result.stdout}")
        except subprocess.CalledProcessError as e:
            print(f"[WSLAgent] Command failed: {e.stderr}")

    def list_home_files(self):
        """List files in the user's home directory."""
        home = os.path.expanduser("~")
        try:
            files = os.listdir(home)
            print(f"[WSLAgent] Files in {home}: {files}")
        except Exception as e:
            print(f"[WSLAgent] Failed to list files: {e}")
