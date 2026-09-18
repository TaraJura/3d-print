# Software a modelování

Údaje zachycují instalaci a uživatelská potvrzení z 18.–19. 9. 2026. Nejsou slibem podpory jiné verze systému ani návodem instalátory znovu stahovat.

## Místní systém a slicer

- Systém: Ubuntu **26.04.1 LTS, x86_64**.
- Anycubic Slicer Next: uživatel dokončil instalaci přes `apt` a potvrdil spuštění.
- [Oficiální download](https://www.anycubic.com/slicerNextDownload) uváděl pro Linux pouze Ubuntu 24.04. Funkční spuštění na 26.04 je místní zkušenost, nikoli deklarovaná podpora výrobce.
- Použitý soubor: `AnycubicSlicerNext_linux-v2.0.0.5-20260913065625.deb`, [oficiální URL](https://cdn-universe-slicer.anycubic.com/prod/pool/main/a/anycubicslicernext/AnycubicSlicerNext_linux-v2.0.0.5-20260913065625.deb).
- Instalovaný dpkg balíček: `anycubicslicernext`, verze **2.0.06**. Verze v názvu souboru a verze balíčku se liší.
- Velikost staženého balíčku byla **153 422 098 B**; velikost a SHA256 byly ověřeny proti [oficiálnímu indexu](https://cdn-universe-slicer.anycubic.com/prod/dists/noble/main/binary-amd64/Packages). Samotný hash zde nebyl uchován; při novém stažení jej ověř znovu proti odpovídajícímu indexu.
- Program: `/usr/bin/AnycubicSlicerNext`.
- Zdroje: `/usr/share/AnycubicSlicerNext/resources/`; systémové profily: `/usr/share/AnycubicSlicerNext/resources/profiles/Anycubic/`.

Výběr všech materiálů v průvodci pouze zpřístupní profily v katalogu. Skutečný filament a správnou tiskárnu je nutné zvolit pro konkrétní úlohu. Parametry jsou v [materiálech a profilech](materialy.md).

## FreeCAD

Používá se **FreeCAD 1.1.3**, [oficiální vydání](https://github.com/FreeCAD/FreeCAD/releases/tag/1.1.3). AppImage byl při přípravě ověřen SHA256 proti vydání a uživatel potvrdil spuštění.

SHA256 použitého AppImage: `3a853eb69ee595f779f2255dbf80a765926981d8ff68903cefee4dfb03a8f5ef`.

- Aplikace: `/home/novakj/Applications/FreeCAD_1.1.3-Linux-x86_64-py311.AppImage`.
- Položka menu: `/home/novakj/.local/share/applications/org.freecad.FreeCAD.desktop`.
- Agent modeluje přes Python API/makra FreeCADu. Uživatel otevírá a prohlíží FCStd. Nativní ovládání GUI agentem nebylo v této linuxové relaci dostupné.
- Běžný systémový `python3` nemá automaticky moduly `FreeCAD`, `Part`, `Sketcher` ani `MeshPart`. Makro proto nepředstavuj jako samostatný systémový Python skript.

### Spuštění makra ve FreeCADu

Pro prohlížení nebo změnu tabulky stačí otevřít [policka-90x50.FCStd](../models/policka-na-zaruben/policka-90x50.FCStd) ve FreeCADu. Uložený model má běžné objekty a výrazy; jeho přepočet nepotřebuje znovu spouštět makro.

Při vědomé regeneraci modelu:

1. Otevři FreeCAD a ulož rozpracované změny. Regenerace vychází z hodnot v makru, nikoli ze změn již provedených v jiném otevřeném FCStd.
2. Přes otevření souboru zvol zdejší [policka.FCMacro](../models/policka-na-zaruben/policka.FCMacro). V editoru makra zkontroluj `VALUES` a výstup `OUT`.
3. Spusť otevřené makro příkazem **Makro → Spustit makro / Macro → Execute macro**. Použij makro z tohoto checkoutu, nikoli původní kopii v `Documents`.
4. Makro používá `OUT = Path(__file__).resolve().parent`: vedle sebe uloží `policka-90x50.FCStd`, `policka-90x50.stl` a `kontrola-modelu.json`. Existující soubory těchto jmen může přepsat. PNG ani textové poznámky samo neobnoví.
5. Po změně ověř geometrii a soulad exportu, obnov skutečný náhled a poznámky. Při jiných výsledných rozměrech slaď také názvy souborů a popis dokumentu; původní makro obsahuje název `90x50` napevno.

Pokud makro vybíráš v dialogu **Makro → Makra… / Macro → Macros…**, nastav adresář uživatelských maker na jeho složku v checkoutu, vyber `policka.FCMacro` a spusť jej. Nezakládej kvůli tomu druhou kopii modelu jako nový zdroj pravdy.

### Skutečně použitý postup bez hlavního GUI

Autor modelu potvrdil vytvoření geometrie přes přibalený Python 3.11 a wrapper `AppRun`, který zachovává potřebné prostředí Python/Qt. Runtime je mimo repozitář v `/home/novakj/.cache/freecad-shelf-1.1.3/runtime`; izolované konfigurace leží vedle něj. Původně byl příkaz spuštěn s makrem v `Documents/3D-models/policka-na-zaruben`.

Stejné volání s cestou do tohoto checkoutu je:

```bash
/home/novakj/.cache/freecad-shelf-1.1.3/runtime/AppRun freecadcmd \
  -u /home/novakj/.cache/freecad-shelf-1.1.3/task-user.cfg \
  -s /home/novakj/.cache/freecad-shelf-1.1.3/task-system.cfg \
  /home/novakj/3d-print/models/policka-na-zaruben/policka.FCMacro
```

**Tato varianta cesty v repozitáři zatím spuštěna nebyla.** Před použitím ověř existenci runtime a konfiguračních souborů a zvaž přepsání výstupů. Cache může být odstraněna; nejde o přenositelnou součást projektu. Trvalá alternativa je spuštění makra v nainstalovaném FreeCADu podle návodu výše. Původní runtime byl extrahován pomocí `unsquashfs` s offsetem `944632`, který platí jen pro konkrétní ověřený AppImage, nikoli obecně pro jiné verze.

### Náhled a uložená viditelnost

Při headless běhu je `App.GuiUp = false`, a proto makro přeskočí část pro GUI. Po takové regeneraci musí navázat otevření v GUI, skrytí všech geometrických pomocných objektů kromě finálního `Shelf` a uložení dokumentu. Současná kopie FCStd už tento stav má ověřený.

Původní render proběhl v izolovaném GUI pod Xvfb se stejnými `task-user.cfg` / `task-system.cfg`, `LIBGL_ALWAYS_SOFTWARE=1`, `LP_NUM_THREADS=1` a `nice -n 15 xvfb-run -a …/runtime/AppRun … render-shelf.FCMacro`. To je popis prostředí, nikoli úplný příkaz k přímému spuštění. Pomocné makro `/home/novakj/.cache/freecad-shelf-1.1.3/render-shelf.FCMacro` má výstup napevno do původní složky; před případným dalším použitím jej uprav pro aktuální checkout. Nekopíruj celý runtime do repozitáře.

Při původním snímání se pohled nastavoval 1 s po startu a snímek pořídil za dalších 1,2 s, aby doběhla animace kamery. Okamžitý snímek neodpovídal zamýšlenému pohledu. Náhled lze také uložit přímo z otevřeného FreeCAD GUI po ustálení pohledu; vždy musí zachycovat aktuální geometrii.

Historické spuštění obsahovalo také `QTWEBENGINE_DISABLE_SANDBOX=1` a `QTWEBENGINE_CHROMIUM_FLAGS=--disable-gpu`; jejich nutnost nebyla testována. Vypnutí sandboxu není požadavek geometrie ani doporučený výchozí postup.

## Poznatky z instalace a odezvy systému

- Při dvojkliku na DEB dlouho načítaly App Center/Files. Instalace lokálního DEB pomocí `sudo apt install` uspěla.
- Upozornění `Download is performed unsandboxed as root … _apt … Permission denied` se týkalo oprávnění pomocného účtu číst stažený soubor. Samo o sobě neznamenalo neúspěšnou instalaci.
- Při souběžném `apt upgrade` a mnoha oknech Chrome se zasekávala myš; byla pozorována aktivita swapu a čekání na disk. Po dokončení upgradu a zavření oken uživatel potvrdil zlepšení.
- Nebyl prokázán pád sliceru, OOM ani konkrétní chyba GPU. Tyto příčiny nelze zpětně uvádět jako zjištěný fakt.

Instalátory, AppImage, rozbalený runtime, systémové launchery a cache do repozitáře nekopírovat.
