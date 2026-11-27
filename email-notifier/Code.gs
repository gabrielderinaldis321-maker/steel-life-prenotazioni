function doPost(e) {
  const properties = PropertiesService.getScriptProperties();
  const expectedSecret = properties.getProperty("EMAIL_WEBHOOK_SECRET");
  const recipient = properties.getProperty("NOTIFY_EMAIL");
  let payload;

  try {
    payload = JSON.parse(e?.postData?.contents || "{}");
  } catch {
    return jsonOutput({ ok: false, reason: "invalid_json" });
  }

  if (!expectedSecret || !recipient || payload.secret !== expectedSecret) {
    return jsonOutput({ ok: false, reason: "unauthorized_or_unconfigured" });
  }

  const booking = payload.booking || {};
  const fields = ["first_name", "last_name", "activity", "day_name", "time_slot"];
  if (fields.some((field) => typeof booking[field] !== "string" || !booking[field].trim())) {
    return jsonOutput({ ok: false, reason: "invalid_booking" });
  }

  try {
    if (MailApp.getRemainingDailyQuota() < 1) {
      return jsonOutput({ ok: false, reason: "daily_quota_reached" });
    }

    const subject = `Prenotazione palestra · ${booking.activity} · ${booking.day_name} ${booking.time_slot}`;
    const body = [
      "È stata registrata una nuova prenotazione.",
      "",
      `Nome: ${booking.first_name} ${booking.last_name}`,
      `Corso: ${booking.activity}`,
      `Giorno: ${booking.day_name}`,
      `Orario: ${booking.time_slot}`,
      "",
      "Il posto è stato salvato nel database condiviso.",
    ].join("\n");

    MailApp.sendEmail({ to: recipient, subject, body });
    return jsonOutput({ ok: true });
  } catch (error) {
    console.error("Invio notifica email non riuscito:", error?.name || "Error");
    return jsonOutput({ ok: false, reason: "send_failed" });
  }
}

function jsonOutput(value) {
  return ContentService.createTextOutput(JSON.stringify(value))
    .setMimeType(ContentService.MimeType.JSON);
}
