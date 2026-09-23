# Vybavení a materiál

Kanonický inventář pomůcek pro elektroniku a montáž v tomto osobním projektu. Stav doplněný **23. 9. 2026** vychází z uživatelských potvrzení, fotografií a zaznamenané zkoušky; údaje o sestavování serva a nové sadě kondenzátorů jsou pouze hlasová hlášení. Nejde o úplnou inventuru domácnosti; celkové počty nebyly sepsané. Parametry tiskárny a sklad filamentů zůstávají v [tiskárně](../docs/tiskarna.md) a [materiálech](../docs/materialy.md).

## Převzatá sada kondenzátorů

Jiří 23. 9. 2026 hlasem potvrdil, že mu sada **přišla a má ji fyzicky k dispozici**. Nejde jen o objednávku nebo katalogový seznam. Z jeho hlasového popisu zazněla napěťová označení **10 V, 16 V, 25 V a 50 V**, kapacity **0,1 µF a 0,47 µF** a údaj **až 1000 µF**. To jsou dílčí údaje z popisu sady, nikoli ověřený úplný seznam variant nebo potvrzení všech kombinací napětí a kapacit.

Počty kusů, typy kondenzátorů, výrobce, SKU a použití v zapojení nejsou potvrzené. Hodnota přepsaná jako „0,20 µF“ je z hlasu nejasná; do zapsaného výčtu ji proto nezařazujeme, dokud Jiří nepřečte štítek. Uvedených 0,1 µF odpovídá 100 nF jako jednotkový převod, ale počet a typ těchto kusů nejsou známé; dostupnost dvou vhodných keramických 100 nF pro původní zapojení zůstává neověřená.

## Nový nákup v Hornbachu

Uživatel potvrdil nákup následujících položek. **Specifikace a počty nejsou úplné; použití je doložené pouze tam, kde je výslovně uvedeno níže.**

| Položka | Co je známé | Co neodvozovat |
|---|---|---|
| Páječka | Zakoupena; nově uživatel hlásil pokus pájet přímo póly článků, stručně zaznamenaný v [řízení V3](auticko/rizeni-v3.md#průběžné-sestavování--hlasové-hlášení-20-9-2026) | Typ, příkon a regulace neznámé; hlášení nepotvrzuje zapájení motorových vodičů |
| Odsávačka pájky | Zakoupena | Provedení a vlastnosti neznámé |
| Pájka / cín | Zakoupena | Slitina, průměr, tavidlo a množství neznámé |
| Nové baterie 1,5 V | Nákup a uvedené napětí potvrzené | Počet, velikost, chemie, změřené napětí ani vložení do držáku nepotvrzené |
| Vteřinové lepidlo | Zakoupeno; později uživatel hlásil použití sekundového lepidla při pokusech s převodovkou V2 | Přesný výrobek, místo a množství neurčené; souvislost se zasekáváním není prokázaná. [Revize V2](../models/auticko-s-prevodovkou/revize-prevodovky.md) |
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
| Držák čtyř AA | Použit jako sériový motorový zdroj; při novém hlasovém sestavování uživatel uvedl články označené 1,5 V | Úplné současné osazení, chemie, stav, napětí ani proudová rezerva neověřené, ani po hlášené náhradě jednoho článku. Dříve zadané odpojení obou přívodů nepotvrdil; měření a řešení zdroje nyní výslovně odložil |
| Dříve použité AA články | Směs Ni-MH s údajem 1,2 V a běžných článků; viděna VARTA LONGLIFE MAX POWER | Úplné složení, stav nabití a napětí neznámé; nemíchat historii s novým nákupem |
| USB powerbanka AlzaPower Vision | Označení přečetl uživatel, původní přepis „Vision All“; potvrzené USB-C i USB-A. U obou přečetl štítkový režim 5 V / 3 A; další režimy a nejistoty jsou v [záznamu sestavování](auticko/rizeni-v3.md#průběžné-sestavování--hlasové-hlášení-20-9-2026) | Přesný model/produktové ID, kapacita, celkový sdílený limit a skutečné výstupní napětí nejsou určené. Štítek není měření ani potvrzené napájení serva |
| Datový USB kabel | Výměna kabelu umožnila rozpoznání a upload UNO R4 WiFi | Původní nefunkční kabel nedokládal poruchu desky |
| Dva upravované náhradní USB kabely | U prvního uživatel uvedl USB-C do powerbanky a červený/černý vodič; u druhého potvrdil USB-A, rozstřižení, stříbrný obal a zelený/červený/dva bílé vodiče | Napájecí dvojice USB-A není určená; žádný bílý automaticky neznamená GND. U USB-C nehlásil přesnou naměřenou hodnotu. Žádný kabel nebyl potvrzeně připojený k servu; nejde o původní potvrzený datový kabel |
| Multimetr | Vlastnictví výslovně potvrzené 20. 9. 2026. Před USB měřením uživatel hlásil COM, V/Ω a rozsah 20 V DC | Typ a přesné označení zdířek nebyly vizuálně ověřené. Pozdější přepnutí na kontinuitu ani pípnutí nepotvrdil, nynější nastavení neznámé; před měřením napětí znovu ověřit VDC a zdířky |
| Propojovací vodiče | Použity při sestavování | Počet a průřezy neznámé; motorové kontakty byly provizorní bez pájení |
| Odpor 10 kΩ | Uživatel potvrdil zapojení mezi enable a GND; identifikace z proužků | Celková zásoba rezistorů není inventarizovaná |
| SW-520D | Identifikovaný náklonový spínač | Není kondenzátor |
| Tower Pro Micro Servo 9g SG-90 | Uživatel přečetl označení a potvrdil vlastnictví; 20. 9. 2026 hlasem potvrdil oranžový vodič → UNO D9 a hnědý → UNO GND, červený uprostřed zůstal volný | Analogová/digitální varianta, skutečné rozměry těla, rozsah a moment nejsou měřené. Napájení, pohyb či fyzická zkouška serva nepotvrzené; stav páčky/táhla není známý |
| Tři plastové páčky k SG90 a středový šroubek | Uživatel výslovně potvrdil jednu jednoramennou, jednu dvouramennou a jednu čtyřramennou; pro řízení je zvolená jednoramenná. Středový upevňovací šroubek má. Na přesnou otázku střed velkého otvoru pro osu serva → střed krajního malého otvoru potvrdil **15 mm** („Je to přesně patnáct milimetrů“). Jde o uživatelské fyzické měření účinného poloměru. Celkovou délku páčky dříve uvedl 20 mm | Starší údaj 19 mm měl neurčený konec měření a není účinným poloměrem; pro návrh platí nově potvrzených 15 mm. Průměr malého otvoru ani velikost dostupného spojovacího šroubku neznáme; drážkování se nebude nahrazovat odhadnutým tištěným profilem |
| Krokový motor, hlasově přečtené označení „StepMotor 28BY…-48, 5 V DC“ | Uživatel 23. 9. 2026 potvrdil, že je k dispozici, a navrhl jej pro první pokusy s robotickou paží | Prostřední písmena štítku nejsou z hlasu jistá; 28BYJ-48 je pouze pravděpodobná varianta. Počet kusů, přesné připojení, stav a funkčnost nejsou potvrzené |
| Silikonový olej | Uživatel potvrdil vlastnictví a namazání hřídelek autíčka pro snížení odporu | Výrobek a složení neznámé; podle uživatele moc nepomohlo, přínos neměřený. [Záznam potíží](auticko/potize-po-montazi.md) |

Při pozdějších pokusech s převodovkou V2 uživatel uvedl olej po sekundovém lepidle. Druh tohoto oleje a místo aplikace nejsou určené; nelze jej automaticky ztotožnit s dříve potvrzeným silikonovým olejem. [Aktuální revize V2](../models/auticko-s-prevodovkou/revize-prevodovky.md).

U jednoramenné páčky SG90 uživatel navíc potvrdil vnitřní ozubení ve středovém otvoru a záměr zajistit páčku původním středovým šroubkem. Nejde o potvrzenou zatěžovací zkoušku nebo přenos momentu bez prokluzu. Návrh používá originální páčku, bez vlastního tištěného drážkování.

Uživatel poskytl [odkaz na LaskaKit MAXI RFID](https://www.laskakit.cz/laskkit-arduino-maxi-starter-kit--rfid/). Zveřejněný katalog není kontrolou všech skutečně vlastněných kusů ani potvrzením varianty desky. Zachovaná identifikace fotografií a součástek je v [historii elektroniky](auticko/elektronika.md).

Pro mechanický návrh SG90 výrobce uvádí nominální obálku **23 × 12,2 × 29 mm**, hmotnost 9 g a záběrný moment 1,8 kg·cm při 4,8 V. Jde o údaje [TowerPro SG90 Analog](https://towerpro.com.tw/product/sg90-analog/) a [SG90 Digital](https://towerpro.com.tw/product/sg90-7/), ověřené 19. 9. 2026, nikoli měření Jirkova kusu či důkaz momentové rezervy v autíčku. Výrobce u běžných serv v odpovědi na digitální stránce uvádí 0–150°, není tedy podklad automaticky požadovat 180°. Typ uší a průměr malého otvoru zůstávají k ověření; účinný poloměr 15 mm i vlastnictví středového šroubku již uživatel potvrdil. Elektronická příprava a následné částečné propojení z 20. 9. 2026 jsou v [řízení V3](auticko/rizeni-v3.md); napájení a fyzická zkouška serva zůstávají nepotvrzené.

## Dostupnost zatím nepotvrzená

- Dva doporučené keramické kondenzátory 100 nF při prvním testu chyběly; nově převzatá sada podle hlasového popisu obsahuje hodnotu 0,1 µF, ale počet, typ a vhodnost těchto kusů pro původní zapojení nejsou potvrzené.
- Malé elektrické krokosvorky a konkrétní konektory motoru nemají potvrzenou dostupnost; multimetr je nově potvrzený výše.
- Malé stahovací pásky pro motor a vhodné pásky pro plošinu jsou montážní požadavek; jejich vlastnictví nebylo potvrzené.

Skutečné podmínky historického testu jsou v [záznamu první zkoušky](auticko/prvni-stolni-test.md). Budoucí použití vybavení zapisovat až podle potvrzení, ne podle toho, že už je nakoupené.
