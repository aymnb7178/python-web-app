"""Small Flask REST API for notes (in-memory storage, JSON in / JSON out).

Run:  python app.py        (http://127.0.0.1:5000/api/health)
"""
import os
from itertools import count

from flask import Flask, jsonify, request

MAX_TITLE = 100
MAX_BODY = 2000


def create_app():
    app = Flask(__name__)
    notes = {}                    # id -> note dict (lost on restart by design)
    ids = count(1)

    def error(status, message):
        return jsonify({"error": message}), status

    def validate(data, partial=False):
        """Return (clean_dict, None) or (None, error_message)."""
        if not isinstance(data, dict):
            return None, "body must be a JSON object"
        out = {}
        for field, limit in (("title", MAX_TITLE), ("body", MAX_BODY)):
            if field in data:
                v = data[field]
                if not isinstance(v, str):
                    return None, f"{field} must be a string"
                v = v.strip()
                if len(v) > limit:
                    return None, f"{field} must be at most {limit} characters"
                out[field] = v
        if not partial and not out.get("title"):
            return None, "title is required"
        if "title" in out and not out["title"]:
            return None, "title cannot be empty"
        return out, None

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "notes": len(notes)})

    @app.get("/api/notes")
    def list_notes():
        q = request.args.get("q", "").strip().lower()
        items = [n for n in notes.values()
                 if not q or q in n["title"].lower() or q in n["body"].lower()]
        return jsonify(items)

    @app.post("/api/notes")
    def create_note():
        data, err = validate(request.get_json(silent=True))
        if err:
            return error(400, err)
        note = {"id": next(ids), "title": data["title"], "body": data.get("body", "")}
        notes[note["id"]] = note
        return jsonify(note), 201

    @app.get("/api/notes/<int:note_id>")
    def get_note(note_id):
        note = notes.get(note_id)
        return jsonify(note) if note else error(404, "note not found")

    @app.patch("/api/notes/<int:note_id>")
    def update_note(note_id):
        note = notes.get(note_id)
        if not note:
            return error(404, "note not found")
        data, err = validate(request.get_json(silent=True), partial=True)
        if err:
            return error(400, err)
        note.update(data)
        return jsonify(note)

    @app.delete("/api/notes/<int:note_id>")
    def delete_note(note_id):
        if notes.pop(note_id, None) is None:
            return error(404, "note not found")
        return "", 204

    @app.errorhandler(404)
    def not_found(_e):
        return error(404, "not found")

    @app.errorhandler(405)
    def bad_method(_e):
        return error(405, "method not allowed")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1",
            host=os.environ.get("FLASK_HOST", "127.0.0.1"),
            port=int(os.environ.get("PORT", "5000")))
