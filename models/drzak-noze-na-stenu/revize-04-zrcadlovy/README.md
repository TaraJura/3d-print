# Zrcadlový V držák nože — aktuální revize 04

Revize z 2. 11. 2026. Jiří označil revizi 03 za ideální a změnil **pouze vodorovnou orientaci při pohledu na stěnu**: špička je nově vpravo, rukojeť vlevo. Jde o přesné zrcadlení `X → 230 − X`; výška Y a hloubka Z zůstávají. Zadní montážní strana je dál u stěny a nůž se vyjímá shora. Není to otočení STL na podložce ani obrácení vzhůru nohama.

[Hlavní skutečný CAD náhled](prehled-navrhu.png) · [boční obrys](nahled-profil.png).

## Co se posunulo

| Místo | X ve V03 | X ve V04 |
|---|---:|---:|
| Špička referenčního nože | −80 | 310 |
| Konec referenční rukojeti | 260 | −30 |
| Sedlo rukojeti | 155–230 | 0–75 |
| Otevřený přechod 10 mm | 145–155 | 75–85 |
| Pata čepele, výška 45 mm | 145 | 85 |
| Stanice čepele, výška 40 mm | 45 | 185 |
| Konec sedla čepele | 0 | 230 |
| Osy vrutů (Y 48 mm) | 35 a 195 | 195 a 35, tedy stejná místa |

Rozměry jsou beze změny: 230 × 60 × 42,314 mm, objem 49 257,095 mm³, 2× Ø5,5 mm s roztečí 160 mm, V 12 mm pod čepelí, 26 → 28,143 mm pod rukojetí, patka 4 × 4 mm. Montáž se nepřepracovávala; lepení není navržené ani ověřené.

Všechny parametry a jejich původ jsou stejné jako ve [V03](../revize-03-tvarovany-dle-noze/README.md#rozměry-co-je-zadání-a-co-výklad). Nic nového se neměřilo. Odskok rukojeti 20 mm (`HandleRiseAssumed`), délka čepele 225 mm, rovný hřbet a průřez rukojeti zůstávají předpoklady.

Skutečný nůž se nezrcadlí, jen se do držáku vloží otočený. Ilustrační nůž je souměrný podle roviny čepele, takže zde zrcadlení odpovídá otočení. U skutečného nože s nesouměrnou rukojetí nebo výbrusem to ověřené není.

## Soubory

- [drzak.FCStd](drzak.FCStd): parametrický FreeCAD; viditelný je jen finální `Holder`.
- [drzak.FCMacro](drzak.FCMacro): zdroj celé revize. Staví beze změny zdroj V03 jako `HolderSource` a přidává nativní `Part::Mirroring` kolem roviny `X = Parameters.Length/2`. Stejně je zrcadlený i referenční nůž. Bez Python proxy.
- [STL — jeden kus](stl/drzak-zrcadlovy.stl), v tiskové orientaci.
- [Nastavená 3MF podložka](rozlozeni/podlozka-01-kobra-x-pla-projekt.3mf) a [její dokumentace](rozlozeni/README.md). `podlozka-01-geometrie.3mf` je jen alternativa bez procesu.
- [audit-montaze.json](audit-montaze.json), [kontrola-modelu.json](kontrola-modelu.json), [kontrola drah](rozlozeni/kontrola-drah-vizualne.md), [predani.json](predani.json), [predani.sha256](predani.sha256).

## Provedené kontroly

Audit znovu otevřel uložený FCStd a prošel **49/49 kontrol**, vázaných na SHA-256 v [audit-montaze.json](audit-montaze.json). Přesné zrcadlení se bralo z uloženého BRep V03 přes `Shape.mirror`.

- **Zrcadlení:** oboustranný rozdíl 0 / 0 mm³ při toleranci 10⁻⁶ mm³; objem, plocha a rozměry shodné s V03; 65 ploch, 175 hran, 114 vrcholů; shoda všech 2000 náhodných bodů. Kontrolní nezrcadlená, na podložce otočená i obrácená V03 se liší o více než 18 000 mm³.
- **Stěna a vršek:** zadní rovina Z 0 se stejnou plochou jako ve V03; prostor nad oběma sedly je volný; širší sedlo vlevo; přechod X 75–85 volný nad patkou.
- **Nůž:** obálka podle `optimalBoundingBox` 340 × 45 × 25 mm, X −30 až 310; bez kolize včetně zdvihu o 60 mm po 1 mm. Jde o ilustraci, ne o fit skutečného nože.
- **Přepočet:** změny výšky stanice, délky rukojeti, odskoku i `Length` na 235 mm (rovina 117,5 mm) drží přesné zrcadlení. Testováno v paměti, hodnoty obnoveny, soubor nezměněn.
- **STL:** 2340 trojúhelníků, uzavřená, jedna komponenta, jednotná orientace; od CAD se liší nejvýše o 0,004 mm a je zrcadlem STL V03 do 0,00001 mm.
- **Náhled:** skutečné CAD rendery; rukojeť vlevo, silueta profilu odpovídá převrácenému náhledu V03.

## Tisk

Podložku otevřít jednou jako celý projekt, nemnožit ani nepřerovnávat. Kobra X 0,4 mm, návrhový nekalibrovaný PLA: 0,20 mm, 4 stěny, 15 % gyroid, tryska 215/205 °C, podložka 50 °C, brim 3 mm, max. průtok 8 mm³/s. Orientace: instalovaná spodní patka, ouška a žebra na podložce.

Nový řez: **1 kus, 300 vrstev, 0 nových ostrovů, 0 segmentů podpor, odhad 54,31 g / 3 h 20 min 37 s**. Vrcholy otvorů tvoří krátké mostky v Z 51 mm. Proč zůstávají podpory vypnuté a jaká varování slicer hlásí, je v [kontrole drah](rozlozeni/kontrola-drah-vizualne.md). Barva je jen vizualizace, fyzická cívka není potvrzená.

## Regenerace

Makro přepisuje jen vlastní FCStd, STL a JSON v této složce, V03 nečte ani nemění. Před spuštěním uložit a zavřít stejnojmenný otevřený dokument. Změny tabulky sladit s makrem; statickou ilustraci nože ani STL/PNG samotná editace parametrů neobnoví.

Spustit přes FreeCAD 1.1.3 (`/home/novakj/.cache/freecad-shelf-1.1.3/runtime/AppRun freecadcmd`, s oddělenými konfiguracemi dle [projektové dokumentace](../../../docs/software.md)): `drzak.FCMacro`, pak v GUI `nahled.FCMacro`, pak `audit-montaze.FCMacro`. Následně `python3 sestavit-nahled.py` a `python3 build_print_projects.py`. Audit a kontrola drah čtou také soubory V03. Runtime není součástí modelu.

## Neověřeno

Fyzický tisk, první vrstva, kvalita mostků, skutečný fit nože, stabilita, těžiště, pevnost, vruty a kotvení ve stěně ani lepení. Špička a přečnívající ostří nejsou kryté. Tiskárna nebyla ovládána.

Předchozí [revize 03](../revize-03-tvarovany-dle-noze/README.md), [V02](../revize-02-otevrene-v/README.md) a [V01](../historie/v01-uzavrene-pouzdro/README.md) zůstávají beze změny jako historie.
