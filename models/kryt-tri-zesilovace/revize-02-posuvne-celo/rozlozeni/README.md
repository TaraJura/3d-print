# Kobra X — kryt tří zesilovačů, revize 02

**Pouze rozměrový a montážní prototyp. PCB je dle zadání 78 × 108 mm; výška osazení 38 mm, tloušťka PCB, výška konektorů a skutečný fit zatím nejsou potvrzeny. PLA není tímto schválené pro provoz horkých zesilovačů.**

Každou podložku otevřít jako celý projekt právě jednou. Obsahuje všechny fyzické kopie; nepřerovnávat ani nenásobit.

| Podložka | Projekt | Kusy | Čas sliceru | Materiál sliceru |
|---|---|---:|---|---:|
| 01 | [podlozka-01-kobra-x-pla-prototyp.3mf](podlozka-01-kobra-x-pla-prototyp.3mf) | 2 | 19h 31m 22s | 245.57 g |
| 02 | [podlozka-02-kobra-x-pla-prototyp.3mf](podlozka-02-kobra-x-pla-prototyp.3mf) | 5 | 2h 42m 26s | 40.63 g |

01: tělo stojí na zadním lemu, čelo leží plochou stranou na podložce. 02: zadní panel vnější plochou dolů, horní pojistka a tři distanční kroužky. Celkem **7 dílů**.

## Proces a podpory

Kobra X 0,4 mm; vrstva 0,20 mm; 4 stěny; 15 % gyroid; 5 horních/dolních vrstev. Vnější stěny 40, vnitřní 70, první vrstva 25 mm/s. Návrhový nekalibrovaný PLA Basic: první vrstva 215 °C, další 205 °C; texturovaná podložka 50 °C; maximální průtok 8 mm³/s. Vnější brim 3 mm, čisticí věž vypnutá. Barva je pouze vizualizace, nepotvrzuje skutečnou cívku.

Podložka 01 má skutečně zapnuté automatické přiléhající podpory `normal(auto) / snug`, včetně podpor na modelu, práh 30°, horní/dolní mezera 0,20 mm, XY odstup 0,35 mm, dvě kontaktní vrstvy. Jsou určené pro lokální převisy předních vodítek a horní kapsy matice. Zadní otvor těla poskytuje přístup k jejich odstranění; drážky a kapsy před montáží prohlédnout. Podložka 02 je bez podpor. Brim není podpora převisů.

## Digitální kontrola

Ověřeny jednotky, měřítko, orientace, počty, rozměry a skutečné vrcholy geometrie po importu i řezu; počet oprav sítě 0. Všechny objekty mají dráhy v první vrstvě a všechny vrstvy obsahují extruzi. Ověřena obálka extruzí na podložce, G-code teploty, maximální průtok a graf nových ostrovů podle skutečných šířek extruze. Graf ověřuje návaznost komponent, nikoli pořadí uvnitř vrstvy ani úplnou fyzickou podporu každého převisu. U samotných podpor zohledňuje nastavenou spodní mezeru 0,20 mm: může ověřit kontakt o dvě vrstvy níže (rozdíl Z nejvýše 0,40 mm); takové výjimky se samostatně zapisují.

Očíslované náhledy: [01](podlozka-01.png), [02](podlozka-02.png). Skutečné dráhy: [01](podlozka-01-vrstvy.png), [02](podlozka-02-vrstvy.png). Podrobné vrstvy jednotlivých dílů jsou v souborech `detail-*-drahy.png`. [Kontrolní protokol](kontrola-rezani.json).

Uložená varování sliceru: not_support_traditional_timelapse. CLI hlášky: calc_exclude_triangles:Unable to create exclude triangles. Neoznačovat řez za bezvarovný, pokud CLI hlášku obsahuje.

Geometrické 3MF jsou alternativy stejných podložek bez procesu; nepřidávají díly k sestavě. Výsledky jsou pouze kontrola digitálních souborů. Tisk, odstranění podpor, funkce posuvu, přesné osazení elektroniky, kotvy ve stěně a provozní chlazení nejsou fyzicky ověřeny. Tiskárna nebyla ovládána.

Regenerace: po finálním exportu CAD spustit `python3 ../build_print_projects.py` ze složky rozložení. Přepíše pouze vlastní podložky, profily, náhledy a kontrolní soubory v této složce. `--reuse-slice` znovu ověří uložené řezy proti aktuálním zdrojům; nově řeže pouze chybějící podložku.
