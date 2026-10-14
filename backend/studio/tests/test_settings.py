"""Configuration regressions without reading local developer credentials."""
import os
import runpy
import secrets
from pathlib import Path
from unittest.mock import patch

from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase


class SettingsTests(SimpleTestCase):
    def load_settings(self, **overrides):
        environment = {"DJANGO_SECRET_KEY": secrets.token_urlsafe(64), **overrides}
        with patch.dict(os.environ, environment, clear=True), patch("dotenv.load_dotenv"):
            return runpy.run_path(Path(__file__).resolve().parents[2] / "config" / "settings.py")

    def test_secure_defaults_when_debug_is_absent(self):
        config = self.load_settings()
        self.assertFalse(config["DEBUG"])
        self.assertTrue(config["SESSION_COOKIE_SECURE"])
        self.assertTrue(config["CSRF_COOKIE_SECURE"])
        self.assertTrue(config["SECURE_SSL_REDIRECT"])

    def test_explicit_debug_allows_local_http(self):
        config = self.load_settings(DJANGO_DEBUG=" True ")
        self.assertTrue(config["DEBUG"])
        self.assertFalse(config["SESSION_COOKIE_SECURE"])
        self.assertFalse(config["SECURE_SSL_REDIRECT"])

    def test_malformed_debug_and_short_secret_fail_at_startup(self):
        with self.assertRaises(ImproperlyConfigured):
            self.load_settings(DJANGO_DEBUG="yes")
        with self.assertRaises(ImproperlyConfigured):
            self.load_settings(DJANGO_SECRET_KEY="change-me")

    def test_hosts_and_origins_trim_whitespace_and_empty_entries(self):
        config = self.load_settings(
            DJANGO_ALLOWED_HOSTS=" localhost, 127.0.0.1, ,",
            DJANGO_CSRF_TRUSTED_ORIGINS=" https://example.test, , https://www.example.test ",
        )
        self.assertEqual(config["ALLOWED_HOSTS"], ["localhost", "127.0.0.1"])
        self.assertEqual(config["CSRF_TRUSTED_ORIGINS"], ["https://example.test", "https://www.example.test"])

    def test_hosted_postgres_uses_ssl_and_keeps_connection_timeout(self):
        config = self.load_settings(DATABASE_URL="postgresql://demo:example@db.example.test:5432/demo")
        database = config["DATABASES"]["default"]
        self.assertEqual(database["ENGINE"], "django.db.backends.postgresql")
        self.assertEqual(database["OPTIONS"]["sslmode"], "require")
        self.assertEqual(database["OPTIONS"]["connect_timeout"], 5)
        self.assertTrue(database["CONN_HEALTH_CHECKS"])

    def test_sqlite_database_url_is_rejected(self):
        with self.assertRaises(ImproperlyConfigured):
            self.load_settings(DATABASE_URL="sqlite:///demo.db")

    def test_render_hostname_configures_exact_origin_and_proxy(self):
        config = self.load_settings(RENDER_EXTERNAL_HOSTNAME="demo.example.test")
        self.assertIn("demo.example.test", config["ALLOWED_HOSTS"])
        self.assertIn("https://demo.example.test", config["CSRF_TRUSTED_ORIGINS"])
        self.assertEqual(config["SECURE_PROXY_SSL_HEADER"], ("HTTP_X_FORWARDED_PROTO", "https"))
        self.assertNotIn("SECURE_PROXY_SSL_HEADER", self.load_settings())

    def test_wildcards_and_malformed_origins_are_rejected(self):
        for override in (
            {"DJANGO_ALLOWED_HOSTS": "*"},
            {"DJANGO_CSRF_TRUSTED_ORIGINS": "https://*.example.test"},
            {"DJANGO_CSRF_TRUSTED_ORIGINS": "https://example.test/path"},
            {"RENDER_EXTERNAL_HOSTNAME": "https://example.test"},
            {"DJANGO_TRUST_PROXY": "yes"},
        ):
            with self.subTest(override=override), self.assertRaises(ImproperlyConfigured):
                self.load_settings(**override)

    def test_local_docker_http_can_keep_debug_disabled(self):
        config = self.load_settings(DJANGO_DEBUG="False", DJANGO_HTTPS="False")
        self.assertFalse(config["DEBUG"])
        self.assertFalse(config["SECURE_SSL_REDIRECT"])
        self.assertFalse(config["SESSION_COOKIE_SECURE"])
        self.assertEqual(config["SECURE_HSTS_SECONDS"], 0)
