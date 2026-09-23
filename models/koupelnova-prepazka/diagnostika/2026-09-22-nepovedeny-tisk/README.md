# Neúspěšný tisk přepážky — 22. 9. 2026

**Potvrzený je neúspěšný fyzický výsledek podle Jiřího, nikoli identita tištěného souboru.** V místních dočasných souborech byl nalezen export starší přepážky pro PLA s jinými teplotami a rychlostmi. Je to konkrétní kandidát k identifikaci, ne prokázaný záznam provedené úlohy. Předané TPU projekty obsahují plnou výšku a zachovaly původní kontrolní otisky.

## Uživatelské hlášení a jeho hranice

Jiří večer 22. 9. 2026 v hlasové úloze uvedl přibližně **1 h 28 min**, pouze jednu vrstvu nebo milimetrové tenké proužky, chuchvalce a natahující se vlásky. Následně potvrdil, že tiskárna úlohu **sama dokončila**, nezastavil ji. Předtím kopíroval díly z druhého projektu. Název tohoto projektu, skutečný odeslaný G-code, režim rychlosti a historie tiskárny nejsou potvrzené. Neproběhlo měření výšky, fotografie ani přímá kontrola výtisku.

Poté chtěl znovu přetáhnout aktuální STL a upozornil, že rozhraní uvádí Anycubic místo Alzamentu. Výslovně požaduje Alzament TPU95A Gray. Zmínku o novém tisku vzápětí korigoval: vstup 4 nenaplnil a vstup 3 byl připravený/označený jako PLA. **Žádný správný nový start, fyzické zavedení TPU ani mapování vstupu tím nejsou potvrzené.** Barva, číslo virtuálního filamentu v projektu a skutečný vstup nejsou zaměnitelné důkazy.

**Následné zpřesnění Jiřího:** do fyzického vstupu **3 dal šedé Alzament TPU95A**, do vstupu **4 právě dává zlaté Alzament PLA Silk**. Zavedení zlatého je probíhající, nikoli potvrzeně dokončené. Pro přepážku je tedy podle přímého hlášení určen vstup 3. Toto zpřesňuje starší nejasnost; agent cívky neviděl a nový start tisku není potvrzený. Logický filament 1 v projektu se při případném odesílání mapuje na fyzický vstup 3, automaticky ho samotné 3MF neurčuje.

Původ hlášení: hlasová úloha `01a0ca09-8987-7f82-880c-534966723e9e`, navazující zprávy do návrhové úlohy `01a0ca0a-c773-79c3-91df-f91381299d8e`.

## Zachování důkazů

Před změnou dokumentace byla vytvořena místní kopie všech **84 souborů** modelové složky (11 544 104 B); cesty, původní časy a SHA256 obsahuje [manifest původních souborů](manifest-puvodnich-souboru.json). Kopie je v `evidence/model/`, včetně staré kořenové reference a kompletní revize 02. Byly zachovány také předchozí předávací manifesty. Všech **70 souborů finální revize 02** před tímto auditem přesně odpovídalo SHA256 při předání.

Relevantní místní exporty byly následně zachovány v `evidence/local-temp/`; [manifest dočasných souborů](manifest-docasnych-souboru.json) obsahuje jejich přesné zdrojové cesty, časy a SHA256. Jde o místní soubory sliceru, nikoli soukromé cloudové logy. Adresář `evidence/` se záměrně neversionuje. Původní modely, STL, 3MF a G-code nebyly při diagnostice regenerovány, smazány ani přepsány. Uživatelský slicer byl pouze nepřímo čten přes místní soubory; jeho okno ani tiskárna nebyly ovládány. Jedna samostatná izolovaná instance CLI ověřila pouze načtení a export nastavení TEST projektu.

## Nalezené programy a rozdíly

V tabulce jsou nastavené povely a odhady sliceru, nikoli naměřené teploty nebo časy tiskárny.

| Program | Objekty / vrstvy / výška | Aktivní filament | Tryska první / další | Výplň / stěny | Normální odhad |
|---|---|---|---|---|---|
| Předaný TEST revize 02 | 2 / 40 / 8 mm | vlastní Alzament TPU95A Gray | 225 / 225 °C | 100 % / 4 | 33 min 9 s |
| Předaná celá revize 02 | 3 / 40 / 8 mm | vlastní Alzament TPU95A Gray | 225 / 225 °C | 100 % / 4 | 5 h 54 min 8 s |
| Předaná historická 10mm varianta | 3 / 50 / 10 mm | vlastní Alzament TPU95A Gray | 225 / 225 °C | 100 % / 4 | 7 h 23 min 4 s |
| Místní export 19:22, `0922-1922-dil-1_plate(01)_PLA_0.2_57m23s.gcode.3mf` | 3 / 50 / 10 mm | Anycubic PLA | 220 / **205 °C** | 15 % / 2 | 57 min 23 s |
| Místní export 20:35, `0922-2035-dil-1_plate(01)_PLA_0.2_49m39s.gcode` | 3 / 40 / 8 mm | Anycubic PLA | 220 / **205 °C** | 15 % / 2 | 49 min 39 s |
| Místní export 20:36, `0922-2036-dil-1_plate(01)_TPU_0.2_2h28m26s.gcode` | 3 / 40 / 8 mm | Anycubic TPU95A | 215 / **210 °C** | 15 % / 2 | 2 h 28 min 26 s |

Všechny uvedené varianty nastavují desku na 60 °C. Export 19:22 skutečně obsahuje `G9111 bedTemp=60 extruderTemp=220` a dále `M104 S205`, aktivní materiál PLA a objemový limit 13 mm³/s. Není to pouze úsudek z názvu souboru. Jeho nominální proces uvádí vnější stěnu 200, vnitřní a výplň 300 mm/s; skutečné povely rychlosti samostatně vyhodnocuje [audit G-code](audit-gcode.md). Předaný experiment má první vrstvu nejvýše 20 a další extruzi nejvýše 40 mm/s, limit 3,2 mm³/s.

Parser pohybů XY s kladnou extruzí přímo potvrdil v obou místních PLA exportech **až 250 mm/s**, v první vrstvě **až 100 mm/s**. Nový systémový TPU export má až 61,315 mm/s a první vrstvu až 50 mm/s. Tím je výrazně jiný tiskový proces doložen i skutečnými příkazy. Není to měření rychlosti fyzického stroje.

Čas 1 h 28 min přesně neodpovídá žádnému z předaných projektů ani jejich alternativním odhadům. Export 19:22 má i tichý odhad 1 h 34 min 31 s; blízkost není identifikací skutečné úlohy. Soubory 20:35 a 20:36 vznikly až při následném řešení, nejsou dokladem předchozího neúspěšného tisku.

## Nezávislé kontroly

[Geometrický audit](audit-geometry.md) přímo načetl všech šest původních 3MF, jejich sítě, typy objektů, build a komponentové transformace. Všechny sítě jsou uzavřené, orientované, tvoří jedno souvislé těleso, mají kladný objem a odpovídají svým STL. Aktuální díly mají délky 193/200/193 mm, šířku 20 mm a výšku sítě 7,99960614 mm; testovací kusy 30 × 20 × 7,99960614 mm. Rozdíl proti přesným 8 mm CAD je teselace oblouku. Všechny leží na Z=0 bez škálování. Není přítomný objekt lepidla, plošný objekt, netisknutelný modifikátor ani chybné snížení výšky.

[Audit G-code](audit-gcode.md) čte skutečné příkazy a extruze ze zachovaných archivů a samostatných souborů, ne původní kontrolní JSON. U předaného TEST souhlasí vložený a vnější G-code bajt po bajtu; obsahuje 40 vrstev do 8 mm, relativní extruzi M83 a absolutní souřadnice G90, bez vloženého předčasného ukončení nebo vypnutí ohřevu. Geometrická výška ani samotné číslo vrstvy však neprokazují, že tiskárna skutečně materiál vytlačila.

Celkem bylo zkontrolováno 17 surových zdrojů, 11 archivů (včetně čtyř dočasných objektových souborů `.model`, které jsou ZIP) a šest unikátních G-code programů. Ani čtyři dočasné sítě nejsou zploštělé; mají výšku cca 8 mm. Dvě cache kopie dílu 1 neznamenají tisk čtyř kusů, G-code obsahuje tři tisknuté objekty. Všech šest má skutečnou kladnou extruzi v 40 nebo 50 výškách do 8 nebo 10 mm; kontrola odlišuje tiskové Z od přejezdového Z-hop. Žádný z těchto programů nepřikazuje pouze jednovrstvý výsledek. Ani tento závěr neprokazuje identitu programu skutečně provedeného tiskárnou.

[Audit předání](audit-predani.md) našel také naše nedostatky v přehlednosti: běžné názvy starých souborů v kořenu a zavádějící interní popis historického úplného 3MF, který stále tvrdí, že obsahuje pouze geometrii. Aktuální revize 02 má interní popis správný. Tyto nejasnosti mohly usnadnit záměnu, ale nejsou důkazem použitého postupu. Zachované historické důkazy se zpětně nepřepisují; aktuální README nyní uvádí selhání a konkrétní celý testovací projekt hned nahoře.

## Alzament a další postup

Oba předané aktuální úplné projekty **už obsahují vlastní** `EXPERIMENT Alzament TPU95A Gray Kobra X 0.4 225C bed60C`, vendor `Alzament`, type `TPU` a jediný filament s ID `EXPERIMENT-Alzament-TPU95A-Gray`. Zdrojový profil má `is_custom_defined=1`, `from=user`, prázdné `inherits` a kompletní nastavení odvozené z přesného systémového TPU95A profilu Kobra X. Název tiskárny Anycubic je správný; výrobce filamentu je Alzament. Výchozí PLA položka uvnitř strojového profilu není vybraným materiálem těchto projektů. Podrobné porovnání uvádí [audit profilu](audit-filament-label.md).

**Nativní načtení celého TEST projektu bylo nyní ověřeno:** AnycubicSlicerNext 2.0.0.5 s novým izolovaným `--datadir`, pouze `--export-settings`, bez přidaných presetů a bez řezání. Import skončil 0 a zachoval vlastní Alzament profil, TPU, 225/225 °C a desku 60/60 °C. SHA256 vstupního 3MF před a po se shoduje. [Výsledek importu](audit-import-cli/result.json) a [účinná nastavení](audit-import-cli/whole-project-settings.json) dokládají, že celý projekt nepřepadl na systémový Anycubic TPU215/210. Nejde o přímou inspekci aktuálního uživatelského GUI. Správný profil tedy není nutné přejmenovávat, instalovat přes existující presety ani měnit jeho parametry.

Pro obnovení známých parametrů otevřít [aktuální TEST-EXPERIMENT 3MF](../../revize-02-8mm/rozlozeni/TEST-EXPERIMENT-spoj-Alzament-TPU95A.3mf) **jako celý projekt do prázdného projektu**. Import samotných STL nebo geometrie do jiného projektu materiál a tiskový proces nepřenese. Zkontrolovat dva kusy, 8 mm, 40 vrstev, vlastní Alzament TPU95A Gray, 225/60 °C, čtyři stěny, 100% výplň a normální odhad 33 min 9 s. Při případném odesílání podle potvrzeného fyzického zavedení mapovat na vstup 3 s šedým TPU, nikoli vstup 4 se zlatým PLA Silk. Agent materiálové nastavení fyzických vstupů ani mapování tiskárny neměnil.

Nalezený rozchod profilů je důvod napravit načtení projektu. **Není zatím prokázanou jedinou příčinou fyzického selhání.** Podávání, skutečný tok, přilnavost, vlhkost, znečištění trysky ani skutečné mapování filamentu nebyly zkontrolované. Chuchvalce a vlásky samy tyto příčiny nerozlišují. Geometrie se nemění a tiskové parametry se neupravují naslepo.

[Rozpor údajů teploty desky](../../revize-02-8mm/rozlozeni/teplotni-rozpor.md) zůstává doložený; připravený Alzament profil je experimentální, ne fyzicky kalibrovaný. Žádná nová úloha nebyla agentem odeslána, spuštěna ani řízena. Pro uzavření příčiny je potřebná vazba na skutečný dokončený soubor a ověřený výsledek následujícího fyzického testu.
