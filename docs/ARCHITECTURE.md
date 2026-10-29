# Architektura 0.1

```
wsgi.py                 vstup pro gunicorn / Render
app/__init__.py         vytvoření serveru, režim a bezpečnostní hlavičky
app/storage.py          databázový adaptér SQLite / MongoDB
app/api/routes.py       API, přihlášení, oprávnění a stavové přechody
app/domain/             výpočty a oddělená ukázková data
app/templates/          prázdná HTML kostra
app/static/js/core/     API klient, zrušení požadavků, společné UI
app/static/js/pages/    moduly načítané podle aktuální stránky
app/static/css/         společný responzivní vzhled
app/static/sw.js        online PWA, bez cache soukromých záznamů
app/static/icons/       ikony instalované aplikace
tests/                  izolované testy serverových pravidel
```

## Vazby

Zákazník → pronájem → konkrétní vozidlo → převoz/úkol → přidělený zaměstnanec → výkaz a předávací protokol → doklady → schválený podklad k odměně.

Vazby jsou ID, nikoli kopie celých karet. Převoz s pronájmem přebírá jeho zákazníka a vozidlo. Výkaz má deterministické ID `report-<id-převozu>`, takže opakované otevření nevytváří duplicity. Jakmile má převoz výkaz, zásadní přiřazení nelze změnit běžnou editací. Historická sazba se ukládá ve výkazu; jméno a aktuální kartu lze načíst samostatně.

## Oprávnění

Každý API požadavek ověřuje relaci na serveru, nikoliv roli poslanou z prohlížeče. Zaměstnanec čte pouze své úkoly a výkazy a jimi přiřazená vozidla. Doklady dědí oprávnění nadřazeného záznamu. Manager nemění majitele. Dispečer nemění ceny ani hodinové sazby a schvaluje pouze převozové výkazy jiných zaměstnanců.

`version` zajišťuje optimistické zamykání: souběžná editace vrátí HTTP 409, nepřepíše novější údaje. Stav výkazu je měnitelný pouze akcí `submit/approve/reject/return`; schválený ani odeslaný výkaz nelze přepsat obyčejným PUT.

## Výpočty

Pracovní minuty minus přestávky × hodinová sazba / 60 + skutečné výdaje + dohodnuté příplatky a odměna. Server počítá pomocí Decimal a ukládá výsledky v haléřích. Přesčas je označená část odpracované doby, nikoliv další násobení. Verze 0.1 neprovádí zákonné mzdové, daňové nebo cestovní náhradové výpočty.

## Ukládání souborů

První implementace ukládá menší přílohy společně s dokumentovými záznamy (Base64, do 10 MB na soubor). Jsou dostupné pouze přihlášenému uživateli s přístupem k rodiči. Pro větší provoz je další krok privátní objektové úložiště a přímé podepsané uploady; Cloudinary/S3/Supabase Storage lze přidat za API dokumentů bez změny všech stránek.

## Omezení první implementace

Databázový adaptér používá jednoduchý seznam záznamů a filtraci na serveru; u větších kolekcí je potřeba přesunout stránkování a filtraci do MongoDB dotazů. Nahrávací limit 10 příloh se kontroluje před zápisem, zatím není transakčně chráněn proti souběžným uploadům. Změna stavu a notifikace jsou dva zápisy, pro produkci následuje transakční outbox. Upozornění používají krátké dotazování, nikoliv WebSockety. Role jsou pevné; dynamický editor oprávnění přijde po ustálení doménových pravidel.
