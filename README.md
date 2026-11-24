# Steel Life — prenotazioni corsi

Sito GitHub Pages statico con API Python/SQLite che gira sul computer della palestra.

## Cosa fa

- Mantiene sul PC un conteggio condiviso per ogni settimana, corso, giorno e orario.
- Blocca in modo atomico il settimo posto in uno slot da sei.
- Dopo la registrazione apre WhatsApp al proprietario, **+39 328 181 4024**, con nome e dettagli della prenotazione già compilati.
- Se il PC o il tunnel non sono raggiungibili, apre WhatsApp come richiesta da confermare manualmente e segnala che il conteggio online non è stato aggiornato.
- Supporta le disdette da nome, cognome e slot selezionato.

## File

- `index.html`: pagina pubblica.
- `server.py`: API e database SQLite locale.
- `AVVIA-SERVER.bat`: avvia l'API su Windows.
- `AVVIO-WINDOWS.md`: configurazione del tunnel e pubblicazione.

Il database `bookings.sqlite3` viene creato al primo avvio e non va caricato su GitHub. Il file `.gitignore` lo esclude.

## Pubblicazione

Questa versione viene pubblicata nella repository `Sala-Pesi-Steel-Life` con GitHub Actions. Dopo il primo deploy il link sarà:

`https://gabrielderinaldis321-maker.github.io/Sala-Pesi-Steel-Life/`

Per abilitare il conteggio condiviso, inserisci in `index.html` l'hostname HTTPS del Cloudflare Tunnel permanente. Le istruzioni sono in `AVVIO-WINDOWS.md`. Senza API configurata il sito apre WhatsApp come richiesta manuale; non mostra un conteggio condiviso inventato.

