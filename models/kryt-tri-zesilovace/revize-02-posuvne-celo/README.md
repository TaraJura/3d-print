# V02 — kompaktní kryt 3 zesilovačů, čelo zasouvané shora

Revize podle Jiřího zadání 22. 10. 2026. **PCB má pevně 78 × 108 mm.** Tato revize nahrazuje prostorový koncept v01. Šířka a délka desek už nejsou odhad, jejich tloušťka a výška osazení však nebyly změřeny. **Před tiskem celého krytu doplnit skutečnou výšku osazení** — aktuální parametr 38 mm nad horní plochou PCB je stále zástupný, nikoli potvrzená hodnota nebo tvrzení o nejmenší možné výšce.

## Co se změnilo

- Vnější tunel **88,4 × 134 × 157,2 mm (šířka × hloubka × výška)** při současné neověřené výšce osazení. Celé vytištěné díly po sestavení, včetně zadních distancí, dolního montážního ouška a horní pojistky, mají obálku **88,4 × 144,8 × 173,5 mm**. Knoflíky, kabely a hlavy spojovacího materiálu v tomto rozměru nejsou započtené.
- Stěny 2,4 mm; místo tří velkých nosných rámečků jsou v těle integrované lišty pro okraje PCB. Součet objemů všech konstrukčních dílů v CAD klesl z 510,12 na 214,99 cm³, tedy o **57,85 %**. Je to porovnání CAD geometrie, nikoli měření spotřeby filamentu; podpory a tiskový proces mají vlastní odhad.
- Čelo je samostatná deska, která se **nasouvá shora** do dvou drážek. Dole dosedá na pevný doraz. Vůle v drážce je návrhově 0,3 mm na kontaktní stranu.
- Horní přídržná lišta dosedá na střechu a čelo; zajistí ji **jeden M3 šroub do vložené matice**. Žádné lepení.
- Zadní víko upevňují **čtyři M3 šrouby do přístupných kapes pro matice**. Víko obsahuje šest malých zadních dorazů, které brání vyjetí desek z lišt; desky nepřenášejí sílu přes RCA ani ovladač.
- Dvě horní klíčové dírky slouží k zavěšení celé sestavy na zeď, dolní dostupné ouško k zajištění proti nadzvednutí. Tři samostatné 8mm distanční kroužky nechávají prostor za zadním panelem.
- Každé patro má zadní kabelový průchod 34 × 18 mm se zaoblením a dva otvory pro stahovací pásek. Uvnitř za PCB zůstává 18 mm. Potřebný ohyb kabelů a vnější průměry se musí ověřit na skutečné kabeláži.

## Rozměry a jejich původ

| Údaj | Hodnota / použití | Evidence |
|---|---|---|
| PCB | **78 × 108 mm** | Uživatel: pevný rozměr, neměnit kvůli konektorům |
| Ovladač | 12 mm široký, 15 mm od kraje PCB | Uživatel; není jednoznačně určeno, zda 15 mm míří na osu nebo okraj |
| RCA dvojice | 25 mm široká, 10 mm od protější hrany | Uživatel, přibližné měření |
| Mezera ovladač–RCA | Hlášeno 20 mm | Zachováno jako původní údaj; řetězec 15+12+20+25+10 dává 82 mm, proto se PCB neroztahuje |
| Výřez RCA | 30 × 22 mm, od 8 do 38 mm od levé hrany PCB při pohledu zepředu | Návrhová rezerva kolem přibližného umístění |
| Výřez ovladače | 23 × 22 mm, od 49 do 72 mm od levé hrany PCB | Pokrývá variantu 15 mm k ose i ke kraji 12mm ovladače; fyzickou polohu ověřit |
| Tloušťka PCB | 1,6 mm, drážka vysoká 2,6 mm | Neměřený návrh |
| Boční vůle PCB | 0,4 mm na každé straně | Návrhová tisková vůle, fyzicky neověřená |
| Volná boční hrana PCB | Nejméně 1,2 mm po obou dlouhých stranách | Podmínka použití těchto lišt; součástky ani pájení nesmějí zasahovat do podpěr |
| Osazení | 38 mm nad horní plochou PCB | **NEMĚŘENO; hlavní dosud chybějící údaj** |
| Mezery nad osazením | 8 mm mezi patry a pod střechou; lokálně menší u montážních bossů mimo osu ventilátoru | Návrh, nikoli tepelná validace |
| Přesah RCA/knoflíku a jejich výška | Zástupná reference v CAD | Neměřeno, zobrazované válce nejsou přesnou kopií modulu |

Názorné reference desek, chladičů, ventilátorů a konektorů se **netisknou**. Součástí souborů STL/3MF je pouze kryt a mechanické díly.

## Montáž bez lepidla

Potřebný navržený spojovací materiál: **4× M3×12, 1× M3×10 a 5× běžná matice M3**. Kapsy jsou navržené pro přibližný rozměr matice 5,5 mm přes plochy a 2,4 mm tloušťky, s návrhovou vůlí. Jejich skutečné vlastnictví ani použití není potvrzené. Tři vruty a kotvy pro zeď zvolit podle skutečné stěny a zatížení; horní klíčové dírky mají širší část Ø9,6 a užší část 5,2 mm.

1. Očistit podporované plochy, vedení a kapsy po tisku. Nanečisto vyzkoušet posuv prázdného čela a matic, bez násilí.
2. Do těla vložit čtyři matice zadních šroubů z vnitřních bočních otvorů a jednu horní matici zevnitř směrem k čelu. Matice se nevkládají přes malé otvory pro šroub.
3. **Čelo zasunout shora do prázdného těla.** K jeho úplnému vložení je nad tělem potřeba alespoň výška čela 154,8 mm. Celý tento krok se pohodlně provede mimo zeď.
4. Osadit horní pojistku a přišroubovat M3×10. Pojistka dosedá přímo na střechu; není mezi ní a tělem navržená vzduchová mezera.
5. Z PCB sejmout stávající bílé nožičky/distanční prvky, pokud překážejí vedení. Lišty jsou určeny pro holé hrany PCB. Ověřit volný pás 1,2 mm a skutečnou tloušťku, výšku součástek i spodních pájených vývodů.
6. Desky jednotlivě zasouvat **zezadu směrem k čelu** do příslušných lišt, až dosednou na přední dorazy PCB. RCA a knoflíky procházejí širokými čelními výřezy. Nepoužívat konektory jako montážní doraz.
7. Zapojit a vést kabely zadními průchody; připravit odlehčení tahu pásky bez přitahování vodičů k hranám otvorů. Nasadit zadní víko s dorazy a připevnit 4× M3×12. Podle skutečných kabelů ověřit, že se nic neskřípne.
8. Na stěnu připravit horní vruty s distančními kroužky a zavěsit **celou sestavenou skříňku**. Distanční kroužky zůstávají na vrutech u zdi: jejich malými otvory neprotáhneš hlavy vrutů a nesmějí být přilepené k posouvané skříňce. Dole přidat třetí distanci a přístupný zajišťovací vrut přes dolní ouško.

**Demontáž čela:** sundat skříňku ze zdi, povolit zadní víko a desky povytáhnout tak, aby konektory a ovladače opustily rovinu čela. Pak odšroubovat horní pojistku a čelo vysunout nahoru. Uzavřené čelní výřezy nemohou přejít přes připojené vyčnívající konektory při svislém pohybu. Čelo proto není určeno k samostatnému vysunutí při osazených deskách.

## Soubory

- [Parametrický FreeCAD](kryt.FCStd), [zdrojové makro](kryt.FCMacro).
- [Zavřený kryt](nahled-zpredu.png), [zasouvání čela](nahled-nasouvani-cela.png), [vnitřek](nahled-vnitrek.png), [zadní víko a dorazy](nahled-zadni-viko.png), [zadní uchycení](nahled-zezadu.png).
- [Tiskové podložky](rozlozeni/README.md): 7 kusů, každá fyzická kopie již zahrnuta. Nastavené projekty jsou určené jako **rozměrový PLA prototyp podmíněný výškou a kontrolou hran PCB**. Před ověřením měr netisknout celou sadu.
- [Geometrický report](kontrola-modelu.json), [nezávislý montážní audit](audit-montaze.json), [parametrický test a porovnání objemů](kontrola-parametru.json).

## Digitální kontrola a její hranice

Sedm dílů má po jednom validním solidu a jedné uzavřené STL komponentě. Statické objemové kolize mezi díly a zadanými PCB jsou nulové. Nezávislý audit ověřuje **souvislé obálky celého pohybu** čela, PCB, zástupných součástek a vložení matic, nikoli jen vybrané polohy. Vyžaduje uvedený volný 1,2mm pás na hranách PCB, předpokládanou výšku osazení a zkouší i hypotetický 2mm přesah pájení pod deskou. Průchod těchto testů není měřením skutečných zesilovačů.

Uložený FCStd obsahuje standardní FreeCAD objekty, tabulku a výrazy. Přepočet nepotřebuje vlastní Python třídu. Makro a exporty jsou sladěné, historická v01 se nepřepisuje. Parametrický test se provádí bez uložení zkušebních hodnot do předávaného CAD.

Tělo se tiskne otevřenou zadní hranou dolů, aby se netiskl široký nepodepřený strop přes celé pouzdro. Lokální podpory pod předními vodítky a kapsou matice řeší uložený slicer projekt; podpory je potřeba odstranit před montáží. Čelo, zadní víko, pojistka a distanční kroužky mají vlastní vhodnou orientaci. Barvy CAD jsou orientační, nepotvrzují cívky ani vícebarevný tisk.

PLA profil je pro rozměrový prototyp. Provozní teplota, vhodnost materiálu, chlazení, skutečné kotvy, hmotnost elektroniky, fyzický fit a fyzický tisk nejsou ověřené. Žádný tisk nebyl spuštěn ani poslán na tiskárnu.
