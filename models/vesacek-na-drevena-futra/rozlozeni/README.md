# Podložka 01 – věšáček na dřevěná futra

| Podložka | Fyzické kusy | Nastavený projekt | Alternativa pouze s geometrií | Náhledy |
|---|---:|---|---|---|
| 01 | 1× věšáček | [Kobra X 0,4 mm, návrhový PLA profil](podlozka-01-kobra-x-pla-projekt.3mf) | [Geometrie 1:1 bez procesu](podlozka-01-geometrie.3mf) | [Rozložení](podlozka-01.png), [skutečné dráhy šesti vrstev](nahled-kritickych-vrstev.png) |

Obě 3MF představují **tutéž jednu podložku**; každou variantu případně importovat samostatně jednou. Model leží zadní dosedací plochou na tiskové podložce. V tiskových souřadnicích zabírá X **108–152 mm**, Y **87–173 mm**, Z **0–58 mm** před lemem. Jediný vrutový otvor míří svisle skrz základnu. Háčky postupně vyrůstají ze základny. Rozmístění a orientaci tvoří [reprodukovatelný generátor](vytvorit-podlozku.py); [kontrolní výstup](kontrola-rozlozeni.json) potvrzuje jeden kus, měřítko v mm, uzavřenou síť a odstup od hran podložky. Geometry-only 3MF nenese profil, filament ani G-code.

Nastavený projekt používá **Anycubic Kobra X s tryskou 0,4 mm**, vrstvy **0,20 mm**, **5 stěn**, **100% přímočarou výplň** a **5mm vnější lem**. Proces má **podpory vypnuté**: dosedací destička leží celou zadní plochou na podložce a kořeny všech tří háčků začínají uvnitř destičky. Z plné výplně v řezu nevznikají vnitřní mosty přes řídkou výplň. Skutečný řez nevytvořil dráhy podpor ani mostů. Vzorkovaná kontrola návaznosti drah po všech vrstvách našla jen dva symetrické body na horních uzavíracích ploškách malých háčků ve vrstvě 150: nejbližší předchozí dráha je zhruba **0,56 mm** daleko; žádný bod neleží dále než 1 mm. Jde o drobnou lokální mezeru při uzavření špiček, nikoli nový díl vznikající ve vzduchu. Tento výpočet nezaručuje bezvadný tisk ani požadovanou pevnost.

Filamentový profil PLA má návrhově **215 °C první vrstva / 205 °C další vrstvy / 50 °C podložka**. Skutečná cívka, vhodná teplota, přilnavost, vrstvená pevnost, únosnost, vrut i odpor proti pootočení na konkrétních futrech nebyly ověřeny. Barva náhledu nedokládá výběr fyzického slotu ani materiálu.

Místní Anycubic Slicer Next dokončil řez s návratovým kódem 0: **290 vrstev**, extruze v každé vrstvě, žádná tisková dráha mimo podložku, `support_used=false`, `outside=false`, bez varování v metadatech 3MF. [Kontrola řezu](kontrola-rezani.json) uvádí profil, rozsah extruzních drah a náhledy skutečného G-code ve vrstvách **1, 33, 40, 55, 270 a 290**; otvor, kořeny a koncové špičky jsou na nich vidět. Odhad sliceru je **57,23 g PLA a přibližně 3 h 12 min**, nikoli změřená spotřeba či čas.

CLI do logu zároveň zapsalo chybu `calc_exclude_triangles:Unable to create exclude triangles` při exportu i řezu. Příčina nebyla určena. Přesto vznikl platný nastavený 3MF a 290 vrstev s G-code; řez proto neoznačujeme za bezchybný. Pracovní `.cache/` byla po kontrole odstraněna; konec logu i s touto hláškou je uložený v kontrolním JSON.

Soubory se obnovují v pořadí [vytvorit-podlozku.py](vytvorit-podlozku.py), [pripravit-projekt.py](pripravit-projekt.py), [nahled-vrstev.py](nahled-vrstev.py). První čte aktuální STL; po změně FCStd je nutné STL a pak obě 3MF znovu vygenerovat. Skripty neovládají tiskárnu. Fyzický tisk ani zavěšení předmětu neproběhly.
