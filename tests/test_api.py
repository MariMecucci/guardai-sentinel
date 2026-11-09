import unittest

try:
    from fastapi.testclient import TestClient
    from sentinel.api import app
except ImportError:
    TestClient = None
    app = None


@unittest.skipIf(TestClient is None, "Install fastapi and httpx for API integration tests")
class ApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health(self):
        r = self.client.get("/health")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["status"], "ok")

    def test_analyze(self):
        r = self.client.post("/analyze", json={"filename": "example.py", "source": "q = f'SELECT * FROM users WHERE name={name}'"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["finding_count"], 1)

    def test_invalid_file(self):
        r = self.client.post("/analyze", json={"filename": "wrong.txt", "source": "anything"})
        self.assertEqual(r.status_code, 422)

    def test_no_code_execution(self):
        r = self.client.post("/analyze", json={"filename": "injection.py", "source": "raise RuntimeError('never execute')"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["finding_count"], 0)


if __name__ == "__main__":
    unittest.main()
