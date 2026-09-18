# Polička na zárubeň — první testovací návrh

Otevřete **policka-90x50.FCStd** ve FreeCADu. Hotový model tvoří jeden kus: spodní deska, dvě zadní montážní ramena, dva průchozí otvory a čtyři malé boční výztuhy. STL je export stejné geometrie pro slicer; jednotky jsou milimetry.

## Rozměry

| Parametr | Hodnota | Stav |
|---|---:|---|
| Šířka × hloubka desky | **90 × 50 mm** | Zadáno uživatelem |
| Tloušťka desky | 4 mm | Návrhová hodnota |
| Šířka jednoho zadního ramene | 16 mm | Návrhová hodnota |
| Výška ramene nad deskou | 30 mm | Návrhová hodnota |
| Celková výška | 34 mm | Odvozená hodnota |
| Tloušťka zadních ramen | 4 mm | Návrhová hodnota |
| Otvory | 2 × Ø 4,5 mm, bez zahloubení | Návrhová hodnota |
| Rozteč středů otvorů | 60 mm | Návrhová hodnota |
| Výška středů otvorů nad horní plochou desky | 18 mm | Návrhová hodnota |
| Výztuhy | 4 × tloušťka 2,4 mm, dosah 12 mm, výška 10 mm | Návrhové hodnoty |

Deska má celkový půdorys 90 × 50 mm; zadní ramena zabírají zadní 4 mm tohoto půdorysu. Svislá montážní plocha je vzadu. Otvory vedou kolmo skrz zadní ramena a jsou přístupné zepředu nad výztuhami.

## Úpravy

Ve stromu FreeCADu otevřete tabulku **Parametry (mm) — upravit sloupec B**. Zelené buňky označují zadaný půdorys, žluté buňky návrhové hodnoty. Po změně rozměrů dokument přepočítejte. Model používá standardní objekty a výrazy FreeCADu; k přepočtu nepotřebuje externí makro ani doplněk.

Makro **policka.FCMacro** slouží k opětovnému vytvoření dokumentu a exportu STL. Po úpravách přímo ve FCStd je nutné exportovat nové STL z finálního objektu **Polička — 1 kus, 2 otvory**; původní soubor STL se sám neaktualizuje.

## Ověření a otevřené body

Geometrie je platný jediný solid a exportovaná STL síť je uzavřená. Ověřen byl také parametrický přepočet při změně šířky 90 → 100 → 90 mm včetně správného posunu druhého otvoru a návratu původního objemu. Pomocné objekty jsou v uloženém dokumentu skryté.

Před funkčním použitím zbývá potvrdit typ a rozměr šroubů, jejich uchycení v konkrétní zárubni, materiál tisku a požadované zatížení. **Nosnost ani rozměrové přizpůsobení skutečné zárubni nebyly ověřeny.** Návrh nebyl odeslán tiskárně ani vytištěn.

Soubor **model-render.png** je náhled přímo z CAD geometrie, nikoli generovaná ilustrace. **kontrola-modelu.json** obsahuje kontrolní rozměry a výsledky kontroly geometrie.
