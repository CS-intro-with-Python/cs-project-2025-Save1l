[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/DESIFpxz)
# CS_2024_project

## Description

Simple Flask server with Docker containerization and GitHub Actions CI/CD pipeline.

## Setup

### Running locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python server.py

# In another terminal, run the client
python client.py
```

### Running with Docker

```bash
# Build the Docker image
docker build -t flask-server .

# Run the container
docker run -d -p 5000:5000 --name flask-server flask-server

# Test with client
python client.py

# Stop the container
docker stop flask-server
docker rm flask-server
```

## Requirements

* Python 3.11+
* Flask - web framework
* requests - HTTP library for client
* Docker - containerization

## Features

* Simple Flask web server with "Hello, World" endpoint
* Dockerized application for easy deployment
* Client script to test server responses
* GitHub Actions CI/CD pipeline that:
  * Builds Docker image on push/pull request
  * Runs containerized server
  * Tests server with client script

## Git

Main branch: `main` - stores the latest stable version

## Success Criteria

* ✅ Flask server returns "Hello, World" on `/` endpoint
* ✅ Client sends request to `/` and checks status code 200
* ✅ GitHub Action builds Docker image
* ✅ GitHub Action runs Docker container
* ✅ GitHub Action runs client test
* ❌ Client modified to break GitHub Action (intentional failure for testing)

