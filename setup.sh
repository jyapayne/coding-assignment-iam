# exit when a command fails
set -e

# init venv
python3 -m venv .venv
source .venv/bin/activate

# install deps
pip install fastapi uvicorn[standard] websockets
