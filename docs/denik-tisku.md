# Deník tisků

Záznamy oddělují hlášení uživatele, kontrolu lokálních souborů, odhady sliceru a fyzická měření. Časy jsou místní pro Europe/Prague, pokud není uvedeno jinak.

## 2026-09-19 — polička na zárubeň, první pokus

**Stav: uživatel zahájil, výsledek nepotvrzen.** Model: [polička 90 × 50 mm](../models/policka-na-zaruben/README.md). Uživatel po půlnoci oznámil zahájení prvního tisku a pro poličku zvolil bílý Alzament PLA Basic.

Fyzická první vrstva ani hotový výtisk nebyly viděny a uživatel zatím neoznámil dokončení. **Lokální logy jednoznačně nepotvrdily, že právě níže popsaný G-code běží na tiskárně.**

### Kontrola lokálních souborů

Podle dokončené read-only kontroly při úvodní práci byl přibližně v **00:07** vytvořen místní G-code pro `policka-90x50.stl`. Nejnovější G-code a autosave se shodovaly v rozměrech a přípravě dílu. Surový G-code ani soukromé cloudové logy sem nebyly kopírovány; následuje přenesený výsledek kontroly.

| Parametr kontrolované přípravy | Hodnota |
|---|---:|
| Rozměry modelu | 90 × 50 × 34 mm |
| Vrstva / počet vrstev | 0,20 mm / 170 |
| Stěny / výplň / podpory | 2 / 15 % / vypnuté |
| Materiál a barva uvedené v přípravě | Bílé PLA |
| Poloha středu | X 130 / Y 130 mm |
| Rotace / spodek | Bez rotace / Z 0 |
| Rozsah tiskových drah X | 85,21–174,79 mm |
| Rozsah tiskových drah Y | 105,21–154,79 mm |
| Přesah mimo podložku | V kontrolované přípravě nezjištěn |
| Odhad času | 41 min 34 s |
| Odhad spotřeby | 14,21 g |
| Start v G-code | Tryska 220 °C / podložka 60 °C |
| Další teplota trysky | 205 °C |
| MVS | 13 mm³/s |

Čas a spotřeba jsou **odhady sliceru**, nikoli naměřená doba či hmotnost. Startovních 220 °C v tomto výstupu se liší od defaultu první vrstvy 215 °C; pro popis tohoto souboru platí zjištěných 220 °C.

### Rychlosti a varování

**Doporučené snížení extruzních rychlostí na nejvýše 100 mm/s v tomto souboru provedeno nebylo.** Profil ponechal vnější stěny 200, vnitřní 300, řídkou výplň 300, plnou výplň 250, horní povrch 200 a první vrstvu 50 mm/s. Průtokový limit rychlosti v G-code omezil; zjištěné přibližné příkazy extruze byly:

| Druh dráhy | Rychlost příkazu v G-code |
|---|---:|
| Vnější stěna | 179,56 mm/s |
| Vnitřní stěna | 166,33 mm/s |
| Řídká výplň | 166,33 mm/s |
| Plná výplň | 199,14 mm/s |
| Horní povrch | 178,88 mm/s |

Tyto hodnoty jsou **G-code feedrate, nikoli měření fyzické tiskárny**. Sport pro tento první nezkalibrovaný test nebyl doporučen; jeho skutečný stav není potvrzený.

Slicer obsahoval varování `bed_temperature_too_high_than_filament` a `not_support_traditional_timelapse`. Podložka 60 °C je současně uvnitř dodavatelského rozsahu Alzament PLA Basic 45–60 °C; samotný text varování nedokládá nebezpečí ani příčinu vady. Fyzický výsledek není znám.

### Co ještě doplnit

- Potvrzení, která úloha skutečně běžela a s jakou cívkou a nastavením.
- Pozorování první vrstvy, dokončení nebo přerušení a případné vady.
- Skutečná doba a spotřeba pouze pokud jsou známé, s uvedením zdroje.
- Naměřené rozměry, uchycení ke konkrétní zárubni, použité šrouby a výsledek funkční zkoušky. Nosnost zatím netvrdit.

## 2026-09-19 — autíčko, první vzorek otvorů pro hřídelku

**Stav: uživatel potvrdil dokončení výtisku, funkční zkouška nevyhověla.** Podle jeho hlášení se hřídelka motoru nevejde ani do největšího otvoru. Jde o uživatelské pozorování, nikoli měření či fotografii zkontrolovanou agentem.

Původní [vzorek v1](../models/jednoduche-auticko/stl/old/vzorek-hridele.stl) má CAD rozměry 36 × 10 × 5,5 mm a otvory Ø 0,9 / 1,0 / 1,1 / 1,2 / 1,3 mm. Nezávislá kontrola vrcholů exportovaného STL potvrdila největší otvor Ø 1,3 mm, průchozí přes celou tloušťku. Výsledek fyzického fitu neurčuje skutečný průměr hřídelky ani příčinu odchylky. Původní ruční údaj 1 mm zůstává nejistý; požadavek na „aspoň dva“ není nové přesné měření.

Skutečný tiskový profil, měřítko importu, materiál/barva, čas, spotřeba a vazba na konkrétní G-code nebyly ověřeny. Naměřené rozměry výtisku nejsou známé.

**Nová příprava:** samostatný [vzorek v2 — zdroj FCStd](../models/jednoduche-auticko/vzorek-hridele-v2.FCStd), na pozdější výslovné přání uživatele snížený na **54 × 48 × 2 mm**, s označenými otvory Ø 1,8 / 2,0 / 2,2 / 2,4 / 2,6 / 2,8 / 3,0 / 3,5 / 4,0 mm. Je určený pouze k rychlé zkoušce vstupu hřídelky; průchod 2mm vzorkem neověřuje fit v otvoru pastorku dlouhém 5,5 mm. Doporučený postup je měřítko 100 %, zkouška od největšího otvoru k menším a zápis těsného fitu i případné vůle. Původní pastorek, model autíčka a vzorek v1 zůstaly beze změny. Při pozdějším ukládání souhrnu už exportované STL v2 v checkoutu nebylo; zdroj FCStd a makro jsou zachované, viz [aktuální stav souborů](../models/jednoduche-auticko/README.md).

**Pozdější hlášení uživatele:** „poslal jsem to tam na tisknutí“. Není doloženo, který soubor nebo verzi odeslal; hlášení proto nepřiřazujeme k v2 ani k jeho aktuální 2mm variantě. Dokončení a fyzický výsledek tohoto dalšího tisku zatím nejsou potvrzené. Agent úlohu neodesílal a tiskárnu neovládal.

## 2026-09-19 — autíčko, zkouška většího otvoru a úprava pastorku

**Stav: uživatel potvrdil nasazení hřídelky do otvoru označeného 2,2 mm.** Výsledek pochází z jeho hlášení, nikoli z měření agentem. Potvrzuje dokončený zkušební kus a možnost nasazení do tohoto otvoru; přesná výška vytištěné verze, skutečný průměr otvoru, vůle a přenos momentu nejsou potvrzené. Hodnota 2,2 mm je značení nominálního CAD otvoru, nikoli nové měření hřídele.

Na výslovný požadavek uživatele se otvor pastorku změnil z návrhových 1,1 mm na **2,2 mm** ve zdrojovém makru, parametrické sestavě a STL. Délka otvoru je 5,5 mm. Netisknutelná motorová hřídel v náhledu používá 2,2 mm pouze jako vizualizaci zvoleného otvoru. Ostatní výrobní rozměry se tím nemění. Původní vzorky jsou zachované jako historie.

Další fyzická zkouška: nasazení celého pastorku bez násilí a ověření, že se na hřídelce neprotáčí. Tisk sestavy ani její jízda dosud potvrzené nejsou. Agent žádnou úlohu tiskárně neodeslal.

## 2026-09-19 — autíčko, samostatný tisk pastorku 2,2 mm

**Stav: uživatel oznámil zadání pouze pastorku k tisku.** Navazuje na aktuální STL s otvorem 2,2 mm. Dokončení, fit po celé délce 5,5 mm a přenos momentu zatím nepotvrdil; výsledek oznámí po vytištění. Skutečný profil, cívka, první vrstva a vazba konkrétního G-code nebyly kontrolovány. Agent úlohu neodesílal a tiskárnu neovládal.

## 2026-09-19 — autíčko, hotový pastorek pasuje

**Stav: uživatel potvrdil dokončený pastorek a uvedl, že krásně pasuje na motor.** Jde o hlášené nasazení hotového dílu s návrhovým otvorem Ø 2,2 mm. Přenos momentu při zátěži, geometrické měření výtisku a chod celého soukolí zatím ověřené nejsou. Skutečný tiskový profil, materiál, čas a spotřeba nebyly doložené.

Uživatel chce pokračovat tiskem zbytku. Pro jedno autíčko zbývá rám 1×, ozubené zadní kolo 1×, druhé zadní kolo 1×, přední kolo 2×, zadní osa 1×, přední osa 1×, krátká rozpěrka 1×, dlouhá rozpěrka 3× a pojistka 2×: celkem 13 kusů. Balíček `zbytek-auticka.zip` obsahuje jednotlivé kusy už v těchto počtech. Další tisk zatím nebyl potvrzen jako zahájený; agent nic neodesílá tiskárně.

## 2026-09-19 — autíčko, zadání tisku zbývajících dílů

**Stav: uživatel oznámil zadání tisku zbývajících dílů.** Slicer mu ukázal **3 hodiny 15 minut**; jde o odhad, nikoli naměřený čas. Konkrétní G-code, rozmístění, profil a skutečná cívka nejsou agentem ověřené. Dokončení a fyzický výsledek zatím nejsou potvrzené. Tisk zadává uživatel; agent tiskárnu neovládal.

## 2026-09-19 — autíčko, první stolní zkouška elektroniky a motoru

**Stav: uživatel potvrdil skutečný přibližně sekundový rozběh motoru po stisku tlačítka v telefonu.** Telefon ovládal Arduino UNO R4 WiFi a ST L293D. Po doplnění baterie zůstal motor bez stisku stát; při následném vyjmutí jednoho článku z držáku už nešel spustit, protože se přerušil sériový obvod. Arduino mělo vlastní USB napájení z powerbanky.

Zkouška proběhla s provizorními kontakty motoru bez pájení, bez kondenzátorů a se smíšenými Ni-MH 1,2V a běžnými AA články. Napětí, proud, přesná délka pulzu a teplota nebyly měřené. Jde o hlášení krátkého stolního běhu, nikoli potvrzení dlouhodobého provozu nebo jízdy. Na konci tohoto prvního pokusu byla jedna AA vyjmutá. Později uživatel napájení přepojoval a motor zkoušel znovu; aktuální obsazení držáku ani připojení USB nelze z tohoto historického záznamu odvodit.

Úplné zapojení, postup, výsledky, původ fotografií, opravy a body pro pokračování jsou v [záznamu u modelu autíčka](../elektronika/auticko/prvni-stolni-test.md). Tisk ostatních dílů zůstává ve stavu **zadaný, dokončení nepotvrzené**, s předchozím odhadem sliceru 3 h 15 min.

## 2026-09-19 — autíčko, snímatelná horní plošina

**Stav: uživatel následně potvrdil dokončení tisku a nasazení plošiny.** Správný dosed ani provozní vůle tím zatím potvrzené nejsou. Předtím požádal o další nosnou plochu bez přetisku rámu, nasazovanou na existující výstupky u kol. Upřesnil rovnou užitnou plochu **170 × 60 mm** podle svého nepájivého pole; umístění Arduina a zdrojů na poli si zařídí sám.

[Nástavec](../models/jednoduche-auticko/strecha.md) je jeden tiskový kus, celkem **180 × 70 × 36 mm**. Má čtyři dosedací kapsy, výřezy pro rozpěrky a okrajové drážky pro pásky. Původní díly ani jejich tiskový balíček se nezměnily. Geometrie je platná a STL po načtení uzavřené; fyzický fit, nosnost a stabilita s vybavením zůstávají neověřené. Profil, řezání, spotřeba a doba tisku tohoto dílu nejsou doložené. Agent tiskárnu neovládal.

## 2026-09-19 — autíčko, potíže po nasazení plošiny

Po nasazení střechy a nahrání ovládání při držení tlačítka uživatel hlásil nepravidelný rozjezd a divný zvuk. Následně upřesnil časovou osu: těžký rozjezd byl už na starém pulzním programu, nový držící režim zpočátku vnímal jako perfektně funkční a nejnověji se autíčko nerozjede ani s koly ve vzduchu. Silikonovým olejem namazal hřídelky; podle jeho hlášení to moc nepomohlo. Přínos nebyl měřený a mechanická příčina není vyloučená. Regrese firmwaru, samotná hmotnost ani jiná příčina nejsou prokázané. Podrobnosti a průběžná USB diagnostika jsou v [samostatném záznamu potíží](../elektronika/auticko/potize-po-montazi.md); nejde o potvrzení bezproblémové jízdy ani správného fitu střechy.

## 2026-09-19 — autíčko, požadavek vrátit sekundový program

Po přerušování při skutečném držení uživatel krátce požádal o rollback, ale před jeho uploadem jej výslovně zrušil a autorizoval dokončení opravy `hold-to-run-v2` během schůzky. [Časová osa](../elektronika/auticko/potize-po-montazi.md) a [firmware](../models/jednoduche-auticko/firmware/prvni-motor/README.md) rozlišují tehdejší softwarové ověření od následné fyzické akceptace, kterou uživatel později potvrdil. Mechanické díly původního autíčka se touto opravou nemění.

## 2026-09-19 — dokončené ovládání při držení v2

Finální zdroj `1760730b…` byl přeložen a nahrán do UNO R4 WiFi: 80 504 B flash / 9 792 B RAM, upload 80 512 B / 20 stran bez chyby. Regresní testy i skutečný Chromium nad simulovanými výstupy prošly. USB po startu potvrdilo v2, vypnuté motorové výstupy a připravený web; agent neposlal motorový povel. [Návod a evidence](../models/jednoduche-auticko/firmware/prvni-motor/README.md) rozlišují tuto technickou kontrolu od pozdější uživatelsky potvrzené zkoušky souvislého držení, puštění a dalšího stisku. Předchozí těžký rozjezd není tímto automaticky uzavřený.

## 2026-09-19 — nové autíčko s převodovkou 12:1

**Stav: model a tiskové podklady dokončené; tisk nebyl spuštěn a fyzická zkouška neproběhla.** Na výslovné zadání uživatele vznikla [samostatná konstrukce](../models/auticko-s-prevodovkou/README.md) s převody 18:54 a 18:72, koly Ø80 mm a užitnou plošinou 170 × 60 mm. Oproti původnímu autíčku s převodem 3:1 a koly Ø60 je teoretický tah 3× a rychlost třetinová, před ztrátami; skutečný rozjezd ani únosnost nejsou změřené.

Hotový [ZIP pro tisk](../models/auticko-s-prevodovkou/tiskovy-balicek.zip) obsahuje 20 kusů ze 13 typů, každý STL se tiskne jednou. Editovatelný FCStd, zdrojové makro, čtyři skutečné CAD náhledy, montážní návod a kontrolní JSON jsou ve stejné složce. Finální kontroly: 13 platných jednotlivých těles a uzavřených STL, 210 dvojic sestavy bez objemové kolize, 25 poloh obou soukolí, obálky rotujících dílů, krajní axiální posuny a tři parametrické zkoušky. Uložená sestava se znovu otevřela se správně viditelnými díly. ZIP i náhledy jsou svázané s finálními soubory pomocí SHA256.

Během kontroly byl zesílen lem za pojistkovou drážkou os na 1,5 mm a upravené podepření mezikola odstranilo možné škrtání při součtu axiálních vůlí. Původních 555 modelových souborů zůstalo podle srovnání hashů beze změny. Pro nový model nejsou připravené G-code ani ověřený tiskový profil, čas či spotřeba. Tiskárna nebyla ovládána.

## 2026-09-19 — potvrzené ovládání v2 a příprava druhého autíčka ve sliceru

**Uživatelská zkouška v2:** po návratu Jiří obnovil stránku a na pokyn k souvislému držení, puštění a novému stisku opakovaně hlásil „Jo, funguje to, perfektní“. Výsledek se vztahuje k nahranému `hold-to-run-v2`, zdroj `1760730b…`. Nejde o změřený doběh, maximální zatížení ani fyzické prověření všech síťových poruch. Historie předchozích problémů zůstává v [záznamu](../elektronika/auticko/potize-po-montazi.md).

**Druhé autíčko 12:1:** uživatel se rozhodl vytisknout celý nový balík a uvedl, že má díly rozložené ve sliceru. Kontrolu tiskové plochy nepožadoval. Zahájení ani dokončení tisku nejsou potvrzené; agent slicer ani tiskárnu neovládal. Původní ZIP se neměnil a čtecí porovnávání opětovného použití dílů bylo na uživatelovo rozhodnutí zastavené.

**Navazující zadání:** třetí samostatná varianta s převodovkou 12:1, koly Ø80, užitnou plošinou 170 × 60 mm a předním zatáčením. Jiří fyzicky přečetl označení vlastněného serva Tower Pro Micro Servo 9g SG-90. Nyní se navrhuje pouze mechanika; elektrické zapojení, napájení serva a ovládání šipkami přijdou později. Funkční firmware i oba předchozí modely mají zůstat zachované.

**Průběžný stav mechaniky zatáčení:** rozměrový návrh se převádí do nového makra, finální FCStd/STL ještě nejsou hotové. Uživatel potvrdil středový šroubek a následně přesně změřil vzdálenost od středu osy serva ke středu krajního malého otvoru jednoramenné páčky: **15 mm**. Tato hodnota je vstupem pro návrh táhla a kontroly pohybu; nahrazuje dřívější nejednoznačné měření. Zbývající neznámé rozměry jsou v [kanonickém inventáři](../elektronika/vybaveni.md).

**Následný milník a změna kol:** vznikl pracovní FCStd a 23 typů STL, zpočátku s koly Ø80 × 8 mm převzatými z V2. Po skutečném CAD náhledu Jiří požádal o širší a trochu menší kola, prioritu tahu a integrovaný tištěný dezén. Návrhová volba je vnější Ø76 × 12 mm, drážky hluboké 1 mm, rozšíření ven od rámu se zachováním vnitřních rovin kol a ozubeného záběru. Převod 12:1 se nemění; prodlouží se zadní osa a přední osičky. Nominální světlost 72zubého věnce Ø66,6 je při kontaktu na Ø76 rovné podlahy 4,7 mm; konzervativně podle kořene dezénu Ø74 zbývá 3,7 mm. Tyto údaje jsou výpočet, nikoli měření hotového výtisku. Teoretický tah proti Ø80 vzroste asi o 5,3 % a rychlost klesne o 5 %; dezén z tvrdého PLA nezaručuje přilnavost gumy. Širší přední kola zvyšují požadavek na řízení, rezerva serva nebyla změřená. Úzká pracovní verze není finálním tiskovým balíčkem. Model, exporty a kontroly se nyní aktualizují; agent netiskne ani nemění firmware.

## 2026-09-19 — dokončená mechanika třetího autíčka

**Stav: dokončený geometricky ověřený CAD prototyp**, fyzická montáž a řízení zatím nepotvrzené. [Model V3](../models/auticko-se-zatacenim/README.md) má převod 12:1, plošinu 170 × 60 mm, kola Ø76 × 12 mm se skutečným dezénem a přední řízení pro SG90 s uživatelem změřeným účinným poloměrem páčky 15 mm. Hotové jsou FCStd, makro, 23 typů STL, čtyři náhledy a balíčky: celá sestava 33 kusů, přestavba z V2 22 kusů při převzetí 11 původních. Proběhly kontroly těles, sítí, kinematiky, kolizí, axiálních vůlí a parametrických změn. Původní modely ani firmware se nezměnily. Fit serva a spoj páčky, zatáčecí síla, přilnavost a životnost vyžadují fyzickou zkoušku.

## 2026-09-19 — V3, rozložení 33 kusů do dvou 3MF

Jiří načítal součásti do Anycubic Slicer Next a po použití Arrange hlásil, že se nevešly všechny; následně si všiml tří kol. Aktuální okno nebylo přístupné, proto **nelze potvrdit, co skutečně načetl**. Složka `stl` obsahuje 23 typů, zatímco kompletní ZIP 33 fyzických kopií včetně čtyř kol; načtení pouze typů může vynechat i další opakované součásti. Samotné zdvojení předního kola tedy není úplná oprava takového importu.

Na výslovný požadavek rozmístit co nejvíce dílů vznikly [dva samostatné geometry-only 3MF](../models/auticko-se-zatacenim/rozlozeni/README.md): **31 kusů na první desce včetně všech čtyř kol, rám a plošina na druhé**. Nic se nezahodilo. Místní konkrétní profil Kobra X 0,4 mm má plochu 260 × 260 mm bez vyloučených zón; systémový proces uvádí Auto Brim 5 mm + mezeru 0,1 mm, skirt 0 a vypnuté podpory. Neuložené uživatelské úpravy se nedaly přečíst a nejsou zaměňované za tyto defaulty.

Umístění používá skutečné STL projekce s konzervativními konvexními obálkami a rezervou pro brim. Minimum mezi obálkami 11,0175 mm, od okraje 6 mm; měřítko 1:1, jen XY posuny a otočení kolem Z, původní tiskové orientace i Z0 zachované. Ověřeno 33 jedinečných kopií, všechny trojúhelníky proti zdroji, 466 dvojic a čtyři kola právě na první desce. Nejde o důkaz matematického globálního optima.

Oba finální soubory prošly skutečným CLI importem/exportem v nainstalovaném Next 2.0.0.5: 31 + 2 samostatných objektů, názvy i všech 110 436 trojúhelníků zachované, největší číselná odchylka vrcholů pod 0,000016 mm. CLI používalo izolovanou konfiguraci; uživatelské presety, otevřený projekt a původní geometrie nebyly upravené. Náhledy jsou skutečné XY projekce geometrie, nikoli snímky živého okna nebo vyslicované vrstvy. **Řezání, dosah skutečných podpor, G-code, spuštění a výsledek tisku se neověřovaly.** Pro rámy/těhlice je nutný náhled lokálních podpor; geometrická rezerva nedokazuje prostor pro libovolné stromové podpory. Tiskárna nebyla oslovena.

## 2026-09-19 — V2, fyzicky hlášené zasekávání a audit převodovky

**Nové uživatelské hlášení:** V2 12:1 se při pokusech opakovaně zasekává; Jiří vnímá odpor jako větší než přínos převodu. Použil sekundové lepidlo a následně olej, ale neznáme místa ani množství. Podezřívá nesprávnou stranu rozpěrky a slíbil přestavbu. Výsledek zatím nepřišel; mechanický test oddělený od motoru není potvrzený. Neodvozujeme z toho konkrétní vadný díl, příčinu, tiskový profil ani dokončení každé části původního balíčku.

[Audit a doporučený směr](../models/auticko-s-prevodovkou/revize-prevodovky.md) zachycuje skutečné rozteče, stohy, 5mm šířku obou záběrů a konstrukční riziko radiální volnosti vyložených os. Záměna rozpěrek 8,6/17,6 by při zachování dosedů posunula zadní ozubení o9 mm mimo záběr; jde o vypočtenou hypotézu, ne kontrolu skutečné montáže. Doporučeno zpřesnit a vyztužit uložení, určit stohy a zkalibrovat provozní vůle; pro větší redukci preferovaný směr16:1 proti prostorově problematičtějším20:1. Finální volba čeká na již položenou otázku kovové osy a pouzdra/ložiska versus tištěné díly. Nová převodovka se negenerovala; modely V2/V3, tiskové soubory i firmware zachované. Žádný upload, ovládání motoru/tiskárny, nákup, commit ani push.

## 2026-09-19 — zadání celé tištěné revize převodovky

Jiří zvolil **všechny nové mechanické díly tištěné**, bez nákupů. Požaduje větší praktickou sílu a dovoluje přepracovat celé uspořádání, ne pouze zvětšit jedno kolo. Úvodních16:1 nebylo jeho maximem ani schválenou konečnou geometrií. [Porovnání architektur](../models/auticko-silovy-prevod-25/architektura.md) rozšiřuje dvoustupňové kandidáty o tři stupně25:1 a36:1.

Dále fyzicky hlásí, že první záběr pracuje dobře, ale výstupní záběr má přibližně „půl zubu“ na **šířku**. Nejde o změřenou polovinu; staré nominální CAD překrytí5mm tím nepřepisujeme. Přímým kritériem nové revize je využití celé šířky užšího pastorku včetně nejhoršího axiálního posuvu.

Předávací kritérium: kompletní ZIP a očíslované rozmístěné3MF mají obsahovat **všechny fyzické kusy včetně přesně čtyř pojezdových kol**. Uživatel nesmí nic ručně násobit. Složka typových STL má zůstat jasně označená jako zdroj jednotlivých typů. Práce na novém CAD a kalibračních vzorcích probíhá; tisk ani hardware nebyly spuštěné.

## 2026-09-19 — hlášená vrstva 0,08 mm a zachování povrchového vzoru

Jiří pro připravovanou revizi uvedl změnu vrstvy z0,20 na0,08 mm kvůli detailu a odporu; zároveň chce ponechat standardní horní vzor Monotonic line. **Uživatelské hlášení nastavení**, nikoli přímá kontrola otevřeného sliceru, osobního profilu, G-code nebo fyzického tisku. První vrstva, šířka extruze, průtok a teploty nebyly tímto hlášením změněné ani ověřené. Geometry-only3MF toto nastavení nevkládají a osobní presety se nepřepisují. Kalibrační vzorky a finální mechanické díly mají použít stejné skutečné nastavení, pokud uživatel0,08 ponechá. Nižší Zvrstva sama nedokazuje přesnější XYotvor nebo lehčí chod převodu.

## 2026-09-19 — předaná kalibrační podložka01 pro novou převodovku

Na dotaz Jiřího byl předaný [kalibrace-podlozka-01.3mf](../models/auticko-silovy-prevod-25/rozlozeni/kalibrace/kalibrace-podlozka-01.3mf), SHA256 `17483261f837416cf2e3dea877f82004a58f6209208fc65509aa5c2c6f16a1ab`. Obsahuje8kusů:5bloků otvorů a3kruhové čepy. Doporučeno100%, Kobra X0,4, jeho běžná vrstva0,08mm a samostatná první0,20mm jako systémový default. Geometry-only3MF neobsahuje tato nastavení ani podpory. Před tiskem je nutné ve sliceru zapnout podpory ležatých čepů a prohlédnout skutečné vrstvy. Objednání tisku ani ovládání tiskárny agentem neproběhlo.

**Následně Jiří oznámil „tiskneme tu kalibrační podložku“: zahájení tisku je potvrzené jeho hlášením. Dokončení ani úspěšný fit zatím nepotvrdil.** Identita odeslaného G-code, skutečné podpory/profil a první vrstva nebyly ověřené. Předaná geometrie, souřadnice a pořadí otvorů jsou zmrazené; případná pozdější geometrická oprava musí dostat novou verzi. Hlavní auto se připravuje nezávisle a jeho návrhové vůle zatím nejsou výsledkem tohoto fyzického vzorku.

## 2026-09-19 — upřesnění celé silové V3 včetně zatáčení

Jiří výslovně upřesnil, že nový převod 25:1 má být součástí **revidované V3 s předním řízením SG90**. Průběžný model s pevnou přední nápravou není dokončením zadání. Připravuje se nový širší předek, všechna kola Ø76 × 12 mm s dezénem a tištěné uchycení vlastněného serva a původní páčky. Účinný poloměr páčky 15 mm a vlastnictví středového šroubku jsou potvrzené; její další rozměry jsou návrhové. Nové mechanické spoje nesmějí předpokládat nepotvrzené M2 šrouby, matice nebo pásky.

Další uživatelský návrh: krátké hladké obvodové vodicí pásy v otvoru s odlehčením mezi nimi pro lehčí chod. Po porovnání pásem 7 / 5 / 4 / 3 mm byl zvolen návrhový kompromis dvou souvislých 5mm pásem na krajích 30mm náboje, s odlehčeným středem Ø9. Proti 7mm pásům je nominální průměrný tlak při stejné síle o 40 % vyšší; menší plocha sama nedokazuje menší tření. Opotřebení vůli zvětšuje, nikoli samo vymezuje. Kalibrační podložka už byla uživatelem zahájená, její soubory zůstávají zmrazené a výsledky fitu dosud nejsou známé.

## Osnova příštího záznamu

Datum a model/verze; stav a zdroj informace; tiskárna a tryska; skutečný materiál/cívka; profil a změny; vazba na konkrétní soubor; odhady; první vrstva a průběh; fyzický výsledek a měření; další změna a její důvod. Neznámé položky nevyplňovat odhadem.

## 2026-09-19 — dokončená revidovaná V3, převod 25:1 a 66 dílů

**Dokončená příprava CAD a tiskových podkladů, fyzický výsledek neověřený.** [Nový model](../models/auticko-silovy-prevod-25/README.md) má třístupňový převod 18→54 /18→60 /22→55, přední řízení SG90 s původní páčkou r15, čtyři kola Ø76 ×12 a plošinu s užitnou plochou170 ×60. Dvě5mm hladká vodicí pásma v každém mezikole odděluje20mm odlehčený střed. Nové spojovací mechanické díly jsou tištěné; používá se pouze již vlastněný původní středový šroubek serva.

Při závěrečné kontrole vyšlo, že standardní hlavy zubů při největší rozteči neměly dostatečný kontaktní poměr. Finální geometrie prodlužuje hlavy malých kol na1,1m a velkých na1,2m; hlavové průměry velkých kol jsou přibližně56,4/62,4/57,4mm. Minimální teoretický kontaktní poměr je1,20401; oba18zubé obrysy mají skutečnou minimální špičku0,558857mm. Kontrola65 fází při nominální i nejmenší rozteči prošla; finální8mm pastorek zůstává uvnitř12mm věnce při všech16 kombinacích návrhových axiálních krajů, s rezervou1,4mm. Nejde o důkaz únosnosti, drsnosti ani tiskové přesnosti.

Kontrolovaná sestava má34typů a66fyzických instancí. Počty souhlasí s kompletním ZIPem i [třemi samostatnými3MF](../models/auticko-silovy-prevod-25/rozlozeni/README.md):26 +27 +13kusů. Všechna čtyři kola jsou na první podložce; žádný díl se ručně nenásobí. Import/export instalovaným Anycubic Slicer Next ověřil geometrii, měřítko, počty a orientace. Okraje≥6mm a mezery obálek≥11,02mm zahrnují uvažovaný brim, nikoli libovolné podpory. G-code, skutečné vrstvy a dosah podpor nejsou ověřené.

Hotové jsou FCStd, čtyři zdroje generátoru,34STLtypů,ZIP,pětCADnáhledů, očíslované náhledy podložek a montážní návod. Prošly statické kolize,21poloh řízení, mechanické dorazy, axiální vůle kol, osm parametrických zkoušek i nezávislý audit. Montážní návod výslovně osazuje motorové čepy před mezikolemA, které by bránilo jejich zasunutí. Kontrola zachování potvrdila90původních souborů a13zmrazených kalibračních podkladů beze změny.

**Kalibrační tisk uživatel dříve zahájil, dokončení a výsledky fitu stále nepotvrdil.** Servo a objímka původní páčky mají kromě r15 návrhové rozměry; nejprve vyžadují malé fyzické zkoušky. Celá nová mechanika, tah, pevnost, přilnavost a životnost zůstávají neověřené. Vrstva0,08mm je uživatelský záměr a není důkazem lepší XYpřesnosti; geometry-only3MF nastavení vrstvy ani Monotonic line nepřepisují. Žádný commit/push, nákup, upload firmwaru ani ovládání tiskárny, motoru nebo serva neproběhly.

## 2026-09-20 — fyzická kalibrace a revize provozních fitů V3 25:1

Uživatel vyzkoušel původní zmrazené vzorky a hlásí subjektivně dobré nasazení největšího čepu jen do největšího otvoru; pro prostřední čep následně uvedl stejný výsledek. Podle skutečných kanonických řad jde o Ø12/12,6 a Ø8/8,6. Přesné pořadí dalšího nevyhovujícího otvoru je v přepisu nejasné. U nejmenšího Ø4 nepotvrdil volné otáčení v žádném otvoru, ani4,3. Způsob očištění, orientace destičky a skutečně změřené průměry nejsou známé; dobré nasazení není automatické potvrzení rotace či radiální vůle.

Následná výslovná návrhová volba: největší hodnoty pro otočná uložení, nejmenší pro pevné spoje podle funkce. V rámu mají být Ø8čepy pevné a mezikola na nich volná; zadní Ø12osa je v rámu otočná, ale náboj hnacího kola na ní pevný. Čepy ani celé auto se nezmenšují. Původní společný parametr zadního kluzného uložení a výstupního náboje se musí oddělit. Nejmenší otvory nejsou fyzicky potvrzené lisované spoje a nesmějí se násilně sestavovat.

Výpočty prokázaly, že větší nominální CAD vůle nelze přenést do původní geometrie bez změny kontroly záběru. Podle nové funkční volby vycházejí relativní radiální rozsahy stupňů0,50/0,70/0,70mm; původní ozubení při největší rozteči nemá souvislý ideální kontakt ve2.a3.stupni a při nejmenší rozteči hrozí kolize. Část přídavku může ve skutečnosti kompenzovat tiskové zmenšení otvoru, ale to bez měření netvrdíme jako skutečnou provozní vůli. Revize vedení a profilu se nyní ověřuje.

Vytvořený archiv86souborů předchozí dokončené varianty včetně ověřených exportů a hashů je pod historie/pred-kalibraci-8_6-12_6-2026-09-20. Původní13zmrazených kalibračních podkladů se nemění. Nový samostatný doplňkový vzorek4,4/4,6/4,8 připravuje další fyzickou zkoušku; žádná z nových hodnot není ověřeným fitem. Deset Ø4čepů hlavní sestavy plní funkci zajištění/přenosu momentu, nikoli otočných ložisek, proto se na ně výsledek neaplikuje paušálně.

Uživatel hlavní sadu zatím netiskne a čeká na novou revizi. Desktopové soubory jsou dosud předchozí varianta a nahradí se odděleně až po úspěšných kontrolách nové. [Průběžný záznam revize](../models/auticko-silovy-prevod-25/revize-fitu-2026-09-20.md) rozlišuje fakta, volby a otevřené body. Agent žádný tisk, G-code, změnu presetů, firmware, ovládání zařízení ani commit/push neprovádí.


### 20. 9. 2026 — pokračování kalibrační revize V3 25:1

- Uživatel doplnil výslovné potvrzení otáčení Ø8 čepu v největším otvoru 8,6. Skutečná boční vůle a průměry změřené nejsou; nominální přídavek 0,6 se nevydává za skutečnou provozní vůli.
- Nový samostatný [vzorek Ø4 V2](../models/auticko-silovy-prevod-25/kalibrace-4-v2/README.md) má 4,4 / 4,6 / 4,8 mm, dvě orientace a 8mm pracovní hloubku; používá původní čep. CAD/STL/3MF ověřené, fyzický tisk a fit nepotvrzené.
- Hlavní zdroj má oddělené fit parametry, avšak nový robustnější profil ozubení neprošel kontrolou kořene při přenosu síly. [Konkrétní důkaz](../models/auticko-silovy-prevod-25/revize-fitu-diagnostika/README.md). Hlavní 66kusová sada proto není vydaná jako hotová revize; předchozí výstupy i desktopové 3MF jsou zachované a označené předkalibrační.
- Hotová a CAD/STL/3MF/Next CLI ověřená je sedmidílná [ruční zkouška původního stupně18→60](../models/auticko-silovy-prevod-25/zkouska-prevodu/README.md) s novými 8,6mm otočnými otvory a 8,1mm pevnými sedly. Má rozhodnout skutečné nasazení, souosost dlouhých nábojů a chod záběru. Žádný nový tisk, G-code, pohyb motoru ani změna firmwaru neproběhly.


### 20. 9. 2026 — předání celé V3 25:1 po revizi fitů

Konečné zadání nahradilo dřívější čekání na další vzorky: Jiří chce celý skutečný tiskový prototyp s původním 20° / m1 ozubením, nikoli další povinný testovací výtisk. [Aktuální sada](../models/auticko-silovy-prevod-25/README.md) má 34 typů a **66 kusů včetně všech čtyř kol**, připravených na [třech 3MF podložkách 26 / 27 / 13](../models/auticko-silovy-prevod-25/rozlozeni/README.md). Žádné další kopírování dílů není potřeba.

- Kluzné otvory mezikol 8,6 a zadní osy 12,6; pevná sedla čepů 8,1, výstupní náboj a zadní D kola 12,1, statické Ø4 spoje 4,1, D ploška 4,05 proti ose 4,00 mm. Nosné čepy se nezmenšují.
- Nominální CAD: 2345 párů bez kolizí, 16 axiálních kombinací s plnou poslední 8mm šířkou a rezervou 1,5 mm, šest ozubených obrysů shodných s archivem, 24 kontrol krajních poloh změněné objímky, 10 změnových parametrických zkoušek. Uložená GUI sestava, náhledy a finální exporty jsou navázané na zdrojové hashe.
- Exporty: 34 uzavřených STL typů / 66 ZIP kopií; tři 3MF zachovávají 202 604 trojúhelníků a všechny počty. Rozložení, import/export Next CLI a nezávislá kontrola původu důkazů prošly. Minimální mezera modelů 11,0206 mm, okraj nejméně 6 mm; podpory a skutečné dráhy je nutné prohlédnout ve sliceru.
- **Plný konzervativní radiální scénář zůstává `false`.** Původní ozubení nepokrývá předpoklad celé nominální CAD vůle jako reálné provozní vůle. Uživatel přijal nominální tiskový prototyp s touto hranicí; skutečná vůle není změřená. Historické kontroly nezměněných částí nejsou vydávány za nové testy.
- Fyzický tisk, montáž, zatížení ani jízda této revize nejsou potvrzené. Další vzorky jsou pouze volitelné. Agent nevytvořil G-code, nespustil tisk ani nezměnil preset, firmware nebo zařízení.

**Umístění:** vše výhradně v projektu `models/auticko-silovy-prevod-25/`, tři podložky v `rozlozeni/`, předchozí revize v `historie/`. Nejnovější pokyn ruší dřívější plán aktualizovat Desktop; již existující kopie na ploše se dále nemění. Pravidlo je zapsané jako kritické v [AGENTS.md](../AGENTS.md). Původní modely, zmrazená kalibrace i firmware zůstaly zachované. Nic nebylo commitováno ani odesláno do Gitu.

## 2026-09-20 — vadné části první várky V3 25:1 a připravený dotisk

Jiří dodal fotografie `20260920_124057.jpg` (první podložka na tiskárně) a `20260920_125550.jpg` (odložené díly). Jde o aktuální 66dílnou V3 25:1 po revizi fitů, nikoli starší 33dílné auto. První původní podložka měla 26 kusů. Na druhé fotografii je 20 kusů: **19 bez velké zjevné vady na viditelné straně a jedna zjevně vadná pravá těhlice**. Šest dalších dílů chybí v odložené sadě. Spodní strany, rozměry, pevnost a fit zachovaných dílů nejsou potvrzené. Druhá původní várka s **27 kusy podle uživatele právě tiskne**; dokončení ani kvalita nepotvrzené. Třetí s **13 kusy zůstává plánovaná**, její absenci nepočítáme jako selhání první várky.

[Opravná sada a přesný inventář](../models/auticko-silovy-prevod-25/rozlozeni/dotisk-prvni-varky-2026-09-20/README.md) obsahuje sedm kopií z původní desky 1, čísla **8, 11, 12, 13, 14, 17, 19**: zadní osu, pravou těhlici, svislý čep, pevný čep převodu, jeden čep serva, příčný klínek a jeden čep plošiny. Vznikly tři samostatné geometrické 3MF **1 / 1 / 5 kusů** a vedle nich výslovně označené plné projekty Next s nastaveným novým procesem dotisku. Geometrické varianty nastavení nenesou; plné projekty vědomě načítají vlastní Kobra X / systémový PLA proces. Uživatelovy uložené presety se neměnily. Žádné kopie není třeba ručně přidávat.

**Evidence možného mechanismu vady:** původní ležaté válcové díly a těhlice mají malé kontaktní plochy a výrazné spodní převisy. Dohledaný lokální kandidát G-code první úlohy má stejných 26 názvů/pořadí, `enable_support=0` a `support_used=false`; 0,12mm vrstvu, první 0,20mm, Auto Brim 5mm/gap0,15, 2 stěny, 15% 3dhoneycomb. Jeho SHA256 a omezený výpis jsou v evidenci dotisku. **Uživatel nepotvrdil identitu tohoto spuštěného souboru a archiv neobsahuje zdrojové sítě.** Absence podpor dobře vysvětluje viditelné vady, ale není jedinou prokázanou příčinou; teplotu, přilnavost ani tok z fotek neurčujeme. Bílý Alzament PLA Basic / Kobra X 0,4 je zadaný kontext, ne údaj odvozený z barvy sliceru.

Osa zůstala vodorovná, otočená D ploškami nahoru; těhlice nově leží horním okem/ramenem (rovinný kontakt 107,73mm² místo 0); obě potřebují podpory. Pět čepů stojí na hlavách, bez podpor v pojistných drážkách, s vnějším brimem 8mm. Je přiznaná horší odolnost svisle tištěných čepů vůči ohybu napříč vrstvami a vratkost Ø4×51,2. Rozměry, geometrie, CAD, původní STL a původní 3MF se neměnily.

**Kontroly:** 7 kopií / 19 446 zachovaných trojúhelníků, uzavřenost a objemy, tuhé rotace, 100% měřítko, Z0, nejmenší mezera 32,5mm a okraj 54,7mm. Nezávislý geometrický audit prošel. Všechny tři opravné varianty byly skutečně lokálně naslicované v izolovaném Next CLI: 0,12/první0,20mm, 4 stěny, 100% rectilinear, vnější brim8/gap0,1, zpomalený proces. Osa/těhlice obsahují Support a Support interface; pět čepů nikoli. Zkontrolovány skutečné dráhy včetně podpor a brimu, všechny extruzní střednice v ploše260×260mm; pořadí trojúhelníků a světové souřadnice po importu shodné do0,00002mm. Odhady 2h44 /1h21 /1h54, celkem přibližně34,67g; nejde o skutečnou spotřebu ani dobu.

Ve výsledku zůstala profilová varování teploty podložky60°C proti materiálové hranici54°C a na dvou podporovaných úlohách traditional timelapse. Jsou zdokumentovaná, nevydáváme řezání za výsledek bez varování. Diagnostický G-code zůstal v ignorované cache a není předáván ke spuštění; plné projekty žádný G-code neobsahují. **Dotisk nebyl odeslán ani spuštěn, tiskárna nebyla oslovena.** Fyzická úspěšnost oprav, oddělitelnost podpor, montáž a jízda zatím nepotvrzené. Elektronika, firmware, Desktop a Git historie se neměnily.

Následná kontrola našla také původní první 3MF již před dotiskem uloženou jako celý projekt Next (čas01:29) s podporami vypnutými. Všech26 meshů a poloh přímo souhlasí s kanonickým manifestem; rozdíl hashe proti historickému exportu je existující změna souboru. Tuto uživatelskou kopii jsme nepřepsali; druhá a třetí stále odpovídají původním hashům. Jde o další přímý doklad uloženého nastavení, nikoli definitivní potvrzení skutečně spuštěného G-code.


## 20. 9. 2026 — druhá várka dokončená, třetí a oprava osy nastojato

**Původ hlášení:** Jiří v navazující hlasové úloze potvrdil dokončení původní podložky 02 V3 25:1 (27 kusů). Nové fotografie druhé várky zatím nedodal, kvalita jednotlivých dílů není vyhodnocená. Fotografie 124057/125550 patří pouze k první várce. Nevznikl nový seznam náhrad druhé várky.

Na jeho výslovné zadání je [původní 03 se 13kusy připravená se šesti čepy nastojato](../models/auticko-silovy-prevod-25/rozlozeni/stojate-cepy-2026-09-20/README.md). Čísla 3, 4, 6, 7, 8, 9 stojí na hlavách; ostatní díly zachovávají funkční orientaci. Nastavený projekt Next má skutečné podpory pouze u plošiny, včetně převisů a příčných otvorů všech čtyř noh. Plošina má základní veřejný proces 0,12mm,15%3Dhoneycomb,2stěny; plná výplň / 4 stěny jsou lokálně jen u12 malých dílů. Finální odhad 6 h 19 min 15 s / 71,23 g. Dosavadní proces uživatelovy plošiny není doložen, původní 03 byla geometry-only.

Také [zadní osa opravné 01](../models/auticko-silovy-prevod-25/rozlozeni/dotisk-prvni-varky-2026-09-20/README.md) stojí na čele, výška 150,6 mm, brim 12 mm, pomalejší pohyby. Skutečné podpory podepírají D přechod a příčný otvor; tenké prstence v pojistných drážkách bude potřeba odstranit. Finální odhad 4 h 39 min 44 s / 19,99 g. Opravná sada stále 7 kusů, podložky 1 / 1 / 5; pravá těhlice i pětčepová03 jsou beze změny. Bilance 19 zachovaných + 7 náhrad + 27 dokončených čekajících na fotky + 13 plánovaných = 66 není prohlášením montážní kvality všech kusů.

**Ověření souborů:** stejné STL/CAD/ZIP a počty, pouze rotace/posuny kopií; původní 01/02 nepřepsané. Starší03 a opravná sada archivované. Nové projekty prošly lokálním řezáním, kontrolou skutečných vrstev/drah, podpory i brim uvnitř 260 × 260 mm; objektová nastavení zachovaná. Nezávislé geometrické a drahové kontroly souhlasí. Profilová varování zůstávají zapsaná. Žádný tisk, firmware upload, commit ani push neproběhl.

**Pravidla:** Jiří schválil výchozí stojatou orientaci našich konkrétních čepů podle opakované zkušenosti, bez univerzálního slibu vyšší pevnosti. Vrstvy napříč osou a stabilita vysoké osy zůstávají fyzicky neověřené. Potřebné podpory se mají skutečně připravit v nastaveném projektu a ověřit řezáním; brim je nenahrazuje. Zapsáno do AGENTS.md a docs/workflow.md. Původní export round_pin Y+90 byl společné pravidlo, nikoli doložená individuální pevnostní optimalizace.

**Otevřené body:** nové fotografie původní 02, fyzický výsledek nové 03 a opravné sady, vyčištění podpor a drážek, fit/montáž/chod. Dokončení hlavní 03 nebo oprav zatím uživatel nepotvrdil.


## 2026-09-20 — druhá várka V3 25:1 a kombinovaný26kusový tisk

Jiří potvrdil dokončení původní02. Fotografie `20260920_185846.jpg` ukazuje její27 pozic na tiskárně, `20260920_192335.jpg` zachované díly obou dosavadních várek. Prokázaný výběr nových náhrad: levá těhlice a pět samostatných čepů (původní02 čísla4,11,12,16,22,23). Pravá těhlice už je v opravě první várky, oba motorové můstky jsou zachované a nepřidávají se. Použitelnost motorového dorazu rámu, přítomnost víka objímky a obou motorových klínků čekají na upřesnění; nejsou automaticky označené jako vadné.

Připravená [jedna kombinovaná podložka26](../models/auticko-silovy-prevod-25/rozlozeni/kombinovana-03-2026-09-20/README.md) obsahuje13 dosud netištěných z původní03 +7 oprav první +6 druhé. Čepy a osa nastojato, obě těhlice otočené, skutečné podpory jen plošina/osa/obě těhlice. Plošina má15 % výplň, ostatní díly100 %, vrstva0,12mm, Kobra X0,4mm. Místní společný řez prošel:26 kopií, plná výška modelových drah, stejné mesh, skutečné obálky extruzí oddělené nejméně3,56mm, okraj4,39mm. Odhad19h37min17s /120,09g. Zaznamenána profilová varování teplotní hranice a timelapse.

Kombinovaná26 nahrazuje samostatnou původní03 a celou první opravnou sadu; netisknout jejich kopie navíc. Kanonický CAD/STL/ZIP zůstaly stejné. Při závěrečné kontrole byla původní02 nalezena nově uložená jako plný Next projekt s vrstvou0,20 a vypnutými podporami; jiný hash je zaznamenán, geometrie27 kusů odpovídá původnímu manifestu. Soubor se nevracel přes aktuální verzi a konkrétní tištěný G-code tím není prokázán.

Jde o počítačově připravený tisk, nikoli fyzický úspěch. Tiskárna nebyla oslovena, tisk26 ani montáž nejsou potvrzené. Rozhodnutí o rámu a nejasném inventáři zůstává otevřené mimo26.

## 22. 9. 2026 — neúspěšná koupelnová přepážka a rozdílné tiskové profily

Jiří večer v hlasové úloze nahlásil přibližně 1 h 28 min dlouhou úlohu, kterou tiskárna sama dokončila, ale zůstaly jen tenké proužky, chuchvalce a vlásky. Předtím kopíroval díly z jiného projektu. **Jde o hlášené fyzické selhání; skutečný dokončený soubor není identifikovaný.** Není doložená fotografie, měřená výška, režim rychlosti ani historie tiskárny. [Podrobná diagnostika a zachované důkazy](../models/koupelnova-prepazka/diagnostika/2026-09-22-nepovedeny-tisk/README.md).

Před dokumentačními změnami bylo zachováno 84 původních modelových souborů a relevantní místní exporty. Všech 70 předaných souborů aktuální revize 02 odpovídalo původním SHA256. Přímé audity 3MF/STL/G-code potvrdily plné 8mm díly a 40 skutečných extruzních vrstev, žádné omylem exportované lepidlo, škálování nebo předčasné ukončení. Historická varianta má 10 mm a 50 vrstev. Počítačový audit není důkazem fyzicky vytlačeného materiálu.

Místní export z 19:22 je konkrétní kandidát: tři starší 10mm díly, **profil PLA, první tryska 220 °C a dále 205 °C, skutečné extruzní příkazy až 250 mm/s a první vrstva až 100 mm/s**, dvě stěny a 15% výplň. Vazba tohoto souboru na dokončenou úlohu není potvrzená; nelze jej vydávat za jistou příčinu. Nový export po reimportu z 20:36 již uvádí Anycubic TPU95A, ale má 215/210 °C, standardní proces a 15% výplň. To není předaný vlastní Alzament experiment.

Oba předané aktuální úplné 3MF mají vlastní **Alzament TPU95A Gray, 225/225 °C, desku 60/60 °C, první vrstvu nejvýše 20 mm/s, ostatní extruzi nejvýše 40 mm/s, čtyři stěny a 100% výplň**. Nativní načtení celého testovacího projektu do izolovaného Anycubic Slicer Next bez externích presetů toto nastavení zachovalo. Test obsahuje dva kusy a odhad 33 min 9 s, celá lišta tři kusy a 5 h 54 min 8 s. Soubory nebylo třeba přejmenovat ani geometricky opravit; doporučené obnovení nastavení je otevřít celý TEST3MF, nikoli přetahovat STL do jiného procesu. Dokumentace předání byla zpřesněna.

Pozdější přímé hlášení Jiřího: **šedé Alzament TPU95A dal do fyzického vstupu 3**, do **vstupu 4 právě dává zlaté Alzament PLA Silk**; dokončení zavedení zlata nepotvrzené. Pro přepážku je určen vstup 3. Logický filament 1 z projektu je při případném odesílání nutné správně přiřadit, samotné 3MF fyzický vstup neurčuje. Nový start ani správné softwarové mapování nebyly potvrzené. Kanonická zásoba v [materiálech](materialy.md) doplnila použití s původem hlášení, nikoli odhad spotřeby.

Podávání, přilnavost, vlhkost a skutečný průtok zůstávají nevyšetřené; chuchvalce samy příčinu neurčují. Rozpor doporučených teplot desky zůstává zdokumentovaný. Tiskové parametry se neměnily naslepo, žádný další tisk ani ovládání zařízení neproběhly. Neproběhl commit ani push.
