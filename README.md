# URL Shortener

A URL shortener built with FastAPI, SQLModel, and SQLite, with a browser UI for auth and link management.

## Features

- User registration and login with JWT bearer tokens
- Create short links per user account
- List links with pagination (`limit`, `offset`)
- Update and delete only your own links
- Track click counts for each short code
- Browser UI served from FastAPI (`/home` and `/app`)
- Rate limit on link creation (`5/minute`)

## Tech Stack

- FastAPI
- SQLModel / SQLAlchemy
- SQLite (`database.db`)
- HTML, CSS, JavaScript (vanilla)
- Python 3.13

## Project Structure

```text
URL Shortener/
|- auth.py
|- database.py
|- main.py
|- models.py
|- requirements.txt
|- static/
|  |- app.js
|  `- styles.css
|- templates/
|  `- index.html
`- README.md
```

## Setup

### 1. Create and activate virtual environment

Windows (PowerShell):

```bash
python -m venv my_env
.\my_env\Scripts\activate
```

macOS/Linux:

```bash
python -m venv my_env
source my_env/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
SECRET_KEY=replace-with-a-long-random-secret
```

If `SECRET_KEY` is missing, the app uses a dev-only fallback secret.

### 4. Run the app

```bash
python -m uvicorn main:app --reload
```

Open:

- UI: http://localhost:8000/home
- UI (alt): http://localhost:8000/app
- Docs: http://localhost:8000/docs

## Auth Flow

1. Register with `POST /register`
2. Login with `POST /login` (form fields: `username`, `password`)
3. Use `Authorization: Bearer <token>` for protected endpoints

The browser UI stores and sends the token automatically after login.

## API Endpoints

### Public

- `GET /` -> redirects to `/home`
- `GET /home` -> serves UI
- `GET /app` -> serves same UI
- `POST /register` -> create user
- `POST /login` -> return JWT token
- `GET /{short_code}` -> redirect to original URL and record click

Example register body:

```json
{
  "username": "alice",
  "password": "secret123"
}
```

### Protected

- `POST /shorten_url` -> create short URL
- `GET /links` -> list your links (`?limit=10&offset=0`)
- `GET /{short_code}/stats` -> clicks for your short URL
- `PATCH /{short_code}` -> update original URL
- `DELETE /{short_code}` -> delete short URL and its clicks

Example shorten body:

```json
{
  "original_url": "https://instagram.com"
}
```

## Notes

- Database tables are created on startup.
- If `original_url` has no scheme, `https://` is automatically added.
- Short-code redirect route is intentionally defined after explicit routes.