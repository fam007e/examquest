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
        subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)

    python_exe = get_python_executable()

    print("📦  Syncing Python dependencies...")
    subprocess.run([python_exe, "-m", "pip", "install", "-U", "pip"], check=True)
    subprocess.run([python_exe, "-m", "pip", "install", "-r", "requirements.txt"], check=True)

def run_app():
    """Start both backend and frontend servers and monitor them."""
    python_exe = get_python_executable()

    # 1. Start the Backend
    print("🚀 Starting Backend (FastAPI)...")
    with subprocess.Popen(
        [python_exe, "-m", "uvicorn", "main:app", "--app-dir", "backend", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    ) as backend_proc:

        # 2. Wait for backend to be ready
        time.sleep(2)

        # 3. Check/Start the Frontend
        if not os.path.exists("frontend/node_modules"):
            print("📦 node_modules not found. Installing frontend dependencies...")
            subprocess.run(["npm", "install"], cwd="frontend", check=True)

        print("💻 Starting Frontend (Vite)...")
        # Using 'with' for Popen to ensure proper resource management
        with subprocess.Popen(
            ["npm", "run", "dev"],
            cwd="frontend",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        ) as frontend_proc:

            print("\n" + "="*40)
            print("✅ Application is running!")
            print("👉 Backend:  http://localhost:8000")
            print("👉 Frontend: http://localhost:5173")
            print("="*40)
            print("\nPress Ctrl+C to stop both servers.\n")

            try:
                while True:
                    # We could pipe logs here if desired, but keeping it clean
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
                backend_proc.terminate()
                frontend_proc.terminate()
                print("👋 Goodbye!")

if __name__ == "__main__":
    try:
        setup_venv()
        run_app()
    except Exception as e: # pylint: disable=broad-exception-caught
        print(f"❌ Error during startup: {e}")
        sys.exit(1)
