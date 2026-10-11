# Build container: runs the tests, then packages the game for the web with pygbag.
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Tests must pass before anything gets built. Output lands in game/build/web.
CMD ["sh", "-c", "pytest -q && pygbag --build game"]
