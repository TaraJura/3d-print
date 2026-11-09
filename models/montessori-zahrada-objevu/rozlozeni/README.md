# Montessori Zahrada objevů – připravené podložky

Každý nastavený projekt otevřít samostatně **jednou jako celý projekt** v Anycubic Slicer Next. Všechny kopie už jsou rozmístěné. Nemnožit, nepřerovnávat ani automaticky neorientovat.

| Nastavený projekt | Fyzické kusy | Odhad času | Odhad materiálu |
|---|---:|---:|---:|
| [01 – PLA Basic — svetla zakladna (barva navrh)](podlozka-01-kobra-x-pla-projekt.3mf) | 1 | 12 h 16 min | 210.93 g |
| [02 – PLA Basic — kameny (barva navrh)](podlozka-02-kobra-x-pla-projekt.3mf) | 5 | 8 h 23 min | 153.54 g |

Celkem **6 kusů, 20 h 39 min, 364.47 g** podle lokálního sliceru. Fyzický tisk, spotřeba, mechanická odolnost, fit a vhodnost pro konkrétní dítě neověřeny.

**Anycubic Kobra X, 0,4 mm; návrhový nekalibrovaný profil PLA Basic:** vrstva i první vrstva 0,20 mm; 4 stěny; 20 % gyroid; 5 horních a 5 dolních vrstev; vnější stěny 40 mm/s, vnitřní 70 mm/s, výplň 80 mm/s, první vrstva 25 mm/s. Tryska první 215 / další 205 °C, texturovaná podložka 50 °C, max. průtok 8 mm³/s. Každá podložka má jediný filament; čisticí věž vypnutá. **Podpory vypnuté podle tiskové orientace; vnější brim 3 mm je přilnavost, nikoli podpora převisů.** Brim opatrně odstranit a povrch prohlédnout. Základna má vypnuté speciální rozpoznávání úzké plné výplně (`detect_narrow_internal_solid_infill=0`), kameny ponechávají výchozí `1`; filtr gap fill je `0` u obou.

Před tiskem vybrat skutečné cívky PLA Basic a odpovídající fyzické vstupy tiskárny; barvy náhledu jsou návrh a nepotvrzují fyzický filament. Skladové zůstatky nejsou tímto úkolem ověřeny. Oba projekty jsou připravené pro PLA Basic; případná záměna za Silk, TPU nebo jiný materiál vyžaduje odpovídající profil.

- [Očíslovaná podložka 01](podlozka-01.png) · [skutečné dráhy 01](podlozka-01-vrstvy.png)
- [Očíslovaná podložka 02](podlozka-02.png) · [skutečné dráhy 02](podlozka-02-vrstvy.png)
- [Manifest kusů a umístění](manifest.json) · [kontrola obou řezů](kontrola-rezani.json)

Čísla v náhledech znamenají pořadí na konkrétní podložce:

| Podložka / číslo | Díl | Výška při tisku |
|---|---|---:|
| 01 / 01 | 01 — zakladna / 5 sedel / hmatova spirala | 12 mm |
| 02 / 01 | 03 — Trojuhelnik / 2 dulku / 24 mm | 24 mm |
| 02 / 02 | 06 — Sestiuhelnik / 5 dulku / 60 mm | 60 mm |
| 02 / 03 | 05 — Petiuholnik / 4 dulku / 48 mm | 48 mm |
| 02 / 04 | 02 — Kruh / 1 dulku / 12 mm | 12 mm |
| 02 / 05 | 04 — Ctverec / 3 dulku / 36 mm | 36 mm |

Kontroly: uzavřenost a jedna komponenta každé STL, zachování vrcholů/počtů/orientace/umístění ve 3MF, správná tiskárna a nastavení, kontakt všech kusů na první vrstvě, extruze každé vrstvy a uvnitř podložky, kontrola nových oddělených ostrůvků z reálných drah. Grafická kontrola ostrůvků potvrzuje spojení alespoň některé dráhy komponenty s předchozí vrstvou; **neověřuje pořadí nanášení v téže vrstvě ani plošnou podporu celého převisu**. Výsledky a skutečná varování jsou v kontrolním JSON. Brim a případné drobné mosty/převisy jsou viditelné v obrázcích drah.

Varování uložená slicerem: žádná. CLI navíc vypsalo `calc_exclude_triangles:Unable to create exclude triangles`. Operace skončily exit 0; zachování geometrie a počtů bylo ověřeno samostatně. Funkce vynechávání objektů není fyzicky ověřená.

Doplňková [kontrola mikrovyplně](kontrola-mikrocarek-finalni.json) porovnává konkrétní místa v Z 10,6 mm. Vypnutí rozpoznávání úzké plné výplně základny odstranilo dvě původní krátké úsečky (0,159 a 0,152 mm); druhá nebyla při nanášení doloženě podepřená. Samotný filtr gap fill tento jiný typ výplně neodstranil, proto zůstává ve finále na 0. [Skutečný detail finálních drah](kriticka-vrstva-01-mikrovypln.png) vznikl z téhož předávaného G-code. Přesný původní nález zůstává v [diagnostice](kontrola-mikrocarek.json).

[Kontrola spodních hran](kontrola-spodnich-hran.json) ověřila skutečné vnější dráhy vrstev 2–8 všech šesti dílů, včetně spodního R1 kamenů. Minimální vypočtený nominální překryv drah byl 0.029 mm. Výpočet používá skutečné WIDTH a vzorkování nejvýše 0,15 mm; fyzické spojení vrstev ani hladkost hrany neprokazuje.

Nastavené projekty obsahují skutečný lokálně vytvořený G-code. `podlozka-01-geometrie.3mf` a `podlozka-02-geometrie.3mf` jsou pouze alternativy stejného počtu kusů bez procesu, filamentu a G-code; **netisknout navíc**.

Regenerace po exportu STL: `python3 ../build_print_projects.py`. Čte `../print-manifest.json`, přepíše zdejší podložky, profily, náhledy a kontrolní JSON. `--reuse-verified` zachová již ověřený řez jen při shodě hashů STL/projektu/geometrie a umístění; `--geometry-only` tvoří pouze alternativní geometrii; `--only-plate 1` nebo `2` je dílčí diagnostika a nenahradí závěrečnou kontrolu celku. Logy a izolované datadir zůstávají v ignorované `.cache/`. Program nepřepisuje globální presety a neprovádí tiskárnové I/O.

Žádná tisková úloha nebyla odeslána ani spuštěna.
