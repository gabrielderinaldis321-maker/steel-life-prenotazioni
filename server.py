"""Small SQLite-backed booking API for the Steel Life GitHub Pages site."""
from __future__ import annotations

import json
import os
import sqlite3
from contextlib import closing
from datetime import date, datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from zoneinfo import ZoneInfo
from urllib.parse import parse_qs, urlparse

HOST = "127.0.0.1"  # cloudflared connects locally; do not bind to the public network
PORT = int(os.environ.get("STEEL_LIFE_PORT", "8765"))
DB_PATH = Path(__file__).with_name("bookings.sqlite3")
ALLOWED_ORIGINS = {
    item.strip().rstrip("/")
    for item in os.environ.get(
        "STEEL_LIFE_ALLOWED_ORIGINS",
        "https://gabrielderinaldis321-maker.github.io,http://localhost:8765",
    ).split(",")
    if item.strip()
}
CAPACITY = 8
SALA_PESI_CAPACITY = 8
SCHEDULE = {
    "MMA": {
        "Lunedì": ("18:00 - 19:00", "19:00 - 20:00", "20:00 - 21:00"),
        "Mercoledì": ("18:00 - 19:00", "19:00 - 20:00", "20:00 - 21:00"),
        "Venerdì": ("18:00 - 19:00", "19:00 - 20:00", "20:00 - 21:00"),
    },
    "Boxe": {"Martedì": ("18:00 - 19:00",), "Giovedì": ("18:00 - 19:00",)},
    "Kickboxing": {"Martedì": ("19:00 - 20:00",), "Giovedì": ("19:00 - 20:00",)},
    "BJJ": {"Martedì": ("20:00 - 21:00",), "Giovedì": ("20:00 - 21:00",)},
    "Sala Pesi": {
        "Lunedì": tuple(f"{hour:02d}:00 - {hour + 1:02d}:00" for hour in range(7, 21)),
        "Martedì": tuple(f"{hour:02d}:00 - {hour + 1:02d}:00" for hour in range(7, 21)),
        "Mercoledì": tuple(f"{hour:02d}:00 - {hour + 1:02d}:00" for hour in range(7, 21)),
        "Giovedì": tuple(f"{hour:02d}:00 - {hour + 1:02d}:00" for hour in range(7, 21)),
        "Venerdì": tuple(f"{hour:02d}:00 - {hour + 1:02d}:00" for hour in range(7, 21)),
        "Sabato": tuple(f"{hour:02d}:00 - {hour + 1:02d}:00" for hour in range(7, 13)),
    },
}


def capacity_for(activity: str) -> int:
    return SALA_PESI_CAPACITY if activity == "Sala Pesi" else CAPACITY


def connect() -> sqlite3.Connection:
    db = sqlite3.connect(DB_PATH, timeout=15, isolation_level=None)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA busy_timeout = 15000")
    return db


def initialize() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with closing(connect()) as db:
        db.execute("PRAGMA journal_mode = WAL")
        db.execute(
            """CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY,
                week_start TEXT NOT NULL,
                activity TEXT NOT NULL,
                day_name TEXT NOT NULL,
                time_slot TEXT NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )"""
        )
        db.execute(
            """CREATE INDEX IF NOT EXISTS bookings_slot_idx
               ON bookings(week_start, activity, day_name, time_slot)"""
        )
        db.execute(
            """CREATE UNIQUE INDEX IF NOT EXISTS bookings_person_slot_idx
               ON bookings(week_start, activity, day_name, time_slot,
                           first_name COLLATE NOCASE, last_name COLLATE NOCASE)"""
        )
        today = date.today()
        week_start = (today - timedelta(days=today.weekday())).isoformat()
        db.execute("DELETE FROM bookings WHERE week_start < ?", (week_start,))


def valid_week(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        return None
    return value if parsed.weekday() == 0 else None


def valid_slot(activity: object, day_name: object, time_slot: object) -> bool:
    return (
        isinstance(activity, str)
        and isinstance(day_name, str)
        and isinstance(time_slot, str)
        and time_slot in SCHEDULE.get(activity, {}).get(day_name, ())
    )


def booking_window_error(week: str, day_name: str, time_slot: str, activity: str) -> str | None:
    offsets = {"Lunedì": 0, "Martedì": 1, "Mercoledì": 2, "Giovedì": 3, "Venerdì": 4, "Sabato": 5}
    year, month, day = map(int, week.split("-"))
    start_hour, start_minute = map(int, time_slot[:5].split(":"))
    class_date = date(year, month, day) + timedelta(days=offsets[day_name])
    now = datetime.now(ZoneInfo("Europe/Rome"))
    if class_date < now.date():
        return "Non puoi prenotare una fascia oraria già passata."
    if class_date != now.date():
        return "Puoi prenotare solo le fasce di oggi."
    starts_at = datetime(class_date.year, class_date.month, class_date.day, start_hour, start_minute, tzinfo=ZoneInfo("Europe/Rome"))
    if starts_at <= now:
        return "Questo orario è già passato."
    return None


class BookingHandler(BaseHTTPRequestHandler):
    server_version = "SteelLifeAPI/1.0"
    max_body_bytes = 4096

    def log_message(self, fmt: str, *args: object) -> None:
        # Avoid writing names or booking form data to the terminal log.
        print(f"{self.log_date_time_string()} {self.address_string()} {fmt % args}")

    def _headers(self, status: int = 200) -> None:
        origin = self.headers.get("Origin", "").rstrip("/")
        self.send_response(status)
        if origin in ALLOWED_ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")

    def _json(self, body: dict, status: int = 200) -> None:
        raw = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self._headers(status)
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _read_body(self) -> dict:
        size = int(self.headers.get("Content-Length", "0"))
        if size < 2 or size > self.max_body_bytes:
            raise ValueError("Richiesta non valida.")
        value = json.loads(self.rfile.read(size).decode("utf-8"))
        if not isinstance(value, dict):
            raise ValueError("Richiesta non valida.")
        return value

    def do_OPTIONS(self) -> None:
        self._headers(204)
        self.end_headers()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/health":
            self._json({"ok": True})
            return
        if parsed.path != "/api/slots":
            self._json({"error": "Endpoint non trovato."}, 404)
            return
        week = valid_week(parse_qs(parsed.query).get("week_start", [None])[0])
        if not week:
            self._json({"error": "Settimana non valida."}, 400)
            return
        with closing(connect()) as db:
            rows = db.execute(
                """SELECT activity, day_name, time_slot, COUNT(*) AS booked
                   FROM bookings WHERE week_start = ?
                   GROUP BY activity, day_name, time_slot""",
                (week,),
            ).fetchall()
        counts = {
            f"{row['activity']}|{row['day_name']}|{row['time_slot']}": row["booked"]
            for row in rows
        }
        self._json({"week_start": week, "capacity": CAPACITY, "counts": counts})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        try:
            origin = self.headers.get("Origin", "").rstrip("/")
            if origin not in ALLOWED_ORIGINS:
                self._json({"error": "Origine non autorizzata."}, 403)
                return
            if self.headers.get_content_type() != "application/json":
                self._json({"error": "Formato richiesta non valido."}, 415)
                return
            body = self._read_body()
            week = valid_week(body.get("week_start"))
            activity = body.get("activity")
            day_name = body.get("day_name")
            time_slot = body.get("time_slot")
            first = body.get("first_name")
            last = body.get("last_name")
            if not week or not valid_slot(activity, day_name, time_slot):
                self._json({"error": "Corso o settimana non validi."}, 400)
                return
            if not isinstance(first, str) or not isinstance(last, str):
                self._json({"error": "Inserisci nome e cognome."}, 400)
                return
            first, last = first.strip(), last.strip()
            if not (1 <= len(first) <= 80 and 1 <= len(last) <= 80):
                self._json({"error": "Nome e cognome devono contenere da 1 a 80 caratteri."}, 400)
                return

            if parsed.path == "/api/book":
                window_error = booking_window_error(week, day_name, time_slot, activity)
                if window_error:
                    self._json({"ok": False, "reason": "BOOKING_WINDOW", "error": window_error}, 409)
                    return
                result = self._book(week, activity, day_name, time_slot, first, last)
                self._json(result, 200 if result["ok"] else 409)
            elif parsed.path == "/api/cancel":
                result = self._cancel(week, activity, day_name, time_slot, first, last)
                self._json(result, 200 if result["ok"] else 404)
            else:
                self._json({"error": "Endpoint non trovato."}, 404)
        except (ValueError, json.JSONDecodeError):
            self._json({"error": "Richiesta non valida."}, 400)
        except sqlite3.IntegrityError:
            self._json({"ok": False, "reason": "ALREADY_BOOKED", "error": "Hai già prenotato questo slot."}, 409)
        except Exception:
            self._json({"error": "Errore temporaneo del servizio."}, 500)

    @staticmethod
    def _book(week: str, activity: str, day_name: str, time_slot: str, first: str, last: str) -> dict:
        with closing(connect()) as db:
            db.execute("BEGIN IMMEDIATE")
            count = db.execute(
                "SELECT COUNT(*) FROM bookings WHERE week_start=? AND activity=? AND day_name=? AND time_slot=?",
                (week, activity, day_name, time_slot),
            ).fetchone()[0]
            capacity = capacity_for(activity)
            if count >= capacity:
                db.rollback()
                return {"ok": False, "reason": "FULL", "booked": count, "remaining": 0}
            cursor = db.execute(
                """INSERT INTO bookings(week_start,activity,day_name,time_slot,first_name,last_name)
                   VALUES(?,?,?,?,?,?)""",
                (week, activity, day_name, time_slot, first, last),
            )
            count += 1
            db.commit()
            return {"ok": True, "booking_id": cursor.lastrowid, "booked": count, "remaining": capacity-count}

    @staticmethod
    def _cancel(week: str, activity: str, day_name: str, time_slot: str, first: str, last: str) -> dict:
        with closing(connect()) as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute(
                """SELECT id FROM bookings WHERE week_start=? AND activity=? AND day_name=? AND time_slot=?
                   AND first_name=? COLLATE NOCASE AND last_name=? COLLATE NOCASE LIMIT 1""",
                (week, activity, day_name, time_slot, first, last),
            ).fetchone()
            if row is None:
                db.rollback()
                return {"ok": False, "reason": "NOT_FOUND"}
            db.execute("DELETE FROM bookings WHERE id=?", (row["id"],))
            count = db.execute(
                "SELECT COUNT(*) FROM bookings WHERE week_start=? AND activity=? AND day_name=? AND time_slot=?",
                (week, activity, day_name, time_slot),
            ).fetchone()[0]
            db.commit()
            return {"ok": True, "booked": count, "remaining": capacity_for(activity)-count}


if __name__ == "__main__":
    initialize()
    print(f"Steel Life API in ascolto su http://{HOST}:{PORT}")
    print(f"Database SQLite: {DB_PATH}")
    ThreadingHTTPServer((HOST, PORT), BookingHandler).serve_forever()
