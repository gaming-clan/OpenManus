def inject_keys_env(keys):
    """Injects keys into os.environ for runtime use."""
    for k, v in keys.items():
        os.environ[k] = v


import json
import os


def load_keys():
    # Prefer project-level keys.txt (project root). If not present, fall back to
    # user's home directory keys.txt to preserve previous behavior.
    home = os.path.expanduser("~")
    project_keys = os.path.join(os.getcwd(), "keys.txt")
    home_keys = os.path.join(home, "keys.txt")
    keys = {}
    keys_path = None
    if os.path.exists(project_keys):
        keys_path = project_keys
    elif os.path.exists(home_keys):
        keys_path = home_keys

    if keys_path:
        with open(keys_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip() and not line.strip().startswith("#"):
                    if "=" in line:
                        k, v = line.strip().split("=", 1)
                        keys[k.strip()] = v.strip()
    return keys


def save_keys(keys):
    # Save to C:\Users\Administrator\keys.txt
    home = os.path.expanduser("~")
    keys_path = os.path.join(home, "keys.txt")
    with open(keys_path, "w", encoding="utf-8") as f:
        for k, v in keys.items():
            f.write(f"{k}={v}\n")
