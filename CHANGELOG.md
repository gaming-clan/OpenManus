# Changelog

## 2025-09-14
- Added WSL/local sandbox fallback so OpenManus can run without Docker on Windows.
- Added `keys.example.txt` as a sample API keys file. Copy to `keys.txt` and edit with your own provider keys.
- Updated setup script to guide users to copy `keys.example.txt` to `keys.txt`.
- Configuration loaders prefer a project-level `keys.txt` before falling back to `~/keys.txt`.
