"""Check a real same-origin build; optional fictional booking/cancellation exercise."""
import argparse
from datetime import date, timedelta
from http.cookiejar import CookieJar
import json
import re
import secrets
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPCookieProcessor, Request, build_opener


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("origin")
    parser.add_argument("--exercise-bookings", action="store_true", help="Creates one fictional account and two cancelled visits; never deletes existing data.")
    args = parser.parse_args()
    origin = args.origin.rstrip("/")
    parsed = urlsplit(origin)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.path:
        parser.error("Supply an HTTP(S) origin without a path.")
    opener = build_opener(HTTPCookieProcessor(CookieJar()))
    csrf = ""

    def request(path, data=None):
        nonlocal csrf
        headers = {"Accept": "application/json", "Origin": origin}
        if data is not None:
            headers.update({"Content-Type": "application/json", "X-CSRFToken": csrf})
        with opener.open(Request(origin + path, data=None if data is None else json.dumps(data).encode(), headers=headers), timeout=15) as response:
            payload = response.read()
            if "application/json" in response.headers.get("Content-Type", ""):
                body = json.loads(payload)
                if isinstance(body, dict):
                    csrf = body.get("csrfToken", csrf)
                return body
            return payload

    assert request("/api/health/") == {"status": "ok"}
    html = request("/").decode()
    assert 'id="root"' in html
    assets = re.findall(r'(?:src|href)="(/assets/[^"]+)"', html)
    assert assets, "No production assets in index.html"
    for path in assets + ["/favicon.svg", "/images/studio.jpg", "/static/admin/css/base.css"]:
        assert request(path), f"Missing asset: {path}"
    catalog = request("/api/catalog/")
    assert len(catalog["services"]) >= 5 and len(catalog["barbers"]) >= 4
    print("PASS: health, React index, production assets, Admin CSS, real catalog")
    if not args.exercise_bookings:
        return
    email = "demo-" + secrets.token_hex(8) + "@example.test"
    password = secrets.token_urlsafe(24)
    request("/api/auth/session/")
    session = request("/api/auth/register/", {"first_name": "Demo Visitor", "email": email, "password": password})
    assert session["user"]["email"] == email
    request("/api/auth/logout/", {})
    assert request("/api/auth/login/", {"email": email, "password": password})["user"]
    for training in (False, True):
        service = next(item for item in catalog["services"] if item["is_training"] == training)
        barber = next(item for item in catalog["barbers"] if service["id"] in item["services"])
        starts_at = None
        for offset in range(1, 8):
            day = date.fromisoformat(catalog["today"]) + timedelta(days=offset)
            path = "/api/availability/?" + urlencode({"service": service["id"], "barber": barber["id"], "date": day.isoformat()})
            slots = request(path)["slots"]
            if slots:
                starts_at = slots[0]
                break
        assert starts_at, "No available seeded appointment within seven days"
        visit = request("/api/appointments/", {
            "service": service["id"], "barber": barber["id"], "starts_at": starts_at,
            "contact_name": "Demo Visitor", "contact_email": email,
            "contact_phone": "+48 555 010 123", "notes": "Fictional smoke-check details",
        })
        assert visit["status"] == "confirmed"
        if training:
            assert visit.get("supervisor"), "Training supervisor not saved"
        assert any(item["id"] == visit["id"] for item in request("/api/appointments/"))
        assert request(f'/api/appointments/{visit["id"]}/cancel/', {})["status"] == "cancelled"
        assert starts_at in request(path)["slots"]
        print("PASS: " + ("training + supervisor" if training else "regular") + " booking, account listing, cancellation, released availability")
    request("/api/auth/logout/", {})
    print("PASS: registration, logout, login; fictional account and cancelled records retained")


if __name__ == "__main__":
    main()
