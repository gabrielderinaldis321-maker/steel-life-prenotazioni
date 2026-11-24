# Steel Life — prenotazioni corsi

Sito pubblico GitHub Pages e API Cloudflare Workers + database D1. Il database resta online anche quando il PC della palestra è spento.

## Funzioni

- Orari originali per MMA, Boxe, Kickboxing e BJJ.
- Conteggio condiviso aggiornato tra i dispositivi.
- Limite massimo applicato dall'API: 6 prenotazioni per corso, giorno, orario e settimana.
- Apertura di WhatsApp al proprietario, **+39 328 181 4024**, con il messaggio già compilato.
- Disdetta cercando la prenotazione con nome, cognome e fascia oraria.

## File

- `index.html`: pagina pubblica.
- `cloudflare-worker/src/index.js`: API delle prenotazioni.
- `cloudflare-worker/migrations/0001_create_bookings.sql`: schema D1.
- `cloudflare-worker/wrangler.toml`: configurazione del Worker.
- `CLOUDFLARE-D1-GUIDA.md`: procedura di configurazione e collegamento.

## Configurazione necessaria

Per rendere attivo il conteggio servono un account Cloudflare del proprietario, un database D1 e il deploy del Worker. Dopo il deploy, inserire l'indirizzo HTTPS del Worker nella costante `API_BASE` in `index.html` e pubblicare la modifica.

Senza un Worker configurato, la pagina continua a funzionare come richiesta manuale via WhatsApp, ma non registra prenotazioni né mostra conteggi condivisi. Non inserire password o chiavi private in questa repository pubblica.
