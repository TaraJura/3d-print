# Kontrola drah — zdobené pouzdro V05, 3. 11. 2026

Kontrola vychází z G-code uloženého ve finálním projektu [podlozka-01-kobra-x-pla-projekt.3mf](podlozka-01-kobra-x-pla-projekt.3mf). SHA-256 projektu, G-code a STL jsou v [kontrola-rezani.json](kontrola-rezani.json). Tiskárna nebyla ovládána.

## Co bylo prohlédnuto

- [Očíslovaný náhled](podlozka-01.png): 1 kus uprostřed podložky, deska k zadní straně tiskárny, reliéf dopředu.
- [Skutečné vrstvy](podlozka-01-vrstvy.png) a [detail dílu](detail-01-01_pouzdro-zdobene_01-drahy.png):
  - **Z 0,2:** patka desky, blok žebra a koncovka, kolem nich souvislý brim. Přesah přes obrys je 7,5 mm na každou stranu, nastavených 8 mm se měří od kompenzovaného obrysu.
  - **Z 6–10:** spodní montážní otvor odděluje kousek desky; roste od podložky a nad otvorem se znovu spojí.
  - **Z 16:** poslední plná vrstva dna. **Z 16,4:** dutina otevřená.
  - **Z 24–204:** tělo, žebro a zadní lišta. Reliéf je vidět v obrysu.
  - **Z 222–233,8:** náběh se rozšiřuje k ústí.
  - **Z 234,2–248:** nad ústím zůstává jen zadní deska a dvě ouška, horní otvor je v pravém.

## Automatické výsledky tohoto řezu

| Kontrola | Výsledek |
|---|---|
| Vrstvy | 1240, všechny s extruzí, nejvyšší Z 248 mm |
| Nové nepřipojené ostrovy | 0 |
| Segmenty podpor | 0, podpory jsou v projektu vypnuté |
| Dráha čepele, Z nad dnem až po ústí | 0 tahů přes obdélník 45 × 3 mm v 1090 vrstvách; střed tahu nejméně 0,91 mm od obdélníku |
| Odstup od obdélníku dutiny | střed tahu nejméně 0,21 mm, tedy polovina šířky tahu |
| Uzavřený konec | Poslední tahy pod čepelí v Z 16,0 mm |
| Montážní otvory | 0 tahů uvnitř vepsané kružnice Ø5,5 mm v obou otvorech, po 27 vrstvách |
| `Bridge` | 137 tahů, jen na třech místech, viz níže |
| `Overhang wall` | 0 tahů |
| `Internal Bridge` | 647 tahů, Z 15,2–233,2 mm, role sliceru pro vnitřní výplň |
| Největší průtok, úseky od 0,1 mm | 8,045 mm³/s při návrhovém limitu 8; kontrola připouští 0,12 kvůli zaokrouhlení G-code |
| Podložka | Slicer nehlásí přesah; rezerva extruzí a brimu od okraje 83,8 mm |
| Opravy sítě | 0 |
| Odhad sliceru | 160,35 g / 10 h 26 min 37 s |

## Kde jsou mosty

- **Z 1,2 mm, 131 tahů do 3,2 mm:** mezi spodním blokem žebra a sražením zadní desky je u podložky úzká drážka, široká nejvýše 1,1 mm. V této vrstvě se uzavírá. První vrstvy tu proto mají desku a blok vedle sebe, spojené jsou od Z 1,2.
- **Z 11,0 a 245,0 mm, po 3 tazích do 4,65 mm:** vrchol obou montážních otvorů nad 45° střechou. Délka zahrnuje i část na materiálu, není to měření volné mezery.

## Převisy a podpory

Podpory jsou vypnuté a 0 segmentů při vypnutých podporách samo nic nedokazuje. Rozhodnutí proto stojí na geometrii: dutina je shora otevřená a dolní plochy mají 45°. Výjimkou jsou čtyři přechody dolních křídel límce, kde je lokálně až cca 49,2° podle STL, nad 45,5° asi 31 mm². Řez je tam bez nových ostrovů a slicer tam nevytvořil převisovou stěnu. Kvalitu těchto míst ukáže až tisk.

## Omezení

- Slicer hlásí `not_support_traditional_timelapse` a CLI vypisuje `calc_exclude_triangles:Unable to create exclude triangles`. Řez proto není označený jako bezvarovný.
- Díl je vysoký 248 mm na patce 78 × 31,6 mm, poměr výšky k hloubce 7,8 : 1, a tiskárna má pohyblivou podložku. Těžiště leží nad půdorysem a statická rezerva proti překlopení bez brimu je asi 7°. To nedokazuje, že se díl při tisku neuvolní nebo nerozkmitá.
- Graf návaznosti neprokazuje přilnavost, kvalitu mostů a převisů ani pevnost. Otevření projektu v GUI sliceru nebylo zkoušeno a opětovné načtení tohoto projektu v CLI neproběhlo.
- Dráha čepele v G-code počítá se středy tahů a nominální šířkou. Skutečný fit závisí na tisku; švy jsou nastavené na zadní stranu, tedy i na zadní stěnu dutiny.
