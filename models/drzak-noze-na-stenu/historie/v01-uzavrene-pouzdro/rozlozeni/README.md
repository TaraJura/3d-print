# Kobra X — nástěnný držák nože

**Návrhový tiskový prototyp. Skutečný fit nože, manipulace s krytem, pevnost a kotvy ve stěně nejsou fyzicky ověřeny.**

Každou podložku otevřít jako celý projekt právě jednou. Obsahuje všechny fyzické kopie; nepřerovnávat ani nenásobit.

| Podložka | Projekt | Kusy | Čas sliceru | Materiál sliceru |
|---|---|---:|---|---:|
| 01 | [podlozka-01-kobra-x-pla-projekt.3mf](podlozka-01-kobra-x-pla-projekt.3mf) | 2 | 13h 2m 40s | 231.67 g |
| 02 | [podlozka-02-kobra-x-pla-projekt.3mf](podlozka-02-kobra-x-pla-projekt.3mf) | 2 | 3h 54m 39s | 65.52 g |

Celkový počet tištěných dílů: **4**. Přesný seznam, orientace a digitální rozměry dílů jsou v [manifestu](manifest.json) a [CAD manifestu](../print-manifest.json).

## Proces a podpory

Kobra X 0,4 mm; vrstva 0,20 mm; 4 stěny; 15 % gyroid; 5 horních/dolních vrstev. Vnější stěny 40, vnitřní 70, první vrstva 25 mm/s. Návrhový nekalibrovaný PLA Basic: první vrstva 215 °C, další 205 °C; texturovaná podložka 50 °C; maximální průtok 8 mm³/s. Vnější brim 3 mm, čisticí věž vypnutá. Barva je pouze vizualizace, nepotvrzuje skutečnou cívku.

Podložka 01: automatické přiléhající podpory `normal(auto) / snug`, i na modelu, práh 30°, horní/dolní mezera 0,20 mm, XY odstup 0,35 mm, dvě kontaktní vrstvy. Skutečně v G-code: 8579 segmentů podpor.

- 01_vanicka-leva_01: Záchytný lem v Z=32–35 mm a přechody stupňového spoje; podpory přístupné z otevřené vaničky.
- 02_vanicka-prava_01: Záchytný lem v Z=32–35 mm a přechody stupňového spoje; podpory přístupné z otevřené vaničky.

Podložka 02: automatické přiléhající podpory `normal(auto) / snug`, i na modelu, práh 30°, horní/dolní mezera 0,20 mm, XY odstup 0,35 mm, dvě kontaktní vrstvy. Skutečně v G-code: 628 segmentů podpor.

- 03_kryt-levy_01: Plochým pohledovým čelem dolů; všechny otvory svisle, bez podpor.
- 04_kryt-pravy_01: Spodní přesah středového spoje je 1,6 mm nad podložkou.

Brim je pro přilnavost a nenahrazuje podporu převisů. Spáry, montážní otvory a dosedací plochy před sestavením zbavit brimu a případných podpor.

## Digitální kontrola

Ověřeny jednotky, měřítko, orientace, počty, rozměry a skutečné vrcholy geometrie po importu i řezu; počet oprav sítě 0. Všechny objekty mají dráhy v první vrstvě a všechny vrstvy obsahují extruzi. Ověřena obálka extruzí na podložce, G-code teploty, maximální průtok a graf nových ostrovů podle skutečných šířek extruze. Graf ověřuje návaznost komponent, nikoli pořadí uvnitř vrstvy ani úplnou fyzickou podporu každého převisu. U samotných podpor zohledňuje nastavenou spodní mezeru 0,20 mm: může ověřit kontakt o dvě vrstvy níže (rozdíl Z nejvýše 0,40 mm); takové výjimky se samostatně zapisují.

Podložka 01: [očíslovaný náhled](podlozka-01.png), [skutečné dráhy](podlozka-01-vrstvy.png).

Podložka 02: [očíslovaný náhled](podlozka-02.png), [skutečné dráhy](podlozka-02-vrstvy.png).

Podrobné vrstvy jednotlivých dílů jsou v souborech `detail-*-drahy.png`. [Kontrolní protokol](kontrola-rezani.json). Detail kritických podpor: [lem vaničky](podpory-01-levy-lem.png), [spoj vaničky](podpory-01-pravy-spoj.png), [přesah pravého krytu](podpory-02-pravy-kryt.png), [datový protokol](kontrola-podpor-detail.json), [záznam vizuální kontroly](kontrola-drah-vizualne.md).

Uložená varování sliceru: not_support_traditional_timelapse. CLI hlášky: calc_exclude_triangles:Unable to create exclude triangles. Neoznačovat řez za bezvarovný, pokud CLI hlášku obsahuje.

Geometrické 3MF jsou alternativy stejných podložek bez procesu; nepřidávají díly k sestavě. Výsledky jsou pouze kontrola digitálních souborů. Tisk, odstranění podpor, funkce krytu, přesný fit nože, kotvy ve stěně a pevnost nejsou fyzicky ověřeny. Tiskárna nebyla ovládána.

Regenerace: po finálním exportu CAD spustit `python3 ../build_print_projects.py` ze složky rozložení. Přepíše pouze vlastní podložky, profily, náhledy a kontrolní soubory v této složce. `--reuse-slice` znovu ověří uložené řezy proti aktuálním zdrojům a profilům; nově řeže jen chybějící nebo změněnou podložku. U nezměněného SHA G-code zachová již dokončený audit drah.
