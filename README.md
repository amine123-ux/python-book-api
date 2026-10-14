# Python Book REST API

A small REST API for creating, listing, searching, retrieving, and deleting books. Flask handles HTTP routes and SQLite persists records.

## Endpoints
| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Check service health |
| GET | `/api/books` | List books |
| GET | `/api/books?q=clean` | Search title or author |
| GET | `/api/books/<id>` | Retrieve one book |
| POST | `/api/books` | Create a book |
| DELETE | `/api/books/<id>` | Delete a book |

## Requirements and setup
Python 3.10+ recommended.
```bash
python -m venv .venv
# Windows PowerShell:
.venv\\Scripts\\Activate.ps1
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
```

## Run
```bash
python app.py
```
Service runs at `http://127.0.0.1:5000`.

Example create request:
```bash
curl -X POST http://127.0.0.1:5000/api/books ^
  -H "Content-Type: application/json" ^
  -d "{\\"title\\":\\"Clean Code\\",\\"author\\":\\"Robert Martin\\",\\"year\\":2008}"
```
On macOS/Linux, replace `^` with `\\` at the end of continued lines, or send the request as one line.

## Tests
```bash
python -m unittest discover -s tests -v
```

## Engineering notes
- Uses parameterised SQL statements to avoid SQL injection through user-supplied search text.
- Validates request payloads and returns appropriate HTTP status codes.
- Uses a unique constraint to prevent duplicate title/author pairs.
- Database path can be configured using `BOOK_API_DATABASE`.

## Resume bullet examples — only after you run and understand the project
- Built a Flask REST API backed by SQLite to create, search, retrieve, and delete book records through HTTP endpoints.
- Implemented request validation, parameterised SQL queries, duplicate-record handling, and REST status codes including `201`, `400`, `404`, and `409`.
- Wrote automated endpoint tests covering creation, search, validation failures, duplicate records, and deletion.
