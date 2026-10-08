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
