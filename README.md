# 3D tisk

Osobní projekt Jiřího Nováka: parametrické modely, nastavení a zkušenosti s 3D tiskem. Znalosti i nové modely patří sem, aby šlo v další úloze pokračovat bez opakovaného vysvětlování. Nejde o firemní TechTools projekt ani o TechTools Brain.

Jiří popíše požadovaný díl nebo změnu běžným jazykem. Agent připraví model programově ve FreeCADu a Jiří si výsledek prohlédne.

## Kde začít

- [AGENTS.md](AGENTS.md) — pravidla pro další práci agentů.
- [Tiskárna](docs/tiskarna.md) — Anycubic Kobra X, ověřené údaje a neznámé.
- [Software](docs/software.md) — FreeCAD, Anycubic Slicer Next a spuštění makra.
- [Materiály a profily](docs/materialy.md) — Alzament PLA Basic, defaulty a startovací doporučení.
- [Postup práce](docs/workflow.md) — od zadání přes model a slicer k vyhodnocení tisku.
- [Deník tisků](docs/denik-tisku.md) — skutečně hlášený průběh a výsledky.
- [Modely](models/README.md) — přehled všech dílů a jejich zdrojů.

## Aktuální stav k 19. 9. 2026

Tiskárna je **Anycubic Kobra X s tryskou 0,4 mm**. K dispozici je bílý a černý **Alzament PLA Basic 1,75 mm**. Uživatel potvrdil spuštění FreeCADu a Anycubic Slicer Next na Ubuntu 26.04.1 LTS.

První model je [polička na zárubeň 90 × 50 mm](models/policka-na-zaruben/README.md). Její geometrie byla ověřena a uživatel model otevřel i importoval do sliceru. Uživatel oznámil zahájení prvního tisku; **fyzický výsledek ani první vrstva zatím nejsou potvrzené**. U zkontrolovaného lokálního G-code není jednoznačně doloženo, že jde právě o úlohu běžící na tiskárně. Podrobnosti jsou v [deníku](docs/denik-tisku.md).

Další model je [jednoduché autíčko s jedním motorem](models/jednoduche-auticko/README.md): čtyři kola, společná zadní náprava a ozubený převod. První FCStd a jednotlivé STL jsou vytvořené a geometricky zkontrolované. **Uživatel na dalším vytištěném vzorku potvrdil nasazení do otvoru označeného 2,2 mm. [Pastorek](models/jednoduche-auticko/stl/pastorek.stl), sestava a zdroj jsou podle toho upravené.** Další krok je tisk pastorku a ostatních dílů; fyzická montáž a jízda ještě ověřené nejsou.

## Jak zapisovat poznatky

U nového údaje uvést původ: zadání uživatele, fyzické měření, údaj výrobce, kontrola souboru, návrhová hodnota nebo doporučení. Zadané rozměry nejsou automaticky měřením skutečného předmětu. Doporučení není potvrzené nastavení a kontrola modelu není důkaz úspěšného výtisku.

Nové parametry, změny modelů a relevantní zkušenosti zapisovat do příslušné dokumentace a složky modelu. Po tisku doplnit deník podle skutečného výsledku. **Vytvoření STL, úspěšné řezání ani odeslání úlohy nestačí k označení tisku za úspěšný.**

## Projekt a Git

Aktuální místní checkout je `/home/novakj/3d-print`; osobní repozitář je [TaraJura/3d-print](https://github.com/TaraJura/3d-print). Git příkazy spouštět v tomto checkoutu: domovský adresář `/home/novakj` má vlastní, odlišný repozitář. Zdejší obsah se přípravou dokumentace automaticky necommituje ani nepublikuje.

Malé záměrné soubory FCStd, STL a PNG patří k modelu a jsou verzovatelné. Instalátory, runtime, přístupové údaje, cache a automatické zálohy do projektu nepatří. Původní kopie poličky v `Documents/3D-models` zůstala zachovaná kvůli otevřeným souborům; další práci ukládat sem.
