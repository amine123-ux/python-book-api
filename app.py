
"""Small REST API for a book collection using Flask and SQLite."""

import os
import sqlite3
from pathlib import Path
from flask import Flask, jsonify, request, g


def create_app(test_config=None):
    app = Flask(__name__)

    app.config.update(
        DATABASE=os.environ.get(
            "BOOK_API_DATABASE",
            str(Path(__file__).with_name("books.db"))
        ),
        TESTING=False,
    )

    if test_config:
        app.config.update(test_config)

    def connect_db():
        db = sqlite3.connect(app.config["DATABASE"])
        db.row_factory = sqlite3.Row

        db.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                year INTEGER,
                UNIQUE(title, author)
            )
        """)

        return db

    def get_db():
        if "database" not in g:
            g.database = connect_db()
        return g.database

    @app.teardown_appcontext
    def close_db(exception=None):
        db = g.pop("database", None)
        if db is not None:
            db.close()

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/api/books")
    def list_books():
        query = request.args.get("q", "").strip()
        db = get_db()

        if query:
            rows = db.execute(
                "SELECT * FROM books "
                "WHERE title LIKE ? OR author LIKE ? ORDER BY title",
                (f"%{query}%", f"%{query}%")
            ).fetchall()
        else:
            rows = db.execute(
                "SELECT * FROM books ORDER BY title"
            ).fetchall()

        return jsonify([dict(row) for row in rows])

    @app.get("/api/books/<int:book_id>")
    def get_book(book_id):
        row = get_db().execute(
            "SELECT * FROM books WHERE id = ?", (book_id,)
        ).fetchone()

        if row is None:
            return jsonify({"error": "Book not found"}), 404

        return jsonify(dict(row))

    @app.post("/api/books")
    def create_book():
        payload = request.get_json(silent=True) or {}
        title = payload.get("title", "")
        author = payload.get("author", "")
        year = payload.get("year")

        if not isinstance(title, str) or not title.strip():
            return jsonify({"error": "title is required"}), 400

        if not isinstance(author, str) or not author.strip():
            return jsonify({"error": "author is required"}), 400

        if year is not None and (
            not isinstance(year, int)
            or isinstance(year, bool)
            or year < 0
            or year > 2100
        ):
            return jsonify({
                "error": "year must be a valid integer between 0 and 2100"
            }), 400

        db = get_db()

        try:
            cursor = db.execute(
                "INSERT INTO books (title, author, year) VALUES (?, ?, ?)",
                (title.strip(), author.strip(), year)
            )

            row = db.execute(
                "SELECT * FROM books WHERE id = ?",
                (cursor.lastrowid,)
            ).fetchone()

            db.commit()
            return jsonify(dict(row)), 201

        except sqlite3.IntegrityError:
            db.rollback()
            return jsonify({
                "error": "This title and author already exist"
            }), 409

    @app.delete("/api/books/<int:book_id>")
    def delete_book(book_id):
        db = get_db()
        cursor = db.execute(
            "DELETE FROM books WHERE id = ?", (book_id,)
        )
        db.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Book not found"}), 404

        return "", 204

    return app


if __name__ == "__main__":
    create_app().run(debug=False)
