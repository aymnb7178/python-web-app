# python-web-app

A small **Flask REST API** for notes: create, read, update, delete and search, with JSON input validation and JSON error responses.

> Written with AI assistance (Claude), reviewed and published by the repository owner.

## Run

```bash
pip install -r requirements.txt
python app.py                         # http://127.0.0.1:5000
python -m unittest -v                 # 7 tests
```

Debug mode is off and the server listens on `127.0.0.1` only unless you opt in with `FLASK_DEBUG=1` / `FLASK_HOST=0.0.0.0`.

## Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/api/health` | `{"status":"ok","notes":<count>}` |
| GET | `/api/notes?q=text` | list notes, optional case-insensitive search in title/body |
| POST | `/api/notes` | create; JSON `{"title": "...", "body": "..."}` (title required, max 100; body max 2000) |
| GET | `/api/notes/<id>` | one note |
| PATCH | `/api/notes/<id>` | change title and/or body |
| DELETE | `/api/notes/<id>` | delete (204) |

Errors are JSON: `{"error": "..."}` with 400 (invalid input), 404 or 405.

```bash
curl -X POST localhost:5000/api/notes -H 'Content-Type: application/json' -d '{"title":"Hello","body":"first note"}'
curl localhost:5000/api/notes?q=hello
```

## Verified

- ✅ 7 tests with Flask's test client: full CRUD flow, ids never reused, validation (missing/blank/wrong-type/too-long/invalid JSON/non-object), search, JSON 404/405 errors, isolated stores per app instance.
- 🟡 The curl examples were not run against a live server (the test client exercises the same routes).

## Limits

Notes are stored **in memory** and disappear on restart; no authentication, no pagination. A database (see [todo-app-flask](https://github.com/aymnb7178/todo-app-flask) for a SQLite example) would be the next step.

## Author

Aymen - [github.com/aymnb7178](https://github.com/aymnb7178)
