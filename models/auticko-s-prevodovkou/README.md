# Autíčko s převodovkou 12:1

Nový samostatný mechanický prototyp s poháněnou společnou zadní osou, dvěma volnými předními koly a snímatelnou horní plošinou. Původní [autíčko](../jednoduche-auticko/README.md) a jeho střecha zůstávají zachované. Nové osy, kola, pojistky, rám ani plošinu se starými díly nekombinuj. Výjimkou je tentýž motor a geometricky shodný původní pastorek18z s otvorem2,2 mm; jeho opětovné použití závisí na nepoškozeném uložení a nasazení.

**Stav: nová geometrie, fyzicky nevytisknuto ani nevyzkoušeno.** Není prokázané, že samotný převod odstraní dosavadní těžký rozjezd/bzučení. Tento problém se podle uživatele objevil už před změnou ovládání; namazání hřídelek silikonovým olejem prý moc nepomohlo. Motor, napájení, tření i přenos momentu pastorkem mají stále neověřené vlastnosti. Aktuální zapojení a firmware patří do [elektroniky](../../elektronika/auticko/README.md), inventář do [vybavení](../../elektronika/vybaveni.md).

## Soubory pro tisk a prohlížení

- [Tiskový balíček ZIP](tiskovy-balicek.zip): každý přiložený STL tisknout jednou; opakované díly mají samostatné očíslované kopie.
- [Parametrický FreeCAD model](auticko-s-prevodovkou.FCStd), [zdrojové makro](auticko-s-prevodovkou.FCMacro), [kontrola geometrie](kontrola-modelu.json).
- [Sestava](sestava.png), [odkrytý pohon](prevodovka.png), [zvednutá plošina](rozlozena-plosina.png), [všechny tiskové díly](tiskove-dily.png). Jde o skutečné CAD náhledy; rozložení dílů je ilustrační, nikoli připravená tisková podložka.

## Co se změnilo

Dvě čelní evolventní soukolí **18:54 a 18:72** dávají celkem **12:1**, modul 0,9 mm, úhel 20°. Původní model měl 18:54, tedy 3:1. Při stejných otáčkách motoru je nová zadní osa ideálně čtyřikrát pomalejší s čtyřikrát větším momentem před ztrátami. Protože se průměr kol zvětšil ze 60 na 80 mm, ideální obvodová rychlost vozítka klesne na třetinu a tažná síla vzroste třikrát. Skutečnou rychlost, sílu ani nosnost bez motorových údajů a fyzické zkoušky nezaručujeme; další soukolí přidává tření.

Větší kola dávají 72zubému kolu nominální světlost 6,7 mm. Tištěné osy mají Ø8 mm, souvislou D plochu a tisknou se naležato pro lepší orientaci vrstev vůči ohybu. Pojistkové drážky mají kořen Ø6,8 mm a za drážkou je 1,5 mm materiálu. Kola jsou bez pneumatik; přilnavost materiálu k povrchu nebyla změřena. Vozítko nemá řízení ani diferenciál. **Dva vnější záběry obracejí směr vůči původnímu jednostupňovému převodu:** zadní osa nyní běží stejným směrem jako motor. Při první zkoušce s koly ve vzduchu ověř směr; případnou záměnu dvou vodičů motoru dělej pouze s vypnutým napájením. Tento CAD úkol firmware nemění.

| Rozměr | Návrh |
|---|---:|
| Rám | 180 × 44 × 4 mm |
| Kola | Ø80 × 8 mm |
| Rozvor | 118 mm |
| Kola přes vnější boky | 96 mm |
| Osa zadní / meziosa / motor / přední (X) | 32 / 72,7 / 105,3 / 150 mm |
| Osy nad spodní stranou rámu (Z) | 24 mm |
| Osové vzdálenosti 1. / 2. stupně | 32,6 / 40,7 mm |
| Plošina vně | 180 × 70 × 4 mm |
| Rovná užitná plocha | **170 × 60 mm**, X5..175, Y−30..30 |
| Spodek / vršek plošiny | Z70 / 74 mm |
| Kola → spodek plošiny | 6 mm |

Motorové tělo **Ø22,5 × 26 mm** a přední hřídel délky **6 mm** pocházejí z ručního měření uživatele s neznámou přesností. Otvor pastorku **2,2 mm**, délka **5,5 mm**, vycházejí z uživatelem potvrzeného nasazení původního pastorku. Není to změřený průměr hřídele ani ověřený přenos momentu. Kulatý otvor je pracovní předpoklad. Motorová reference neobsahuje nezměřené kontakty; zadní čelo Y3 a prostor za ním jsou otevřené. Žádná konkrétní kolébka pro baterie, powerbanku či Arduino není vymyšlená: vybavení se připevňuje na obecnou rovnou plochu.

## Kolik čeho tisknout

| STL | Počet | Orientace |
|---|---:|---|
| [rám](stl/ram.stl) | 1 | základnou dolů |
| [plošina](stl/plosina-170x60.stl) | 1 | rovnou horní plochou dolů, sloupky nahoru |
| [zadní kolo 72z](stl/kolo-zadni-72z.stl) | 1 | vnější plochou kola dolů, ozubením nahoru |
| [zadní pravé kolo](stl/kolo-zadni-prave.stl) | 1 | plochou dolů |
| [přední kolo](stl/kolo-predni.stl) | 2 | plochou dolů |
| [pastorek 18z, otvor 2,2](stl/pastorek-18z-otvor-2_2.stl) | 1 | čelem dolů |
| [mezikolo 54/18z](stl/mezikolo-54_18z.stl) | 1 | velkým kolem dolů |
| [hlavní osa 101,3](stl/osa-hlavni-101_3.stl) | 2 | naležato souvislou D plochou dolů |
| [meziosa 65,2](stl/osa-mezi-65_2.stl) | 1 | naležato souvislou D plochou dolů |
| [rozpěrka 8,6](stl/rozperka-8_6.stl) | 1 | plochou dolů |
| [rozpěrka 17,6](stl/rozperka-17_6.stl) | 3 | plochou dolů |
| [rozpěrka 1,6](stl/rozperka-1_6.stl) | 2 | plochou dolů |
| [C pojistka](stl/pojistka-c.stl) | 3 | plochou dolů |

Celkem **20 tištěných dílů, 13 různých STL**. ZIP už obsahuje počty; po importu jeho souborů znovu nenásobit počty z tabulky. Tisk měřítkem 100 %, jednotky mm. Plošina a rám jsou samostatné díly; netiskne se prostorově sestavený FCStd jako jeden kus.

Všechny STL už jsou v uvedené orientaci na Z0. Pro PLA a 0,4mm trysku je rozumný neověřený začátek 0,16–0,20 mm vrstva; ozubení a osy potřebují dostatek obvodů, např. 4–5. Skutečný profil tiskárny, průtok, smrštění a teploty nejsou tímto modelem ověřené. Při náhledu vrstev zkontrolovat zejména vodorovné otvory uložení Ø8,6, tenké pojistky, spodní hranu zubů a mezery v drážkách. Otvory ložisek obsahují krátké přemostění; plošina se tiskne obrácená a kapsy otevřené nahoru. Zuby nejsou zavěšené nad prázdnem: zadní věnec podpírá široký ráfek a malé mezikolo podpírá disk. Neslibujeme tisk bez potřebné korekce profilu. Pojistky/uložení a otvor pastorku je vhodné ověřit před dlouhým tiskem rámu/plošiny.

## Montáž

Souřadnice: X směrem od zadní k přední nápravě, Y napříč, Z nahoru. Ozubení je na levé straně Y záporné. Pracovat s odpojeným motorovým napájením.

1. Odstranit otřepy a ověřit, že každá osa projde oběma uloženími rámu bez nucení a že se kola/převod mohou volně otáčet. Nenatlačovat nepřesnou D díru násilím; skutečná tisková vůle je neověřená. Přední kola mají kruhový otvor, zadní D otvor.
2. **Zadní osa:** na osu od volného konce navléknout ozubené kolo tak, aby rovná vnější strana ležela u příruby a ozubení mířilo dovnitř. Přidat rozpěrku 8,6. Prostrčit zleva oběma zadními bloky rámu; na pravé straně doplnit rozpěrku 17,6, pravé D kolo a C pojistku do drážky.
3. **Přední osa:** přední volné kolo, rozpěrka 17,6, oba přední bloky, rozpěrka 17,6, druhé volné kolo a pojistka. Přední kola se otáčejí samostatně na D ose; plochá část osy je kvůli tisku, ne k záběru těchto kol.
4. **Meziosa:** od příruby malé 18zubé kolo, směrem k rámu velké 54zubé kolo. Obě jsou jedním tištěným dílem. Navléknout mezikolo a rozpěrku 1,6, prostrčit oběma prostředními bloky, napravo doplnit druhou rozpěrku 1,6 a pojistku. Souvislé D plochy umožňují nasunutí přes celou volnou délku osy.
5. Při zasouvání otáčet koly, aby zuby zapadly do mezer. Zadní pravé kolo a D osa mají stejnou orientaci D plochy jako zadní levé. Pojistka musí skutečně zapadnout do drážky a nesmí axiálně sevřít rotující díly. Zkontrolovat volné otáčení celé převodovky ještě **bez motoru**.
6. Opatrně nasadit pastorek na motorovou hřídel; v CAD je 0,5 mm mezera mezi pastorkem a čelem motoru. Nepřenášet sílu přes ložiska motoru a nepovažovat dosavadní nasazení za zaručené pevné uložení. Motor vložit do dvou sedel, natočený kontakty k otevřenému pravému konci, a připevnit **dvěma vhodnými stahovacími páskami** skrz svislé otvory 3 × 3,2 mm. Pásky jsou potřebný netištěný materiál, jejich konkrétní vlastnictví/rozměr zde netvrdíme.
7. Plošinu nasadit čtyřmi kapsami na horní části předních a zadních bloků. Kapsy mají návrhově 0,3 mm vůli na každé straně a hloubku 2 mm. Samotné kapsy nezajišťují proti nadzvednutí. Pro jízdu ji stáhnout **dvěma vhodně dlouhými páskami** přes boční otvory u X125 a X165 a kolem rámu, mimo kola a soukolí. Potřebný průřez musí projít 3mm šířkou otvoru; délku zvolit podle skutečné trasy a nákladu. Na této trase nesmí být sevřené kabely ani kontakty. Pro sejmutí se pásky uvolní/odstraní; není to pevně zajištěný beznástrojový zámek.
8. Vybavení upevnit samostatně na plošinu, kabely vést mimo zuby a kola, ponechat přístup ke kontaktům motoru. Nejprve ověřit lehkost pohybu a jištění bez napájení, potom řízenou zkoušku s koly ve vzduchu a až následně s lehkým nákladem na zemi. Tato posloupnost je doporučení, nikoli provedený test.

### Montážní stohy a vůle

Hlavní osy začínají Y−50, příruba končí−48, levé kolo leží−48..−40 a pravé40..48. Pravá drážka je48,3..49,8, pojistka48,4..49,7, konec osy51,3. Vzdálenost příruba–vnitřní čelo pojistky je96,4 mm; součet tlouštěk kol, rozpěrek a šířky rámu mezi vnějšími dosedy je95,2 mm. **Celková axiální rezerva hlavního stohu je1,2 mm** (0,4 mezi vnějšími čely kol a dorazy plus0,8 ve vnitřních mezerách). Samotná pojistka má v drážce dalších0,2 mm vůli. Rozpěrky nejsou předepnuté a tření čel může být po tisku jiné.

Meziosa začíná−38,4, příruba končí−36,4. Mezikolo zabírá−36..−24, rozpěrka−23,8..−22,2, rám má vnější dosedy−22 a22, pravá rozpěrka22,2..23,8, pojistka23,9..25,2. Drážka je23,8..25,3 a konec26,8. Mezi dorazy je60,3 mm proti součtu dílů59,2 mm: **celková axiální rezerva meziosového stohu je1,1 mm**, plus0,2 mm vůle pojistky v drážce. Mezi mezikolem a motorovým čelem je nominálně **1 mm**, po využití návrhových axiálních mezer se může zmenšit; tisk ani pružnost se v CAD nesimulují. Malé18z mezikolo navazuje přímo na velké, bez mezery: velké zabíráY−29..−24 a malé−36..−29. Podpěrný disk končíY−29, tedy2 mm od zadního ozubení, aby zůstala rezerva i při součtu axiálních posunů. Mezikolo se nesmí dotýkat motoru. Příruba meziosy míjí levé kolo o nominálně1,6 mm vY.

Uložení Ø8,6 proti oseØ8 dává radiálně0,3 mm. D díry Ø8,3 mají radiálně0,15 mm a plocha3,0 proti2,8 mm dává0,2 mm vůli. To jsou návrhové hodnoty, ne potvrzené vůle po vytištění. Pružnost C pojistek, pevnost os, tření a nosnost plošiny se musí teprve ověřit.

## Parametry a regenerace

Ve FCStd jsou běžné rozměry v tabulce `Parameters`, sloupecB. Model tvoří standardní `Part::Box`, `Part::Cylinder`, booleany, `Part::Extrusion` a `App::Link`; nepotřebuje vlastní Python proxy třídu. Změna průměru kol posune plošinu podle její výškové vazby. Změna osové vůle přepočte polohu meziosy a motoru. Geometrická editovatelnost sama nepotvrzuje sestavitelnost libovolné kombinace.

**Počet zubů, modul a úhel ozubení se mění v konstantách zdrojového makra a vyžadují regeneraci**, obrysy nejsou živý parametrický generátor. Ověřená varianta je pouze12:1. Změna převodu může vyžadovat další změnu otvorů rámu, průměrů prstenců, podepření zubů a vůlí; makro při kolizích končí chybou. Není dovoleno změnit pouze číslo v tabulce a označit obrys za nové ozubení. Také delší osy, tloušťky kol, jejich Y polohy a rozpěrky tvoří jeden montážní stoh: upravit jej společně a znovu zkontrolovat.

Makro zapisuje výhradně vedle sebe a přepisuje místní model, STL, kontrolníJSON a ZIP; náhledy generuje následné [GUI makro](nahled.FCMacro). Neuložené ruční změny před regenerací zálohovat. Spustit přes skutečný FreeCAD1.1.3 popsaný v [software](../../docs/software.md), nikoli běžný Python. Konkrétní izolovaný běh:

```bash
/home/novakj/.cache/freecad-shelf-1.1.3/runtime/AppRun freecadcmd -u /home/novakj/3d-print/models/auticko-s-prevodovkou/.runtime/user.cfg -s /home/novakj/3d-print/models/auticko-s-prevodovkou/.runtime/system.cfg /home/novakj/3d-print/models/auticko-s-prevodovkou/auticko-s-prevodovkou.FCMacro
```

Následné GUI makro použije tutéž cestu s `nahled.FCMacro` bez `freecadcmd`, ideálně v odděleném `xvfb-run` s `LIBGL_ALWAYS_SOFTWARE=1`. Výsledný model se ukládá s viditelnou sestavou; zdroje tiskových dílů a konstrukční tvary jsou skryté.

## Ověření a otevřené body

**Dokončené kontroly 2026-09-19:** všech13 finálních dílů je platný jediný solid a všech13 STL je uzavřená orientovaná manifold síť s jednou souvislou komponentou. ZIP obsahuje20 správných kopií.210 statických dvojic i25 pohybových poloh obou převodů mají nulový objemový průnik; prošly také popsané axiální meze a změna/vrácení tří parametrů. Uložený FCStd se znovu otevřel se správnou viditelností21 objektů sestavy včetně netisknutelné reference motoru. Všechny čtyři skutečné CAD náhledy byly otevřeny a vizuálně zkontrolovány. Původní kontrolované CAD soubory zůstaly shodné hashem.

Přesné výsledky běhu jsou v [kontrola-modelu.json](kontrola-modelu.json). Kontrolujeme každý konečný díl jako jeden platný solid, uzavřenost exportů, všechna statická tělesa sestavy,25 vzorků společného otočení obou soukolí přes jednu rozteč velkého kola a válcové obálky rotujících kol/ozubení proti rámu, plošině a tělu motoru. Doplněná kontrola krajních axiálních posunů používá zadní kolo−1,0/+0,5mm a mezikolo−0,9/+0,5mm; rozšířený test se opakuje po otevření uloženého FCStd. Parametrická zkouška mění a vrací průměr kola80→82, motoru22,5→23 a osovou přirážku0,2→0,3 mm. Následně se model ukládá, otevírá a ověřuje jeho viditelnost. Původní CAD/STL/PNG/makra jsou porovnána hashem.

Nezávislá kontrola skutečných binárních STL a hashů je v [overeni-exportu.json](overeni-exportu.json), reprodukovatelná přes [ověřovací skript](overit-exporty.py). Vedle nulových kolizí má každý pár hlavových kružnic překrytí1,6 mm a ideální příčný součinitel záběru přibližně1,434 / 1,455 při zvětšené osové vzdálenosti. To analyticky potvrzuje překrývající se záběr ideálních evolvent, nikoli funkci vytištěných zubů.

Důkaz nulového objemového průniku nenahrazuje správné vůle skutečného výtisku. Zvětšení každé osové vzdálenosti o0,2 mm poskytuje návrhovou zubovou vůli, nikoli kalibrovaný backlash. Žádné měření únosnosti, účinnosti, tření, deformace, životnosti, proudu či zahřívání motoru, přilnavosti kol ani maximálního zatížení nebylo provedeno. Plošina není univerzální potvrzení kompatibility elektroniky. G-code nebyl vytvořen, tiskárna nebyla ovládána a nový model nebyl fyzicky vyzkoušen.
