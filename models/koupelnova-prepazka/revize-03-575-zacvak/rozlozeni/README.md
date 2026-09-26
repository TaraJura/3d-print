# Revize 03 – podložky pro přepážku 575 mm se zacvaknutím

Stav 23. 9. 2026: **místně nastavené a řezané experimentální projekty**, ověřené z finálních STL po doplnění oboustranného vedení spoje v Z. Pro Anycubic Kobra X s tryskou 0,4 mm. Tiskárna nebyla ovládána a žádný soubor nebyl odeslán. Fyzický tisk, podávání TPU, zacvaknutí ani těsnost této revize nejsou ověřené.

| Celý projekt k otevření | Obsah jedné podložky | Odhad sliceru v normálním režimu |
|---|---|---:|
| [TEST-EXPERIMENT-575-snap-Alzament-TPU95A.3mf](TEST-EXPERIMENT-575-snap-Alzament-TPU95A.3mf) | **Samostatný test:** 2 kusy, každý 40 × 20 × 8 mm | **43 min 5 s**, 7,55 g |
| [EXPERIMENT-prepazka-575-snap-Alzament-TPU95A.3mf](EXPERIMENT-prepazka-575-snap-Alzament-TPU95A.3mf) | **Plná přepážka:** 3 kusy, délky 208,333333 / 208,333333 / 190,333333 mm, šířka 20 mm, výška 8 mm | **6 h 4 min 9 s**, 71,27 g |

Otevřít jako **celý projekt** a zachovat projektové profily. Aktivní materiál má název `EXPERIMENT 575 snap Alzament TPU95A Gray Kobra X 0.4 225C bed60C`. Samotné kopírování dílů do jiného projektu nepřenáší jistotu těchto nastavení. Testovací pár není součást tříkusové hlavní sestavy. Před zkouškou spoje je třeba odstranit lem; fyzická vůle a síla zacvaknutí jsou předmětem testu.

Geometry-only alternativy jsou [hlavní podložka](prepazka-575-snap-pracovni-geometrie.3mf) a [samostatný test](TEST-575-snap-pracovni-geometrie.3mf). Obsahují jen geometrii v mm, bez procesu, filamentu a G-code; nejsou samostatně připravené k tisku.

## Nastavení a zachovaný rozpor teplot

Oba řezané projekty mají jednu cívku Alzament TPU95A, trysku **225 °C pro všechny vrstvy**, texturovanou PEI desku **60 °C**, vrstvy **0,2 mm**, první vrstvu nejvýše **20 mm/s**, ostatní extruzní pohyby nejvýše **40 mm/s**, limit objemového průtoku **3,2 mm³/s**, násobitel průtoku 1,0, 4 stěny, 5 horních/dolních vrstev a 100% výplň. Vnější lem má 5 mm s mezerou 0,1 mm. Podpory jsou vypnuté podle níže popsané kontroly geometrie a drah. Jde o návrhové hodnoty, nikoli kalibraci konkrétní cívky. Úzká ramena západek nemají prostor pro čtyři samostatné stěny; jejich skutečné dráhy jsou zkontrolované zvlášť.

**60 °C zůstává neověřenou návrhovou volbou.** [Alzament TDS](https://dwn.alza.cz/manual/161249) uvádí desku 60–80 °C, [produkt Gray](https://www.alza.cz/alzament-tpu-95a-1-kg-gray-d13015353.htm) 30–50 °C; průnik není. Podklady a jejich původ jsou v [evidenci materiálů](../../../../docs/materialy.md#alzament-tpu-95a-gray). Projekt zachovává zděděný `temperature_vitrification = 60` i varování `bed_temperature_too_high_than_filament`, kód `1000C001`; mez profilu nebyla zvýšena za účelem umlčení varování. Tryska 225 °C leží v průniku uvedených rozsahů trysky.

Hmotnosti jsou odhady při zděděné hustotě 1,24 g/cm³, která nebyla pro Alzament změřena. Čas sliceru není závazná délka skutečného tisku.

## Provedené kontroly

- Všech 5 STL je uzavřených, konzistentně orientovaných, s jedinou souvislou sítí a bez degenerovaných či zdvojených trojúhelníků. Místní minimum XYZ je nula, měřítko 1:1, bez otočení; rovná spodní plocha leží na Z=0. Rozměry jsou načtené z aktuálního CAD auditu. Tolerance síťové aproximace proti CAD je 0,001 mm.
- Skutečný místní profil Kobra X 0,4 mm potvrzuje desku 260 × 260 mm. Hlavní díly mají 20 mm mezi obálkami; nejmenší okrajová rezerva geometrie je 25,833 mm. Test má mezi díly 20 mm. Skutečné dráhy včetně poloviny šířky čáry a lemu jsou uvnitř desky; hlavní podložka má mezní X 21,141–238,859 mm, Y 75,308–184,692 mm. Mezi obálkami sousedních lemů zůstává 10,616 mm.
- Obě podložky mají **40 skutečně extrudovaných vrstev Z=0,2 až 8,0 mm**, každý díl v každé vrstvě. Z=8,4 mm je pouze přejezdový zdvih. G-code používá absolutní XYZ (`G90`) a relativní E (`M83`), bez `G92`. Skutečné extruzní rychlosti splňují 20/40 mm/s.
- G-code vložený uvnitř 3MF se bajtově shoduje s uloženým `plate_1.gcode`. Geometrie řezaného projektu má stejné vrcholy a trojúhelníky jako původní STL: maximální odchylka při serializaci je pod 0,000005 mm. Slicer neprovedl opravy sítí.
- U všech 40 průřezů každého dílu bylo ověřeno, že každý vyšší ostrůvek navazuje na materiál předchozí vrstvy. Horní oblý profil někdy dělí průřez na dvě podepřené oblasti. Žádná nově začínající nepodepřená oblast ani přesah nad obálku předchozí vrstvy zvětšenou o **0,11 mm** nebyly nalezeny. Obě větve rybiny rostou nominálně o 0,1 mm na vrstvu 0,2 mm. To je geometrický důvod pro vypnuté podpory; stále nejde o fyzický test TPU.
- V každé relevantní vrstvě Z=0,2–3,0 mm jsou skutečné extruzní dráhy obou ramen západek. Oblasti female jsou posouzené jako dutiny s okolními stěnami, audit nevyžaduje tisk do prázdného prostoru. [Detail TEST západek](experimentalni-TEST-slice/nahled-drah-zapadek.png) ukazuje průřez STL a skutečné dráhy v Z=0,2 / 1,2 / 2,8 mm.
- Oba celé projekty byly znovu načtené nativním Anycubic Slicer Next 2.0.0.5 v izolovaném dočasném datovém adresáři, bez externího přepsání profilů a bez nového řezání. Aktivní TPU, 225/60 °C, Kobra X 0,4 mm, proces i všechny trojúhelníky a umístění zůstaly zachované. Původní 3MF zůstaly bajtově nezměněné. Toto je nativní CLI kontrola, nikoli snímek GUI.

Výpočet průtoku z krátkých zaokrouhlených G-code úseků dává syrové maximum 3,2725 mm³/s (main) a 3,2283 (test). Audit tyto hodnoty neskrývá: zápis XY na 0,001 mm a E na 0,00001 mm má u velmi krátkých úseků velkou relativní chybu. Dolní mez po započtení zaokrouhlení nepřekročila 3,2 mm³/s; nastavený limit zůstává 3,2. Úplná evidence je v auditech G-code.

CLI při prvním importu geometrie hlásí také `calc_exclude_triangles:Unable to create exclude triangles` pro prázdnou oblast výluky desky; skončilo s kódem 0 a skutečné obálky drah jsou nezávisle ověřené. Do složky nebyly kopírovány soukromé profily, cloudové logy, tokeny ani runtime.

## Výsledky a reprodukce

| Evidence | Hlavní podložka | TEST |
|---|---|---|
| Geometrie a rozmístění | [JSON](kontrola-podlozky.json) | [JSON](kontrola-podlozky-TEST.json) |
| Skutečný G-code a nastavení | [JSON](experimentalni-slice/kontrola-gcode.json) | [JSON](experimentalni-TEST-slice/kontrola-gcode.json) |
| Průřezy a západky | [JSON](experimentalni-slice/kontrola-zacvaknuti.json) | [JSON](experimentalni-TEST-slice/kontrola-zacvaknuti.json) |
| Nativní otevření celého projektu | [JSON](experimentalni-slice/kontrola-nativniho-importu.json) | [JSON](experimentalni-TEST-slice/kontrola-nativniho-importu.json) |
| Náhled skutečných vrstev 1/20/40 | [PNG](experimentalni-slice/nahled-skutecnych-vrstev.png) | [PNG](experimentalni-TEST-slice/nahled-skutecnych-vrstev.png) |

[Závěrečná kontrola hashů](kontrola-finalniho-stavu.json) zachovává původní hash CAD reportu v době generace a samostatně uvádí hash po následném GUI ověření rodičovským agentem. STL zůstaly stejné; toto doplnění nevyvolalo další řezání.

Po změně CAD/STL spustit v pořadí `vytvor_podlozku.py`, `priprav_experimentalni_slice.py`, `zkontroluj_slice.py`, `over_native_import.py`; zopakovat se `--sample` pro samostatný pár. `schema_modelu.py` načítá rozměry i oblasti kontroly z `../kontrola-modelu.json`. Audit drah potřebuje Python s Matplotlib a Shapely; ostatní skripty používají standardní Python. Generátory zapisují pouze sem. Řezání vyžaduje místně instalovaný Anycubic Slicer Next a jeho přesné systémové profily Kobra X.

Výška těla je 8 mm. Lepicí lože a montážní geometrie nejsou součástí tiskových 3MF; jejich aktuální návrh určuje [README revize](../README.md). Tyto soubory nepotvrzují výslednou instalační výšku, pevnost zacvaknutí, odolnost vůči vodě ani těsnost slepené sestavy.
