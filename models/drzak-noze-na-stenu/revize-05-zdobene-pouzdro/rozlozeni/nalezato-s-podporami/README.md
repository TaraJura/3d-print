# Kobra X — pouzdro V05 naležato s podporami

**Preferovaný tisk V05. Digitálně ověřený návrh, fyzický tisk ani odstranění podpor ověřené nejsou.**

Projekt: **[pouzdro-nalezato-kobra-x-pla-projekt.3mf](pouzdro-nalezato-kobra-x-pla-projekt.3mf)**, 1 kus. Otevřít jednou jako celek a nepřerovnávat. Pět blokátorů a tři vynucovače podpor jsou součástí téhož objektu, nejsou to další kusy.

[Přehled orientace, podpor a řezů](nahled-orientace-a-podpor.png) · [očíslovaná podložka](podlozka-01.png) · [skutečné vrstvy](podlozka-01-vrstvy.png) · [detail drah](detail-01-01_pouzdro-zdobene-nalezato_01-drahy.png) · [protokol](kontrola-nalezato.json)

## Proč tato varianta

Hlášení Jiřího, předané 3. 11. 2026 přes koordinátora:

- Ručně otočený tisk naležato bez podpor „propadal na visícím přechodu“.
- Původní svislá varianta: „na výšku to nevyšlo“. Konkrétní příčina není známá.

Který G-code se skutečně tiskl, není známé. Tyto zápisy nejsou důkaz příčiny.

## Orientace

- [STL naležato](../../stl/pouzdro-zdobene-nalezato.stl) je tuhé otočení svislého STL, otočení je v [generátoru](../../build_nalezato.py). Geometrie se nemění, odchylka vrcholů nejvýše 0,000011 mm.
- Dolů je dlouhý bok na straně spodního otvoru (X dílu = tisková výška), tisková výška 78 mm.
- Dlouhá osa je vodorovně a o 45° natočená v rovině podložky. Půdorys 197,7 × 187,5 mm se tak vejde i s plným brimem 8 mm. Rezerva všech extruzí od okraje je 26,1 mm.
- Strop dutiny přemosťuje jen krátkou osu 4,4 mm, u ústí až 8,8 mm. Díl má na podložce jen 67,2 mm² ve dvou koncích zadní desky, tělo začíná ve výšce 9,9 mm. Podpory jsou proto nosné.

## Podpory

38785 tahů podpory a 22223 tahů rozhraní, odhadem 29 g.

| Oblast | Tahy | Délka | Tisková výška |
|---|---:|---:|---|
| Kanál mezi deskou a tělem, pod žebrem a bloky | 15195 | 230,4 m | 0,2–35,8 mm |
| Pod hřebenem a za tělem | 11104 | 31,6 m | 0,2–35,8 mm |
| Pod límcem a tělem u ústí | 11383 | 27,9 m | 0,2–35,8 mm |
| Pod koncovkou a tělem u dna | 10435 | 25,8 m | 0,2–24,8 mm |
| Pod zadní deskou | 9447 | 24,3 m | 0,2–27,6 mm |
| Pod horním uchem a kolem dolního ucha | 3444 | 9,2 m | 0,2–64,8 mm |

- **V dutině a náběhu 0 tahů podpory, v otvorech 0.** Bez blokátoru dutiny by jich v dutině bylo 26734, blokátor tedy skutečně pracuje.
- **Hřeben těla:** zapnutý tisk tenkých stěn posunul první stopu ze 10,4 na 10,2 mm, vzduch nad rozhraním je tak 0,2 mm místo 0,4 mm. Na 125 rovinách délky je přímo pod stopou rozhraní s vrchem 9,8 mm na 86 z nich, jinde leží nejbližší tah rozhraní dál, protože má rozteč 0,5 mm. Plochy 45° pod tělem a límcem jsou podepřené do výšky 15,3 mm.
- **Ploché stropy:** žebro ve výšce 36 mm, bloky 17 a 25 mm, deska 26 mm a horní ucho 64 mm mají podporu s mezerou nad rozhraním převážně 0,2 mm, viz protokol. Nejvýš 4,8 mm široký pruh žebra u těla podporu záměrně nemá a překlene ho most od těla.
- **Odstranění:** 99,1 % vzorků podpor má volnou cestu k bývalé podložce. Zbytek je hlavně věž pod horním uchem na výstupku dolního ucha, z té má volný výstup podél Y 41 z 41 testovaných bodů. Věž má dolní mezeru 0 a řídkou patu na okraji desky, aby nespadla. Je přístupná zezadu i od ústí, ale patu může být nutné odstřihnout a začistit. Čisté odlomení bez stop se neslibuje.

## Tisk

Kobra X 0,4 mm, návrhový nekalibrovaný červený PLA: 0,20 mm, 4 stěny, 15 % gyroid, tryska 215/205 °C, podložka 50 °C, brim 8 mm, max. průtok 8 mm³/s. Podpory normal snug, nad rozhraním 0,2 mm, od stěn 0,4 mm. Červená je jen barva v projektu, při odeslání vybrat skutečnou cívku. Brim leží těsně u pásků modelu, bez mezery a bez kompenzace první vrstvy, aby se s nimi spojil. Odhad sliceru **186,5 g / 11h 15m 43s**.

Po tisku: odstranit brim a koberec podpor, vylomit podpory z kanálu směrem k bývalé podložce, věž pod uchem odstřihnout u paty a místo začistit. Dutinu a otvory projet až po začištění.

## Kontrola tohoto řezu

| Kontrola | Výsledek |
|---|---|
| Vrstvy, kusy | 390 vrstev, 1 kus, 1 tisknutelná součást, opravy sítě 0 |
| Objem proti svislému STL | 174542,62 a 174542,65 mm³, uzavřená jedna komponenta |
| Nové ostrovy | 0 nepodepřených |
| Dráha čepele 45 × 3 mm přes ústí | 0 tahů v 226 vrstvách, boční odstup hrany tahu nejméně 0,70 mm |
| Dutina v tisku | otevřená od výšky 15,6 do 62,6 mm, tedy 47,0 mm; od čepele 0,9 a 1,1 mm |
| Most nad dutinou | 545 tahů do 8,8 mm včetně kotvení, odchylka od krátké osy nejvýš 0,006° |
| Uzavření náběhu | 72 převisových tahů, odchylka nejvýš 0,037°, délka do 6,1 mm |
| Montážní otvory | 0, 0 tahů uvnitř kružnice Ø5,5 mm, po 28, 28 vrstvách |
| Brim | 513 mm²; dotýká se 41 % obvodu pásku u dna a 82 % u ústí, zbytek obvodu brim nemá |
| První vrstva | model 75 mm², podpory 9258 mm²; těžiště 20,4 mm uvnitř obalu s podporami, mimo samotný kontakt modelu |
| Největší průtok | 8,052 mm³/s |
| Svislé STL, FCStd a svislý projekt | bitově beze změny, hashe v protokolu |

Uložená varování sliceru: not_support_traditional_timelapse. CLI hlášky: calc_exclude_triangles:Unable to create exclude triangles.

## Omezení

- Neověřeno: tisk, přilnavost, odstranění podpor a povrch po nich, kvalita mostů a stropu náběhu, fit nože, pevnost. Vrstvy jsou teď rovnoběžně s rovinou X = konst., pevnost se proti svislému tisku liší. Slicer ani graf drah to neprokážou.
- Těžiště leží mimo kontakt modelu, díl tedy nese koberec podpor a rozhraní bez pevného spoje. Přilnavost je největší riziko.
- Věž pod horním uchem je vysoká asi 50 mm a v osách tahů 3,6 × 12,1 mm v půdorysu. Je to nejštíhlejší podpora řezu, sledovat ji od výšky asi 40 mm.
- Před tiskem změřit na noži vzdálenost od špičky k začátku širší rukojeti, jak uvádí [README revize](../../README.md).
- Projekt nebyl otevřen v GUI sliceru. Tiskárna nebyla ovládána.

Starší nesoulad, který tato varianta neřeší: `rozlozeni/podlozka-01-geometrie.3mf` má už před touto úlohou hash `e0d2d8ce…` místo hodnoty ve starém manifestu. Soubor ani `stl/pouzdro-zdobene.3mf` nebyly obnoveny ani změněny.

Regenerace: `python3 ../../build_nalezato.py`. Přepíše jen `stl/pouzdro-zdobene-nalezato.stl` a tuto složku.
