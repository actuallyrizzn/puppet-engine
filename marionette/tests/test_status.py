import subprocess
import time
import requests
import pytest
import sys
import os

@pytest.fixture(scope="module")
def uvicorn_server():
    # Start the FastAPI app in a subprocess
    proc = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "marionette.api.main:app", "--port", "8001"
    ], env={**os.environ, "PYTHONPATH": os.getcwd()})
    time.sleep(2)  # Give server time to start
    yield
    proc.terminate()
    proc.wait()

def test_status(uvicorn_server):
    resp = requests.get("http://127.0.0.1:8001/status")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"} 