const CAPACITY = 6;
const ALLOWED_ORIGIN = "https://gabrielderinaldis321-maker.github.io";
const SCHEDULE = {
  MMA: {
    "Lunedì": ["18:00 - 19:00", "19:00 - 20:00", "20:00 - 21:00"],
    "Mercoledì": ["18:00 - 19:00", "19:00 - 20:00", "20:00 - 21:00"],
    "Venerdì": ["18:00 - 19:00", "19:00 - 20:00", "20:00 - 21:00"],
  },
  Boxe: { "Martedì": ["18:00 - 19:00"], "Giovedì": ["18:00 - 19:00"] },
  Kickboxing: { "Martedì": ["19:00 - 20:00"], "Giovedì": ["19:00 - 20:00"] },
  BJJ: { "Martedì": ["20:00 - 21:00"], "Giovedì": ["20:00 - 21:00"] },
};

function json(data, status = 200, origin = "") {
  const headers = {
    "content-type": "application/json; charset=utf-8",
    "cache-control": "no-store",
    "access-control-allow-methods": "GET, POST, OPTIONS",
    "access-control-allow-headers": "Content-Type",
    "vary": "Origin",
  };
  if (origin === ALLOWED_ORIGIN) headers["access-control-allow-origin"] = origin;
  return new Response(JSON.stringify(data), { status, headers });
}

function validWeek(value) {
  if (typeof value !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
  const date = new Date(`${value}T00:00:00Z`);
  return !Number.isNaN(date.valueOf()) && date.toISOString().slice(0, 10) === value && date.getUTCDay() === 1;
}

function validSlot(activity, day, time) {
  return typeof activity === "string" && typeof day === "string" && typeof time === "string"
    && (SCHEDULE[activity]?.[day] || []).includes(time);
}

function validName(value) {
  return typeof value === "string" && value.trim().length >= 1 && value.trim().length <= 80;
}

async function handle(request, env) {
  const origin = request.headers.get("Origin") || "";
  if (request.method === "OPTIONS") {
    if (origin !== ALLOWED_ORIGIN) return new Response(null, { status: 403 });
    return new Response(null, {
      status: 204,
      headers: {
        "access-control-allow-origin": origin,
        "access-control-allow-methods": "GET, POST, OPTIONS",
        "access-control-allow-headers": "Content-Type",
        "access-control-max-age": "86400",
        "vary": "Origin",
      },
    });
  }
  if (origin !== ALLOWED_ORIGIN) return json({ error: "Origine non autorizzata." }, 403, origin);

  const url = new URL(request.url);
  if (request.method === "GET" && url.pathname === "/api/health") return json({ ok: true }, 200, origin);
  if (request.method === "GET" && url.pathname === "/api/slots") {
    const week = url.searchParams.get("week_start");
    if (!validWeek(week)) return json({ error: "Settimana non valida." }, 400, origin);
    const rows = await env.DB.prepare(
      "SELECT activity, day_name, time_slot, COUNT(*) AS booked FROM bookings WHERE week_start = ? GROUP BY activity, day_name, time_slot",
    ).bind(week).all();
    const counts = {};
    for (const row of rows.results) counts[`${row.activity}|${row.day_name}|${row.time_slot}`] = row.booked;
    return json({ week_start: week, capacity: CAPACITY, counts }, 200, origin);
  }

  if (request.method !== "POST" || !["/api/book", "/api/cancel"].includes(url.pathname)) {
    return json({ error: "Endpoint non trovato." }, 404, origin);
  }
  if (request.headers.get("content-type")?.split(";")[0] !== "application/json") {
    return json({ error: "Formato della richiesta non valido." }, 415, origin);
  }

  let body;
  try { body = await request.json(); } catch { return json({ error: "Richiesta non valida." }, 400, origin); }
  const { week_start: week, activity, day_name: day, time_slot: time } = body || {};
  const first = typeof body?.first_name === "string" ? body.first_name.trim() : "";
  const last = typeof body?.last_name === "string" ? body.last_name.trim() : "";
  if (!validWeek(week) || !validSlot(activity, day, time)) {
    return json({ error: "Corso o settimana non validi." }, 400, origin);
  }
  if (!validName(first) || !validName(last)) return json({ error: "Nome e cognome sono obbligatori." }, 400, origin);

  if (url.pathname === "/api/book") {
    try {
      // A single conditional insert is serialized by D1 and cannot exceed six places.
      const result = await env.DB.prepare(
        `INSERT INTO bookings (week_start, activity, day_name, time_slot, first_name, last_name)
         SELECT ?, ?, ?, ?, ?, ?
         WHERE (SELECT COUNT(*) FROM bookings WHERE week_start = ? AND activity = ? AND day_name = ? AND time_slot = ?) < ?
         RETURNING id`,
      ).bind(week, activity, day, time, first, last, week, activity, day, time, CAPACITY).run();
      if (!result.meta.changes) {
        const current = await env.DB.prepare(
          "SELECT COUNT(*) AS booked FROM bookings WHERE week_start = ? AND activity = ? AND day_name = ? AND time_slot = ?",
        ).bind(week, activity, day, time).first();
        return json({ ok: false, reason: "FULL", error: "Corso completo.", booked: current.booked, remaining: 0 }, 409, origin);
      }
      const current = await env.DB.prepare(
        "SELECT COUNT(*) AS booked FROM bookings WHERE week_start = ? AND activity = ? AND day_name = ? AND time_slot = ?",
      ).bind(week, activity, day, time).first();
      return json({ ok: true, booked: current.booked, remaining: CAPACITY - current.booked }, 200, origin);
    } catch (error) {
      if (String(error).includes("UNIQUE constraint failed")) {
        return json({ error: "Hai già una prenotazione per questo corso e orario." }, 409, origin);
      }
      throw error;
    }
  }

  const removal = await env.DB.prepare(
    `DELETE FROM bookings WHERE id = (
       SELECT id FROM bookings WHERE week_start = ? AND activity = ? AND day_name = ? AND time_slot = ?
       AND first_name = ? COLLATE NOCASE AND last_name = ? COLLATE NOCASE LIMIT 1
     )`,
  ).bind(week, activity, day, time, first, last).run();
  if (!removal.meta.changes) return json({ error: "Prenotazione non trovata.", reason: "NOT_FOUND" }, 404, origin);
  const current = await env.DB.prepare(
    "SELECT COUNT(*) AS booked FROM bookings WHERE week_start = ? AND activity = ? AND day_name = ? AND time_slot = ?",
  ).bind(week, activity, day, time).first();
  return json({ ok: true, booked: current.booked, remaining: CAPACITY - current.booked }, 200, origin);
}

export default {
  fetch(request, env) {
    return handle(request, env).catch((error) => {
      console.error("Booking API failed", error?.name || "Error");
      return json({ error: "Servizio temporaneamente non disponibile." }, 500, request.headers.get("Origin") || "");
    });
  },
};

