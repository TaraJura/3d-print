# Otevřený V držák nože — aktuální revize 02

Jiří 30. 10. 2026 odmítl uzavřené pouzdro jako zbytečně velké. Nové zadání: **dva body uchycení ke stěně, jednoduché otevřené V, položit nůž ostřím dolů a ihned jej vzít jedním pohybem**. Tato revize nahrazuje původní čtyřdílné pouzdro.

Výsledkem je **jeden tištěný díl**, dlouhý 230 mm, se souvislým V žlabem, zaobleným dnem a dvěma montážními oušky. Nemá kryt, západky ani další vyjímatelné díly. [Vizualizace](prehled-navrhu.png) ukazuje skutečnou CAD geometrii; [pohled na profil](nahled-profil.png) ukazuje rozevření V.

## Rozměry a původ

| Údaj | mm | Původ |
|---|---:|---|
| Délka nože | 340 | Zadání Jiřího |
| Výška nože | 45 | Zadání Jiřího |
| Max. šířka rukojeti | 25 | Zadání Jiřího |
| Délka držáku | 230 | Návrh — jeden díl pro Kobra X |
| Celková výška / hloubka od stěny | 55 / 45,24 | CAD |
| Světlé rozevření V nahoře | 34 | Návrh |
| Úhel V / kolmá tloušťka stěn | 90° / 3 | Návrh |
| Zaoblení vnitřního dna | R2 | Návrh |
| Skutečná hloubka V po zaoblení | 16,17 | CAD |
| Otvory / jejich rozteč | 2× Ø5,5 / 160 | Návrh; skutečné vruty neznámé |
| Montážní ouška | 24 × 55 × 4 | Návrh, zaoblený horní konec |

Při geometrickém vystředění má 340mm referenční nůž přesah přibližně 55 mm na obou koncích. **To neurčuje těžiště. Špička ani přečnívající ostří nejsou kryté.** Přesný obrys, délka čepele/rukojeti zvlášť, tloušťka čepele, hmotnost, těžiště, materiál stěny a skutečné vruty nejsou zadány.

Ilustrační nůž v náhledech má celkovou obálku 340 × 45 mm a rukojeť širokou 25 mm. Jeho rozdělení na čepel a rukojeť, 2mm čepel a ostatní tvary jsou pouze reference. **Nejde o model skutečného Jiřího nože ani ověření jeho stability.** Zelená barva je návrhová; skutečnou cívku nepotvrzuje.

## Montáž a použití

Připevnit vodorovně dvěma vhodnými vruty podle skutečné stěny. Osy otvorů jsou X35 a X195 mm od levého konce, Y43 mm od spodku dílu. Montážní plocha oušek přiléhá ke stěně; žebra přenášejí zatížení žlabu do oušek. Návrhové hlavy Ø10 × 3 mm a přímý přístup nástroje Ø10 mm byly digitálně zkontrolovány při vyjmutém noži.

Nůž položit shora ostřím dolů, vyjmout přímo nahoru za rukojeť. Vhodnou podélnou polohu ověřit na skutečném noži tak, aby se nepřeklápěl, neklouzal a dal se bezpečně uchopit. Otevřený žlab nemá koncové dorazy. Zaoblené plastové dno může být v kontaktu s ostřím; otřepy, vhodnost kontaktu a opotřebení je nutné posoudit na fyzickém výtisku.

## Model a tisk

- [drzak.FCStd](drzak.FCStd): jeden finální objekt `Holder`, plně omezené nativní skici, tabulka `Parameters`, výrazy a standardní booleany. Bez vlastního Python proxy.
- [drzak.FCMacro](drzak.FCMacro): zdroj, export STL a parametrické/geometrické kontroly.
- [stl/drzak-v.stl](stl/drzak-v.stl): 1 kus, již v tiskové orientaci.
- [rozlozeni/README.md](rozlozeni/README.md): jedna nastavená podložka Kobra X 0,4 mm a kontrola skutečných drah.
- [kontrola-modelu.json](kontrola-modelu.json), [audit-montaze.json](audit-montaze.json): výsledky digitálních kontrol.
- [nahled.FCMacro](nahled.FCMacro) a [sestavit-nahled.py](sestavit-nahled.py): skutečné CAD náhledy a jejich popisky.

Tiskne se spodní plochou souvislé patky, žeber a oušek na podložce; dlouhá osa leží v podložce. Stěny V rostou přibližně pod 45°. Návrhová orientace nevyžaduje podpory; vrcholy otvorů Ø5,5 mm tvoří krátké mosty, jejich skutečné dráhy jsou součástí kontroly sliceru. Brim zlepšuje přilnavost a nenahrazuje podpory. Otevřít nastavenou 3MF **jednou jako celý projekt**, nic nenásobit ani nepřerovnávat.

## Co bylo ověřeno

Platnost jednoho tělesa, jeden solid, uzavřená jednokomponentová STL, rozměry a přepočet nativních vazeb. Parametrický test změnil délku na 240 mm, rozevření na 36 mm a R2 na R2,2 a obnovil finální hodnoty. Kontrola vyjmutí používá samostatné obdélníkové řezy tloušťky 1 / 2 / 3 / 4 / 6 / 10 / 25 mm v odpovídajících výškách V a jejich volný zdvih o 40 mm.

Nezávislý montážní audit prošel **27/27 kontrolami** a je navázaný na finální SHA-256 FCStd. Nastavená 3MF podložka obsahuje 1 kus, 275 vrstev a skutečně 0 segmentů podpor. Odhad sliceru je **61,52 g / 3 h 22 min 2 s**; kontrola první vrstvy a návaznosti všech vrstev prošla. Mosty vrcholů obou otvorů jsou podrobně zachycené ve [vizuální kontrole drah](rozlozeni/kontrola-drah-vizualne.md). Zůstávají dokumentované hlášky sliceru o timelapse a vytvoření exclude triangles, proto se řez neoznačuje za bezvarovný.

Tyto řezy **neprokazují usazení celého neznámého tuhého nože**: čepel a rukojeť mohou při současném kontaktu změnit náklon a stabilitu. Nůž v náhledu je pouze bezkolizní ilustrační příklad. Fyzický tisk, přilnavost, rozměrový fit, pevnost, kotvy, stabilita a opotřebení ostří nejsou ověřeny. Tiskárna nebyla ovládána.

## Regenerace

Makro zapisuje pouze vedle sebe a přepisuje svoje FCStd, STL a JSON. Před spuštěním uložit a zavřít otevřený stejnojmenný dokument. Změny tabulky FCStd sladit s hodnotami v makru, jinak regenerace obnoví původní hodnoty. Použít skutečný FreeCAD 1.1.3:

```bash
/home/novakj/.cache/freecad-shelf-1.1.3/runtime/AppRun freecadcmd \
  -u /home/novakj/.cache/freecad-shelf-1.1.3/task-user.cfg \
  -s /home/novakj/.cache/freecad-shelf-1.1.3/task-system.cfg \
  /home/novakj/3d-print/models/drzak-noze-na-stenu/revize-02-otevrene-v/drzak.FCMacro
```

Po změně geometrie obnovit audit, náhledy a řez. GUI render lze spustit izolovaně přes `LIBGL_ALWAYS_SOFTWARE=1 LP_NUM_THREADS=2 xvfb-run -a …/runtime/AppRun …/nahled.FCMacro`; následně `python3 sestavit-nahled.py` a `python3 build_print_projects.py`. Uložená viditelnost ukazuje jen finální držák, referenční nůž a vruty jsou skryté.
