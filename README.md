# Ronnia API

The backend for the https://ronnia.me website.

## Requirements

Install the requirements with `pip install -r requirements.txt`.

## Setting up the backend server

### Manual deployment

Assuming you are using Linux based environment:

1. Create a virtual environment with `python3 -m venv venv`.
2. Activate the virtual environment with `source venv/bin/activate`.
3. Install the requirements with `pip install -r requirements.txt`.
4. Add the current folder to the `PYTHONPATH` environment variable with `export PYTHONPATH=$PYTHONPATH:$(pwd)`.
5. Create a `.env` file with the following variables:
    - `DEBUG_MODE`: Whether to run the server in debug mode.
    - `JWT_SECRET_KEY`: The secret key for creating JSON Web Tokens.
    - `JWT_ALGORITHM`: The algorithm to use for creating JSON Web Tokens.
    - `LOG_LEVEL`: The log level for the server.
    - `MONGODB_URL`: The URL to the MongoDB database.
    - `OSU_CLIENT_ID`: The client ID for the osu! API.
    - `OSU_CLIENT_SECRET`: The client secret for the osu! API.
    - `OSU_REDIRECT_URI`: The redirect URI for the osu! API.
    - `TWITCH_CLIENT_ID`: The client ID for the Twitch API.
    - `TWITCH_CLIENT_SECRET`: The client secret for the Twitch API.
    - `TWITCH_REDIRECT_URI`: The redirect URI for the Twitch API.
6. Run the server with `uvicorn  app.main:app --host :: --port ${PORT}`.

### Docker 🐳

Build the Dockerfile and run the image.

1. Build the Dockerfile with `docker build -t ronnia-backend --build-arg PORT=5000 .`.
2. Run the image with `docker run --name ronnia-backend-server -d -p 5000:5000 ronnia-backend`.
3. The server should now be running on `http://localhost:5000`.


### Docker Compose

Create a `docker-compose.yml` file with the following content:

```yaml
version: "3"

services:
  ronnia-backend:
    build:
      context: .
      args:
        PORT: 5000
    ports:
      - "5000:5000"
    image: ronnia-backend
    restart: always
    env_file: ..env
```

Make sure that your `.env` file is in the same folder as the `docker-compose.yml` file. 

The server should now be running on `http://localhost:5000`.