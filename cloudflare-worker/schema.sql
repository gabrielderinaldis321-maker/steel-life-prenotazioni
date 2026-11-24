CREATE TABLE IF NOT EXISTS bookings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  week_start TEXT NOT NULL,
  activity TEXT NOT NULL,
  day_name TEXT NOT NULL,
  time_slot TEXT NOT NULL,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS bookings_slot_idx
  ON bookings (week_start, activity, day_name, time_slot);

CREATE UNIQUE INDEX IF NOT EXISTS bookings_person_slot_idx
  ON bookings (week_start, activity, day_name, time_slot, first_name COLLATE NOCASE, last_name COLLATE NOCASE);

