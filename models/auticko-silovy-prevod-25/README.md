# Revidovaná V3: převod 25:1 a přední řízení SG90

**Tiskový prototyp po revizi fitů z 20. 9. 2026: celé autíčko, 34 typů a 66 fyzických dílů na třech podložkách.** Zachovává původní ozubení 20° / modul 1 a nominální rozteče. Otvory jsou upravené podle kalibrace a funkce spoje. Na výslovné zadání se předává celá sada bez dalších povinných zkušebních výtisků.

**Fyzický stav 20. 9. 2026:** obě první várky jsou dokončené a částečně vadné. Pro další tisk je hotová [kombinovaná03 — jedna podložka,26 kusů](rozlozeni/kombinovana-03-2026-09-20/README.md):13 dosud netištěných +7 náhrad první várky +6 druhé. Všech26 je skutečně naslicováno, čepy a osa nastojato, obě těhlice i plošina s připravenými podporami. Nahrazuje samostatnou původní03 a všechny tři podložky sedmidílného dotisku; jejich kopie nepřidávat. **Rám, víko objímky páčky a úplnost obou motorových klínků zůstávají otevřené.** CAD/STL/ZIP a rozměry sestavy jsou zachované; počítačová kontrola není fyzická montáž.

Nominální CAD a exporty jsou ověřené; fyzický výsledek se posuzuje samostatně. **Scénář, ve kterém se celá nominální CAD vůle projeví jako skutečná radiální vůle, neprošel a zůstává označený `false`.** Není podmínkou tohoto autorizovaného prototypu. Chod, fit, nosnost a životnost celého nového výtisku zatím nejsou potvrzené. [Přesný rozsah kontroly](#co-je-ověřené) a [historie revize](revize-fitu-2026-09-20.md).

## Soubory k tisku a prohlížení

**Aktuální připravený tisk:** [nastavený projekt26 kusů](rozlozeni/kombinovana-03-2026-09-20/auticko-25-kombinovana-03-nastaveny-projekt.3mf), [číslovaný náhled](rozlozeni/kombinovana-03-2026-09-20/podlozka.png), [návod a ověření](rozlozeni/kombinovana-03-2026-09-20/README.md). Otevřít jako celý projekt, měřítko100 %, nic nekopírovat ani automaticky nerozmísťovat.

Úplný původní kusovník zůstává66 kusů ve skupinách26 /27 /13. Původní01 a02 jsou zachované záznamy již tištěných várek, ne pokyn k jejich opakování. Oba soubory jsou nyní uložené jako Next projekty s vypnutými podporami;01 má dřívější zachovaný hash,02 byla později přebalená s profilem0,20mm. Geometrie02 stále odpovídá původnímu manifestu27 kusů; konkrétní tištěný G-code tím není prokázán. [Přehled variant a zachování](rozlozeni/README.md).

- [Editovatelná sestava FreeCAD](auticko-silovy-prevod-25.FCStd).
- [Alternativa: kompletní ZIP s 66 jednotlivými STL kopiemi](tiskovy-balicek.zip). Každý soubor jednou; neimportovat současně sadu 3MF a ZIP.
- CAD náhledy: [rovně](rovne.png), [doleva](doleva.png), [doprava](doprava.png), [mechanismus](mechanismus.png), [rozložená sestava](rozlozena-sestava.png). Barvy rozlišují díly, nikoli filament.
- [Montážní návod](montaz.md), [rozměry a architektura](architektura.md), [strojový stav revize](stav-revize.json).
- Zdroj: [hlavní makro](auticko-silovy-prevod-25.FCMacro), [geometrie řízení](rizeni-geometrie.py), [uchycení serva](servo-uchyceni.py), [sestavení řízení](rizeni-sestava.py). Pro regeneraci ponechat všechny čtyři soubory vedle sebe. Uložený FCStd používá standardní editovatelné objekty a tabulky.

Vše se předává přímo v tomto projektu. Starší kopie na ploše se neaktualizují a nejsou touto revizí. [Předchozí dokončená varianta je archivovaná](historie/pred-kalibraci-8_6-12_6-2026-09-20/README.md). Nové mechanické díly nemíchat s původními V2/V3; použije se stávající motor, SG90, originální jednoramenná páčka a její středový šroubek.

## Rozměry spojů této revize

| Funkce | Návrhový rozměr v mm |
|---|---|
| Mezikola otočná na Ø8 čepech | Ø8,6 ve dvou 5mm vodicích pásmech; 20mm střed Ø9 |
| Pevné Ø8 čepy v rámu | Sedlo Ø8,1 |
| Zadní Ø12 osa otočná v rámu | Otvor Ø12,6 |
| Výstupní ozubené kolo na zadní ose | Samostatný otvor Ø12,1; moment přenáší příčný klíček |
| Zadní kola na D koncích osy | Kruhová část Ø12,1; ploška 4,05 od osy proti plošce osy 4,00 |
| Statické Ø4 zajišťovací čepy a klíček | Otvory Ø4,1 |
| Sedla plošiny | Ø8,1 |
| Přední otočné Ø8 spoje | Ø8,6, beze změny |
| Otočné Ø6 klouby táhel | Ø6,5, beze změny |
| Motorový pastorek | Otvor Ø2,2, beze změny |

Průměry nosných čepů a os se nezmenšovaly. Jiří na dřívějším vzorku potvrdil otáčení Ø8 čepu v otvoru 8,6 a vyhovující nasazení Ø12 do 12,6. Nejde o měření skutečné vůle celého nového auta. Nejmenší pevné otvory 8,1 / 12,1 / 4,1 jsou návrhová volba podle zadání; jejich fit nebyl fyzicky potvrzen. Při montáži je nesestavovat násilím.

## Co konstrukce obsahuje

Tři stupně **18→54, 18→60 a 22→55 dávají 25:1**. Původní modul 1 mm, úhel 20° a rozteče 36,4 / 39,4 / 38,9 mm zůstávají. Výstupní 8mm pastorek je vystředěný v 12mm věnci; při kontrolovaných axiálních krajních polohách zbývá rezerva 1,5 mm. Proti převodu 12:1 je ideální moment 2,083× při 48 % otáček, před ztrátami.

Mezikola běží na pevných oboustranně podepřených čepech se dvěma krátkými vodicími pásmy. Zadní osa má kruhové pracovní části a D konce pro kola. Pojistky drží polohu, nemají stahovat otočná čela. Všechna čtyři kola mají Ø76 × 12 mm a skutečný dezén; užitná plocha plošiny je 170 × 60 mm.

Řízení používá SG90 a originální páčku s uživatelem změřeným účinným poloměrem 15 mm. Ostatní rozměry konkrétní páčky a těla serva nejsou fyzicky ověřené. Nové mechanické spojovací díly jsou tištěné; návrh nevyžaduje nové M2 šrouby, ložiska ani osy. Elektrika serva zůstává samostatnou etapou.

## Dřívější uživatelský záměr ve sliceru

Aktuální kombinovaný projekt má ověřenou vrstvu0,12mm; následující odstavec zachycuje starší hlášení, nikoli jeho nastavení. Jiří dříve uvedl, že změnil běžnou výšku vrstvy z **0,20 na 0,08 mm** a horní povrch chce ponechat na standardním **Monotonic line**. Jde o jeho hlášení nastavení, nikoli o námi přečtené živé UI, osobní preset nebo hotový G-code. Potvrzení spuštění či dokončení tisku nové revize z něj neplyne.

Pokud toto nastavení ponechá, mechanické díly mají použít stejnou 0,08mm vrstvu a stejné ostatní nastavení. **První vrstva se tím automaticky nemění.** V místním systémovém profilu Kobra X 0,4 byl ověřen rozsah **0,08–0,28 mm**; Standard uvádí běžnou i první vrstvu **0,20 mm** a horní vzor `monotonicline`. Dokládá to [read-only záznam profilu](rozlozeni/profil-podlozky.json), nikoli kontrola neuloženého okna sliceru. Geometry-only 3MF obsahují pouze geometrii a rozmístění: výšku vrstvy, vzor povrchu, průtok, teploty ani osobní presety nepřepisují.

Nižší vrstva může zjemnit odstupňování oblých ploch ve směru Z; sama neopravuje XY průměry otvorů, tvar zubů, nesouosost ani neprokazuje nižší tření. Přepnutí mezi Rectilinear, Monotonic line a Archimedean chords není doložená oprava mechaniky; změna vzoru není součástí tohoto návrhu.

## Tiskové orientace a podpory

STL zachovávají původní exportní souřadnice; aktuální tiskové orientace třetí podložky a opravné sady určují jejich generátory a 3MF. Automatické otočení v nástroji Arrange může změnit povrchy, které se opírají o podpory; samotná kalibrace jiné orientace pak nemusí platit.

| Skupina | Orientace a co zkontrolovat ve skutečných vrstvách |
|---|---|
| Kola, výstupní kolo, motorový pastorek | Plochým čelem na podložku; u dezénu zkontrolovat drobné převisy a skutečné vyplnění špiček zubů |
| Dvojkola A/B | Velké ozubené čelo leží na podložce. Vyvýšené malé ozubení má spodní převisy: může potřebovat lokální podpory **na těle modelu**, pouze podpory z podložky nemusejí stačit |
| Kruhové čepy a zadní osa | Původní01/02 zůstávají historicky naležato. **Aktuální03 a opravy** mají čepy na hlavách a zadní osu svisle s lokálními podporami. Není to obecná záruka větší pevnosti; u 150,6mm osy zkontrolovat stabilitu, příčný otvor a pojistné drážky |
| Těhlice, čelisti a držáky | Původní export vyžaduje kontrolu osiček, ramen, kapes a vodorovných otvorů. **Pravá těhlice v dotisku** je nově otočená na oko/rameno, stále s podporami včetně podpor na modelu. Levá těhlice byla na nových fotografiích také vadná; obě jsou v kombinované26 otočené a se skutečnými podporami |
| Plošina | Horní plochou na podložku, nohy nahoru; u dvou zadních nohou je 2mm boční převis, který vyžaduje kontrolu lokální podpory. Zkontrolovat také příčné otvory v nohách |
| Rám | Dnem na podložku; zkontrolovat vodorovné otvory a místní převisy kolem vidlic, motoru a serva |
| Pojistky, táhla, podložky, objímka páčky | Zachovat export; zejména drážky víka objímky, malé pojistky a jejich oddělení od podpor vyžadují prohlídku vrstev |

Rozmístění samotných modelů ani jejich rezervy pro brim nedokazují prostor pro libovolné podpory. Před tiskem je potřeba prohlédnout skutečně vygenerované dráhy, případně zvětšit mezery. Nové nastavené projekty03 a opravné sady podpory obsahují a prošly kontrolou skutečných drah; geometry-only alternativy proces nemají. Projekty neobsahují G-code a místní řezání nepotvrzuje fyzický výsledek.

## Kusovník

<!-- BOM-BEGIN -->
**Kusovník: 34 různých typů, celkem 66 fyzických kusů.** Počty jsou odvozené ze skutečných montážních instancí uložené sestavy. Kompletní ZIP obsahuje každou kopii zvlášť; tabulka není pokyn k dalšímu násobení součástí ve sliceru.

| Typ STL | Počet | Místo v sestavě |
|---|---:|---|
| [mezikolo-a-54_18](stl/mezikolo-a-54_18.stl) |1 |U motoru; velké 54 a malé 18 zubů |
| [mezikolo-b-60_22](stl/mezikolo-b-60_22.stl) |1 |U zadní osy; velké 60 a malé 22 zubů |
| [vystupni-kolo-55](stl/vystupni-kolo-55.stl) |1 |Na zadní ose, zajištěné příčným klínkem |
| [pastorek-18-otvor-2_2](stl/pastorek-18-otvor-2_2.stl) |1 |Nový pastorek motoru; fit 2,2 znovu ověřit |
| [ram-25](stl/ram-25.stl) |1 |Společný rám s uložením pohonu i řízení |
| [pevny-cep-8x53_9](stl/pevny-cep-8x53_9.stl) |2 |Po jednom do každého mezikola |
| [pojistka-6_9](stl/pojistka-6_9.stl) |7 |2 pevné čepy +2 svislé čepy +2 přední kola +1 kloub páčky |
| [pricny-klinek-4x27_1](stl/pricny-klinek-4x27_1.stl) |1 |Spoj výstupního kola a zadní osy |
| [pojistka-3_1](stl/pojistka-3_1.stl) |10 |1 klínek osy +2 motor +4 plošina +2 servo +1 objímka páčky |
| [spolecny-cep-mustku-4x30_5](stl/spolecny-cep-mustku-4x30_5.stl) |2 |Dva dlouhé čepy pro oba motorové můstky |
| [cep-plosiny-4x19_5](stl/cep-plosiny-4x19_5.stl) |4 |Po jednom do každé nohy plošiny |
| [pojistka-osy-10_9](stl/pojistka-osy-10_9.stl) |4 |2 vnitřní zajištění zadní osy +2 zadní kola |
| [osa-zadni-12x150_6](stl/osa-zadni-12x150_6.stl) |1 |Kruhové pracovní plochy, D konce pro zadní kola |
| [rozperka-zadni-17_6](stl/rozperka-zadni-17_6.stl) |2 |Jedna na každé straně zadní osy |
| [kolo-76x12-zadni-d](stl/kolo-76x12-zadni-d.stl) |2 |Dvě poháněná zadní kola s D otvorem |
| [kolo-76x12-predni](stl/kolo-76x12-predni.stl) |2 |Dvě volně otočná přední kola |
| [motorovy-mustek](stl/motorovy-mustek.stl) |2 |Dva horní motorové třmeny |
| [motorovy-klinek](stl/motorovy-klinek.stl) |2 |Po jednom přítlačném klínku do každého můstku |
| [plosina-170x60](stl/plosina-170x60.stl) |1 |Plošina s užitnou plochou 170 × 60 |
| [servo-viko](stl/servo-viko.stl) |1 |Zachycení původních uší SG90 |
| [servo-cep-4x51_2](stl/servo-cep-4x51_2.stl) |2 |Dva čepy víka serva |
| [objimka-packy-spodek](stl/objimka-packy-spodek.stl) |1 |Spodní tvarové zachycení originální páčky |
| [objimka-packy-viko](stl/objimka-packy-viko.stl) |1 |Zasouvací víko s vlastním otočným čepem |
| [objimka-cep-4x25_5](stl/objimka-cep-4x25_5.stl) |1 |Zajištění spodku a víka objímky |
| [podlozka-packy-1_8](stl/podlozka-packy-1_8.stl) |1 |Distanční podložka pod oko servotáhla |
| [celist-horni](stl/celist-horni.stl) |2 |Jedna horní vidlice na každé straně řízení |
| [svisly-cep-8](stl/svisly-cep-8.stl) |2 |Dva svislé čepy řízení |
| [tehlice-leva](stl/tehlice-leva.stl) |1 |Levá otočná těhlice s osičkou předního kola |
| [tehlice-prava](stl/tehlice-prava.stl) |1 |Pravá otočná těhlice s osičkou předního kola |
| [spojovaci-tahlo](stl/spojovaci-tahlo.stl) |1 |Propojení obou ramen řízení, odsazení dopředu |
| [servo-tahlo-r15](stl/servo-tahlo-r15.stl) |1 |Propojení originální páčky s levým ramenem |
| [cep-tahla-dlouhy](stl/cep-tahla-dlouhy.stl) |1 |Levý kloub s oběma táhly |
| [cep-tahla-kratky](stl/cep-tahla-kratky.stl) |1 |Pravý kloub spojovacího táhla |
| [pojistka-kloubu-4_9](stl/pojistka-kloubu-4_9.stl) |2 |Po jedné pod každý kloub táhla |

**Přesně čtyři kola:** dvě přední a dvě zadní. Mezi opakované díly patří také všechny rozpěrky, podložky, čepy a pojistky. Původní motor, servo, jeho jednoramenná páčka a středový šroubek jsou referenční vlastněné součásti, netisknou se a nejsou v 66 kusech.
<!-- BOM-END -->

## Montáž a elektronika

[Montážní návod](montaz.md) rozlišuje zadní rozpěrky, klínek, zajištění motoru a řízení. **Mezikolo B → motor, můstky a jejich oba dlouhé čepy → mezikolo A.** Po nasazení A už levý motorový čep nelze přímo zasunout.

Po očištění výtisků zkus jednotlivá uložení a pak postupně celé otáčky převodů. Při tvrdém místě se vrať k poslednímu přidanému dílu; nepřemáhej převod motorem. Doplňkové [kalibrační vzorky](kalibrace/README.md), [Ø4 V2](kalibrace-4-v2/README.md) a [ruční zkouška převodu](zkouska-prevodu/README.md) jsou zachované jako volitelné podklady, nikoli povinná podmínka tisku této sady.

Aktuální zapojení a fyzické zkoušky ovládání jsou v [elektronice autíčka](../../elektronika/auticko/README.md), vybavení v [inventáři](../../elektronika/vybaveni.md). Tato revize firmware ani zapojení nemění. Tři vnější záběry obracejí směr výstupu proti motoru; první elektrickou zkoušku provést s koly nad podložkou. Přepojovat pouze bez napájení.

## Co je ověřené

- [Kontrola aktuální revize](kontrola-revize-fitu.json): nominální sestava bez nepovolených průniků, shoda šesti původních ozubených obrysů s archivem, změněné otvory, relevantní krajní polohy objímky a celá 8mm šířka posledního záběru s rezervou 1,5 mm.
- [Souhrn CAD a parametrů](kontrola-modelu.json) a [GUI](kontrola-gui.json): vazba na zdroj, platná tělesa, uložená a znovu otevřená sestava a nové skutečné náhledy.
- [Nezávislá kontrola zdroje a původu důkazů](nezavisla-kontrola-revize.json): konkrétní aktuální FCStd a zdroje, archiv a explicitní rozsah převzatých kontrol nezměněného ozubení/řízení. Staré kontroly se nevydávají za nový průchod všech kombinací vůlí.
- [Exportní kontrola](overeni-exportu.json): všech 34 uzavřených STL, 66 fyzických kopií, čtyři kola, shoda ZIP/3MF/kusovníku, rozmístění a import/export Anycubic Slicer Next. [Podrobnosti podložek](rozlozeni/README.md).

**Hranice výsledku:** `nominal_cad_validation_pass=true` se vztahuje k nominální geometrii autorizovaného tiskového prototypu. `full_nominal_radial_clearance_scenario_pass=false` zůstává přiznané: kdyby celé nominální rozdíly průměrů tvořily reálnou provozní vůli, původní záběr tento rozsah nepokrývá. Skutečná vůle zatím není změřená. První várka je nyní doložená fotkami s vadami, druhá se tiskne; montáž, souvislý chod pod zatížením, trakce a životnost zůstávají neověřené. Původní celá sada neobsahuje nastavení podpor; samostatný dotisk má vlastní návod a kontrolu skutečných drah.
