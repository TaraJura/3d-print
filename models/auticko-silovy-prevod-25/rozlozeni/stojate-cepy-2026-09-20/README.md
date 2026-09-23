# Původní podložka 03: čepy nastojato

**Samostatná alternativa. Pro aktuální pokračování použij [kombinovanou26](../kombinovana-03-2026-09-20/README.md), která už zahrnuje všech těchto13 kusů i opravy první a druhé várky. Netisknout obě varianty.** Následující nastavení a odhady patří pouze této samostatné13kusové variantě.

**Pro tisk otevři [nastavený projekt Next — původní 03, 13 kusů](auticko-25-03-stojate-nastaveny-projekt.3mf) jako celý projekt.** Má šest čepů nastojato, plošinu se skutečně připravenými podporami, Kobra X 0,4 mm a proces 0,12 mm. Nic nerozmísťuj ani nekopíruj. Vyber skutečnou cívku, znovu proveď Slice a zkontroluj vrstvy. Projekt neobsahuje G-code a nic sám netiskne.

Alternativa [pouze geometrie](../auticko-25-podlozka-03.3mf) nese stejné díly a polohy, ale **nenese podpory, brim ani proces**. Nekombinuj ji s nastaveným projektem: vznikly by duplicitní díly. [Očíslovaný náhled skutečné geometrie](../podlozka-03.png).

## Stav a počty

- Původní 01: 26 kusů, částečně vadný výtisk; [samostatný dotisk](../dotisk-prvni-varky-2026-09-20/README.md) stále obsahuje 7 náhrad na podložkách **1 / 1 / 5**. Jeho zadní osa je také nově nastojato. Dotisková 03 s pěti čepy není tato původní 03 se třinácti díly.
- Původní 02: **27 kusů, dokončení tisku potvrzeno Jiřím 20. 9. 2026**. Nové fotografie zatím nedodal; kvalita jednotlivých kusů není známá. Fotky první várky se k ní nevztahují. Žádný další díl nepřidáváme do opravné sady.
- Tato původní 03: **13 kusů, tisk zatím nepotvrzený**. Plošina, rozpěrka, šest čepů a pět pojistek. Počty celé sestavy zůstávají **26 / 27 / 13 = 66**.

Číslování je shodné s [úplným kusovníkem](../kusovnik-podlozek.md). Otočené jsou pouze čepy **3, 4, 6, 7, 8, 9**, Y −90° oproti zdrojovému STL. Stojí na hlavách; rozpěrka už byla svisle. Plošina zůstává horní plochou dolů, nohy nahoru. Pojistky leží naplocho. Rozměry ani geometrie žádného dílu se nezměnily.

## Proč byly původně naležato

Hlavní makro mělo společné exportní pravidlo `round_pin → Y +90°`. Ve zdroji není doložený individuální výpočet pevnosti ani optimalizace pro tyto čepy. Tehdejší dokumentace počítala s podporami spodních oblouků, jejich skutečné nastavení a řezání však původní předání nedotáhlo. Místní uložený projekt první podložky měl podpory vypnuté.

Širší hlava při položení zvedala dřík těchto čepů o 1,5–2 mm nad podložku. Nastojato začíná dřík na hlavě. Jiří opakovaně hlásí lepší výsledek této orientace; pro naše díly je nyní výchozí. **Není to obecná záruka vyšší pevnosti v ohybu:** vrstvy jsou napříč osou a vysoké díly mohou kmitat. [Schválená projektová pravidla](../../../../AGENTS.md) požadují posouzení každého dílu a skutečné podpory tam, kde jsou potřebné.

## Skutečně uložené nastavení a kontroly

Proces používá Kobra X 0,4, vrstvu **0,12 mm**, první **0,20 mm**, vnější brim **8 mm / mezera 0,1 mm** a tisk po vrstvách. **Plošina má systémový proces 0,12 mm: 2 stěny, 15 % 3D honeycomb, vnější stěny 60 a vnitřní 150 mm/s.** Stejné hodnoty má dochovaný uložený projekt původní 01; to nepotvrzuje vlastní dřívější proces plošiny, protože původní 03 byla geometry-only. První vrstva je zpomalená na 20 mm/s kvůli přilnavosti.

**Pouze 12 malých dílů má lokálně 4 stěny, 100 % rectilinear a pomalejší rychlosti**: vnější 30, vnitřní 50, malé obvody 20 mm/s. Přenos plné výplně na celou plošinu byl při přípravě odstraněn. Aktuální odhad je **6 h 19 min 15 s / 71,23 g**; nejde o fyzicky naměřený čas či spotřebu.

**Podpory jsou zapnuté pouze pro objekt plošiny; u ostatních 12 dílů jsou objektově vypnuté.** Normal auto / Snug, 45°, podpory také na modelu, malé převisy neignorovat; rozhraní 3 vrstvy, horní/dolní odstup 0,12 mm, XY 0,35 mm. Místní řez skutečně obsahuje oporu spodních převisů do Z 3,92 mm a v příčných otvorech všech čtyř noh Z 65,24–68,84 mm. Podpory jsou přístupné z otevřených stran/konců otvorů; skutečnou snadnost odstranění ověří až výtisk. Po odstranění ověř průchodnost a fit.

Všechny podpory leží v oblasti plošiny do Y 116,75 mm, malé díly začínají od Y 151 mm: **žádné podpory kolem stojatých čepů nebo v jejich drážkách**. Malé přesahy horních okrajů drážek zůstávají bez podpor. Brim je oddělený prostředek přilnavosti.

- [Skutečné dráhy](evidence/puvodni-03-drahy.png) a [vybrané vrstvy](evidence/puvodni-03-vrstvy.png).
- [Kontrola geometrie](overeni-geometrie.json): 13 objektů, všech šest správně vztyčeno, měřítko 1:1, minZ 0, maxZ 72 mm. Nejmenší mezera obálek 23 mm, okraj 25 mm. Žádná změna trojúhelníků, CAD, STL ani ZIP; původní 01/02 nepřepsané.
- [Kontrola skutečného projektu a řezu](overeni-projektu.json): přesný dodaný projekt byl načten a naslicován. Podpory na úrovni objektů zachované, numerická odchylka světových vrcholů pod 0,00002 mm. Veškeré střednice extruzních drah modelu, brimu a podpor uvnitř 260 × 260 mm. Startovací/custom G-code a skutečný chod tiskárny nejsou předmětem této kontroly.
- Jediná normalizace konfigurace při načtení: Next prodlouží nulové pole `machine_max_junction_deviation` ze dvou nul na tři. Tisková, materiálová a objektová nastavení jsou zachovaná.

Projekty **vědomě načítají svůj profil**. Použitý systémový Anycubic PLA má 220 °C první / 205 °C další, podložku 60 °C; není to kalibrace skutečného Alzamentu. Osobní uložené presety se nezměnily. Slicer hlásí `bed_temperature_too_high_than_filament` (60 °C versus profilová hranice 54 °C) a `not_support_traditional_timelapse`. CLI navíc zapisuje `calc_exclude_triangles` pro prázdné vyloučené zóny; oba řezy skončily exit 0 a dráhy jsou uvnitř podložky. Nejde o výsledek bez varování.

## Stojatá zadní osa v dotisku

[Aktualizovaný projekt dotisku 01](../dotisk-prvni-varky-2026-09-20/projekty-next/dotisk-25-01-nastaveny-projekt.3mf) má jedinou osu výšky **150,6 mm**, vnější brim **12 mm**, vnější stěny 20 mm/s, vnitřní 30 mm/s, malé obvody 15 mm/s, výchozí zrychlení 500 mm/s² (vnější 300). Odhad **4 h 39 min 44 s / 19,99 g**. Brim nenahrazuje tuhost vysoké osy; její kmitání ani pevnost vrstev nejsou fyzicky ověřené.

Podpory jsou potřeba pod jednostranným přesahem až 2 mm na konci dolní D plošky u Z 19,3 mm a v příčném otvoru Ø4,1 mm se středem Z 52,3 mm. Řez obsahuje podporu přechodu do Z 19,16 a podporu otvoru v Z 50,60–54,20. Otvor má přístup z obou konců, po vyčištění musí zůstat průchozí. **Automatika vytvořila i tenké podporové prstence u čtyř pojistných drážek** (Z 1,76–2,84 / 45,56–46,37 / 104,00 / 147,80). Před nasazením pojistek drážky vyčisti; snadná odstranitelnost zatím není fyzicky prokázaná.

[Dráhy stojaté osy](evidence/dotisk-01-drahy.png), [kritické vrstvy](evidence/dotisk-01-vrstvy.png). Pravá těhlice a pět čepů na dalších dvou opravných podložkách zůstávají beze změny, včetně jejich ověřených projektů. Opravný kusovník se nezvětšil.

## Reprodukce a ochrana dalších exportů

Použij `/home/novakj/.cache/auticko-packing/venv/bin/python`:

1. `pripravit.py` zde: z kanonického ZIPu znovu vytvoří pouze původní 03, její PNG a aktuální manifest 66 dílů s explicitními 3D transformacemi. Při změně zdrojových hashů vyžaduje nové posouzení. Kanonické01/02, FCStd a ZIP chrání kontrolou hashů.
2. `../dotisk-prvni-varky-2026-09-20/vytvorit-dotisk.py`: vytvoří 1/1/5 oprav, osu i pět čepů nastojato; fyzické tvary nemění.
3. `projekty.py` zde: vytvoří původní 03 a opravenou01 jako skutečné Next projekty a oba přesné soubory naslicuje v ignorované `.cache/stojate-2026-09-20/`.
4. `overit.py` zde: znovu ověří projekty, import, dráhy a vytvoří PNG. [Přesné příkazy](evidence/prikazy.json).

Původní XY-only aktualizátor/packer nesmí přepisovat kanonický manifest. Generátor Core 3MF rozumí `rotation_matrix` + `translation_mm` a dovolí hromadný export pouze do nového adresáře, aby nepoškodil uživatelsky uloženou01. Historické XY-only validátory a náhledy nejsou důkazem této nové orientace. Hlavní FCMacro zachovává souřadnice kanonických STL kvůli návaznosti; přímo u exportu odkazuje na aktuální orientační generátory.

[Předchozí třetí podložka, celý manifest a opravná sada](../../historie/pred-stojatou-orientaci-2026-09-20/README-ARCHIV.md) jsou zachované odděleně. Fyzický tisk nové03 ani stojaté osy není potvrzený. Žádná úloha nebyla odeslaná tiskárně, commit/push nebyl proveden.
