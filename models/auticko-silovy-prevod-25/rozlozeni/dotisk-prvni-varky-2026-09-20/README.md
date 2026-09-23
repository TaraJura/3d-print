# Dotisk první várky V3 25:1 — 20. 9. 2026

**Tato sedmidílná sada je samostatná alternativa. Aktuální [kombinovaná26](../kombinovana-03-2026-09-20/README.md) už obsahuje všech těchto7 kusů, zbývajících13 z původní03 a6 nových náhrad druhé várky.** Při použití kombinované26 tyto tři úlohy znovu netisknout. Druhá várka byla dokončena a fotografie doložily vadnou levou těhlici a pět čepů; rám a neúplný inventář se řeší zvlášť.

## Nejjednodušší otevření: nastavené projekty Next

Tyto tři projekty už mají správné orientace, **Kobra X 0,4**, nový pojmenovaný proces dotisku a níže ověřené podpory/brim. Ulož rozpracovaný projekt a otevři **jeden jako celý projekt**, nikoli „Import geometry only“. Nic nepřerovnávej ani nekopíruj. Potom vyber skutečnou cívku, proveď Slice a prohlédni vrstvy. Neobsahují G-code a nic samy netisknou.

| Otevřít jako projekt | Kusů | Již uložené podpory / brim |
|---|---:|---|
| [01 — zadní osa, nastavený projekt](projekty-next/dotisk-25-01-nastaveny-projekt.3mf) | 1 | Osa nastojato, Normal auto / Snug; vnější brim **12 mm** |
| [02 — pravá těhlice, nastavený projekt](projekty-next/dotisk-25-02-nastaveny-projekt.3mf) | 1 | Normal auto / Snug, také na modelu; vnější brim 8 mm |
| [03 — pět čepů, nastavený projekt](projekty-next/dotisk-25-03-nastaveny-projekt.3mf) | 5 | Podpory vypnuté; vnější brim 8 mm |

**Tyto projekty záměrně načítají své tiskové a materiálové nastavení.** Používají systémový Anycubic PLA jako výchozí procesní podklad, nikoli kalibrovaný profil konkrétního Alzamentu. Vlastní uložené presety nebyly měněné; v otevřeném projektu však platí načtené hodnoty. U nezměněných 02/03 se proti ověřenému řezu liší pouze název procesu. Aktualizovaná 01 byla znovu naslicovaná přímo z dodaného projektu; Next pouze rozšířil nulové pole `machine_max_junction_deviation` ze dvou nul na tři. Tisková nastavení a geometrie jsou shodné. [Ověření skutečných projektů](overeni-projektu-next.json).

## Alternativa: pouze geometrie, vlastní nastavení

| Otevřít jednou, do prázdného projektu | Kusů | Potřebné nastavení | Číslovaný náhled |
|---|---:|---|---|
| [01 — zadní osa](dotisk-25-podlozka-01.3mf) | 1 | Osa nastojato, podpory zapnout + vnější brim **12 mm** | [PNG](podlozka-01.png) |
| [02 — pravá těhlice](dotisk-25-podlozka-02.3mf) | 1 | Podpory zapnout, také na modelu + vnější brim 8 mm | [PNG](podlozka-02.png) |
| [03 — pět čepů](dotisk-25-podlozka-03.3mf) | 5 | Podpory vypnout, vnější brim 8 mm | [PNG](podlozka-03.png) |

**Tyto alternativní 3MF obsahují pouze geometrii a rozmístění. Podpory, brim ani tiskový profil v nich nejsou.** Importuj geometrii, zvol **Anycubic Kobra X 0.4 nozzle** a svoji cívku **bílého Alzament PLA Basic**; ručně nastav proces podle další části. Měřítko **100 %**, tisk po vrstvách; Arrange a Auto orient nepoužívat, žádné kopie nepřidávat. Jednotlivé podložky otevírat samostatně. CAD/STL/ZIP i původní 01/02 zůstaly zachované; původní 03 má vlastní novou stojatou revizi. Nepoužívat současně nastavený projekt a jeho geometrickou alternativu — šlo by o duplicitní díly.

## Nastavení před řezáním

Toto je nový doporučený proces, ověřený místním řezáním; nejde o potvrzení nastavení uživatelova otevřeného sliceru. Pro reprodukci výsledných drah použij:

- Vrstva **0,12 mm**, první **0,20 mm**; **4 stěny**, **100 % rectilinear**. Horní povrch ponechat **Monotonic line**.
- **Brim: Outer brim / vnější, u osy 01 12 mm, u 02/03 8 mm; mezera 0,1 mm**. Zvol vnější brim výslovně, nikoli Auto. Brim drží první vrstvu; nenahrazuje podpory.
- Pro podložky 01 a 02: **Enable support zapnout**, **Normal (auto)**, styl **Snug**, práh **45°**. **On build plate only vypnout**, **Ignore small overhangs vypnout**. Rozhraní 3 horní vrstvy, mezera horní/dolní **0,12 mm**, XY odstup **0,35 mm**, rozteč základních podpor **2 mm**. U těhlice jsou podpory potřebné i uvnitř kapsy nad částí dílu.
- Pro podložku 03 podpory **vypnout**, aby se nezaplnily malé pojistné drážky. Jediné zbývající převisy čepů jsou 0,5–0,6mm horní okraje těchto drážek; prohlédni jejich vrstvy.
- První vrstva **20 mm/s**, vnější stěny nejvýše **30 mm/s**, vnitřní **50 mm/s**, malé obvody **20 mm/s** (práh 20 mm), podpory **40 mm/s**, jejich rozhraní **30 mm/s**. Výchozí zrychlení **1000 mm/s²**, vnější stěny/první vrstva **500 mm/s²**. **Výjimka pro vysokou stojatou osu01:** vnější stěny 20, vnitřní 30, malé obvody 15, podpory 30 a rozhraní 20 mm/s; výchozí/vnitřní/cestovní zrychlení 500, vnější 300 mm/s². Úplný seznam změn je v [JSON nastavení](doporucene-nastaveni.json).

Teploty a chlazení ověř pro skutečnou cívku; geometrické 3MF je nepřepisují. Diagnostické řezání použilo místní systémový profil Anycubic PLA pro Kobra X, který ve výsledku uvádí **220 °C první / 205 °C další, podložku 60 °C**. To není kalibrace Alzamentu. Nastavení 0,08 mm bylo dřívějším záměrem uživatele; dohledaný kandidát první úlohy i tento kontrolní dotisk mají 0,12 mm. Při volbě jiné vrstvy znovu prohlédni podpory a drážky.

Po řezu zkontroluj v náhledu **skutečné podpory stojaté osy u konce dolní D plošky a v příčném otvoru; u těhlice pod tělem, ramenem, kapsou a boční osičkou**. U čepů má být pět oddělených hlav s brimem a žádné podpory v drážkách. Srovnání skutečně vypočtených drah: [osa](evidence/drahy-01.png), [těhlice](evidence/drahy-02.png), [čepy](evidence/drahy-03.png). Neodesílat znovu původní G-code s vypnutými podporami.

## Co je zachované a co chybí

Podkladem jsou dvě fotky `20260920_124057.jpg` (na tiskárně) a `20260920_125550.jpg` (odložené díly), porovnané s [původní první podložkou](../podlozka-01.png) a [kompletním kusovníkem](../kusovnik-podlozek.md). Identita zdrojů a všech 26 pozic je uložená v [inventáři](inventar.json).

Na druhé fotografii je **20 fyzických kusů**, z toho **19 bez velké zjevné vady na viditelné straně** a **jedna viditelně vadná pravá těhlice**. Šest dílů první podložky ve vyložené sadě chybí. Fotka původního tisku ukazuje poškozené čepy a volná vlákna; neprokazuje přesné rozměry zbylých dílů.

| Původní č. na desce 1 | Díl do dotisku | Kusů | Důvod |
|---:|---|---:|---|
| 8 | `osa-zadni-12x150_6__01` | 1 | Chybí mezi odloženými díly; původní tisk spodní strany podezřelý |
| 11 | `tehlice-prava__01` | 1 | Viditelně vadné spodní plochy, rameno a boční osička |
| 12 | `svisly-cep-8__02` | 1 | Chybí mezi odloženými díly |
| 13 | `pevny-cep-8x53_9__01` | 1 | Chybí mezi odloženými díly |
| 14 | `servo-cep-4x51_2__01` | 1 | Chybí mezi odloženými díly |
| 17 | `pricny-klinek-4x27_1__01` | 1 | Chybí mezi odloženými díly |
| 19 | `cep-plosiny-4x19_5__04` | 1 | Chybí mezi odloženými díly |

Zachovat: **4 kola, 2 dvojkola, víko serva, jeden motorový můstek, obě táhla, jednu horní čelist, dva motorové klínky a šest C pojistek** (4× malá 3,1; 1× 6,9; 1× kloubová 4,9). Celkem 19 kusů. Před montáží ověř i jejich spodní strany, otvory a drážky; fotografie nepotvrzuje funkční fit.

Původní kusovník má66 dílů: první26 +druhá27 +třetí13. První fotografická bilance byla19 zachovaných +7 k náhradě. Nové snímky obou várek rozšířily výběr oprav o6 z druhé; ty jsou v kombinované26, nikoli v této sedmidílné alternativě. **Rám, víko objímky a oba motorové klínky zůstávají předmětem upřesnění**, proto nelze vykazovat66 prokazatelně použitelných fyzických dílů. [Aktuální inventář](../kombinovana-03-2026-09-20/inventar-druhe-varky.json).

## Zjištění a změny orientace

V původních STL leží osy a kruhové hlavy na úzkém oblouku; větší hlava navíc zvedá dřík nad podložku. Původní těhlice nemá na Z0 skutečnou rovinnou plochu. Takové orientace vyžadují podpory. V lokálním archivu byl nalezen [kandidát G-code první várky](evidence/puvodni-gcode-kandidat.json): všech 26 správně pojmenovaných dílů, **podpory vypnuté**, `support_used=false`, Auto Brim 5 mm. [Původní náhled](evidence/puvodni-plate_1.png). **Není potvrzeno, že právě tento G-code byl spuštěn; archiv neobsahuje zdrojové mesh sítě pro ověření revize.** Chybějící podpory jsou silné vysvětlení viditelných vad, nikoli jediná prokázaná příčina. Fotky nedokazují teplotu, tok, čistotu podložky ani konkrétní příčinu odtržení.

Také samotná lokální původní první 3MF byla již před touto úpravou uložená jako projekt Next s vypnutými podporami a vrstvou 0,12 mm. U ní se podařilo přímo ověřit shodu všech 26 meshů a poloh s kanonickým manifestem; liší se obal a přidaná nastavení. Nebyla dotiskem přepsána. [Evidence této existující změny](overeni-zachovani.json) vysvětluje rozdíl proti historickému hashi původního geometrického exportu; nezaměňuje uložení projektu za potvrzení spuštěného tisku.

- Zadní osa je nově **nastojato, Y −90° vůči STL**, na D čele; výška 150,6 mm. Brim 12 mm a pomalejší rychlosti omezují problémy kotvení, nezaručují tuhost ani pevnost vrstev. **Lokální podpory zůstávají nutné:** 2mm jednostranný převis na konci dolní D plošky v Z 19,3 a příčný otvor Ø4,1 se středem Z 52,3. Podpora otvoru je přístupná z obou konců, po odstranění ověř průchodnost. Automatika vytvořila i tenké podporové prstence u čtyř pojistných drážek; před montáží je vyčisti. Skutečná odstranitelnost a pevnost osy zatím nejsou fyzicky ověřené. [Nové dráhy, kritické vrstvy a technické omezení](../stojate-cepy-2026-09-20/README.md#stojatá-zadní-osa-v-dotisku).
- Pravá těhlice je otočená **Y −90° vůči zdrojovému STL**, horním okem/ramenem na podložku. Skutečný rovinný kontakt je **107,73 mm² místo 0**; výška 32,9 mm. Podpory zůstávají pod ostatním tělem a osičkou i na modelu v kapsách.
- Pět čepů je otočeno **Y −90°**, hlavou dolů. Dříky pak začínají na hlavě a pracovní kruhové plochy nemají podporu po délce. **Nevýhodou jsou vrstvy napříč osou a neověřená odolnost vůči ohybu.** Čep Ø4 × 51,2 mm je nejštíhlejší; brim omezuje odtržení základny, nikoli kývání nahoře. Čepy při nasazování neohýbat násilím.

Rozměry dílů, fit, ozubení, CAD a všechny původní STL zůstávají stejné. Změnil se pouze způsob položení sedmi kopií a návrh tiskového procesu. Podpory odstranit bez poškození pracovních průměrů; ověřit volný chod ručně před motorovým zatížením.

## Co bylo ověřeno

- [Geometrie a počty](overeni-dotisku.json): 7 kopií, 1 / 1 / 5 objektů, všech **19 446 trojúhelníků** shodných se zdrojem po tuhém otočení/posunu, uzavřené sítě, kladné objemy, Z0 a měřítko 1:1. Nejmenší mezera **32,5 mm**, okraj celé opravné sady **78,5 mm**; osa sama má okraj 124 mm. Každý 3MF byl znovu otevřen a porovnán se zdrojem; nezávislý audit souhlasí.
- [Místní řezání](overeni-rezani.json): všechny tři soubory skutečně prošly Anycubic Slicer Next CLI v izolované cache. Ověřeny názvy, počty, indexy trojúhelníků a zachované orientace po importu; odchylka vrcholů pod 0,00002 mm. Dráhy podpor/rozhraní jsou na 01 a 02, na 03 žádné. Brim je ve všech třech. Střednice všech extruzních drah modelu, podpor a brimu leží uvnitř 260 × 260 mm s velkou rezervou. Zdejší kontrola nehodnotí provedení startovacího G-code na zařízení.
- Odhady tohoto pomalého plného procesu: **01 nastojato: 4 h 39 min 44 s / 19,99 g; 02: 1 h 21 min / 6,55 g; 03: 1 h 54 min / 7,77 g**. To jsou odhady sliceru, nikoli skutečné časy nebo spotřeba.
- Slicer zapsal varování `bed_temperature_too_high_than_filament`: profil má podložku 60 °C a materiálovou hranici 54 °C. Na 01/02 také `not_support_traditional_timelapse`. Jsou zachována v reportu; **výsledek není bez varování**. Žádná z těchto hodnot není měřením uživatelova filamentu. Diagnostický G-code se nepředává ke spuštění.

**Fyzický dotisk zatím neproběhl.** Přilnavost, odstranění podpor, skutečná kruhovitost, pevnost čepů a funkčnost montáže se musí ověřit výtiskem. Tiskárna nebyla oslovena a uživatelovy presety se nezměnily.

## Zdroje a opakování

- [Inventář fotek a pozic](inventar.json), [omezený výpis původního kandidáta](evidence/puvodni-gcode-kandidat.json). Neukládají soukromé cloudové konfigurační položky.
- [Generátor 3MF a číslovaných náhledů](vytvorit-dotisk.py): čte kanonické STL/ZIP, zapisuje jen výstupy do této složky. Hlavní FCStd se pro otočení neregeneruje.
- Aktuální stojatou 01 a původní 03 připravuje [společný generátor projektů](../stojate-cepy-2026-09-20/projekty.py), s [aktuální kontrolou](../stojate-cepy-2026-09-20/overeni-projektu.json). Předchozí ležatá 01 je pouze v archivu, nepoužívat jako aktuální.
- [Opakování místního řezání](naslicovat-overeni.py), [kontrola drah a importu](overit-drahy.py), [použité příkazy/profily](evidence/rezani-prikazy.json). Izolované výstupy jsou v ignorované `.cache/dotisk-2026-09-20/`, nejsou doručovanými 3MF ani nastavením uživatelova sliceru.
- Python pro zdejší nástroje: `/home/novakj/.cache/auticko-packing/venv/bin/python`. Pro kontrolu již existujících slice: `python overit-drahy.py /home/novakj/3d-print/.cache/dotisk-2026-09-20`.

Zdroj: aktuální úplný ZIP celé V3 25:1, SHA256 `3e6ea7b537a1b2cb9197cbcf23623bbfbc9b7354323d0415af6e7eac19d7aa6f`. Dotisk není starší 33dílné autíčko ani nová geometrická revize.
