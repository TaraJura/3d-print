# Audit předání přepážky po neúspěšném tisku

22. 9. 2026. Rozsah: názvy balíků, jejich popisy, návody a historie artefaktů. Výchozí hlášení předané zadavatelem auditu: tisk trval 88 minut, zůstaly tenké proužky přibližně jedné vrstvy, hrudky a vlákna. Nejde o vlastní pozorování tiskárny. Geometrii sítí, skutečné dráhy a příčinu potíží s TPU posuzují samostatné audity.

**Předání obsahuje doložené nejasnosti, ale z těchto souborů nelze určit, co bylo skutečně otevřeno, přepočteno a odesláno tiskárně.** Není podklad pro připsání volby nesprávného souboru uživateli. Chybný popis historického 3MF je naše chyba; rozvětvení balíčku je slabina našeho předání, nikoli důkaz příčiny fyzického selhání.

## Zajištění podkladů

Čten byl zmrazený strom [evidence/model](evidence/model/) podle [manifestu původních souborů](manifest-puvodnich-souboru.json), snapshot `2026-09-22T20:35:44.315139+02:00`. Ověřeno SHA-256 všech **84 souborů**, bez neshody. Časy níže jsou zachycené `mtime`, nikoli čas otevření, přenosu či začátku tisku. Může je zachovat kopírování.

Žádné makro, FreeCAD, generátor podložky ani slicer nebyl v tomto auditu spuštěn. ZIPy 3MF byly pouze čteny. Vznikl pouze tento report mimo `evidence/`; původní soubory, profily a dokumentace nebyly měněny.

## Které balíky skutečně existují

V tabulce jsou cesty relativní ke zmrazenému modelu. `revize-02-8mm/` je aktuální revize; `revize-02-8mm/historie/reference-10mm/` je archiv. Každá varianta má dvojici se stejnou příponou `.3mf`.

| Varianta | Soubor v jejím `rozlozeni/` | Ověřený typ obsahu | Deklarované kusy / vrstvy |
|---|---|---|---|
| Aktuální celá lišta | `prepazka-B-pracovni-geometrie.3mf` | Jen model, bez profilů a G-code | 3 / žádné řezání uvnitř |
| Aktuální celá lišta | `EXPERIMENT-prepazka-B-Alzament-TPU95A.3mf` | Model, nastavení projektu a vložený G-code | 3 / 40 dle hlavičky G-code |
| Aktuální vzorek | `TEST-spoj-pracovni-geometrie.3mf` | Jen model, bez profilů a G-code | 2 / žádné řezání uvnitř |
| Aktuální vzorek | `TEST-EXPERIMENT-spoj-Alzament-TPU95A.3mf` | Model, nastavení projektu a vložený G-code | 2 / 40 dle hlavičky G-code |
| Historická celá lišta | `prepazka-B-pracovni-geometrie.3mf` | Jen model, bez profilů a G-code | 3 / žádné řezání uvnitř |
| Historická celá lišta | `EXPERIMENT-prepazka-B-Alzament-TPU95A.3mf` | Model, nastavení projektu a vložený G-code | 3 / 50 dle hlavičky G-code |

Všechny tři úplné projekty uvádějí nastavení tiskárny `Anycubic Kobra X 0.4 nozzle`, experimentální proces TPU, vrstvu 0,2 mm a trysku 225 °C. Geometry-only soubory tato nastavení neobsahují. Při jejich novém řezání závisí proces na nastavení skutečně použitém ve sliceru; tento audit nezná tehdejší stav UI.

## Konkrétní nejasnosti předání

1. **Chybná metadata historického úplného projektu.** U historického `EXPERIMENT-prepazka-B-Alzament-TPU95A.3mf` obsahuje `3D/3dmodel.model` titul „Přepážka B — pracovní geometrie, 3 díly“ a popis „Pouze geometrie 1:1. Bez tiskového procesu, filamentu a G-code.“ Přitom ZIP obsahuje `Metadata/project_settings.config` i `Metadata/plate_1.gcode`. To je skutečný rozpor obsahu a popisu. Aktuální úplné projekty už mají správný popis místně řezaného experimentu. Není doloženo, zda slicer tento popis uživateli ukázal.

2. **Stará geometrie zůstala také přímo v kořeni modelu.** [Kořenové README](evidence/model/README.md), řádek 3, správně přesměrovává na revizi 02. Pod ním ale zůstává celé staré předání: přímé STL odkazy na řádcích 29–31, FCStd/makra na 51–53, 10mm kontrola na 62–67 a staré náhledy. Stejné základní názvy `prepazka-B.FCStd`, `dil-1.stl` atd. existují i v aktuální revizi. Přímý starší odkaz či výběr souboru bez přečtení horního upozornění vede stále k 10mm variantě. Záměna 8 a 10 mm sama nevysvětluje jednovrstvý výsledek.

3. **Čtyři aktuální 3MF jsou nabídnuty téměř rovnocenně.** [Návod podložek](evidence/model/revize-02-8mm/rozlozeni/README.md), řádky 7–10, uvádí jako první celou lištu a ve sloupcích nejprve geometry-only, potom úplný projekt. Pokyn nejprve provést samostatný test přichází až na řádku 63. Názvy rozlišují test a experiment, ale neobsahují číslo revize; dvě historické varianty mají dokonce stejné základní názvy jako aktuální. Balíček nevede jedním výrazným vstupem k jedinému konkrétnímu prvnímu testu.

4. **Pokyn otevřít celý projekt existuje, praktická volba importu není doložená.** Řádek 32 návodu podložek výslovně říká otevřít celý projekt bez automatického uspořádání a otáčení. Řádek 16 správně odlišuje geometry-only. Chybí však konkrétní postup pro případ volby „projekt“ versus „pouze geometrie“ a kontrola viditelných údajů po otevření. Náhledy vrstev byly podle řádku 53 vytvořené z G-code, nikoli z GUI sliceru. Není tedy doložené znovuotevření předávaného balíku v uživatelském importním toku se zachovaným procesem.

5. **Připravené soubory a nevyřešený tiskový stav jsou v jednom předání.** Návod uvádí „připravené dvě podložky“ a nabízí hlavní projekt s G-code; současně na řádcích 40 a 63 přiznává nevyřešenou teplotu desky, nekalibrovaný materiál a potřebu zkoušky. Omezení nejsou skrytá, ale přímé odkazy a rozsáhlé geometrické kontroly mohou působit jako dokončené předání k tisku. Jednoznačný stav prvního tiskového kroku měl být před odkazy. Z tohoto rozporu nelze vyvodit konkrétní fyzikální příčinu hrudek či vláken.

Opačná evidence je důležitá: v hlavních třech zmrazených README nebyl nalezen neexistující modelový odkaz; rozlišení experimentu, historie a geometry-only je textově přítomné. Aktuální živý `models/README.md:7` při auditu odkazuje přímo na revizi 02. Tento index však není součástí zmrazených 84 souborů, takže jeho stav v okamžiku tisku nelze tímto snapshotem dokázat.

## Časy souborů a údaj 88 minut

Všechny časy jsou 22. 9. 2026, časové pásmo `+02:00`, podle snapshot manifestu.

| `mtime` | Zachycený artefakt |
|---|---|
| 19:07:56 | Historický 10mm geometry-only 3MF |
| 19:09:37–38 | Historický 10mm G-code a úplný experimentální 3MF |
| 19:17:16 | Aktuální 8mm geometry-only 3MF |
| 19:17:21 | Aktuální hlavní G-code a úplný 3MF |
| 19:18:11–12 | Oba 3MF pro vzorek a jeho G-code |
| 19:19:53 | Kořenový starý FCStd, kontrolní JSON a tři STL mají novější `mtime` |
| 19:25:36 | README aktuální revize |
| 19:27:16 | Kořenové README s přesměrováním |
| 19:29:32 / 19:30:16 | Aktuální návod podložek / dodatek o teplotním rozporu |

U kořenových souborů z 19:19:53 se FCStd a JSON liší od hashů v [původním přenosovém seznamu](evidence/transferred.json); tři STL mají stále stejné hashe jako stará archivní geometrie. [Finální přenosový seznam](evidence/final-manifest.json) tyto dva kořenové soubory výslovně eviduje jako `protected_legacy_bytes`. Samotná změna `mtime` neidentifikuje proces ani člověka a nedokládá změnu aktuálního 3MF. Aktuální soubory ve snapshotu se shodují s finálním přenosovým seznamem.

Hlavičky G-code přímo uvnitř úplných 3MF uvádějí následující **odhady**, shodné se zaokrouhlenými údaji návodů:

| Úplný projekt | Normal | Silent | Sport |
|---|---:|---:|---:|
| Historická celá lišta, 10 mm | 7 h 23 min 4 s | 13 h 59 min 39 s | 5 h 57 min 49 s |
| Aktuální celá lišta, 8 mm | 5 h 54 min 8 s | 11 h 11 min 18 s | 4 h 45 min 55 s |
| Aktuální dvoudílný vzorek | 33 min 9 s | 1 h 0 min 19 s | 27 min 40 s |

**88 minut neodpovídá žádnému z těchto uložených odhadů.** Může jít o dobu do přerušení, jinak přepočtenou úlohu, změněný režim či jiný soubor; tyto možnosti nejsou potvrzené. Snapshot z 20:35:44 není čas dokončení tisku, proto od něj nelze odečíst 88 minut a určit začátek. Ani pozdější datum návodu nedokládá, jaký text měl uživatel k dispozici při zahájení.

## Kandidát příčiny a potřebný důkaz

**Kandidát související s předáním:** otevření čisté geometrie nebo import pouze geometrie z úplného projektu mohl vést k novému řezání s jiným procesem. Nabídka několika 3MF a starých kopií tuto cestu umožňuje. Zde je to hypotéza k prověření, nikoli zjištění o postupu Jiřího. Historická/aktuální záměna je další možnost, ale obě uložené úplné lišty deklarují desítky vrstev.

Rozhodující bude konkrétní odeslaný G-code nebo uložený projekt skutečné úlohy, jeho hash, záznam tiskárny s názvem a stavem dokončeno/přerušeno a případné snímky tehdejších nastavení. Do té doby nelze 88 minut přiřadit k našemu konkrétnímu řezu ani vysvětlit fyzické vady pouze dokumentací. Další tisk ani změna profilu nejsou součástí tohoto auditu.

Po určení skutečné úlohy má opravené předání začínat jediným přesným souborem pro první zkoušku, s revizí v názvu, očekávanými rozměry/počtem vrstev/odhadem času a kontrolou zachování procesu po otevření. Geometry-only a historie mají být oddělené od tohoto hlavního vstupu. Nyní jde pouze o doporučení; důkazní soubory zůstaly zachované.
