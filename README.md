# CS Project 2025 – Gaming Storefront

## Description

This project implements a small e-commerce themed web app built with Flask. It exposes three HTML pages (`/`, `/home`, and `/pricing`) styled with Bootstrap and custom assets. The project includes:

- a Flask server that renders the storefront pages and serves static assets
- Google OAuth 2.0 authentication for user login
- Shopping cart functionality with PostgreSQL database persistence
- Swagger UI for interactive API documentation
- Logging
- a requests-based client used for automated route checks
- Docker Compose setup with web and db containers
- GitHub Actions workflows that build the image, run the container, and exercise the HTTP endpoints

## Application Routes

| Route      | Template          | Description                           |
|------------|-------------------|---------------------------------------|
| `/`        | `templates/index.html`  | Landing page with catalog overview     |
| `/home`    | `templates/home.html`   | User profile with shopping cart widget |
| `/pricing` | `templates/pricing.html`| Product pricing cards                  |
| `/swagger` | -                       | Swagger UI API documentation           |


Static files (images, stylesheets, favicons) live under `templates/source` and are exposed via the `/source` prefix.

## Repository Layout

```
.
├── server.py                 # Flask application entry point
├── models.py                 # SQLAlchemy models (User, CartItem)
├── auth.py                   # OAuth authentication blueprint
├── logger.py                 # Logging configuration
├── client.py                 # Requests-based tests for routes
├── templates/                # HTML templates and static assets
├── tests/
│   ├── unit_test.py          # Unit tests with pytest
│   └── integration_test.py   # Docker integration tests
├── logs/                     # Application logs
├── requirements.txt          # Python dependencies
├── Dockerfile                # Container build definition
├── docker-compose.yml        # Multi-container Docker setup
└── .github/workflows/        # CI (Docker + route checks)
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key for sessions | `dev-secret-key-change-in-production` |
| `DATABASE_URL` | Database connection string | `sqlite:///cart.db` |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | - |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | - |

## Running Locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 server.py
```

The server listens on `http://127.0.0.1:5000`. Static assets are available under `/source/...` (e.g. `http://127.0.0.1:5000/source/styles/mycss.css`).

### Route Tests

With the server running, execute the client tests:

```bash
python client.py
```

The script checks that all public routes respond with HTTP 200 and contain expected text fragments.

## Testing

### All Tests

```bash
docker-compose up -d
pytest -v
docker-compose down -v
```

#### Only Unit Tests

```bash
pytest tests/unit_test.py -v
```

Unit tests cover:
- Input validation for cart API endpoints
- Cart item CRUD operations
- Error handling

#### Only Integration Tests

```bash
docker-compose up -d
pytest tests/integration_test.py -v
docker-compose down -v
```

## Docker

### Docker Compose (Recommended)

The project includes a `docker-compose.yml` with Flask app and PostgreSQL:

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Production Build

```bash
# Build
docker build -t gaming-store .

# Run
docker run -d -p 5000:5000 --name gaming-store gaming-store

# Check the routes (from host)
python client.py

# Tear down when finished
docker stop gaming-store
docker rm gaming-store
```

The container runs `flask run` with host `0.0.0.0`, so the application is reachable externally via the mapped port.

### Development Mode (Hot Reload)

For development with automatic reboot when code changes, use volume mount:

```bash
# Docker build
docker build -t gaming-store .

# Docker run
docker run -d -p 5000:5000 -v "$(pwd)":/app --name docker-store gaming-store

# Stop
docker stop docker-store && docker rm docker-store
```

When files (`.py`, `.html`, `.css`, etc.) change, Flask will automatically reload the application thanks to `FLASK_RUN_RELOAD=true` and code mounting.

## Logging

The application using files for structured logging:

| Log File | Description |
|----------|-------------|
| `logs/app.log` | Application logs |
| `logs/db.log` | SQLAlchemy database query logs |

Logs are rotated at 10MB with 5 backup files retained.

## Database Models

### User
- `id` - Primary key
- `email` - User email (unique)
- `name` - Display name
- `google_id` - Google OAuth ID (unique)

### CartItem
- `id` - Primary key
- `user_id` - Foreign key to User
- `product_name` - Product name
- `product_price` - Product price
- `quantity` - Item quantity (default: 1)

## CI/CD

Two GitHub Actions workflows (`.github/workflows/test.yml` and `test_docker.yml`) provide automated checks:

1. **Build** – docker build to ensure the image compiles.
2. **Run** – container launch with port mapping and log inspection.
3. **Route validation** – executes `client.py` (and curl) against the running container to confirm every route is reachable from outside the container.

The workflows trigger on pushes and pull requests targeting `main`. A passing status is required before deploying changes.
