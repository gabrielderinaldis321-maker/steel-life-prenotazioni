# Steel Life — prenotazioni corsi

Sito pubblico GitHub Pages collegato a un’API Cloudflare Workers e al database D1. Le prenotazioni e i posti disponibili sono condivisi tra tutti i dispositivi e restano online anche a PC spento.

## Funzioni

- Orari per MMA, Boxe, Kickboxing e BJJ.
- Conteggio condiviso e aggiornato automaticamente.
- Limite massimo di 8 prenotazioni per corso, giorno, orario e settimana.
- I turni che iniziano alle 19:00 si aprono 48 ore prima; ogni persona può prenotarli al massimo 2 volte a settimana.
- Dopo una prenotazione riuscita si apre WhatsApp al proprietario (**+39 328 181 4024**) con il messaggio già compilato.
- Le disdette aggiornano il conteggio condiviso e aprono WhatsApp.

## Servizi pubblici

- Sito: https://gabrielderinaldis321-maker.github.io/steel-life-prenotazioni/
- API: https://steel-life-prenotazioni-api.gabrielderinaldis321.workers.dev

## File

- `index.html`: pagina pubblica.
- `cloudflare-worker/src/index.js`: API delle prenotazioni.
- `cloudflare-worker/migrations/0001_create_bookings.sql`: schema D1.
- `cloudflare-worker/wrangler.toml`: configurazione del Worker e del database.
- `CLOUDFLARE-D1-GUIDA.md`: procedura di configurazione.

Il codice è in una repository pubblica. Non inserire password o chiavi API nei file.

