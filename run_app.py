#!/usr/bin/env python3
"""
Script to set up the virtual environment and run both backend and frontend servers.
"""
import os
import subprocess
import sys
import time

def get_python_executable():
    """Return the path to the python executable in the virtual environment."""
    if os.name == 'nt':
        return os.path.join(".venv", "Scripts", "python.exe")
    return os.path.join(".venv", "bin", "python")

def setup_venv():
    """Create a virtual environment if it doesn't exist and install dependencies."""
    if not os.path.exists(".venv"):
        print("🛠️  Creating virtual environment (.venv)...")
        subprocess.run(
            [sys.executable, "-m", "venv", ".venv"], check=True
        )  # nosec

    python_exe = get_python_executable()

    print("📦  Syncing Python dependencies...")
    subprocess.run(
        [python_exe, "-m", "pip", "install", "-U", "pip"], check=True
    )  # nosec
    subprocess.run(
        [python_exe, "-m", "pip", "install", "-r", "requirements.txt"], check=True
    )  # nosec

def run_app():
    # pylint: disable=too-many-branches
    """Start both backend and frontend servers and monitor them."""
    python_exe = get_python_executable()
    is_windows = os.name == 'nt'

    # 1. Start the Backend
    print("🚀 Starting Backend (FastAPI)...")
    # We do not pipe stdout/stderr to avoid buffer saturation issues on Windows.
    # Logs will flow naturally to the console.
    # pylint: disable=consider-using-with
    backend_proc = subprocess.Popen(
        [python_exe, "-m", "uvicorn", "main:app", "--app-dir", "backend", "--port", "8000"],
        bufsize=1
    ) # nosec

    try:
        # 2. Wait for backend to be ready
        time.sleep(2)

        # 3. Check/Start the Frontend
        if not os.path.exists("frontend/node_modules"):
            print("📦 node_modules not found. Installing frontend dependencies...")
            if is_windows:
                subprocess.run(
                    ["npm.cmd", "install"], cwd="frontend", check=True
                )  # nosec
            else:
                subprocess.run(
                    ["npm", "install"], cwd="frontend", check=True
                )  # nosec

        print("💻 Starting Frontend (Vite)...")
        # Check if Node.js supports --disable-warning=DEP0205 via feature detection
        node_env = os.environ.copy()
        try:
            # Test if Node accepts --disable-warning=DEP0205
            res = subprocess.run(
                ["node", "--disable-warning=DEP0205", "-v"],
                capture_output=True,
                check=False
            )  # nosec
            if res.returncode == 0:
                node_opts = node_env.get("NODE_OPTIONS", "")
                node_env["NODE_OPTIONS"] = f"{node_opts} --disable-warning=DEP0205".strip()
        except FileNotFoundError:
            # Node.js is not installed; handled later during Vite launch
            pass
        except subprocess.SubprocessError as e:
            print(f"⚠️ Warning during Node warning-suppression check: {e}")

        # pylint: disable=consider-using-with
        if is_windows:
            frontend_proc = subprocess.Popen(
                ["npm.cmd", "run", "dev"],
                cwd="frontend",
                env=node_env
            )  # nosec
        else:
            frontend_proc = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd="frontend",
                env=node_env
            )  # nosec

        print("\n" + "="*40)
        print("✅ Application is running!")
        print("👉 Backend:  http://localhost:8000")
        print("👉 Frontend: http://localhost:5173")
        print("="*40)
        print("\nPress Ctrl+C to stop both servers.\n")

        while True:
            time.sleep(1)
            # Check if processes are still alive
            if backend_proc.poll() is not None:
                print("❌ Backend stopped unexpectedly.")
                break
            if frontend_proc.poll() is not None:
                print("❌ Frontend stopped unexpectedly.")
                break
    except KeyboardInterrupt:
        print("\n🛑 Stopping servers...")
    finally:
        # Clean shutdown regardless of how we exited
        if 'backend_proc' in locals() and backend_proc.poll() is None:
            backend_proc.terminate()
        if 'frontend_proc' in locals() and frontend_proc.poll() is None:
            frontend_proc.terminate()
        print("👋 Goodbye!")

if __name__ == "__main__":
    try:
        setup_venv()
        run_app()
    except Exception as e: # pylint: disable=broad-exception-caught
        print(f"❌ Error during startup: {e}")
        sys.exit(1)
