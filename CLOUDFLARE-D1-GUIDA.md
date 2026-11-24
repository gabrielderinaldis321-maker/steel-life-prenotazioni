# Attivare il conteggio online gratuito

Il sito statico resta su GitHub Pages. L'API e il database passano a Cloudflare Workers + D1: il PC può rimanere spento. Il piano gratuito attuale include quote ampie per un piccolo calendario palestra (Workers: 100.000 richieste al giorno; D1: 5 milioni di righe lette e 100.000 scritte al giorno, con limiti di spazio). Le quote e il servizio gratuito possono cambiare; superate le quote giornaliere, le operazioni si fermano fino al reset e non parte una fattura automatica per il piano Free.

## Serve l'account Cloudflare del proprietario

Il codice è pronto, ma `database_id` e URL del Worker vengono assegnati all'interno del suo account. Non inserire password o token Cloudflare nel repository pubblico.

1. Accedi a Cloudflare e apri **Workers & Pages**.
2. Crea un database D1 chiamato `steel-life-prenotazioni`.
3. Copia l'ID assegnato nel campo `database_id` di `wrangler.toml`.
4. Crea un Worker da `src/index.js` e collegagli il database con binding `DB`.
5. Esegui `migrations/0001_create_bookings.sql` una sola volta dalla console SQL di D1.
6. Pubblica il Worker e copia l'indirizzo HTTPS assegnato.
7. Inserisci l'indirizzo in `API_BASE` all'inizio del `index.html` e pubblica la modifica su GitHub.

La API consente solo al sito GitHub Pages Steel Life di fare richieste dal browser. Non espone una lista pubblica dei nomi: rende visibili soltanto i conteggi per corso.

