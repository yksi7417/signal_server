"""
Shared fixtures for integration tests.
"""

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import psutil
import pytest
import requests

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def kill_existing_servers(port=8080):
    """Kill any existing processes running on the specified port."""
    killed_processes = []

    try:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                # Get connections for this specific process
                connections = proc.connections()
                if connections:
                    for conn in connections:
                        if hasattr(conn, 'laddr') and conn.laddr and conn.laddr.port == port:
                            print(f"Killing process {proc.info['pid']} ({proc.info['name']}) using port {port}")
                            proc.terminate()
                            killed_processes.append(proc.info['pid'])

                            # Wait for process to terminate, then force kill if needed
                            try:
                                proc.wait(timeout=5)
                            except psutil.TimeoutExpired:
                                proc.kill()

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

    except Exception as e:
        print(f"Error while killing existing servers: {e}")

    if killed_processes:
        print(f"Killed {len(killed_processes)} processes using port {port}")
        time.sleep(2)  # Give time for ports to be released

    return killed_processes


def wait_for_server_start(base_url, max_attempts=30, timeout=1):
    """Wait for the aiohttp server to start and be responsive."""
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{base_url}/", timeout=timeout)
            if response.status_code == 200:
                print(f"Server is responsive after {attempt + 1} attempts")
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    return False


def start_test_server():
    """Start a fresh aiohttp server and return the process."""
    # Change to project directory
    os.chdir(project_root)

    # Start aiohttp server in background with proper output handling
    if os.name == 'nt':  # Windows
        process = subprocess.Popen(
            [sys.executable, "app.py"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )
    else:  # Unix-like
        process = subprocess.Popen(
            [sys.executable, "app.py"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            preexec_fn=os.setsid
        )

    return process


def stop_test_server(process):
    """Stop the aiohttp server process gracefully."""
    if process and process.poll() is None:
        try:
            if os.name == 'nt':  # Windows
                # Kill the entire process group
                subprocess.run(['taskkill', '/F', '/T', '/PID', str(process.pid)],
                             capture_output=True, check=False)
            else:  # Unix-like
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)

            # Wait for graceful shutdown
            try:
                process.wait(timeout=5)
                print("Server stopped gracefully")
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
                print("Server force killed")

        except Exception as e:
            print(f"Error stopping server: {e}")
            try:
                process.kill()
                process.wait()
            except:
                pass


@pytest.fixture(scope="session")
def global_test_server():
    """Session-wide aiohttp server fixture that manages server lifecycle."""
    base_url = "http://localhost:8080"

    print("\n" + "="*60)
    print("SETTING UP INTEGRATION TEST ENVIRONMENT")
    print("="*60)

    # Kill any existing servers on port 8080
    print("1. Killing any existing servers on port 8080...")
    kill_existing_servers(8080)

    # Start fresh aiohttp server
    print("2. Starting fresh aiohttp server...")
    process = start_test_server()

    # Wait for server to be responsive
    print("3. Waiting for server to start...")
    if not wait_for_server_start(base_url, max_attempts=30):
        stop_test_server(process)
        pytest.fail("Server failed to start within 30 seconds")
    print(f"4. Server is ready for testing! pid={process.pid}")
    print("="*60)

    yield process, base_url

    # Cleanup
    print("\n" + "="*60)
    print("CLEANING UP INTEGRATION TEST ENVIRONMENT")
    print("="*60)
    print("Stopping server...")
    stop_test_server(process)
    print("Integration test cleanup complete!")
    print("="*60)
