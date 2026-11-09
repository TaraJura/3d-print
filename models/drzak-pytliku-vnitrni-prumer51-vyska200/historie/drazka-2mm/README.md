**HISTORIE — PŘEKONANÁ DRÁŽKA 2 mm.** Pro aktuální zadání použít [verzi s drážkou 6 mm](../../README.md). Geometrie tohoto archivu zůstává beze změny.

# Držák pytlíků – vnitřní průměr 51 mm, výška 200 mm

Historické STL: [drzak-pytliku-vnitrni-prumer51-vyska200.stl](stl/drzak-pytliku-vnitrni-prumer51-vyska200.stl).

**Oprava zadání 17. 10. 2026:** 50 mm je šířka samotného sáčku či role. Nominální dutina má **vnitřní průměr 51 mm**, tedy návrhovou celkovou vůli 1 mm (0,5 mm na každé straně). Odvozený kruhový obvod je **160,221225 mm**. Starší varianta s vnitřním obvodem 50 mm / Ø15,9155 mm je překonaná a pro toto zadání se nepoužívá. Skutečný rozměr role, fit a dostatečnost vůle nebyly fyzicky ověřeny.

Vnější rozměry jsou **54,2 × 55,8 × 200 mm**. Výška je **200 mm**, výdejní drážka má čistou šířku **2 mm** se zaoblenými podélnými hranami R0,3 mm; ústí je zaoblením mírně rozevřené, prostřední hrdlo zůstává 2 mm. Plášť a dno mají 1,6 mm. Zachována jsou plochá záda, plné zadní rohy, horní sklon 20°, zadní montážní otvory Ø6,1 mm se zahloubením Ø12 mm a středy 42,9272 / 157,3989 mm nad podložkou. Spodní průchozí otvor je Ø17 mm.

Regenerace proběhla parametricky z předchozí rekonstrukce vstupu `trash-bag-holder-d60-l200_g.3mf`; geometrie se plošně neškálovala. [drzak.FCStd](drzak.FCStd) obsahuje standardní FreeCAD objekty a tabulku parametrů. [drzak.FCMacro](drzak.FCMacro) přepíše pouze zdejší FCStd, STL a kontrolní JSON; [nahled.FCMacro](nahled.FCMacro) obnovuje skutečné CAD náhledy. [kontrola-modelu.json](kontrola-modelu.json) obsahuje rozměry a kontrolu tělesa; nezávislé ověření STL a skutečného řezu je v [kontrola-stl.json](kontrola-stl.json).

Požadováno je pouze STL; slicer a tisk si připravuje uživatel. Řezání a fyzický tisk ani průchod konkrétní fólie drážkou nebyly ověřeny. Cizí Bambu profil původního 3MF se nepřenáší. Tisk ani tiskárna nebyly spuštěny.

Ověřeno: jeden validní solid, skutečný řez Z100 s vnitřním Ø51,000 mm a čistou drážkou 2,000 mm; STL má jednu spojenou uzavřenou komponentu, každou hranu právě u dvou trojúhelníků, konzistentní orientaci a žádné degenerované plochy. Vnější rozměry STL jsou 54,2 × 55,8 × 200 mm.
