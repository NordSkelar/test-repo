# Brick Builder

A tiny brick-building sandbox written in Python with pygame. It runs in the browser through
[pygbag](https://github.com/pygame-web/pygbag) and is deployed to GitHub Pages by GitHub Actions.

## Controls

| Input | Action |
|---|---|
| Left click | Place brick (or pick a color in the toolbar) |
| Right click | Remove brick |
| `1`–`8` / mouse wheel | Choose color |
| `Q` / `E` | Brick width smaller / bigger (1–4) |
| `Z` | Undo |
| `C` | Clear board |

## How the pipeline works

On every push or pull request, `.github/workflows/deploy.yml`:

1. Stamps the short commit hash into the game (shown in the toolbar).
2. Builds the Docker image from `Dockerfile`.
3. Runs the container, which runs `pytest` and stops if any test fails, then runs `pygbag --build game`.
4. Uploads `game/build/web` as the Pages artifact.
5. On `main` only, deploys it to `https://<you>.github.io/<repo>/`.

## One-time setup

1. Create a repo on GitHub and push this folder to it on the `main` branch.
2. In the repo, go to **Settings → Pages → Build and deployment → Source** and choose **GitHub Actions**.
3. Push a commit, or run the workflow from the **Actions** tab. When it finishes, the site link appears on the run.

## Running locally

```bash
pip install pygame-ce pygbag pytest
python game/main.py            # desktop window
pytest                          # logic tests
pygbag game                     # browser version at http://localhost:8000
```

Or build exactly what CI builds:

```bash
docker build -t brick-builder .
docker run --rm -v "$PWD/game:/app/game" brick-builder
```

## Project layout

```
game/main.py     drawing, input, main loop (async for pygbag)
game/grid.py     pure game logic: placement, removal, undo
tests/           pytest tests for grid.py
Dockerfile       the build container
.github/workflows/deploy.yml
```
