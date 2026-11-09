# Kobra X — tvarovaný držák nože, revize 03

**Návrhový tiskový prototyp. Skutečný fit nože, stabilita uložení, pevnost a kotvy ve stěně nejsou fyzicky ověřeny.**

Každou podložku otevřít jako celý projekt právě jednou. Obsahuje všechny fyzické kopie; nepřerovnávat ani nenásobit.

| Podložka | Projekt | Kusy | Čas sliceru | Materiál sliceru |
|---|---|---:|---|---:|
| 01 | [podlozka-01-kobra-x-pla-projekt.3mf](podlozka-01-kobra-x-pla-projekt.3mf) | 1 | 3h 20m 50s | 54.32 g |

Celkový počet tištěných dílů: **1**. Přesný seznam, orientace a digitální rozměry dílů jsou v [manifestu](manifest.json) a [CAD manifestu](../print-manifest.json).

## Proces a podpory

Kobra X 0,4 mm; vrstva 0,20 mm; 4 stěny; 15 % gyroid; 5 horních/dolních vrstev. Vnější stěny 40, vnitřní 70, první vrstva 25 mm/s. Návrhový nekalibrovaný PLA Basic: první vrstva 215 °C, další 205 °C; texturovaná podložka 50 °C; maximální průtok 8 mm³/s. Vnější brim 3 mm, čisticí věž vypnutá. Barva je pouze vizualizace, nepotvrzuje skutečnou cívku.

Podložka 01: podpory vypnuté; tisková orientace z CAD exportu se spodní patkou dolů. Skutečně v G-code: 0 segmentů podpor.

- 01_drzak-tvarovany_01: Souvislá patka a svislé stojiny pod oběma sedly. StěnyV rostou45°;10mm přechod je shora otevřený. Ověřit návaznost tvarovaných sedel a vrcholy otvorůØ5,5mm.

Brim je pro přilnavost a nenahrazuje podporu převisů. Montážní otvory a dosedací plochy před montáží zbavit brimu a otřepů.

## Digitální kontrola

Ověřeny jednotky, měřítko, orientace, počty, rozměry a skutečné vrcholy geometrie po importu i řezu; počet oprav sítě 0. Všechny objekty mají dráhy v první vrstvě a všechny vrstvy obsahují extruzi. Ověřena obálka extruzí na podložce, G-code teploty, maximální průtok a graf nových ostrovů podle skutečných šířek extruze. Graf ověřuje návaznost komponent, nikoli pořadí uvnitř vrstvy ani úplnou fyzickou podporu každého převisu. Podpory jsou v tomto projektu vypnuté; graf nepoužil žádnou výjimku kontaktu přes podporovou mezeru.

Podložka 01: [očíslovaný náhled](podlozka-01.png), [skutečné dráhy](podlozka-01-vrstvy.png).

Podrobné vrstvy jednotlivých dílů jsou v souborech `detail-*-drahy.png`. [Kontrolní protokol](kontrola-rezani.json). [Záznam vizuální kontroly](kontrola-drah-vizualne.md). Detaily skutečných mostků u otvorů: [otvor 01](detail-otvor-01-mostky.png), [otvor 02](detail-otvor-02-mostky.png), [datová kontrola](kontrola-mostku.json), [detail otevřeného přechodu](detail-prechod-drahy.png).

Uložená varování sliceru: not_support_traditional_timelapse. CLI hlášky: calc_exclude_triangles:Unable to create exclude triangles. Neoznačovat řez za bezvarovný, pokud CLI hlášku obsahuje.

Geometrické 3MF jsou alternativy stejných podložek bez procesu; nepřidávají díly k sestavě. Výsledky jsou pouze kontrola digitálních souborů. Tisk, odstranění případných podpor, přesný fit nože, stabilita uložení, kotvy ve stěně a pevnost nejsou fyzicky ověřeny. Tiskárna nebyla ovládána.

Regenerace: po finálním exportu CAD spustit `python3 ../build_print_projects.py` ze složky rozložení. Přepíše pouze vlastní podložky, profily, náhledy a kontrolní soubory v této složce. `--reuse-slice` znovu ověří uložené řezy proti aktuálním zdrojům a profilům; nově řeže jen chybějící nebo změněnou podložku. U nezměněného SHA G-code zachová již dokončený audit drah.
