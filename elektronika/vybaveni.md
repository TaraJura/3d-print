# Vybavení a materiál

Kanonický inventář pomůcek pro elektroniku a montáž v tomto osobním projektu. Stav k **19. 9. 2026** vychází z uživatelských potvrzení, fotografií a zaznamenané zkoušky. Nejde o úplnou inventuru domácnosti; celkové počty nebyly sepsané. Parametry tiskárny a filamentů zůstávají v [tiskárně](../docs/tiskarna.md) a [materiálech](../docs/materialy.md).

## Nový nákup v Hornbachu

Uživatel potvrdil nákup následujících položek. **Specifikace, počty a jejich použití zatím nejsou potvrzené.**

| Položka | Co je známé | Co neodvozovat |
|---|---|---|
| Páječka | Zakoupena | Typ, příkon, regulace ani připravenost k použití neznámé |
| Odsávačka pájky | Zakoupena | Provedení a vlastnosti neznámé |
| Pájka / cín | Zakoupena | Slitina, průměr, tavidlo a množství neznámé |
| Nové baterie 1,5 V | Nákup a uvedené napětí potvrzené | Počet, velikost, chemie, změřené napětí ani vložení do držáku nepotvrzené |
| Vteřinové lepidlo | Zakoupeno | Přesný výrobek, množství a použití neznámé |
| Svěrky | Zakoupeny | Počet, rozměry a provedení neznámé; nejde automaticky o elektrické krokosvorky |

Při prvním stolním pokusu uživatel páječku a cín neměl. To je historický stav před tímto nákupem. Nákup sám nepotvrzuje zapájení motorových vodičů, výměnu baterií ani slepení mechanických dílů.

## Potvrzené součástky a vybavení u autíčka

| Položka | Evidence / známé provedení | Omezení |
|---|---|---|
| Arduino UNO R4 WiFi | Uživatel, USB identifikace a úspěšné uploady | Další Arduino desku nelze určit jen z katalogu sady |
| ST L293D, DIP16 | Detail čipu a výslovné potvrzení uživatele; použit v prvním testu | Odběr motoru a rezerva pod zátěží nejsou měřené |
| Modul TI ULN2003AN | Čitelné označení na detailní fotografii | Pro pohon autíčka byl nakonec použit L293D |
| Samostatný dvouvodičový DC motor | Bez nápisu, podle uživatele není z uvedené sady; první rozběh potvrzen | Rozsah 1–6 V je pracovní předpoklad, proud neznámý; mechanické údaje v [modelu](../models/jednoduche-auticko/README.md) |
| Nepájivé pole | Použito při testu; uživatel zadal rozměr 170 × 60 mm pro horní plošinu | Vnitřní propojení konkrétních lišt nebylo celé nezávisle proměřeno |
| Držák čtyř AA | Použit jako sériový motorový zdroj | Aktuální obsazení držáku není potvrzené |
| Dříve použité AA články | Směs Ni-MH s údajem 1,2 V a běžných článků; viděna VARTA LONGLIFE MAX POWER | Úplné složení, stav nabití a napětí neznámé; nemíchat historii s novým nákupem |
| USB powerbanka | Při první stolní zkoušce napájela Arduino | Typ, kapacita a aktuální připojení neznámé |
| Datový USB kabel | Výměna kabelu umožnila rozpoznání a upload UNO R4 WiFi | Původní nefunkční kabel nedokládal poruchu desky |
| Propojovací vodiče | Použity při sestavování | Počet a průřezy neznámé; motorové kontakty byly provizorní bez pájení |
| Odpor 10 kΩ | Uživatel potvrdil zapojení mezi enable a GND; identifikace z proužků | Celková zásoba rezistorů není inventarizovaná |
| SW-520D | Identifikovaný náklonový spínač | Není kondenzátor |
| Tower Pro Micro Servo 9g SG-90 | Uživatel 19. 9. 2026 fyzicky přečetl označení a potvrdil vlastnictví; určeno pro návrh předního zatáčení | Analogová/digitální varianta, skutečné rozměry těla, rozsah a moment nejsou měřené; dosud nebylo zapojené ani odzkoušené v této sestavě |
| Tři plastové páčky k SG90 a středový šroubek | Uživatel výslovně potvrdil jednu jednoramennou, jednu dvouramennou a jednu čtyřramennou; pro řízení je zvolená jednoramenná. Středový upevňovací šroubek má. Na přesnou otázku střed velkého otvoru pro osu serva → střed krajního malého otvoru potvrdil **15 mm** („Je to přesně patnáct milimetrů“). Jde o uživatelské fyzické měření účinného poloměru. Celkovou délku páčky dříve uvedl 20 mm | Starší údaj 19 mm měl neurčený konec měření a není účinným poloměrem; pro návrh platí nově potvrzených 15 mm. Průměr malého otvoru ani velikost dostupného spojovacího šroubku neznáme; drážkování se nebude nahrazovat odhadnutým tištěným profilem |
| Krokový motor s označením „StepMotor 28BY…-48, 5VDC“ | Uživatel přečetl štítek, hlasový přepis prostředních písmen kolísá; může odpovídat 28BYJ-48 uvedenému v katalogu sady | Přesný přepis typu ještě nepotvrzený; není to druhý dvouvodičový DC motor. Pro navržené zatáčení SG90 se nepoužije |
| Silikonový olej | Uživatel potvrdil vlastnictví a namazání hřídelek autíčka pro snížení odporu | Výrobek a složení neznámé; podle uživatele moc nepomohlo, přínos neměřený. [Záznam potíží](auticko/potize-po-montazi.md) |

U jednoramenné páčky SG90 uživatel navíc potvrdil vnitřní ozubení ve středovém otvoru a záměr zajistit páčku původním středovým šroubkem. Nejde o potvrzenou zatěžovací zkoušku nebo přenos momentu bez prokluzu. Návrh používá originální páčku, bez vlastního tištěného drážkování.

Uživatel poskytl [odkaz na LaskaKit MAXI RFID](https://www.laskakit.cz/laskkit-arduino-maxi-starter-kit--rfid/). Zveřejněný katalog není kontrolou všech skutečně vlastněných kusů ani potvrzením varianty desky. Zachovaná identifikace fotografií a součástek je v [historii elektroniky](auticko/elektronika.md).

Pro mechanický návrh SG90 výrobce uvádí nominální obálku **23 × 12,2 × 29 mm**, hmotnost 9 g a záběrný moment 1,8 kg·cm při 4,8 V. Jde o údaje [TowerPro SG90 Analog](https://towerpro.com.tw/product/sg90-analog/) a [SG90 Digital](https://towerpro.com.tw/product/sg90-7/), ověřené 19. 9. 2026, nikoli měření Jirkova kusu či důkaz momentové rezervy v autíčku. Výrobce u běžných serv v odpovědi na digitální stránce uvádí 0–150°, není tedy podklad automaticky požadovat 180°. Typ uší a průměr malého otvoru zůstávají k ověření; účinný poloměr 15 mm i vlastnictví středového šroubku již uživatel potvrdil. Konkrétní elektrické zapojení a napájení serva se určí později.

## Dostupnost zatím nepotvrzená

- Dva doporučené keramické kondenzátory 100 nF při prvním testu chyběly; nový nákup jejich dostupnost nepotvrdil.
- Multimetr, malé elektrické krokosvorky a konkrétní konektory motoru nemají potvrzenou dostupnost.
- Malé stahovací pásky pro motor a vhodné pásky pro plošinu jsou montážní požadavek; jejich vlastnictví nebylo potvrzené.

Skutečné podmínky historického testu jsou v [záznamu první zkoušky](auticko/prvni-stolni-test.md). Budoucí použití vybavení zapisovat až podle potvrzení, ne podle toho, že už je nakoupené.
