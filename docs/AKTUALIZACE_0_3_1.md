# Aktualizace 0.3.1 — menu a nastavení

Tento balíček navazuje na aktualizaci 0.3. Obsahuje pouze změny menu a nastavení.
Nahrajte soubory ze složky app se zachováním cest. Dokumentace a test jsou nepovinné pro běh.
V Renderu stačí Deploy latest commit. Start Command a připojení databáze se nemění.

Pořadí menu: Domovská strana, Vozový park, Rozvoz a svoz, Pronájmy, Zákazníci,
Zaměstnanci, Výkazy, Finance, Statistiky, Pošta, Dokumenty, Správa uživatelů, Nastavení.
Položky se dále omezují podle oprávnění uživatele.

Profil je dostupný kliknutím na iniciálu nebo jméno přihlášeného uživatele dole.
Každý tím otevře svůj vlastní profil. Majitel a manager mohou spravovat další profily
v položce Zaměstnanci. Odhlášení zůstává samostatným tlačítkem.

Nastavení obsahuje Import a Nový vůz. Přístup mají majitel a manager.
Nový vůz otevře formulář interní nabídky včetně měsíční ceny a technických údajů.
Nabídka může být vytvořena bez SPZ ve stavu K doplnění. Fotografie se přidávají
v detailu uloženého vozu. Před přiřazením k pronájmu/převozu je nutné údaje ověřit.
Vytváření vozidel je zakázané dispečerovi i zaměstnanci také na serveru.
Dispečer může nadále upravovat provozní údaje existujících vozidel, nikoli cenu.
Změny interní nabídky se automaticky nepublikují na veřejném effectdeal.com.

43 automatických testů prošlo. Mobilní prohlížeč ověřil pořadí menu, otevření vlastního
profilu majitele a řidiče, vytvoření nabídky bez SPZ, záložku importu a německé popisky.
