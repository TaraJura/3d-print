# Ověření načítání připraveného rozložení v Anycubic Slicer Next

Datum: 2026-09-19. Testovaná instalace: `/usr/bin/AnycubicSlicerNext`, verze `2.0.0.5`.

Finální soubory jsou obyčejné core 3MF v milimetrech. Každá fyzická součást má vlastní resource/object a build/item. Souřadnice jsou uložené přímo ve vrcholech, tedy zachovávají rozmístění, nikoliv hromadu samostatně centrovaných STL. Žádné tiskové, materiálové ani strojové presety nejsou v těchto souborech.

## Skutečně provedený test

Oba soubory byly načteny místním Next přes CLI a znovu exportovány do izolované cache. Nebyl spuštěn slicing, vygenerován G-code ani oslovena tiskárna. Osobní konfigurace sliceru nebyla použita ani změněna. Reexporty z cache se **nedodávají uživateli**, protože CLI do nich přidává výchozí nastavení. Dodávají se původní obecné 3MF.

Reprodukce (cesty lze upravit):

```bash
DISPLAY= /usr/bin/AnycubicSlicerNext \
  --datadir /home/novakj/.cache/auticko-layout-3mf/isolated-final-profile \
  --arrange 0 --orient 0 --debug 3 \
  --export-3mf roundtrip.3mf \
  --outputdir /home/novakj/.cache/auticko-layout-3mf/final-auticko-v3-podlozka-01 \
  /home/novakj/3d-print/models/auticko-se-zatacenim/rozlozeni/auticko-v3-podlozka-01.3mf
```

Pro druhou desku se v cestách změní `01` na `02`.

- Deska 1: **31** samostatných objektů, **102 484** trojúhelníků. Všechny názvy a počty vrcholů zachovány, maximum rozdílu každého světového vrcholu je **0,000015715 mm** (číselná přesnost float32).
- Deska 2: **2** samostatné objekty, **7 952** trojúhelníků. Všechny názvy a počty vrcholů zachovány, maximum rozdílu světových vrcholů je **0,000007679 mm**.
- Ve všech 33 objektech zůstaly přesně stejné indexy všech trojúhelníků, včetně pořadí a orientace. Všechny stojí na Z=0.
- Ověřena geometrie/import/export. Nebylo otevřeno ani vizuálně zkontrolováno živé uživatelovo okno.
- CLI při tomto testu nepoužívá reálný tiskový profil; test prokazuje bezeztrátový geometrický import. Rozměry podložky a mezery ověřuje samostatný geometrický audit finálního rozložení.

Strojová evidence v projektu: [souhrn](overeni-importu.json) a [topologie](overeni-topologie-importu.json). Podrobné dočasné audity a CLI logy zůstávají v místní cache `/home/novakj/.cache/auticko-layout-3mf/`; nejsou součástí tiskových souborů.

## Načtení v GUI

V novém/prázdném projektu se zvolenou tiskárnou **Anycubic Kobra X 0,4 mm** a uživatelovým filamentem načíst **jednu** připravenou 3MF. Pokud slicer nabídne dialog, zvolit **Import geometry only**. Na jednu desku nenačítat obě 3MF naráz. Znovu nepouštět Arrange ani Auto orient: rozmístění a tiskové orientace jsou již uložené. Při práci ve stávajícím projektu jej nejprve uložit jako vlastní kopii; neodstraňovat ho bez zálohy.

Oficiální zdrojový kód potvrzuje, že generic 3MF může při importu posunout celou skupinu na střed podložky; nezarovnává jednotlivé objekty zvlášť. Finální souhrnný bounding box obou souborů je již vystředěn v (130, 130), tedy na ploše 260×260. Není nutný žádný přesun ani doplňování kopií.

Zdroj: `https://github.com/ANYCUBIC-3D/AnycubicSlicerNext`, revize `6103ed8b511609658d00d0538cc7f0609cdb57da`:

- `src/slic3r/GUI/Plater.cpp`: ř. 4386 vynechá individuální centrování pro 3MF, 4413–4415 volá pouze centrování celé skupiny; 11162–11194 explicitní cesta Import geometry only → LoadStrategy::LoadModel.
- `src/libslic3r/Model.cpp`: ř. 686–706 `center_instances_around_point` přičte všem instancím stejný XY posun.
- `src/libslic3r/Format/bbs_3mf.cpp`: ř. 3382 čte název objektu z atributu `name`.

Tento zdrojový commit je samostatné doložení chování; není tvrzeno, že přesně odpovídá lokálnímu buildu. Lokální build je samostatně doložen reálným roundtripem výše.
