# CS Project 2025 – Gaming Storefront

#Link
[My_Project](https://cs-project-2025-save1l-production.up.railway.app/)

## Description

This project implements a small e-commerce themed web app built with Flask. It exposes three HTML pages (`/`, `/home`, and `/pricing`) styled with Bootstrap and custom assets. The project includes:

- a Flask server that renders the storefront pages and serves static assets
- a requests-based client used for automated route checks
- Docker support for reproducible builds and containerized execution
- GitHub Actions workflows that build the image, run the container, and exercise the HTTP endpoints

## Application Routes

| Route      | Template          | Description                           |
|------------|-------------------|---------------------------------------|
| `/`        | `templates/index.html`  | Landing page with catalog overview     |
| `/home`    | `templates/home.html`   | User profile with shopping cart widget |
| `/pricing` | `templates/pricing.html`| Product pricing cards                  |

Static files (images, stylesheets, favicons) live under `templates/source` and are exposed via the `/source` prefix.

## Repository Layout

```
.
├── client.py                 # Requests-based smoke tests for routes
├── server.py                 # Flask application entry point
├── templates/                # Jinja/HTML templates and static assets
├── requirements.txt          # Python dependencies (Flask, requests)
├── Dockerfile                # Container build definition
└── .github/workflows/        # CI pipelines (Docker + route checks)
```

## Running Locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python server.py
```

The server listens on `http://127.0.0.1:5000`. Static assets are available under `/source/...` (e.g. `http://127.0.0.1:5000/source/styles/mycss.css`).

### Route Smoke Tests

With the server running, execute the client smoke tests:

```bash
python client.py
```

The script checks that all public routes respond with HTTP 200 and contain expected text fragments.

## Docker

### Production Build

```bash
# Build
docker build -t gaming-storefront .

# Run
docker run -d -p 5000:5000 --name gaming-storefront gaming-storefront

# Check the routes (from host)
python client.py

# Tear down when finished
docker stop gaming-storefront
docker rm gaming-storefront
```

The container runs `flask run` with host `0.0.0.0`, so the application is reachable externally via the mapped port.

### Development Mode (Hot Reload)

Для разработки с автоматической перезагрузкой при изменении кода используйте volume mount:

```bash
# Вариант 1: Docker Compose (рекомендуется)
docker-compose up

# Вариант 2: Docker run с volume
docker build -t gaming-storefront .
docker run -d -p 5000:5000 \
  -v "$(pwd):/app" \
  -v /app/__pycache__ \
  --name flask-dev \
  gaming-storefront

# Остановить
docker stop flask-dev && docker rm flask-dev
# или для docker-compose:
docker-compose down
```

При изменении файлов (`.py`, `.html`, `.css` и т.д.) Flask автоматически перезагрузит приложение благодаря `FLASK_RUN_RELOAD=true` и монтированию кода.

## CI/CD

Two GitHub Actions workflows (`.github/workflows/test.yml` and `test_docker.yml`) provide automated checks:

1. **Build** – docker build to ensure the image compiles.
2. **Run** – container launch with port mapping and log inspection.
3. **Route validation** – executes `client.py` (and curl) against the running container to confirm every route is reachable from outside the container.

The workflows trigger on pushes and pull requests targeting `main`. A passing status is required before deploying changes.

### Railway Deployment

The app can be deployed to [Railway](https://railway.com/) using the Dockerfile:

```bash
railway login
railway init     # create new project and link this repo
railway up       # builds the Docker image and deploys
```

Set the service start command to `flask run --host=0.0.0.0 --port=${PORT}` so Railway binds to the provided port. Environment variables (if any) can be managed in the Railway dashboard.

## Future Improvements

- Add persistence for the shopping cart and profile data
- Automate Railway deployments via GitHub Actions
- Expand the client tests with content assertions for each page

