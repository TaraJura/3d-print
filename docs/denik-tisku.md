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

## Osnova příštího záznamu

Datum a model/verze; stav a zdroj informace; tiskárna a tryska; skutečný materiál/cívka; profil a změny; vazba na konkrétní soubor; odhady; první vrstva a průběh; fyzický výsledek a měření; další změna a její důvod. Neznámé položky nevyplňovat odhadem.
