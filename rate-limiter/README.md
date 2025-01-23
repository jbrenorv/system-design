## Create a virtual environment
```bash
cd rate-limiter
python3 -m venv .venv
source .venv/bin/activate
```

## Install FastAPI and run
```bash
pip install "fastapi[standard]"
fastapi dev main.py
```

## Test
Open a new terminal window and run:
```bash
python -m pytest tests/
```
