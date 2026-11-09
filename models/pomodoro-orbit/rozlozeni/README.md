# Pomodoro Orbit – připravené podložky

Každý nastavený projekt otevřít samostatně **jednou jako celý projekt** v Anycubic Slicer Next. Všechny kopie už jsou rozmístěné. Nemnožit, nepřerovnávat ani automaticky neorientovat.

| Nastavený projekt | Fyzické kusy | Odhad času | Odhad materiálu |
|---|---:|---:|---:|
| [01 – černá](podlozka-01-kobra-x-pla-projekt.3mf) | 3 | 4 h 25 min | 62.23 g |
| [02 – zlatá](podlozka-02-kobra-x-pla-projekt.3mf) | 6 | 2 h 20 min | 25.57 g |

Celkem **9 kusů, 6 h 45 min, 87.80 g** podle lokálního sliceru. Fyzický tisk, spotřeba, hladkost pohybu a fit neověřeny.

**Anycubic Kobra X, 0,4 mm; návrhové nekalibrované profily:** vrstva 0,16 / první 0,20 mm; 3 stěny; 20 % gyroid; 5 horních a 5 dolních vrstev; vnější stěny 40 mm/s, první 25 mm/s. Černá PLA Basic: vnitřní 70 mm/s, tryska první 215 / další 205 °C, texturovaná podložka 50 °C, max. průtok 8 mm³/s. Zlatá Alzament PLA Silk Gold: vnitřní stěny i výplň nejvýše 50 mm/s, tryska 220 / podložka 50 °C, max. průtok 5,5 mm³/s. Každá podložka má jediný filament; čisticí věž vypnutá. **Podpory vypnuté podle tiskové orientace; vnější brim 3 mm je přilnavost, nikoli podpora převisů.** Brim opatrně odstranit z pracovních obvodů.

Před tiskem vybrat skutečné cívky a odpovídající fyzické vstupy tiskárny; barvy v projektu je nepotvrzují. Skladové zůstatky nejsou tímto úkolem ověřeny. Podložka 01 obsahuje odlišný profil PLA Basic, podložka 02 profil Silk Gold. Záměna materiálů vyžaduje změnu profilu.

- [Očíslovaná podložka 01](podlozka-01.png) · [skutečné dráhy 01](podlozka-01-vrstvy.png)
- [Očíslovaná podložka 02](podlozka-02.png) · [skutečné dráhy 02](podlozka-02-vrstvy.png)
- [Manifest kusů a umístění](manifest.json) · [kontrola obou řezů](kontrola-rezani.json)

Kontroly: uzavřenost a jedna komponenta každé STL, zachování vrcholů/počtů/orientace/umístění ve 3MF, správná tiskárna a nastavení, kontakt všech kusů na první vrstvě, extruze každé vrstvy a uvnitř podložky, kontrola nových oddělených ostrůvků z reálných drah. Grafická kontrola ostrůvků potvrzuje spojení alespoň některé dráhy komponenty s předchozí vrstvou; **necertifikuje plošnou podporu celého převisu**. Výsledky a skutečná varování jsou v kontrolním JSON. Brim a případné drobné mosty/převisy jsou viditelné v obrázcích drah.

Varování uložená slicerem: žádná. CLI navíc vypsalo `calc_exclude_triangles:Unable to create exclude triangles`. Operace skončily exit 0; zachování geometrie a počtů bylo ověřeno samostatně. Funkce vynechávání objektů není fyzicky ověřená.

Nastavené projekty obsahují skutečný lokálně vytvořený G-code. `podlozka-01-geometrie.3mf` a `podlozka-02-geometrie.3mf` jsou pouze alternativy stejného počtu kusů bez procesu, filamentu a G-code; **netisknout navíc**.

Regenerace po exportu STL: `python3 pripravit-podlozky.py`. Čte `../print-manifest.json`, přepíše zdejší podložky, profily, náhledy a kontrolní JSON. `--reuse-verified` zachová již ověřený řez jen při shodě hashů STL/projektu/geometrie a umístění; `--geometry-only` tvoří pouze alternativní geometrii; `--only-plate 1` nebo `2` je dílčí diagnostika a nenahradí závěrečnou kontrolu celku. Logy a izolované datadir zůstávají v ignorované `.cache/`. Program nepřepisuje globální presety a neprovádí tiskárnové I/O.

Doplňková kontrola [kužele a kapsy šroubu](kriticke-vrstvy-screw.png) a [stropů tří slepých otvorů koruny](kriticke-vrstvy-crown.png) používá přímo stejný finální G-code, bez dalšího řezání. Šedě je předchozí vrstva, tmavě současná. Kužel ve vrstvách Z 12,36 / 12,52 / 14,92 / 20,04 mm plynule rozšiřuje obvod. Dno kapsy je dokončeno ve vrstvě 21,80 mm; v 21,96 mm už střed nemá extruzní dráhy (nejbližší dráha je 12,55 mm od osy), takže se přes otvor kapsy nevytváří strop. Tři otvory Ø3,8 mm koruny jsou otevřené do vrstvy 1,80 mm a v 1,96 mm slicer vytváří skutečné krátké mosty s návazností na jejich okraje; následující vrstva je uzavírá. Náhledy byly vizuálně prohlédnuty. Fyzická kvalita těchto mostů a fit otvorů dosud nejsou potvrzené. [Přesná evidence a hashe](kontrola-kritickych-vrstev.json), regenerace pouze těchto panelů: `python3 zkontrolovat-kriticke-vrstvy.py`.

Žádná tisková úloha nebyla odeslána ani spuštěna.
