# Notifica automatica via email

Questo progetto Apps Script invia al proprietario una mail dopo che la prenotazione è stata salvata nel database. L'indirizzo del destinatario e il segreto restano nelle proprietà private dello script e di Cloudflare: non vanno inseriti nel sito pubblico o nell'URL.

## Configurazione gratuita iniziale

1. Accedi con l'account Google che deve inviare le email e crea un progetto su [script.google.com](https://script.google.com).
2. Copia il contenuto di `Code.gs` in `email-notifier/Code.gs`.
3. In **Impostazioni progetto → Proprietà script**, aggiungi:
   - `NOTIFY_EMAIL`: indirizzo che riceve gli avvisi.
   - `EMAIL_WEBHOOK_SECRET`: una stringa casuale lunga almeno 32 caratteri.
4. Da **Distribuisci → Nuova distribuzione**, scegli **App web**:
   - **Esegui come**: te.
   - **Chi può accedere**: chiunque.
   Il webhook è pubblico, ma accetta solo richieste che contengono il segreto impostato sopra.
5. Copia l'URL della distribuzione che termina con `/exec`.
6. Nel Worker Cloudflare `steel-life-prenotazioni-api`, in **Settings → Variables and Secrets**, aggiungi:
   - `EMAIL_WEBHOOK_URL`: URL `/exec` della distribuzione.
   - `EMAIL_WEBHOOK_SECRET`: lo stesso segreto. Impostalo come **Secret**.
7. Pubblica una nuova versione del Worker dopo aver salvato le variabili.

Il sito registra sempre la prenotazione prima dell'avviso email. Se l'email non è configurata o l'invio fallisce, il posto resta occupato e il sito apre comunque WhatsApp come promemoria.

## Quote

Google Apps Script ha limiti giornalieri di invio e Google può modificarli. Per un account Gmail personale la documentazione indica attualmente una quota di 100 destinatari email al giorno; controlla sempre la [pagina ufficiale delle quote](https://developers.google.com/apps-script/guides/services/quotas). Non è una garanzia di servizio o di gratuità per sempre.
