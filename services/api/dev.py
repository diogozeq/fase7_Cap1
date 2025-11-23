"""Bootstrap a local venv for the API and run the server."""
import os
import subprocess
import sys
from pathlib import Path
import venv

ROOT = Path(__file__).parent
VENV_DIR = ROOT / ".venv"
MARKER = VENV_DIR / ".deps_installed"
IS_WIN = os.name == "nt"


def venv_python() -> Path:
    return VENV_DIR / ("Scripts/python.exe" if IS_WIN else "bin/python")


def ensure_venv():
    if not VENV_DIR.exists():
        print("[api] Creating virtualenv at", VENV_DIR)
        venv.EnvBuilder(with_pip=True).create(VENV_DIR)


def pip_install(python: Path, args):
    # Make sure pip exists (older venvs can miss it)
    try:
        subprocess.check_call([str(python), "-m", "pip", "--version"])
    except subprocess.CalledProcessError:
        subprocess.check_call([str(python), "-m", "ensurepip", "--upgrade"])
    subprocess.check_call([str(python), "-m", "pip", *args])


def main():
    ensure_venv()
    py = venv_python()
    print(f"[api] Using interpreter: {py}")
    if MARKER.exists():
        print("[api] Dependencies already installed, skipping pip install")
    else:
        try:
            pip_install(py, ["install", "-r", str(ROOT / "requirements.txt")])
            MARKER.touch()
        except subprocess.CalledProcessError:
            if MARKER.exists():
                MARKER.unlink()
            raise
    env = os.environ.copy()
    env.setdefault("PYTHONUNBUFFERED", "1")
    root_dir = ROOT.parent.parent
    env["PYTHONPATH"] = str(root_dir) + os.pathsep + env.get("PYTHONPATH", "")
    subprocess.check_call([str(py), str(ROOT / "main.py")], env=env)


if __name__ == "__main__":
    main()
