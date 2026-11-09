**PŘEKONANÁ VARIANTA — NEPOUŽÍVAT PRO AKTUÁLNÍ ZADÁNÍ.** Dne 17. 10. 2026 Jiří upřesnil, že 50 mm je šířka sáčku, nikoli obvod. Aktuální je [držák s vnitřním průměrem 51 mm](../drzak-pytliku-vnitrni-prumer51-vyska200/README.md). Tato složka uchovává historický výsledek předchozího výkladu.

# Držák pytlíků – vnitřní obvod 50 mm, výška 200 mm

Historické STL (překonané): [drzak-pytliku-obvod50-vyska200.stl](stl/drzak-pytliku-obvod50-vyska200.stl).

Zadání z 17. 10. 2026: výška **200 mm**, výslovně upřesněný **vnitřní obvod 50 mm**, následně co nejužší výdejní drážka. Kruhová vnitřní obálka má proto Ø **15,915494 mm**. Nejde o průměr 50 mm. Výdejní drážka má **čistou šířku 2 mm**, podélné hrany jsou zaoblené R0,3 mm; zaoblení rozevírá ústí, prostřední průchod zůstává 2 mm. Skutečný rozměr role nebyl změřen.

Vstup: `/home/novakj/Downloads/trash-bag-holder-d60-l200_g.3mf`. Z jeho skutečné sítě bylo zjištěno: vnitřní Ø60 mm, výška 199,673752 mm, plášť 1,6 mm, horní sklon 20°, dno s otvorem Ø20 a dva zadní montážní otvory Ø6,1 se zahloubením Ø12 mm. Původní 3MF nebyl změněn. Cizí profil Bambu P1S se nepřenáší.

Model je parametricky rekonstruovaný ze změřených ploch původní sítě. Zachovává válcový zásobník, rovná záda, šikmý horní lem, spodní průchozí otvor a oba montážní otvory. Stěna a dno zůstávají 1,6 mm; zadní rohy jsou plné místo původních odlehčovacích dutin, které by se při zúžení staly příliš tenkými. Dno má otvor Ø5,305165 mm. Montážní otvory zůstávají Ø6,1 / zahloubení Ø12 mm, středy Z42,9272 a Z157,3989 mm nad podložkou. Skutečné šrouby a montáž nejsou potvrzené. Spodní konec výdejní drážky je oblý R1 mm, nejnižší bod 11,7573 mm nad dnem.

## Zdroje a ověření

- [drzak.FCStd](drzak.FCStd): standardní FreeCAD objekty, tabulka parametrů a výrazy, včetně zaoblení hran.
- [drzak.FCMacro](drzak.FCMacro): regenerace ve FreeCADu 1.1.3; přepisuje zdejší FCStd, STL a kontrolní JSON.
- [nahled.png](nahled.png), [nahled-shora.png](nahled-shora.png): skutečná CAD geometrie; obnovuje [nahled.FCMacro](nahled.FCMacro).
- [kontrola-modelu.json](kontrola-modelu.json) a nezávislá [kontrola-stl.json](kontrola-stl.json): validní jedno těleso, jedna spojená uzavřená STL komponenta, každá hrana právě u dvou trojúhelníků, konzistentní orientace, bez degenerací. Skutečné STL rozměry **19,115494 × 20,715494 × 200 mm**; ověřený řez má drážku 2,000 mm a vnitřní poloměr 7,957747155 mm. Přepočet obvodu 50→55→50 a výšky 200→190→200 prošel. Přední stěna ve výškách zadních otvorů zůstává zachovaná.
- `vstup/`: původní náhledy a průřezy, pouze podklady pro rozměrovou analýzu.

Požadováno je výslovně pouze STL, přípravu sliceru a tisk provádí uživatel. V této zakázce není připravena tisková 3MF podložka ani ověřeno řezání nebo fyzický výtisk. Pro svislé postavení na dně je vhodné ve sliceru posoudit brim a průběh horizontálních montážních otvorů; jde o doporučení, nikoli nastavení předaného souboru. Uzavřená síť a správné CAD rozměry nepotvrzují skutečný fit ani to, zda konkrétní fólie dobře prochází 2mm drážkou.
