
venv:
    python -m venv .venv

run:
    .venv/bin/python -m uvicorn main:app --reload

install:
    .venv/bin/pip install -r requirements.txt

zip:
    mkdir -p deploy
    zip -r deploy/deploy.zip static templates *.py justfile requirements.txt