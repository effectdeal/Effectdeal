# Ověření dodávky 0.1

- 11 automatizovaných backend testů prošlo (`python -m pytest -q`).
- Ověřeno přihlášení, CSRF, přístup k cizím záznamům, omezení Dispečera, konflikty souběžných změn, soubory, zmrazení sazby a stavový proces výkazů.
- Skutečný Chromium prohlížeč: prošlo všech 12 sekcí bez JavaScriptové chyby.
- Ověřen lazy loading: modul výkazů se nestahuje při úvodním přehledu.
- V prohlížeči prošla úprava → odeslání → schválení výkazu.
- Mobilní viewport 390 × 844: bez horizontálního přetékání hlavní stránky; screenshot v `mobile.png`.
- Desktop screenshot v `desktop.png`.

Neověřeno v této dodávce: nasazení do vašeho Render účtu, připojení k vašemu MongoDB, nastavení UptimeRobot a instalace na konkrétní iPhone/Android. Příslušné přístupy nebyly připojeny. Součástí jsou soubory a návod pro vlastní nasazení.
