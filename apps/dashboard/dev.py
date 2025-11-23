"""Launch Streamlit on a free port to avoid clashes."""
import socket
import subprocess
import sys
import os


def choose_port(preferred: int) -> int:
    """Try preferred port on all interfaces; fall back to an ephemeral free one if it's busy."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind(("", preferred))  # detect if anything already listening on the port
            return preferred
        except OSError:
            sock.bind(("", 0))
            return sock.getsockname()[1]


if __name__ == "__main__":
    preferred = int(os.getenv("DASHBOARD_PORT", "8510"))
    attempt_ports = [preferred] + list(range(8511, 8521))
    last_error = None

    for port_try in attempt_ports:
        port = choose_port(port_try)
        print(f"[dashboard] Starting Streamlit on port {port} (preferred {preferred})")
        cmd = [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "app.py",
            "--server.port",
            str(port),
            "--server.headless",
            "true",
            "--server.enableCORS",
            "false",
            "--server.enableXsrfProtection",
            "false",
        ]
        try:
            subprocess.run(cmd, check=True)
            sys.exit(0)
        except subprocess.CalledProcessError as e:
            last_error = e
            print(f"[dashboard] Port {port} failed, trying another... ({e})")
            continue

    if last_error:
        print("[dashboard] Failed to start Streamlit after multiple attempts. Set DASHBOARD_PORT to a free port and retry.")
        sys.exit(last_error.returncode)
