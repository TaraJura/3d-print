# Kobra X — zdobené pouzdro na nůž, revize 05

**Návrhový tiskový prototyp. Skutečný fit nože, přilnavost vysokého dílu, pevnost a kotvy ve stěně nejsou fyzicky ověřeny.**

Projekt otevřít jednou jako celek. Obsahuje jediný fyzický kus; nepřerovnávat ani nenásobit.

| Podložka | Projekt | Kusy | Čas sliceru | Materiál sliceru |
|---|---|---:|---|---:|
| 01 | [podlozka-01-kobra-x-pla-projekt.3mf](podlozka-01-kobra-x-pla-projekt.3mf) | 1 | 10h 26m 37s | 160.35 g |

Díl stojí svisle ústím nahoru uprostřed podložky, jako po montáži. Přesné rozměry a orientace jsou v [manifestu](manifest.json) a [CAD manifestu](../print-manifest.json).

## Proces a materiál

Kobra X 0,4 mm; vrstva 0,20 mm; 4 stěny; 15 % gyroid; 5 horních a dolních vrstev; šev vzadu na straně stěny. Vnější stěny 40, vnitřní 70, první vrstva 25 mm/s. Vnější brim 8 mm.

Návrhový nekalibrovaný červený PLA odvozený z profilu Anycubic PLA @Kobra X 0.4: první vrstva 215 °C, další 205 °C, podložka 50 °C (při 60 °C slicer hlásí, že je to pro profil příliš), max. průtok 8 mm³/s. Červená je jen barva v projektu. [Sklad](../../../../docs/materialy.md) eviduje Elegoo PLA Red 14.0007.203, ale zavedení do tiskárny, vstup ani kalibrace nejsou potvrzené. Při odeslání je nutné vybrat skutečnou cívku.

Podpory jsou vypnuté, dutina je shora otevřená. Dolní plochy mají 45°, jen čtyři přechody dolních křídel límce lokálně až cca 49,2° podle STL (asi 31 mm² nad 45,5°); slicer tam nevytvořil žádnou převisovou stěnu a řez je bez nových ostrovů. V G-code je 0 segmentů podpor.

## Kontrola tohoto řezu

| Kontrola | Výsledek |
|---|---|
| Vrstvy | 1240, nejvyšší extruze Z 248 mm |
| Nové nepřipojené ostrovy | 0 |
| Dráha čepele od dna po ústí | 0 tahů přes obdélník 45 × 3 mm v 1090 vrstvách; nejmenší odstup středu tahu 0.910 mm |
| Uzavřený konec | Poslední tahy pod čepelí v Z 16 mm |
| Montážní otvory | 0, 0 tahů uvnitř vepsané kružnice Ø5.5 mm |
| Brim | 1677 tahů, Z 0.2–0.2 mm; přesah přes obrys první vrstvy 7.53–7.54 mm |
| Most | 137 tahů, Z 1.2–245 mm |
| Převisové stěny | 0 tahů |
| Vnitřní most výplně | 647 tahů, Z 15.2–233.2 mm |
| Největší průtok, úseky od 0,1 mm | 8.045 mm³/s |
| Rezerva extruzí od okraje podložky | 83.81 mm; přesah false |
| Opravy sítě | 0 |

Uložená varování sliceru: not_support_traditional_timelapse. CLI hlášky: calc_exclude_triangles:Unable to create exclude triangles.

[Očíslovaný náhled](podlozka-01.png), [skutečné dráhy](podlozka-01-vrstvy.png), [detail dílu](detail-01-01_pouzdro-zdobene_01-drahy.png), [záznam vizuální kontroly](kontrola-drah-vizualne.md), [protokol](kontrola-rezani.json). `podlozka-01-geometrie.3mf` je alternativa bez procesu; nepřidává díl.

Graf ostrovů ověřuje návaznost drah, nikoli pořadí uvnitř vrstvy ani kvalitu převisů. Tisk, odstranění brimu, přesný fit nože a pevnost nejsou ověřené. Tiskárna nebyla ovládána.

Regenerace: po finálním exportu CAD spustit `python3 ../build_print_projects.py`. Přepíše jen vlastní soubory v této složce.
