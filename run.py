import sys
import os
import torch

print(f"Current directory: {os.getcwd()}")
print(f"Python version: {sys.version}")
print(f"Python path: {sys.executable}")
print(f"PyTorch version: {torch.__version__}")

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run_server(
        debug=True,
        host='127.0.0.1',
        port=8050
    ) 