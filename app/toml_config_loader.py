import re
import tomllib
from pathlib import Path


def load_keys(keys_path: str = None):
    import os

    keys = {}
    if keys_path is None:
        home = os.path.expanduser("~")
        keys_path = os.path.join(home, "keys.txt")
    with open(keys_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip() and not line.strip().startswith("#"):
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    keys[k.strip()] = v.strip()
    return keys


def inject_keys_in_toml(toml_dict, keys):
    # Recursively replace ${Key} with value from keys
    if isinstance(toml_dict, dict):
        return {k: inject_keys_in_toml(v, keys) for k, v in toml_dict.items()}
    elif isinstance(toml_dict, list):
        return [inject_keys_in_toml(i, keys) for i in toml_dict]
    elif isinstance(toml_dict, str):

        def replacer(match):
            key = match.group(1)
            return keys.get(key, match.group(0))

        return re.sub(r"\$\{([^}]+)\}", replacer, toml_dict)
    else:
        return toml_dict


def load_config_with_keys(
    toml_path: str = "config/config.toml", keys_path: str = "keys.txt"
):
    with open(toml_path, "rb") as f:
        toml_data = tomllib.load(f)
    keys = load_keys(keys_path)
    return inject_keys_in_toml(toml_data, keys)


# Example usage:
# config = load_config_with_keys()
# print(config)
