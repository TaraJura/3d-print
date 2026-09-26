# Připravené podložky první robotické ruky

Soubory jsou pro **Anycubic Kobra X, trysku 0,4 mm**. Každou podložku otevři v Anycubic Slicer Next **jako samostatný celý projekt, právě jednou**. Kopie a poloha jsou již připravené; nic nepřidávej ani automaticky nepřerovnávej.

| Pořadí | Nastavený projekt k otevření | Obsah | Očíslovaný náhled |
|---|---|---|---|
| 1 | [Měrka motoru](podlozka-merka-01-nastaveny-projekt.3mf) | 1 zkušební kus; **není součástí montáže** | [01 – měrka](podlozka-merka-01.png) |
| 2 | [Kompletní první sestava](podlozka-sestava-01-nastaveny-projekt.3mf) | 12 fyzických kusů | [01 – sestava](podlozka-sestava-01.png) |

Měrka ověřuje nominální rozteč montážních otvorů a tvar hřídelky typu 28BYJ-48 na **skutečném** motoru. Po tisku ověř, zda sedí na konkrétní kus, teprve pak rozhodni o tisku celé sestavy. Nesprávný fit uprav v parametrickém modelu a znovu vygeneruj STL i podložky.

## Montážní kusovník na podložce sestavy

| Díl | Počet |
|---|---:|
| Výměnná horní plošina autíčka | 1 |
| Otočná základna s kluzným prstencem | 1 |
| Nadloktí | 1 |
| Předloktí s pevně otevřenou dvouprstou rukou | 1 |
| Čep kloubu (osové a aretační spoje) | 4 |
| Snímatelná C-pojistka čepu | 4 |
| **Celkem** | **12** |

Měřítko všech objektů je 100 %. Horní plošina leží při tisku velkou rovnou plochou na podložce a kapsy míří nahoru. Čtyři čepy stojí na hlavě, podélnou osou Z. Poloha je zapsaná ve zdrojových STL a [manifestu](dily.json), proto se při opakování nevrátí jiná orientace.

## Proces a podpory

- Uložený proces vychází ze systémové kombinace **Kobra X 0,4 mm / Anycubic PLA / 0,16 mm Standard**. Pro prototyp je z ní odvozený jasně pojmenovaný nekalibrovaný profil Alzament PLA Basic s podložkou **50 °C v první i dalších vrstvách**. Hodnota je v dodavatelském rozsahu 45–60 °C; přilnavost konkrétní cívky při 50 °C musí potvrdit tisk. Ostatní hodnoty filamentu jsou původní Anycubic PLA, zejména tryska 215 / 205 °C, a nejsou kalibrací Alzamentu. Proces má 4 stěny, 20% výplň, 0,20mm první vrstvu, 5mm brim a rychlosti 20 mm/s první vrstva, 60 mm/s vnější stěny a 90 mm/s vnitřní stěny. Čepy mají objektově 100% výplň.
- **Skutečné podpory jsou zapnuté pouze u otočné základny**, včetně podpory pod kotoučem uvnitř kluzného prstence a u horních čelistí. Slicer je při místním řezu skutečně vytvořil. Po tisku je nutné vyčistit spodní kluznou plochu, D profil hřídelky a otvory; odstranitelnost a funkční vůle zatím nejsou fyzicky ověřené.
- Měrka, plošina, nadloktí, předloktí, čepy a pojistky mají podpory vypnuté. Brim slouží jen k přilnavosti; na čtyřech svislých čepech nenahrazuje fyzické ověření stability a pevnosti vrstev.
- V Next zkontroluj reálnou PLA cívku a její vstup. Název profilu ani barva náhledu volbu fyzické cívky nepotvrzují. Změna materiálu či procesu vyžaduje nový řez a kontrolu drah.

Po změně na 50 °C místní řez **měrky nehlásí žádné varování**. Řez sestavy stále hlásí `not_support_traditional_timelapse`; týká se režimu časosběru. Izolovaný kontrolní řez se změnou jediného parametru `timelapse_type` z 0 na 1 varování také nezrušil. Proto zůstává výchozí hodnota 0; další zásah do režimu časosběru nebo profilu tiskárny by neměl ověřený přínos pro tento model. [Audit řezu](overeni.json) a [kontrola varování](kontrola-casosberu.json) ukládají přesný výsledek.

## Co bylo ověřeno v počítači

- Každé ze sedmi aktuálních STL je vodotěsné a jeden solid. [Manifest](rozlozeni.json) zapisuje SHA256 STL pro každou kopii a audit je porovnal s aktuálními soubory.
- Oba nastavené projekty prošly importem i lokálním řezem Next. V geometrii, nastaveném projektu a po řezu zůstalo všech 13 samostatných objektů: 1 měrka a 12 montážních kusů. Audit ověřil v obou projektech texturovanou podložku, 50 °C pro první i další vrstvy, skutečný příkaz `M140 S50` v místním G-code a zachování všech objektových podpor. Největší odchylka souřadnic vrcholů při importu je v [auditu](overeni.json).
- Na montážní podložce je nejmenší mezera **modelů 16 mm**. Skutečné obálky všech extruzních drah modelu, podpor a brimu mají nejmenší mezeru **6,57 mm** a nejmenší odstup od kraje **7,27 mm**. Měrka má od kraje **7,26 mm** včetně drah.
- [Skutečné dráhy sestavy](podlozka-sestava-01-drahy.png) a [kritické vrstvy podpor](podlozka-sestava-01-kriticke-vrstvy.png) byly vykreslené z místního G-code. [Dráhy měrky](podlozka-merka-01-drahy.png) prošly stejnou kontrolou. Diagnostický G-code zůstává v ignorované `.cache`, není tiskovým předávacím souborem.
- Odhad Next: měrka **9 min 15 s / 2,07 g**, sestava **5 h 25 min 8 s / 82,58 g**. Jde o odhad procesu, nikoli o naměřený tisk.

Fyzický fit motoru, vyčištění podpor, pevnost čepů, kontakt kluzného prstence, zajištění plošiny, zatížitelnost paže ani stabilita autíčka nebyly ověřené. Tiskárně nebyla poslána žádná úloha.

## Alternativa a obnova

[Geometrie měrky](podlozka-merka-01-geometrie.3mf) a [geometrie sestavy](podlozka-sestava-01-geometrie.3mf) jsou **pouze rozmístění bez tiskových, materiálových a podporových nastavení**. Použij je jen při vědomé volbě vlastního procesu. Nekombinuj geometrickou a nastavenou verzi jedné podložky v jedné úloze.

Zdroj pořadí a počtů je [dily.json](dily.json). Po změně FreeCAD makra a jeho STL spusť z kořene projektu postupně `pripravit.py`, `projekt.py` a `overit.py` místním Pythonem s numpy, trimesh, shapely a matplotlib. Generátor zapisuje jen do této složky a do ignorované lokální cache. Nastavené projekty jsou vytvořené ze stejné geometrie, kterou audit následně kontroluje po importu i řezu.
