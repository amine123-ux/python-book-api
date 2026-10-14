import tempfile
import unittest
from pathlib import Path
from app import create_app

class BookApiTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.app = create_app({"TESTING": True, "DATABASE": str(Path(self.temp_dir.name) / "test.db")})
        self.client = self.app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(200, response.status_code)
        self.assertEqual({"status": "ok"}, response.get_json())

    def test_create_and_get_book(self):
        response = self.client.post("/api/books", json={"title": "Clean Code", "author": "Robert Martin", "year": 2008})
        self.assertEqual(201, response.status_code)
        book_id = response.get_json()["id"]
        detail = self.client.get(f"/api/books/{book_id}")
        self.assertEqual(200, detail.status_code)
        self.assertEqual("Clean Code", detail.get_json()["title"])

    def test_validation_rejects_blank_title(self):
        response = self.client.post("/api/books", json={"title": " ", "author": "Someone"})
        self.assertEqual(400, response.status_code)

    def test_duplicate_book_returns_conflict(self):
        payload = {"title": "Clean Code", "author": "Robert Martin"}
        self.client.post("/api/books", json=payload)
        response = self.client.post("/api/books", json=payload)
        self.assertEqual(409, response.status_code)

    def test_search_and_delete(self):
        self.client.post("/api/books", json={"title": "Clean Code", "author": "Robert Martin"})
        response = self.client.get("/api/books?q=clean")
        self.assertEqual(1, len(response.get_json()))
        book_id = response.get_json()[0]["id"]
        self.assertEqual(204, self.client.delete(f"/api/books/{book_id}").status_code)
        self.assertEqual(404, self.client.get(f"/api/books/{book_id}").status_code)

if __name__ == "__main__":
    unittest.main()
