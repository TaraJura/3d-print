# Kontrola drah — zrcadlový držák V04, 2. 11. 2026

Kontrola vychází z G-code uloženého ve finálním projektu [podlozka-01-kobra-x-pla-projekt.3mf](podlozka-01-kobra-x-pla-projekt.3mf), který byl pro V04 nově nařezán. Výsledky V03 se nepřebírají. SHA-256 projektu, G-code a STL jsou v [kontrola-rezani.json](kontrola-rezani.json) a [kontrola-mostku.json](kontrola-mostku.json). Tiskárna nebyla ovládána.

## Co bylo prohlédnuto

- [Očíslovaný náhled](podlozka-01.png): 1 fyzický kus, délka 230 mm v rovině podložky. Širší sedlo rukojeti je vlevo (X 8–83), otevřený přechod uprostřed (X 83–93), užší sedlo čepele vpravo (X 93–238). Instalovaná svislá osa Y je tisková Z. Obálka sítě je 230 × 42,314 × 59,996 mm.
- [Skutečné vrstvy](podlozka-01-vrstvy.png): první vrstva má souvislou patku, dvě žebra a dvě ouška, kolem nich je 3mm brim. Sedlo čepele začíná růst od paty a dál stoupá směrem ke špičce vpravo. Sedlo rukojeti vlevo roste výš. Nevzniká plovoucí střecha nad dutinou. Nejvyšší vrstva je Z 60,0 mm.
- [Detail přechodu](detail-prechod-drahy.png): patka spojuje obě sedla do Z 4,0 mm. Od Z 4,2 mm je X 83–93 otevřené. Automatická kontrola všech vrstev nad patkou našla **0 extruzních tahů ve vnitřních 9,4 mm** (X 83,3–92,7); okraje 0,3 mm jsou vynechané kvůli šířce obvodové extruze.
- Mostky u otvorů [01](detail-otvor-01-mostky.png) a [02](detail-otvor-02-mostky.png): v Z 50,8 mm jsou místní převisové stěny, v Z 51,0 mm uzavírají vrchol každého otvoru tři mostové tahy. Nejdelší celý tah má 5,944 mm a obsahuje i část na materiálu, není to měření volné mezery. Oba PNG jsou bitově shodné s V03: v této výšce jsou ouška samostatné souměrné ostrůvky na stejném X, takže dráhy v okně náhledu vyšly stejně. Jsou nově vygenerované z G-code V04.

## Automatické výsledky tohoto řezu

| Kontrola | Výsledek |
|---|---|
| Vrstvy | 300, všechny s extruzí, stejné výšky jako V03 |
| Nové nepřipojené ostrovy | 0 |
| Segmenty podpor | 0 (podpory jsou v projektu vypnuté) |
| Podložka | Slicer nehlásí přesah; nejmenší rezerva extruzí a brimu od okraje 5,386 mm |
| Kontakt | Objekt má dráhy v první vrstvě, brim vygenerován, opravy sítě 0 |
| Most a převisová stěna | 6 + 36 tahů, jen na ouškách v Z 50,8–51,0 mm |
| `Internal Bridge` | 485 tahů v Z 7,4–25,6 mm, role sliceru pro vnitřní výplň; V03 měla 506 |
| Největší průtok, úseky od 0,1 mm | 8,009 mm³/s při návrhovém limitu 8; kontrola připouští 0,12 kvůli zaokrouhlení G-code, V03 měla 8,022 |
| Vnější stěny proti zrcadleným drahám V03 (X → 246 − X) | do 0,0125 mm ve všech 300 vrstvách; šev a výplň se generují samostatně |
| Odhad sliceru | 54,31 g / 3 h 20 min 37 s |

## Proč zůstávají podpory vypnuté

Počet 0 segmentů při vypnutých podporách sám nic nedokazuje. Proto proběhl jeden diagnostický řez téhož procesu se zapnutými automatickými podporami, jen mimo projekt a bez předání. Slicer v něm přidal 504 tahů podpor **výhradně uvnitř obou otvorů Ø5,5 mm**, v Z 45,8–50,4 mm, nikde jinde.

Předávaný projekt nechává otvory bez podpor záměrně, stejně jako V03. Vrchol tvoří krátké mostky a podpora by jinak zůstala ve funkčním otvoru, odkud by se musela odstraňovat. Kvalita mostků je otevřený fyzický bod.

## Omezení

- Slicer hlásí `not_support_traditional_timelapse` a CLI vypisuje `calc_exclude_triangles:Unable to create exclude triangles`. Řez proto není označený jako bezvarovný.
- Předaný projekt se v CLI s izolovaným datadirem znovu načetl a nařezal (exit 0). Nový G-code není bajtově shodný: liší se časové anotace a pořadí tahů v části vrstev. Kontroly platí pro G-code uložený v projektu. Otevření v GUI sliceru nebylo zkoušeno.
- Náhled a graf návaznosti neprokazují přilnavost, kvalitu mostků, pevnost úzkého spojení, kotvení ani stabilitu skutečného nože. Po tisku prohlédnout vršky otvorů a odstranit otřepy.
