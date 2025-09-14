import pytest


def docker_is_available() -> bool:
    try:
        import docker

        client = docker.from_env()
        # Try a lightweight API call
        client.ping()
        return True
    except Exception:
        return False


DOCKER_AVAILABLE = docker_is_available()


def wsl_is_available() -> bool:
    """Return True if WSL is usable on this host."""
    try:
        import subprocess

        res = subprocess.run(["wsl", "-l"], capture_output=True)
        return res.returncode == 0 or res.returncode == 1
    except Exception:
        return False


WSL_AVAILABLE = wsl_is_available()


def pytest_collection_modifyitems(config, items):
    # Skip all tests under tests/sandbox if Docker isn't available
    if not (DOCKER_AVAILABLE or WSL_AVAILABLE):
        skip_reason = (
            "Skipping sandbox tests because neither Docker daemon nor WSL is available"
        )
        for item in list(items):
            try:
                path = str(item.fspath)
            except Exception:
                path = item.nodeid
            if "/tests/sandbox" in path.replace("\\\\", "/") or "tests/sandbox" in path:
                item.add_marker(pytest.mark.skip(reason=skip_reason))
