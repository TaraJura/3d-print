# Nezávislý audit spojů revize 03

Uložené BREP načteny přímo ze ZIP FCStd. Dokument nebyl otevřen ve FreeCAD GUI ani přepočten či uložen; generační makro nebylo spuštěno.
SHA-256 FCStd při načtení: `c333f8114b20a25caf7fad086e23d9c46b89d974fd48ca0e1978676b59fddeba`. Samostatné hashe geometrie jsou v JSON; následné uložení viditelnosti může změnit hash celého FCStd.

## Výsledky

- `valid_single_solids`: **True**
- `nominal_no_overlap`: **True**
- `samples_match_both_joints`: **True**
- `stl_closed_and_vertices_on_cad`: **True**
- `layer_growth_within_0_1mm`: **None**
- `sampled_prescribed_insertion_path_clear`: **True**

## Meze kontroly

Průchod X je vzorkován po 0,5 mm od +19 do +0,5 mm a dále při +0,19 mm během uvolňování. Není to spojitý kolizní důkaz celé dráhy. Jde pouze o předepsanou geometrickou deformaci ramen, nikoli FEA, odhad síly ani důkaz, že skutečný TPU sám projde a vrátí se. Proxy zachovává kořen bez posunu; ramena se po částech smykově deformují a hlava se stlačí o 0,65 mm na stranu.
CAD kontrola převisů: díly 1 a 2 prošly 41 průřezy (start 0,001 mm nad patou, přírůstky 0,2 mm, navíc horní řez; reference zahrnuje přesnou spodní plochu). Plocha mimo předchozí průřez rozšířený o 0,100001 mm byla nulová. U dílu 3 geometrické jádro vrátilo neuzavřený wire; tato metoda proto nemá úplný výsledek a v souhrnu je null. Řádková data této přerušené části se neuložila; průchod prvních dvou dílů dokládá výstup běhu zaznamenaný v JSON. Nejde o ověření skutečné adheze ani kvality drah.
Nominální kontakt a geometrické zachycení nejsou důkazem těsnosti, odolnosti, životnosti ani fyzické rozměrové tolerance. Referenční lepicí lože se netiskne.
Detailní kolize v obou znaménkách X/Y/Z, shody vzorků, STL a vzorkované polohy zasouvací proxy obsahuje audit-spoje.json.
