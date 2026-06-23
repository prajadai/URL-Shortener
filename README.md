# URL Shortener
A link shortening API built with FastAPI and SQLModel.
 
> Built as a learning project to practice REST API design, database modeling, and Python backend development.
 
---
 
## Tech Stack
- **FastAPI** — API framework
- **SQLModel** — ORM and database modeling
- **SQLite** — local database
- **Python 3.13**
---
 
## Getting Started
 
### 1. Clone the repository
```bash
git clone https://github.com/prajadai/URL-Shortener.git
cd url-shortener
```
 
### 2. Create and activate virtual environment
```bash
uv venv my_env
my_env\Scripts\activate  # Windows
source my_env/bin/activate  # Mac/Linux
```
 
### 3. Install dependencies
```bash
uv pip install -r requirements.txt
```
 
### 4. Run the development server
```bash
uv run fastapi dev main.py --reload
```
 
The API will be available at `http://localhost:8000`  
Interactive docs at `http://localhost:8000/docs`
 
---
 
## API Endpoints
 
### `POST /shorten_url`
Takes a long URL and returns a shortened version.
 
**Request body:**
```json
{
  "original_url": "https://instagram.com"
}
```
 
**Response:**
```json
{
  "id": 1,
  "original_url": "https://instagram.com",
  "short_code": "Kd9mXz",
  "created_at": "2024-01-01T00:00:00"
}
```
 
---
 
### `GET /{short_code}`
Redirects the user to the original URL.
 
**Example:** visiting `http://localhost:8000/Kd9mXz` redirects to `https://instagram.com`
 
Returns `404` if the short code does not exist.
 
---
 
## Project Structure
```
url-shortener/
├── main.py          # FastAPI app and endpoints
├── models.py        # SQLModel database models
├── database.py      # Database connection and setup
├── requirements.txt
├── .gitignore
└── README.md
```