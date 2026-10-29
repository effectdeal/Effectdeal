# Stav a navazující rozvoj

Tato dodávka je spustitelný základ 0.1, nikoliv dokončený podnikový informační systém.

## Implementováno
- Python/Render startup, zdravotní endpoint, přihlášení a serverová oprávnění.
- Oddělený demo prostor, produkční MongoDB adaptér a vytvoření prvního majitele z prostředí.
- Responzivní shell, lazy moduly, rušení starých požadavků, stav chyby a opakování.
- Vozidla se základními technickými údaji, cenou za měsíc, ruční polohou, servisní historií a chráněnými přílohami.
- Zaměstnanci, individuální sazby 0 Kč/h, dostupnost a potvrzená poloha.
- Karty zákazníků, měsíční rezervace a editace jejich termínů/stavu.
- Přiřazení převozu, předvyplněný výkaz a opakované otevření bez duplikace.
- Více úseků cesty, datum/čas, minuty, přestávky, kilometry, doprava, účel, výdaje, přesčas a příplatky.
- Odeslání, schválení, zamítnutí a vrácení s důvodem; upozornění v poště.
- Předávací protokol, tachometr, palivo, poškození, fotografie a kreslený podpis.
- Schválené podklady odměn, základní evidence faktur, plateb a kaucí.
- Doporučení nejbližšího zaměstnance z dostupných ručně potvrzených poloh do stáří 24 hodin.
- Online PWA a konfigurace monitoru UptimeRobot.

## Další etapa — společný ověřený provoz
1. Připojit vlastní MongoDB a otestovat mezi několika zařízeními; nastavit zálohy a obnovu.
2. Doplnit obnovu hesel, pozvánky, omezení pokusů o přihlášení, audit a správu relací.
3. Přenést dokumenty do privátního objektového úložiště, antivirovou kontrolu a retenční pravidla.
4. Serverové stránkování, fulltext, filtrování období a agregace přímo nad databází.
5. Spolehlivé notifikace (outbox) a push oznámení při zavřené aplikaci.
6. Dynamické pozice, delegované schvalování a směny.

## Obchodní moduly k rozšíření
- Kontrola překryvů rezervací, automatické ceny prodloužení, smlouvy a verzování protokolů.
- Skutečná obsazenost, ziskovost vozidel, finanční přehledy za týden/měsíc/rok a exporty.
- Oddělený profilový obrázek vozidla, náhledy fotografií, mazání a popisy příloh.
- Generování faktur/PDF, účetní pravidla, párování bankovních pohybů a výplatní integrace.
- Automatické GPS sledování pouze s jasným souhlasem a pravidly; plánování tras.
- Kvalifikované elektronické podpisy či ověření identity (kreslený podpis v 0.1 jimi není).
- Offline zadávání a bezpečná synchronizace konfliktů.

## Co se automaticky neprovádí

Aplikace neodesílá bankovní platby, nevystavuje daňové doklady, nesleduje telefon na pozadí a nespouští UptimeRobot sama. Schválení výkazu znamená pouze schválený podklad. Do demo režimu nevkládejte skutečné osobní údaje nebo účty.
