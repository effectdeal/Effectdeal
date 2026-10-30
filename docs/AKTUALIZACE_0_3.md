# EFFECT DEAL 0.3 — rychlost, dostupnost, doručení a jazyky

Nahrajte pouze soubory z aktualizačního ZIPu při zachování cest.
Obsah je porovnaný s GitHub main při přípravě aktualizace. Původní vozidla,
111 fotografií a katalog se neposílají znovu. Nový obrázek je logo firmy z effectdeal.com.

## Render

Build Command ponechte `pip install -r requirements.txt` (přibyl Pillow pro náhledy).
Start Command doporučujeme:

```sh
python -m scripts.import_catalog && gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 60
```

Import již dokončeného katalogu se přeskočí. Neměňte údaje MongoDB ani SECRET_KEY.
Po nahrání všech souborů proveďte Deploy latest commit. /api/health vrací verzi 0.3.0.

Pro cíl načtení do 2 sekund musí server běžet bez uspávání a databáze být geograficky blízko.
Bezplatný Render může při probuzení čekat desítky sekund. UptimeRobot není záruka rychlosti.
Placený trvale běžící Render odstraňuje uspávání, nikoli latenci sítě a přenos velkých originálů.
Produkční odezvu je nutné měřit po nasazení; lokální testy nejsou měření vašeho MongoDB.

## Co zrychluje aplikaci

- Dokumenty konkrétního vozidla se filtrují již v databázi; index podle rodiče.
- Během jednoho požadavku se stejný rodič/oprávnění nenačítá opakovaně.
- Na přehledech, v galerii a detailu se používají 640px WebP náhledy. Originál až po otevření.
- Náhled vzniká poprvé na serveru a ukládá se do dočasné cache. Originál zůstává v MongoDB.
- Každé načtení náhledu stále vyžaduje přihlášení a kontrolu oprávnění, i při HTTP 304.
- Domovská stránka používá jeden souhrnný endpoint místo čtyř kompletních seznamů.
- JSON odpovědi se komprimují; stránky se dále importují až při otevření.
- Souběžné totožné požadavky bez vlastního abort signálu se slučují; cache se maže po změnách a odhlášení.

## Nedostupnost a úkoly

V detailu vozidla stiskněte Nedostupné, vyplňte povinné datum Od a Do a uložte.
Období je včetně obou dnů, podle času Europe/Prague. Budoucí blokace je vidět v detailu i na kartě,
ale vůz je nedostupný pouze v daném období. Po skončení se odvozený stav vrátí na dostupné.
Překryv s rezervovaným/aktivním pronájmem nebo přiděleným převozem se odmítne.

Při výběru vozidla pro nový úkol se předvyplní známé místo převzetí.
Navázaný pronájem určuje konkrétní vozidlo i zákazníka. Vozidlo se nehádá podle adresy.
Přiřazený úkol zobrazuje Doručení naplánováno. Řidič u vlastního úkolu stiskne Zahájit doručení,
vozidlo zobrazí Probíhá doručení. Kontrolní úkol má samostatný stav Probíhá kontrola.
Dokončení převozu nastaví odvozenou polohu na místo předání. Ručně později potvrzené místo má přednost.
Kontrola vozidla jeho polohu nemění. Zaměstnanec nezískává oprávnění k cenám či cizím úkolům.

## Vzhled a jazyky

Černá, bílá a oranžová #f97316 odpovídají veřejnému webu. Skutečné logo firmy je
na přihlášení, v boční navigaci a v horní liště i na mobilu.
CZ / EN / DE je dostupné před přihlášením i uvnitř aplikace. Volba se pamatuje v prohlížeči.
Přepnutí zachová rozepsané formuláře. Překládá ovládací prvky a systémové popisky,
nikoli jména, adresy, uživatelské poznámky a importované popisy vozidel.

## Ověření a omezení

42 automatických testů: oprávnění, reporty, import, období nedostupnosti, překryvy,
postup úkolu a poloha, počet databázových dotazů a chráněné náhledy.
Chromium: přepnutí 3 jazyků, zachování rozepsaného formuláře, uložení blokace,
zahájení úkolu, automatický stav auta, obnova volby jazyka a mobilní šířka 390 px.
Přímý test produkčního přihlášení a MongoDB nebyl proveden (nemáme soukromé přihlašovací údaje).
Rozšířené účetnictví, skutečné bankovní platby a automatické GPS sledování nejsou součástí této aktualizace.
