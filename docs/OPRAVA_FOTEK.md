# Oprava profilové fotografie a galerie

Tento balíček obsahuje opravu pro původní verzi EFFECT DEAL 0.1.

## Nasazení

1. Rozbalte ZIP.
2. Na GitHubu nahraďte soubory při zachování přesných cest:
   - `app/api/routes.py`
   - `app/static/js/app.js`
   - `app/static/js/core/ui.js`
   - `app/static/js/pages/vehicles.js`
   - `app/static/js/pages/documents.js`
   - `app/static/css/app.css`
3. Commit changes. Render → Manual Deploy → Deploy latest commit.
4. Po dokončení obnovte stránku aplikace. Nastavení Renderu i requirements zůstávají stejné.

Testy a dokumentace jsou přiložené pro další vývoj. Do repozitáře se nahrává obsah ZIPu, nikoliv samotný ZIP.

## Používání

- Vozový park → otevřít vozidlo → Fotografie vozidla.
- Přidat lze i více fotografií najednou (celkem nejvýše 10, JPG/PNG/WebP do 10 MB za soubor).
- První nově nahraná fotografie se automaticky nastaví jako profilová, pokud vozidlo dosud žádnou nemá.
- U kterékoliv další fotografie klikněte na „Nastavit jako profilovou“.
- Zvolený obrázek se objeví na kartě vozidla i v jeho detailu.
- Klepnutí na fotografii otevře zvětšený náhled uvnitř aplikace. Šipky přepínají fotografie, Escape nebo Zavřít náhled zavře.
- Galerie je i u fotografií ve výkazech a předávacích protokolech. V Dokumentech použijte „Zobrazit fotografii“.
- PDF a další dokumenty zůstávají samostatně ke stažení. Fotografii lze dobrovolně stáhnout odkazem v náhledu.

U již dříve nahraných fotek není nutný nový upload: v galerii vyberte profilovou fotografii tlačítkem. Změny profilové fotky může provádět stejná role jako běžné úpravy vozidla; zaměstnanec má pouze náhled přiřazených vozidel.

## Ověření

Prošlo 19 testů serveru: původní workflow i nové testy fotek, přístupů, konfliktů při editaci a limitu 10 příloh.
V Chromium ověřeno nahrání dvou fotek, automatický výběr první, změna a zachování profilové fotky po obnovení, zobrazení na kartě, galerie a přepínání, mobilní šířka 390 px i náhled zaměstnance bez možnosti změny.

Oprava nemění úložiště ani nemaže záznamy. Stále platí omezení původního demo režimu: při nasazení/restartu může Render smazat dočasnou SQLite databázi. Trvalé uchování vyžaduje nakonfigurovanou produkční databázi.
