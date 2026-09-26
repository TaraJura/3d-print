# Přilbička — vizuální koncept

**Aktuální vzhledová varianta:** [v2 — římská velitelská přilba](v2/perspektiva-cad.png), také [zepředu](v2/zepredu-cad.png). Jiří chtěl výraznější, „epický“ generálský vzhled. V2 má červený chochol, bronzovou kupoli, zlacený čelní pás s vavřínem a stylizovaným orlem, zaoblenější lícnice a zadní štít. [Generovaný obrázek](v2/stylova-predloha.png) je pouze stylová předloha ([zadání imagegen](v2/stylova-predloha-prompt.md)); oba soubory `*-cad.png` jsou skutečný náhled odlišné CAD geometrie.

**Stav:** jen ilustrativní náhled. CAD obsahuje otevřené plochy a křivky bez objemu či definovaného nositelného střihu. Není určen pro výrobu, nasazení na dítě ani ochranu hlavy. STL, 3MF a tiskové podložky nebyly vytvořeny: Jiří zatím požádal pouze o vizualizaci k úpravám.

## Zadání a jeho meze

- Jiří uvedl věk dítěte 3 měsíce, šířku hlavy 125 mm a výšku 150 mm. Jde o jeho údaj, nikoli o naše ověřené měření.
- Zvukový přepis požadavku na větší prostor uvnitř není jednoznačný. Širší boční proporce obrázku jsou jen výtvarný návrh; nepředstavují bezpečnou vůli ani anatomický tvar.
- Chybí kompletní tvar hlavy, obvod, poloha uší a čela, účel nošení a klinické posouzení. Dvě uvedené míry nemohou určit bezpečně padnoucí helmu pro kojence.

## Aktuální soubory a kontrola

- `v2/velitelska-prilba.FCMacro` vytváří `v2/velitelska-prilba.FCStd` a dva náhledy přímo ve FreeCADu. Opakované spuštění tyto tři výstupy přepíše.
- Kontrola po sestavení v2: 29 CAD objektů, 0 plných těles a 0 neplatných tvarů; oba výsledné PNG byly otevřeny a vizuálně zkontrolovány. Nejde o kontrolu fitu, materiálu ani bezpečnosti.

## Původní varianta v1

- `koncept.FCMacro` vytvoří otevřenou CAD plochu, uloží `koncept.FCStd` a v GUI pořídí dva PNG náhledy přímo z geometrie FreeCADu. Při opakovaném spuštění tyto tři výstupy přepíše. Rozměry v makru jsou výhradně ilustrativní měřítko a neslouží pro fit.
- `koncept-perspektiva.png` a `koncept-zepredu.png` jsou starší vzhledové náhledy.
- Kontrola v makru vyžaduje nula plných těles.

Pokud má jít o léčebnou kraniální ortézu, musí indikaci a tvar posoudit pediatr a specialista na individuální měření a nasazení. Běžná pokrývka hlavy pro spánek je také samostatná bezpečnostní otázka.
