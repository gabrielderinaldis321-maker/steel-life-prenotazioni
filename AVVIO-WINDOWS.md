# Steel Life: database SQLite sul PC

Questa cartella contiene un'API locale Python e un database SQLite. Il file `bookings.sqlite3` viene creato automaticamente accanto a `server.py`. L'API applica il limite di sei con una transazione SQLite, così due richieste contemporanee non possono prendere lo stesso ultimo posto.

## Avvio locale

1. Installa Python 3 per Windows, se non è già presente.
2. Avvia `AVVIA-SERVER.bat`.
3. Il PC crea/aggiorna il database locale e avvia l'API su `127.0.0.1:8765`.

Il server salva soltanto settimana, corso, slot e nome/cognome. All'avvio di una nuova settimana elimina le prenotazioni delle settimane precedenti.

## Collegare GitHub Pages al PC

Il sito è pubblico, quindi deve raggiungere l'API su Internet. La cartella non apre porte sul router: il server ascolta solo su `127.0.0.1` e `cloudflared` crea una connessione in uscita verso Cloudflare.

Per una prova temporanea, installa `cloudflared` dalla fonte ufficiale Cloudflare, lascia aperto il server e in un secondo terminale esegui:

```powershell
cloudflared tunnel --url http://localhost:8765
```

Cloudflare mostra un hostname `https://....trycloudflare.com`. Inseriscilo in `API_BASE` all'inizio del file `index.html`, senza barra finale. Il sito GitHub Pages già usa un'origine CORS ammessa nell'API.

I Quick Tunnel sono solo per prove: l'indirizzo cambia a ogni avvio e non ha garanzia di disponibilità. Per uso quotidiano serve un tunnel nominato con un hostname stabile nel tuo account Cloudflare. Le istruzioni ufficiali spiegano [come configurare il tunnel](https://developers.cloudflare.com/tunnel/get-started/) e [i limiti dei Quick Tunnel](https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/).

## Pubblicazione del sito

Carica il file `index.html` nella radice del repository GitHub Pages al posto della versione precedente. Poi avvia il server Python e il tunnel sul PC che ospita il database. Il PC deve restare acceso e con Internet; se si spegne, le prenotazioni online vengono temporaneamente sospese e il sito segnala che l'API non risponde.

Quando una prenotazione viene registrata, il sito aggiorna il contatore condiviso e apre WhatsApp con il messaggio già pronto. La persona deve comunque premere **Invia** per avvisare il proprietario.

La API espone solo la lettura dei conteggi e le operazioni di prenotazione/disdetta; non fornisce un endpoint pubblico per scaricare i nomi registrati. Per annullare dal sito è necessario inserire gli stessi nome, cognome e slot della prenotazione.

