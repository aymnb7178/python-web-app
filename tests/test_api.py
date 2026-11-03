import unittest

from app import create_app


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.c = create_app().test_client()

    def make(self, **kw):
        return self.c.post("/api/notes", json=kw)

    def test_health(self):
        r = self.c.get("/api/health")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["status"], "ok")

    def test_crud_flow(self):
        r = self.make(title="  Shopping ", body="milk")
        self.assertEqual(r.status_code, 201)
        note = r.get_json()
        self.assertEqual(note, {"id": 1, "title": "Shopping", "body": "milk"})
        self.assertEqual(self.c.get("/api/notes/1").get_json(), note)
        r = self.c.patch("/api/notes/1", json={"body": "milk, eggs"})
        self.assertEqual(r.get_json()["body"], "milk, eggs")
        self.assertEqual(r.get_json()["title"], "Shopping")
        self.assertEqual(self.c.delete("/api/notes/1").status_code, 204)
        self.assertEqual(self.c.get("/api/notes/1").status_code, 404)

    def test_ids_are_not_reused(self):
        self.make(title="a")
        self.c.delete("/api/notes/1")
        self.assertEqual(self.make(title="b").get_json()["id"], 2)

    def test_validation_errors(self):
        self.assertEqual(self.make().status_code, 400)
        self.assertEqual(self.make(title="  ").status_code, 400)
        self.assertEqual(self.make(title=5).status_code, 400)
        self.assertEqual(self.make(title="x" * 101).status_code, 400)
        self.assertEqual(self.c.post("/api/notes", data="not json").status_code, 400)
        self.assertEqual(self.c.post("/api/notes", json=[1, 2]).status_code, 400)
        self.make(title="ok")
        self.assertEqual(self.c.patch("/api/notes/1", json={"title": ""}).status_code, 400)

    def test_search(self):
        self.make(title="Python tips", body="use venv")
        self.make(title="Groceries", body="apples")
        titles = [n["title"] for n in self.c.get("/api/notes?q=PYTHON").get_json()]
        self.assertEqual(titles, ["Python tips"])
        self.assertEqual(len(self.c.get("/api/notes").get_json()), 2)

    def test_errors_are_json(self):
        r = self.c.get("/api/nope")
        self.assertEqual(r.status_code, 404)
        self.assertIn("error", r.get_json())
        self.assertEqual(self.c.put("/api/notes").status_code, 405)
        self.assertIn("error", self.c.put("/api/notes").get_json())
        self.assertEqual(self.c.delete("/api/notes/99").status_code, 404)

    def test_stores_are_isolated_per_app(self):
        self.make(title="mine")
        other = create_app().test_client()
        self.assertEqual(other.get("/api/notes").get_json(), [])


if __name__ == "__main__":
    unittest.main()
