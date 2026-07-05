# URL Shortener

A URL shortening API built with FastAPI, SQLModel, and SQLite.

This project includes user registration and JWT-based authentication so each user can manage their own links. The database is created automatically on startup as database.db.

## Tech Stack

- FastAPI for the API layer
- SQLModel and SQLAlchemy for ORM and database access
- SQLite for local storage
- Python 3.13

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/prajadai/URL-Shortener.git
cd URL-Shortener
```

### 2. Create and activate a virtual environment

```bash
python -m venv my_env
my_env\Scripts\activate
```

On macOS or Linux:

```bash
source my_env/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the server

```bash
uvicorn main:app --reload
```

The API will be available at http://localhost:8000.
Interactive docs are available at http://localhost:8000/docs.

## Authentication Flow

1. Register a user with `POST /register`.
2. Log in with `POST /login` using form data.
3. Include `Authorization: Bearer <token>` on protected requests.

## API Endpoints

### Public

`POST /register`

Creates a new user.

Request body:

```json
{
  "username": "alice",
  "password": "secret123"
}
```

`POST /login`

Returns a bearer token for the supplied username and password.

`GET /{short_code}`

Redirects to the original URL and records a click.

### Protected

`POST /shorten_url`

Creates a shortened link for the signed-in user.

Request body:

```json
{
  "original_url": "https://instagram.com"
}
```

`GET /links`

Lists the current user's links.

`GET /{short_code}/stats`

Returns click statistics for one of the current user's links.

`PATCH /{short_code}`

Updates the original URL for one of the current user's links.

`DELETE /{short_code}`

Deletes one of the current user's links and its click records.

## Notes

- The database is created automatically on startup as `database.db`.
- Short URLs are normalized to include `https://` when the scheme is omitted.

## Project Structure

```text
URL Shortener/
├── auth.py
├── database.py
├── main.py
├── models.py
├── requirements.txt
└── README.md
```