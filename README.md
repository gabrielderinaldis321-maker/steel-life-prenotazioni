# Steel Life — prenotazioni corsi

Sito pubblico GitHub Pages collegato a un’API Cloudflare Workers e al database D1. Le prenotazioni e i posti disponibili sono condivisi tra tutti i dispositivi e restano online anche a PC spento.

## Funzioni

- Orari per MMA, Boxe, Kickboxing e BJJ.
- La sala pesi usa lo stesso database con conteggio separato e capienza di 8 persone per fascia, con orari da lunedì a sabato.
- Conteggio condiviso e aggiornato automaticamente.
- Limite massimo di 8 prenotazioni per corso, giorno, orario e settimana.
- Si possono prenotare solo i corsi del giorno corrente.
- Anche per la sala pesi si può prenotare solo una fascia della giornata corrente.
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
