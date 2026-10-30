const translations = {};
const rows = `
Probíhá kontrola|Inspection in progress|Kontrolle läuft
Všechny převozy|All transfers|Alle Überführungen
Všechny výkazy|All reports|Alle Abrechnungen
Doporučení vychází pouze z ručně potvrzené polohy a dostupnosti. V první verzi ověřte aktuální polohu se zaměstnancem; automatické sledování GPS není zapnuté.|Suggestions use manually confirmed locations and availability. Confirm the current location with the employee; automatic GPS tracking is not enabled.|Vorschläge nutzen manuell bestätigte Standorte und Verfügbarkeit. Bestätigen Sie den aktuellen Standort mit dem Mitarbeiter; automatische GPS-Ortung ist nicht aktiviert.
Verze 0.1: jednoduchá evidence a souhrny z nejvýše 100 záznamů každého typu. Bankovní integrace, účetní exporty, období a podrobné výpočty vytíženosti patří do další etapy. Částky nejsou daňové ani mzdové výpočty.|Basic records and summaries of up to 100 entries per type. Bank integration, accounting exports, period filters and detailed utilisation calculations are planned for a later stage. Amounts are not tax or payroll calculations.|Einfache Erfassung und Summen aus bis zu 100 Einträgen pro Typ. Bankanbindung, Buchhaltungsexporte, Zeitraumfilter und detaillierte Auslastungsberechnungen sind für eine spätere Phase vorgesehen. Die Beträge sind keine Steuer- oder Lohnberechnungen.

Převoz vozidla|Vehicle transfer|Fahrzeugüberführung
Výkaz a protokol|Report and handover|Abrechnung und Protokoll
Schválení odměny|Payment approval|Vergütungsfreigabe
Testovací data jsou oddělená pro tento prohlížeč. Přepnutí role provedete odhlášením. Ostré přihlášení a společná data se zapnou po připojení MongoDB.|Test data is isolated to this browser. Sign out to change roles. Production login and shared data require MongoDB.|Testdaten sind auf diesen Browser beschränkt. Zum Rollenwechsel abmelden. Produktivanmeldung und gemeinsame Daten benötigen MongoDB.

Osobní údaje|Personal details|Persönliche Angaben
Přístupová role|Access role|Zugriffsrolle
Hodinová sazba|Hourly rate|Stundensatz
Heslo se z bezpečnostních důvodů nezobrazuje.|Passwords are hidden for security.|Passwörter werden aus Sicherheitsgründen nicht angezeigt.
Moje výkazy a pracovní historie →|My reports and work history →|Meine Abrechnungen und Arbeitshistorie →
Dokumenty jsou přístupné zaměstnanci a oprávněné správě účtů.|Documents are accessible to the employee and authorised account administrators.|Dokumente sind für den Mitarbeiter und berechtigte Kontoverwalter zugänglich.
Dokumenty jsou nepovinné. Můžete přiložit například řidičský průkaz. Doklady se nezobrazují ostatním zaměstnancům ani dispečerovi.|Documents are optional. You can attach a driving licence. Other employees and dispatchers cannot view these documents.|Dokumente sind optional, z. B. ein Führerschein. Andere Mitarbeiter und Disponenten können diese Dokumente nicht einsehen.
Profily, přihlašovací údaje, osobní dokumenty a hodinové sazby.|Profiles, login details, personal documents and hourly rates.|Profile, Anmeldedaten, persönliche Dokumente und Stundensätze.
＋ Vytvořit profil|＋ Create profile|＋ Profil erstellen
Vytvořit profil|Create profile|Profil erstellen
Profil ↗|Profile ↗|Profil ↗
← Předchozí|← Previous|← Zurück
Další →|Next →|Weiter →
Kontakt / telefon|Contact / phone|Kontakt / Telefon
Uživatelské jméno pro přihlášení|Login username|Benutzername zur Anmeldung
Heslo (nejméně 12 znaků)|Password (at least 12 characters)|Passwort (mindestens 12 Zeichen)
Název pozice (např. řidič, technik)|Position title (e.g. driver, technician)|Positionsbezeichnung (z. B. Fahrer, Techniker)
Potvrzená GPS šířka|Confirmed GPS latitude|Bestätigter GPS-Breitengrad
Potvrzená GPS délka|Confirmed GPS longitude|Bestätigter GPS-Längengrad
Poloha potvrzena|Location confirmed|Standort bestätigt
Role Zaměstnanec / řidič má pouze vlastní úkoly, výkazy a historii. Název pozice tato oprávnění nerozšiřuje.|Employees / drivers can only access their own tasks, reports and history. Position titles do not extend permissions.|Mitarbeiter / Fahrer sehen nur eigene Aufgaben, Abrechnungen und Historie. Positionsbezeichnungen erweitern keine Rechte.
Role Zaměstnanec / řidič má pouze vlastní úkoly, výkazy a historii. Název pozice tato oprávnění nerozšiřuje. Prázdné heslo ponechá stávající heslo.|Employees / drivers see only their own tasks, reports and history. Position titles do not extend permissions. Leave the password blank to keep it.|Mitarbeiter / Fahrer sehen nur eigene Aufgaben, Abrechnungen und Historie. Positionsbezeichnungen erweitern keine Rechte. Ein leeres Passwortfeld behält das Passwort bei.
Osobní dokumenty (nepovinné)|Personal documents (optional)|Persönliche Dokumente (optional)
JPG, PNG, WebP nebo PDF; nejvýše 10 MB za soubor, 10 dokumentů u profilu. Profil lze vytvořit bez dokumentů.|JPG, PNG, WebP or PDF; up to 10 MB per file and 10 documents per profile. Documents are optional.|JPG, PNG, WebP oder PDF; bis 10 MB pro Datei und 10 Dokumente pro Profil. Dokumente sind optional.
Profil uložen.|Profile saved.|Profil gespeichert.
Profil uložen; zkontrolujte zprávu u dokumentů.|Profile saved; check the document message.|Profil gespeichert; prüfen Sie den Hinweis zu Dokumenten.
Finance a podklady k odměnám|Finances and remuneration records|Finanzen und Vergütungsunterlagen
Součty vycházejí z evidovaných položek. Schválený výkaz je podklad, nikoli potvrzení bankovní platby.|Totals are based on recorded items. An approved report is not confirmation of a bank payment.|Summen basieren auf erfassten Posten. Eine genehmigte Abrechnung bestätigt keine Bankzahlung.
＋ Faktura|＋ Invoice|＋ Rechnung
＋ Zaznamenat platbu|＋ Record payment|＋ Zahlung erfassen
Evidované příjmy|Recorded income|Erfasste Einnahmen
Schválené výkazy|Approved reports|Genehmigte Abrechnungen
Z toho náklady cest|Including travel expenses|Davon Reisekosten
Výsledek po výkazech|Balance after reports|Ergebnis nach Abrechnungen
Schválené podklady zaměstnanců|Approved employee records|Genehmigte Mitarbeiterunterlagen
Výkaz|Report|Abrechnung
Odměna|Remuneration|Vergütung
Výdaje|Expenses|Ausgaben
Celkem|Total|Gesamt
Měsíční ceník|Monthly pricing|Monatliche Preisliste
Evidence faktur|Invoice records|Rechnungsübersicht
Číslo|Number|Nummer
Splatnost|Due date|Fälligkeit
Částka|Amount|Betrag
Platby a vratné kauce|Payments and refundable deposits|Zahlungen und rückzahlbare Kautionen
Vratná kauce|Refundable deposit|Rückzahlbare Kaution
Příjem|Income|Einnahme
Evidovat fakturu|Record invoice|Rechnung erfassen
Číslo faktury|Invoice number|Rechnungsnummer
Částka (Kč)|Amount (CZK)|Betrag (CZK)
Zaznamenat platbu|Record payment|Zahlung erfassen
Pracovní výkaz|Work report|Arbeitsnachweis
Upravit výkaz|Edit report|Abrechnung bearbeiten
Celkem k proplacení|Total to reimburse|Gesamtbetrag zur Auszahlung
Navázaný převoz ↗|Linked transfer ↗|Verknüpfte Überführung ↗
Způsob dopravy|Transport method|Verkehrsmittel
Účel cesty|Purpose of trip|Reisezweck
Čas a vzdálenost|Time and distance|Zeit und Entfernung
Jízdenky|Tickets|Fahrkarten
Tankování|Fuel expenses|Tankkosten
Parkování|Parking|Parkgebühren
Dálniční poplatky|Tolls|Mautgebühren
Mytí|Car wash|Fahrzeugwäsche
Mytí vozu|Car wash|Fahrzeugwäsche
Další výdaje|Other expenses|Weitere Ausgaben
Odměna a výdaje|Remuneration and expenses|Vergütung und Ausgaben
Práce po odečtení přestávek|Work excluding breaks|Arbeitszeit ohne Pausen
Odměna za práci|Pay for work|Arbeitsvergütung
Příplatek víkend|Weekend supplement|Wochenendzuschlag
Příplatek svátek|Public holiday supplement|Feiertagszuschlag
Mimořádná odměna|Bonus|Sondervergütung
Z toho přesčas|Including overtime|Davon Überstunden
Dokončené úkoly|Completed tasks|Abgeschlossene Aufgaben
Odeslat ke schválení|Submit for approval|Zur Freigabe einreichen
Schválit|Approve|Genehmigen
Vrátit k opravě|Return for correction|Zur Korrektur zurückgeben
Zamítnout|Reject|Ablehnen
Moje výkazy a historie|My reports and history|Meine Abrechnungen und Historie
Výkazy zaměstnanců|Employee reports|Mitarbeiterabrechnungen
Vaše cesty, odpracovaný čas, odměny a náhrady výdajů.|Your trips, working time, pay and expense reimbursements.|Ihre Reisen, Arbeitszeit, Vergütungen und Auslagenerstattungen.
Cestovní, pracovní a výdajový výkaz propojený s převozem.|Travel, work and expense reports linked to a transfer.|Reise-, Arbeits- und Auslagenabrechnung mit verknüpfter Überführung.
＋ Nový výkaz|＋ New report|＋ Neue Abrechnung
Nový výkaz|New report|Neue Abrechnung
Všechny stavy|All statuses|Alle Status
Nevyřízené|Pending|Offen
Schválené|Approved|Genehmigt
Vrácené|Returned|Zurückgegeben
Zamítnuté|Rejected|Abgelehnt
Všichni|Everyone|Alle
Pracovní doba|Working time|Arbeitszeit
Odesláno. Majitel dostal upozornění.|Submitted. The owner has been notified.|Eingereicht. Der Inhaber wurde benachrichtigt.
Stav výkazu aktualizován.|Report status updated.|Abrechnungsstatus aktualisiert.
Zamítnout výkaz|Reject report|Abrechnung ablehnen
Důvod pro zaměstnance|Reason for employee|Begründung für Mitarbeiter
Vyplňte důvod.|Enter a reason.|Geben Sie eine Begründung ein.
Název výkazu|Report title|Titel der Abrechnung
Doprava / vozidlo|Transport / vehicle|Verkehrsmittel / Fahrzeug
Odkud|From|Von
Kam|To|Nach
Zahájení|Start|Beginn
Ukončení|End|Ende
Pracovní doba (minuty)|Working time (minutes)|Arbeitszeit (Minuten)
Přestávky (minuty)|Breaks (minutes)|Pausen (Minuten)
Vzdálenost (km)|Distance (km)|Entfernung (km)
Odebrat úsek|Remove leg|Etappe entfernen
＋ Přidat cestu zpět / další destinaci|＋ Add return trip / next destination|＋ Rückfahrt / weiteres Ziel hinzufügen
Z toho přesčas (minuty)|Including overtime (minutes)|Davon Überstunden (Minuten)
Sazba se načítá ze zaměstnaneckého profilu. Přesčasy jsou součást pracovní doby. Fotografie a doklady připojíte po uložení výkazu.|The rate comes from the employee profile. Overtime is included in working time. Attach photos and receipts after saving.|Der Satz stammt aus dem Mitarbeiterprofil. Überstunden sind Teil der Arbeitszeit. Fotos und Belege können nach dem Speichern angehängt werden.
Výkaz uložen.|Report saved.|Abrechnung gespeichert.
Přesčas je součást odpracovaných minut. Případné navýšení vyplňte jako dohodnutou odměnu. Sazba se uloží při odeslání a pozdější změna profilu již výkaz nepřepočítá.|Overtime is included in worked minutes. Enter any supplement as an agreed bonus. The rate is frozen on submission; later profile changes do not recalculate the report.|Überstunden sind in den Arbeitsminuten enthalten. Zuschläge werden als vereinbarte Vergütung erfasst. Der Satz wird beim Einreichen festgeschrieben; spätere Profiländerungen ändern die Abrechnung nicht.
Upozornění na výkazy a změny jejich schválení.|Notifications about reports and approval changes.|Benachrichtigungen zu Abrechnungen und Freigaben.
Nové|New|Neu
Zatím žádné zprávy.|No messages yet.|Noch keine Nachrichten.
Počet nových zpráv se kontroluje každých 15 sekund, když je aplikace otevřená a viditelná.|New messages are checked every 15 seconds while the app is open and visible.|Neue Nachrichten werden alle 15 Sekunden geprüft, solange die App geöffnet und sichtbar ist.
Doklady, smlouvy a fotografie navázané na konkrétní záznam.|Receipts, contracts and photos linked to records.|Belege, Verträge und Fotos zu einzelnen Einträgen.
Soubor|File|Datei
Vazba|Linked record|Verknüpfung
Velikost|Size|Größe
Osobní doklad|Personal document|Persönliches Dokument
Pronájem|Rental|Vermietung
Zobrazit fotografii ↗|View photo ↗|Foto anzeigen ↗
Stáhnout ↗|Download ↗|Herunterladen ↗
Dokumenty přidávejte v profilu zaměstnance nebo v detailu výkazu, vozidla či předávacího protokolu. Přístup je řízený oprávněními jejich záznamu.|Add documents in an employee profile or the details of a report, vehicle or handover. Record permissions control access.|Fügen Sie Dokumente im Mitarbeiterprofil oder in den Details einer Abrechnung, eines Fahrzeugs oder Übergabeprotokolls hinzu. Die Zugriffsrechte des Eintrags gelten.
Správa uživatelů a přístupů|User and access management|Benutzer- und Zugriffsverwaltung
Oprávnění kontroluje server u každého požadavku.|The server checks permissions on every request.|Der Server prüft die Berechtigungen bei jeder Anfrage.
Kompletní přístup, profily, hodinové sazby, finance a schvalování.|Full access, profiles, hourly rates, finances and approvals.|Vollzugriff, Profile, Stundensätze, Finanzen und Freigaben.
Správa provozu a financí. Nemůže změnit profil ani práva majitele.|Manages operations and finances. Cannot change the owner's profile or permissions.|Verwaltet Betrieb und Finanzen. Kann Profil und Rechte des Inhabers nicht ändern.
Přiřazení úkolů, vozidla a pronájmy. Bez změny cen a sazeb. Schvaluje převozové výkazy jiných zaměstnanců.|Assigns tasks, vehicles and rentals. Cannot change prices or rates. Reviews other employees' transfer reports.|Weist Aufgaben, Fahrzeuge und Vermietungen zu. Keine Preis- oder Satzänderungen. Prüft Überführungsabrechnungen anderer Mitarbeiter.
Pouze vlastní profil, úkoly, výkazy, odměny a historie. Přidělená vozidla a související doklady. Bez cizích výkazů, profilů a firemních financí. Stejné osobní omezení platí pro všechny názvy pozic v této roli.|Own profile, tasks, reports, pay and history only. Assigned vehicles and related documents. No access to others' reports, profiles or company finances. The same limits apply to all positions within this role.|Nur eigenes Profil, Aufgaben, Abrechnungen, Vergütungen und Historie. Zugewiesene Fahrzeuge und zugehörige Dokumente. Kein Zugriff auf fremde Abrechnungen, Profile oder Unternehmensfinanzen. Dieselben Grenzen gelten für alle Positionen dieser Rolle.
Uživatelské účty|User accounts|Benutzerkonten
Účty a sazby nastavíte v modulu Zaměstnanci. V produkčním režimu se přihlašuje uživatelským jménem a heslem. Testovací přepínání rolí je povolené pouze v režimu demo.|Manage accounts and rates in Employees. Production login uses a username and password. Role switching is available only in demo mode.|Konten und Sätze werden unter Mitarbeiter verwaltet. Die Anmeldung im Produktivbetrieb erfolgt mit Benutzername und Passwort. Rollenwechsel sind nur im Demomodus möglich.
Otevřít zaměstnance →|Open employees →|Mitarbeiter öffnen →
Databázové a přístupové údaje jsou nastavení serveru. Nevkládají se do prohlížeče ani do veřejného repozitáře.|Database and login secrets are server settings, never entered into the browser or public repository.|Datenbank- und Zugangsdaten gehören in die Serverkonfiguration, niemals in den Browser oder ein öffentliches Repository.
Nabídka z effectdeal.com|Catalogue from effectdeal.com|Angebot von effectdeal.com
Převod veřejné nabídky do vozového parku.|Import the public catalogue into the fleet.|Öffentliches Angebot in den Fuhrpark übernehmen.
Převést celou nabídku|Import entire catalogue|Gesamtes Angebot importieren
Rok|Year|Jahr
Fotografií|Photos|Fotos
Připraveno k importu|Ready to import|Bereit zum Import
Ve vozovém parku ↗|In fleet ↗|Im Fuhrpark ↗
Převedeno ↗|Imported ↗|Importiert ↗
Nabídka byla převedena.|Catalogue imported.|Angebot importiert.
Import vyžaduje kontrolu.|Import needs review.|Import muss geprüft werden.
Zkontrolovat / doplnit import|Check / complete import|Import prüfen / ergänzen
Opakované spuštění zachová vaše úpravy i vybranou profilovou fotografii a doplní chybějící fotografie z balíčku.|Running again preserves edits and the chosen cover photo, adding missing photos from the bundle.|Erneutes Ausführen behält Änderungen und Titelbild bei und ergänzt fehlende Fotos aus dem Paket.
Po importu doplňte skutečnou SPZ, VIN a ověřte dostupnost. Nabídka na webu může zahrnovat více kusů stejného modelu. Vytvoří se jedna karta na nabídku se stavem „K doplnění“.|After import, enter actual registration plates and VINs and verify availability. An offer may represent several vehicles of the same model. One card per offer is created with status “Needs details”.|Ergänzen Sie nach dem Import Kennzeichen und FIN und prüfen Sie die Verfügbarkeit. Ein Angebot kann mehrere Fahrzeuge desselben Modells umfassen. Pro Angebot wird eine Karte mit Status „Angaben ergänzen“ erstellt.
Přenesou se popisy, technické údaje, výbava, měsíční ceny a fotografie.|Descriptions, specifications, equipment, monthly prices and photos are imported.|Beschreibungen, technische Daten, Ausstattung, Monatspreise und Fotos werden importiert.
Nabídka z webu. Doplňte skutečnou SPZ a VIN, zkontrolujte údaje a změňte stav vozidla před přiřazením k pronájmu nebo převozu.|Website offer. Add the actual registration plate and VIN, verify details and change status before assigning a rental or transfer.|Website-Angebot. Ergänzen Sie Kennzeichen und FIN, prüfen Sie die Angaben und ändern Sie den Status vor Zuweisung einer Vermietung oder Überführung.

Domov|Home|Startseite
Vozový park|Fleet|Fuhrpark
Pronájmy|Rentals|Vermietungen
Rozvoz a svoz|Deliveries & collections|Zustellung & Abholung
Zaměstnanci|Employees|Mitarbeiter
Můj profil|My profile|Mein Profil
Import nabídky|Import catalogue|Angebot importieren
Výkazy|Reports|Abrechnungen
Zákazníci|Customers|Kunden
Finance|Finances|Finanzen
Statistiky|Statistics|Statistiken
Dokumenty|Documents|Dokumente
Pošta|Inbox|Posteingang
Správa uživatelů|User management|Benutzerverwaltung
Můj přehled|My overview|Meine Übersicht
Moje vozidla|My vehicles|Meine Fahrzeuge
Moje úkoly|My tasks|Meine Aufgaben
Moje výkazy|My reports|Meine Abrechnungen
Moje dokumenty|My documents|Meine Dokumente
Majitel|Owner|Inhaber
Manager|Manager|Manager
Dispečer|Dispatcher|Disponent
Zaměstnanec|Employee|Mitarbeiter
Zaměstnanec / řidič|Employee / driver|Mitarbeiter / Fahrer
Přihlášení|Sign in|Anmelden
Uživatelské jméno|Username|Benutzername
Heslo|Password|Passwort
Vstoupit do aplikace →|Sign in →|Anmelden →
Přístup pouze pro oprávněné zaměstnance.|Access for authorised employees only.|Zugang nur für berechtigte Mitarbeiter.
VÍTEJTE V EFFECT DEAL|WELCOME TO EFFECT DEAL|WILLKOMMEN BEI EFFECT DEAL
Vaše flotila.|Your fleet.|Ihr Fuhrpark.
V pohybu po celé ČR.|On the move across Czechia.|In ganz Tschechien unterwegs.
Vozidla, převozy, tým a výkazy.|Vehicles, deliveries, team and reports.|Fahrzeuge, Überführungen, Team und Abrechnungen.
Jeden společný pracovní prostor.|One shared workspace.|Ein gemeinsamer Arbeitsbereich.
FIREMNÍ PRACOVNÍ PROSTOR|COMPANY WORKSPACE|UNTERNEHMENSBEREICH
EFFECT DEAL / PRACOVNÍ PROSTOR|EFFECT DEAL / WORKSPACE|EFFECT DEAL / ARBEITSBEREICH
PŘEHLED A PROVOZ|OVERVIEW & OPERATIONS|ÜBERSICHT & BETRIEB
Pronájem vozidel · celá ČR|Vehicle rental · Czechia|Fahrzeugvermietung · Tschechien
↓ Nainstalovat aplikaci|↓ Install app|↓ App installieren
Odhlásit|Sign out|Abmelden
Připojeno|Connected|Verbunden
Spojení přerušeno|Connection lost|Verbindung unterbrochen
Načítám…|Loading…|Wird geladen…
Zkusit znovu|Try again|Erneut versuchen
Stránku se nepodařilo načíst|Unable to load page|Seite konnte nicht geladen werden
Server se nepodařilo připojit. Bezplatný Render se může právě probouzet.|Unable to connect. The free Render server may be starting.|Keine Verbindung. Der kostenlose Render-Server startet möglicherweise gerade.
Neplatné přihlašovací údaje.|Invalid login details.|Ungültige Anmeldedaten.
Přihlaste se prosím.|Please sign in.|Bitte melden Sie sich an.
Obnovte stránku a zkuste to znovu.|Refresh the page and try again.|Laden Sie die Seite neu und versuchen Sie es erneut.
UKÁZKOVÝ REŽIM|DEMO MODE|DEMOMODUS
Vyberte roli pro vyzkoušení pracovního postupu.|Choose a role to try the workflow.|Wählen Sie eine Rolle zum Testen des Arbeitsablaufs.
Ukázková role|Demo role|Demorolle
Zaměstnanec · Jan Novák|Employee · Jan Novák|Mitarbeiter · Jan Novák
Ukázka obsahuje pouze testovací údaje.|The demo contains test data only.|Die Demo enthält nur Testdaten.
Uložit|Save|Speichern
Uloženo|Saved|Gespeichert
Zrušit|Cancel|Abbrechen
Zavřít|Close|Schließen
Zavřít ✕|Close ✕|Schließen ✕
Upravit|Edit|Bearbeiten
Upravit ↗|Edit ↗|Bearbeiten ↗
Otevřít ↗|Open ↗|Öffnen ↗
Detail ↗|Details ↗|Details ↗
Zobrazit ↗|View ↗|Anzeigen ↗
Zobrazit vše →|View all →|Alle anzeigen →
Zobrazit přehled ↗|View overview ↗|Übersicht anzeigen ↗
Nový záznam|New record|Neuer Eintrag
＋ Nový záznam|＋ New record|＋ Neuer Eintrag
Upravit záznam|Edit record|Eintrag bearbeiten
Zatím zde nejsou žádné záznamy.|No records yet.|Noch keine Einträge vorhanden.
K doplnění|Needs details|Angaben ergänzen
K dispozici|Available|Verfügbar
Zapůjčeno|Rented|Vermietet
V servisu|In service|In Wartung
Nedostupné|Unavailable|Nicht verfügbar
Probíhá doručení|Delivery in progress|Zustellung läuft
Doručení naplánováno|Delivery scheduled|Zustellung geplant
Zrušeno|Cancelled|Storniert
Přiděleno|Assigned|Zugewiesen
Probíhá|In progress|In Bearbeitung
Dokončeno|Completed|Abgeschlossen
Koncept|Draft|Entwurf
Čeká na schválení|Awaiting approval|Wartet auf Freigabe
Schváleno|Approved|Genehmigt
Zamítnuto|Rejected|Abgelehnt
Vráceno k opravě|Returned for correction|Zur Korrektur zurückgegeben
Rezervováno|Reserved|Reserviert
Aktivní|Active|Aktiv
Ukončeno|Ended|Beendet
Vystavena|Issued|Ausgestellt
Uhrazeno|Paid|Bezahlt
Stav|Status|Status
Vozidlo|Vehicle|Fahrzeug
Vozidla|Vehicles|Fahrzeuge
Údaje o vozidle|Vehicle details|Fahrzeugdaten
Upravit vozidlo|Edit vehicle|Fahrzeug bearbeiten
Nové vozidlo|New vehicle|Neues Fahrzeug
＋ Přidat vozidlo|＋ Add vehicle|＋ Fahrzeug hinzufügen
↓ Import nabídky z webu|↓ Import website catalogue|↓ Website-Angebot importieren
Poloha, dostupnost a dokumentace každého vozu.|Location, availability and documentation for every vehicle.|Standort, Verfügbarkeit und Dokumentation jedes Fahrzeugs.
Vozidla přiřazená k vašim úkolům.|Vehicles assigned to your tasks.|Ihren Aufgaben zugewiesene Fahrzeuge.
Vozidel v přehledu|Vehicles in overview|Fahrzeuge in der Übersicht
Tovární značka|Make|Marke
Model|Model|Modell
SPZ|Registration plate|Kennzeichen
SPZ k doplnění|Add registration plate|Kennzeichen ergänzen
VIN|VIN|FIN
Rok výroby|Year of manufacture|Baujahr
Barva|Colour|Farbe
Pohon|Drive|Antrieb
Palivo|Fuel|Kraftstoff
Převodovka|Transmission|Getriebe
Výkon (kW)|Power (kW)|Leistung (kW)
Výbava|Equipment|Ausstattung
Popis|Description|Beschreibung
Cena od (Kč/měsíc)|Price from (CZK/month)|Preis ab (CZK/Monat)
Aktuální místo|Current location|Aktueller Standort
GPS šířka|GPS latitude|GPS-Breitengrad
GPS délka|GPS longitude|GPS-Längengrad
Tachometr (km)|Odometer (km)|Kilometerstand (km)
Závady|Defects|Mängel
Konec posledního zapůjčení|Last rental end|Ende der letzten Vermietung
Nedostupné od|Unavailable from|Nicht verfügbar ab
Nedostupné do|Unavailable until|Nicht verfügbar bis
Cena neuvedena|Price not specified|Preis nicht angegeben
/ měsíc|/ month|/ Monat
Poloha k doplnění|Add location|Standort ergänzen
Rok neuveden|Year not specified|Baujahr nicht angegeben
Převodovka neuvedena|Transmission not specified|Getriebe nicht angegeben
Ilustrační náhled|Illustration|Beispielabbildung
Zatím žádná přidělená vozidla.|No assigned vehicles yet.|Noch keine zugewiesenen Fahrzeuge.
Nájezd uvedený na webu|Mileage listed on website|Kilometerstand laut Website
Karoserie|Body type|Karosserie
Otevřít ručně zadanou GPS ↗|Open manually entered GPS ↗|Manuell eingegebene GPS öffnen ↗
Fotografie vozidla|Vehicle photos|Fahrzeugfotos
Fotografie a doklady|Photos and receipts|Fotos und Belege
Nastavit jako profilovou|Set as cover photo|Als Titelbild festlegen
✓ Profilová fotografie|✓ Cover photo|✓ Titelbild
Profilová fotografie byla uložena.|Cover photo saved.|Titelbild gespeichert.
Zatím nebyly přidány žádné fotografie ani doklady.|No photos or documents yet.|Noch keine Fotos oder Dokumente vorhanden.
Stáhnout originál ↓|Download original ↓|Original herunterladen ↓
Zvětšit hlavní fotografii vozidla|Enlarge vehicle cover photo|Fahrzeug-Titelbild vergrößern
Předchozí fotografie|Previous photo|Vorheriges Foto
Další fotografie|Next photo|Nächstes Foto
Zavřít fotografii|Close photo|Foto schließen
Prohlížeč fotografií|Photo viewer|Fotoanzeige
Fotografii nelze načíst. Zavřete náhled a obnovte stránku.|Unable to load photo. Close the preview and refresh.|Foto konnte nicht geladen werden. Schließen Sie die Vorschau und laden Sie neu.
Servisní historie|Service history|Wartungshistorie
＋ Záznam|＋ Record|＋ Eintrag
Servis vozidla|Vehicle service|Fahrzeugwartung
Provedený servis|Service performed|Durchgeführte Wartung
Náklady (Kč)|Costs (CZK)|Kosten (CZK)
Příští servis|Next service|Nächste Wartung
Datum|Date|Datum
Čas|Time|Uhrzeit
Náklady|Costs|Kosten
Termín|Scheduled date|Termin
Trasa|Route|Strecke
Přiřaďte převoz, kontrolu nebo vyzvednutí vozidla.|Assign a delivery, inspection or collection.|Weisen Sie eine Überführung, Kontrolle oder Abholung zu.
Vaše přiřazené převozy, kontroly a historie práce.|Your assigned deliveries, inspections and work history.|Ihre zugewiesenen Überführungen, Kontrollen und Arbeitshistorie.
＋ Přidělit úkol|＋ Assign task|＋ Aufgabe zuweisen
Přidělit úkol|Assign task|Aufgabe zuweisen
Upravit převoz|Edit transfer|Überführung bearbeiten
Navázaný pronájem|Linked rental|Verknüpfte Vermietung
Bez pronájmu|No rental|Ohne Vermietung
Místo převzetí|Collection location|Übernahmeort
Místo předání|Delivery location|Übergabeort
Typ úkolu|Task type|Aufgabentyp
Přistavení|Delivery|Zustellung
Svoz|Collection|Abholung
Kontrola vozidla|Vehicle inspection|Fahrzeugkontrolle
Průběh|Progress|Fortschritt
Pokyny pro zaměstnance|Instructions for employee|Anweisungen für Mitarbeiter
Jeden propojený pracovní záznam|One linked work record|Ein verknüpfter Arbeitseintrag
Převzetí|Collection|Übernahme
Předání|Delivery|Übergabe
Pokyny|Instructions|Anweisungen
Zahájit doručení|Start delivery|Zustellung starten
Dokončit doručení|Complete delivery|Zustellung abschließen
Otevřít převoz →|Open transfer →|Überführung öffnen →
Otevřít / vytvořit výkaz|Open / create report|Abrechnung öffnen / erstellen
Předávací protokol|Handover report|Übergabeprotokoll
Předání zákazníkovi|Customer handover|Übergabe an Kunden
Tachometr při převzetí|Odometer at collection|Kilometerstand bei Übernahme
Tachometr při předání|Odometer at delivery|Kilometerstand bei Übergabe
Tachometr převzetí (km)|Collection odometer (km)|Kilometerstand Übernahme (km)
Tachometr předání (km)|Delivery odometer (km)|Kilometerstand Übergabe (km)
Palivo při převzetí|Fuel at collection|Tankfüllung bei Übernahme
Palivo při předání|Fuel at delivery|Tankfüllung bei Übergabe
Poškození|Damage|Schäden
Poškození a závady|Damage and defects|Schäden und Mängel
Zákazník|Customer|Kunde
Jméno zákazníka|Customer name|Kundenname
Podpis zákazníka|Customer signature|Unterschrift des Kunden
Vymazat podpis|Clear signature|Unterschrift löschen
Podpis zatím nepřiložen.|No signature yet.|Noch keine Unterschrift vorhanden.
Protokol zatím nebyl vyplněn.|Handover report not completed yet.|Übergabeprotokoll noch nicht ausgefüllt.
Ruční podpis v protokolu; nejde o kvalifikovaný elektronický podpis.|Handwritten signature; not a qualified electronic signature.|Handschriftliche Unterschrift; keine qualifizierte elektronische Signatur.
Výkaz převezme přiřazení a trasu. Opakované otevření nevytvoří další kopii.|The report uses the assignment and route. Reopening does not create a duplicate.|Die Abrechnung übernimmt Zuweisung und Strecke. Erneutes Öffnen erzeugt keine Kopie.
Nejbližší dostupný zaměstnanec|Nearest available employee|Nächster verfügbarer Mitarbeiter
Najít podle GPS místa|Find by location GPS|Nach GPS-Standort suchen
Místo zásahu|Task location|Einsatzort
Vyplňte platné souřadnice.|Enter valid coordinates.|Geben Sie gültige Koordinaten ein.
Chybí dostupní zaměstnanci s polohou potvrzenou v posledních 24 hodinách.|No available employees with a location confirmed in the last 24 hours.|Keine verfügbaren Mitarbeiter mit Standortbestätigung in den letzten 24 Stunden.
Probíhající převozy|Active transfers|Laufende Überführungen
Nevyřízené výkazy|Pending reports|Offene Abrechnungen
Nová upozornění|New notifications|Neue Benachrichtigungen
Aktuální převozy|Current transfers|Aktuelle Überführungen
OD ZADÁNÍ PO SCHVÁLENÍ|FROM ASSIGNMENT TO APPROVAL|VON ZUWEISUNG BIS FREIGABE
Méně přepisování.|Less paperwork.|Weniger Schreibarbeit.
Více času na práci.|More time to work.|Mehr Zeit für die Arbeit.
Otevřít převozy →|Open transfers →|Überführungen öffnen →
Moje aktivní úkoly|My active tasks|Meine aktiven Aufgaben
Moje čekající výkazy|My pending reports|Meine offenen Abrechnungen
Moje schválené odměny|My approved earnings|Meine genehmigten Vergütungen
Moje výdaje ke schváleným výkazům|My expenses in approved reports|Meine Auslagen in genehmigten Abrechnungen
Všechny moje úkoly →|All my tasks →|Alle meine Aufgaben →
Profil a osobní dokumenty →|Profile and personal documents →|Profil und persönliche Dokumente →
Moje pracovní historie|My work history|Meine Arbeitshistorie
Moje výkazy →|My reports →|Meine Abrechnungen →
Hodinová sazba:|Hourly rate:|Stundensatz:
Váš osobní pracovní přehled. Úkoly, výkazy a historie vaší práce.|Your personal overview. Tasks, reports and work history.|Ihre persönliche Übersicht. Aufgaben, Abrechnungen und Arbeitshistorie.
Váš provoz na jednom místě. Každý převoz propojuje vozidlo, zaměstnance a výkaz.|Your operations in one place. Every transfer links a vehicle, employee and report.|Ihr Betrieb an einem Ort. Jede Überführung verbindet Fahrzeug, Mitarbeiter und Abrechnung.
Otevřete převoz, vytvořte předvyplněný výkaz a připojte doklady. Schválené výkazy najdete ve finančních podkladech.|Open a transfer, create a prefilled report and attach receipts. Approved reports appear in financial summaries.|Öffnen Sie eine Überführung, erstellen Sie eine vorausgefüllte Abrechnung und fügen Sie Belege hinzu. Genehmigte Abrechnungen erscheinen in den Finanzunterlagen.
Schválené částky jsou podklady k vyúčtování. Neoznačují provedenou bankovní platbu.|Approved amounts are settlement records, not confirmation of a bank payment.|Genehmigte Beträge sind Abrechnungsgrundlagen und bestätigen keine Bankzahlung.
Jméno|First name|Vorname
Příjmení|Last name|Nachname
Kontakt (telefon)|Contact (phone)|Kontakt (Telefon)
Telefon|Phone|Telefon
Role|Role|Rolle
Pozice|Position|Position
Dostupnost|Availability|Verfügbarkeit
Dostupný|Available|Verfügbar
Nedostupný|Unavailable|Nicht verfügbar
Hodinová sazba (Kč/h)|Hourly rate (CZK/h)|Stundensatz (CZK/h)
Sazba|Rate|Stundensatz
E-mail|Email|E-Mail
Kontakt|Contact|Kontakt
Profil|Profile|Profil
Nový zaměstnanec|New employee|Neuer Mitarbeiter
Upravit profil|Edit profile|Profil bearbeiten
＋ Přidat zaměstnance|＋ Add employee|＋ Mitarbeiter hinzufügen
Osobní dokumenty|Personal documents|Persönliche Dokumente
Měsíční pronájmy|Monthly rentals|Monatliche Vermietungen
Rezervace, prodloužení a ukončení pronájmu. Částky jsou měsíční.|Reservations, extensions and rental termination. Prices are monthly.|Reservierungen, Verlängerungen und Mietende. Preise gelten pro Monat.
Vyberte zákazníka|Select customer|Kunden auswählen
Vyberte vozidlo|Select vehicle|Fahrzeug auswählen
Od|From|Von
Do|Until|Bis
Měsíční cena (Kč)|Monthly price (CZK)|Monatspreis (CZK)
Vratná kauce (Kč)|Refundable deposit (CZK)|Rückzahlbare Kaution (CZK)
Poznámka|Note|Notiz
Období|Period|Zeitraum
Cena / měsíc|Price / month|Preis / Monat
Upravit / prodloužit|Edit / extend|Bearbeiten / verlängern
Osobní a firemní karty s kontakty.|Personal and company contact records.|Kontaktkarten für Privat- und Firmenkunden.
Jméno / firma|Name / company|Name / Firma
Typ|Type|Typ
Osoba|Individual|Privatperson
Firma|Company|Firma
Adresa pobytu / sídla|Residential / registered address|Wohn- / Geschäftsadresse
Adresa|Address|Adresse
IČO|Company registration number|Unternehmensnummer
Soubor může mít nejvýše 10 MB.|Maximum file size is 10 MB.|Maximale Dateigröße: 10 MB.
Vyplňte platné datum.|Enter a valid date.|Geben Sie ein gültiges Datum ein.
Konec nedostupnosti nesmí být před začátkem.|The end of unavailability cannot precede the start.|Das Ende der Nichtverfügbarkeit darf nicht vor dem Beginn liegen.
Vozidlo je v tomto období nedostupné.|The vehicle is unavailable during this period.|Das Fahrzeug ist in diesem Zeitraum nicht verfügbar.
Nedostupnost se překrývá s pronájmem.|Unavailability overlaps a rental.|Die Nichtverfügbarkeit überschneidet sich mit einer Vermietung.
V tomto období má vozidlo přidělený převoz. Nejdříve převoz přesuňte nebo zrušte.|A transfer is assigned during this period. Reschedule or cancel it first.|In diesem Zeitraum ist eine Überführung zugewiesen. Verschieben oder stornieren Sie sie zuerst.
Nejdříve doplňte skutečnou SPZ vozidla.|Enter the vehicle's actual registration plate first.|Ergänzen Sie zuerst das tatsächliche Kennzeichen.
Nejdříve doplňte a ověřte vozidlo z nabídky.|Complete and verify the catalogue vehicle first.|Ergänzen und prüfen Sie zuerst das Fahrzeug aus dem Angebot.
Vozidlo je v servisu.|The vehicle is in service.|Das Fahrzeug ist in Wartung.
U vozidla již probíhá jiný převoz.|Another transfer is already in progress for this vehicle.|Für dieses Fahrzeug läuft bereits eine andere Überführung.
Záznam je zastaralý. Obnovte ho.|This record is outdated. Refresh it.|Dieser Eintrag ist veraltet. Laden Sie ihn neu.
Záznam mezitím upravil jiný uživatel. Obnovte stránku.|Another user changed this record. Refresh the page.|Ein anderer Benutzer hat den Eintrag geändert. Laden Sie die Seite neu.
`;
for (const line of rows.trim().split('\n')) {const [cs,en,de]=line.split('|');translations[cs]={en,de};}
let language='cs';try{language=localStorage.getItem('effectdeal-language')||'cs'}catch{}
if(!['cs','en','de'].includes(language))language='cs';
export const getLanguage=()=>language;
export const locale=()=>({cs:'cs-CZ',en:'en-GB',de:'de-DE'}[language]);
export function t(text){
 if(language==='cs')return text;
 if(translations[text])return translations[text][language]||text;
 if(text.endsWith(' (Kč)'))return t(text.slice(0,-5))+' (CZK)';
 const rules=[
 [/^Úsek (\d+)$/, language==='en'?'Leg $1':'Etappe $1'],
 [/^Aktuální režim: (.+)$/, (_,x)=>(language==='en'?'Current mode: ':'Aktueller Modus: ')+(x==='ukázka'?'Demo':language==='en'?'Production':'Produktion')],
 [/^(\d+) nabídek · (\d+) fotografií$/,language==='en'?'$1 offers · $2 photos':'$1 Angebote · $2 Fotos'],
 [/^Zobrazeno (\d+) z (\d+) záznamů\. Verze 0\.1 zobrazí nejvýše 100 položek na přehled\.$/,language==='en'?'Showing $1 of $2 records. Up to 100 items per overview.':'$1 von $2 Einträgen angezeigt. Bis zu 100 Einträge pro Übersicht.'],
 [/^Stav webu k (.+)\. Přenesou se popisy, technické údaje, výbava, měsíční ceny a fotografie\.$/,language==='en'?'Website snapshot: $1. Descriptions, specifications, equipment, monthly prices and photos are imported.':'Website-Stand: $1. Beschreibungen, technische Daten, Ausstattung, Monatspreise und Fotos werden importiert.'],
 [/^(\d+) zaměstnanců$/, language==='en'?'$1 employees':'$1 Mitarbeiter'],
 [/^(\d+) výkazů · strana (\d+)$/, language==='en'?'$1 reports · page $2':'$1 Abrechnungen · Seite $2'],
 [/^(\d+) úseků$/, language==='en'?'$1 legs':'$1 Etappen'],
 [/^Dobrý den, (.+)$/, language==='en'?'Hello, $1':'Guten Tag, $1'],
 [/^Převoz (.+)$/, language==='en'?'Transfer $1':'Überführung $1'],
 [/^Nedostupnost: (.+)$/, language==='en'?'Unavailable: $1':'Nicht verfügbar: $1'],
 [/^(\d+) fotografií$/, language==='en'?'$1 photos':'$1 Fotos'],
 [/^Přidat fotografie vozu \(do 10 MB za soubor\)$/, language==='en'?'Add vehicle photos (up to 10 MB per file)':'Fahrzeugfotos hinzufügen (bis 10 MB pro Datei)'],
 [/^Přidat fotografie nebo doklady \(do 10 MB za soubor\)$/, language==='en'?'Add photos or receipts (up to 10 MB per file)':'Fotos oder Belege hinzufügen (bis 10 MB pro Datei)'],
 [/^← (.+)$/, (_,x)=>'← '+t(x)],
 [/^0([1-4])\s+(.+)$/, (_,n,x)=>'0'+n+'  '+t(x)],
 ];
 for(const [pattern,replacement] of rules)if(pattern.test(text))return text.replace(pattern,replacement);
 return text;
}
const originals=new WeakMap();const attributes=new WeakMap();
export function translateDOM(root=document.body){
 if(!root)return;
 const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);let node;
 while(node=walker.nextNode()){
  const parent=node.parentElement;
  if(!parent||parent.closest('script,style,textarea,[data-no-translate]')||(['TD','DD'].includes(parent.tagName)&&!parent.classList.contains('empty')))continue;
  let original=originals.get(node);
  if(!original||node.nodeValue!==original.translated){original={source:node.nodeValue};}
  const source=original.source,trimmed=source.trim();const translated=source.replace(trimmed,t(trimmed));
  original.translated=translated;originals.set(node,original);if(node.nodeValue!==translated)node.nodeValue=translated;
 }
 for(const element of root.querySelectorAll('[aria-label],[title],[placeholder]')){
  let original=attributes.get(element)||{};
  for(const key of ['aria-label','title','placeholder'])if(element.hasAttribute(key)){
   if(!original[key]||element.getAttribute(key)!==original[key].translated)original[key]={source:element.getAttribute(key)};
   original[key].translated=t(original[key].source);if(element.getAttribute(key)!==original[key].translated)element.setAttribute(key,original[key].translated);
  }attributes.set(element,original);
 }
 document.documentElement.lang=language;
}
export function languagePicker(){return `<select class="language-picker" data-language aria-label="Language"><option value="cs" ${language==='cs'?'selected':''}>CZ</option><option value="en" ${language==='en'?'selected':''}>EN</option><option value="de" ${language==='de'?'selected':''}>DE</option></select>`}
export function initLanguage(){
 document.addEventListener('change',event=>{if(!event.target.matches('[data-language]'))return;language=event.target.value;try{localStorage.setItem('effectdeal-language',language)}catch{}document.querySelectorAll('[data-language]').forEach(e=>e.value=language);translateDOM();document.title=t(document.querySelector('#breadcrumb')?.textContent||'Přihlášení')+' · EFFECT DEAL';});
 let queued=false;new MutationObserver(()=>{if(queued)return;queued=true;queueMicrotask(()=>{queued=false;translateDOM()})}).observe(document.body,{childList:true,subtree:true,characterData:true});translateDOM();
}
