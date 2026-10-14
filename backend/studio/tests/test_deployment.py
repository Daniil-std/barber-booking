from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.db import OperationalError
from django.test import Client, SimpleTestCase, TestCase, override_settings


@override_settings(SECURE_SSL_REDIRECT=False)
class HealthTests(TestCase):
    def test_health_is_public_and_checks_database(self):
        response = self.client.get("/api/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
        self.assertIn("no-store", response["Cache-Control"])

    def test_database_failure_is_redacted(self):
        with patch("studio.views.connection.cursor", side_effect=OperationalError("private connection information")):
            response = self.client.get("/api/health/")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"status": "unavailable"})

    def test_health_does_not_redirect_private_http_probes(self):
        with override_settings(SECURE_SSL_REDIRECT=True):
            self.assertEqual(Client().get("/api/health/").status_code, 200)
            self.assertEqual(Client().get("/").status_code, 301)


@override_settings(SECURE_SSL_REDIRECT=False)
class FrontendServingTests(SimpleTestCase):
    def test_frontend_assets_and_reserved_routes(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "index.html").write_text('<div id="root"></div>', encoding="utf-8")
            (root / "assets").mkdir()
            (root / "assets" / "demo-abcdefgh.js").write_text("/* asset */", encoding="utf-8")
            with override_settings(FRONTEND_DIST=root, WHITENOISE_ROOT=root):
                client = Client()
                index = client.get("/")
                self.assertEqual(index.status_code, 200)
                self.assertIn(b'id="root"', b"".join(index.streaming_content))
                self.assertIn("no-store", index["Cache-Control"])
                asset = client.get("/assets/demo-abcdefgh.js")
                b"".join(asset.streaming_content)
                asset.close()
                self.assertEqual(asset.status_code, 200)
                self.assertIn("immutable", asset["Cache-Control"])
                self.assertEqual(client.get("/api/not-a-route/").status_code, 404)
                self.assertEqual(client.get("/admin/").status_code, 302)

    def test_missing_frontend_build_is_explicit(self):
        with TemporaryDirectory() as directory, override_settings(FRONTEND_DIST=Path(directory)):
            response = Client().get("/")
            self.assertEqual(response.status_code, 503)
            self.assertEqual(response.json(), {"status": "frontend_unavailable"})
