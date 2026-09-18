# Od zadání k výtisku

## Postup

1. **Zadání:** popis dílu, účel, skutečně zadané rozměry v mm. Oddělit měření uživatele od návrhových hodnot. Chybějící údaje potřebné pro uchycení a funkci nepovažovat za ověřené.
2. **Model:** ve `models/<nazev>/` vytvořit nebo upravit parametrický FreeCAD dokument, tabulku parametrů a zdrojové makro. Jiří popisuje změnu; agent modeluje programově podle [postupu pro FreeCAD](software.md#spuštění-makra-ve-freecadu).
3. **Geometrická kontrola:** ověřit požadované rozměry, platnost tělesa a počet solidů (polička má být jeden kus), uzavřenost exportované STL sítě a případné změněné parametrické vazby. Výsledek zaznamenat. Kontrola geometrie nevypovídá o nosnosti ani skutečném fitu.
4. **Náhled a dokument:** uložit finální FCStd, odpovídající STL a náhled z reálné CAD geometrie. Pomocné tvary v dokumentu skrýt. Uživatel otevře FCStd a prohlédne si díl.
5. **Slicer:** importovat nebo přetáhnout STL do Anycubic Slicer Next. Vybrat Kobra X 0,4 mm, skutečný materiál a správnou cívku/slot. Ověřit rozměry, orientaci, spodní plochu a polohu na podložce. Samotná barva modelu výběr fyzické cívky nedokazuje.
6. **Nastavení a řezání:** vědomě zvolit výšku vrstvy, teploty, rychlosti, stěny, výplň a podpory; odlišit default od doporučení a skutečné konfigurace. Po řezání zkontrolovat náhled vrstev a drah, varování, případné přesahy a odhady.
7. **Tisk:** spouští uživatel. Agent bez zadání neposílá úlohy ani neprovádí zásahy do tiskárny. V deníku zachytit, co bylo skutečně spuštěno a zda je prokázaná vazba na konkrétní G-code.
8. **Vyhodnocení:** podle uživatelského hlášení, fotografie či měření doplnit první vrstvu, dokončení, vady, rozměry a funkční zkoušku. Upravit model či profil podle výsledku a zaznamenat důvod změny.

## Co znamenají soubory

| Soubor | Úloha |
|---|---|
| `.FCStd` | Editovatelný parametrický dokument FreeCADu |
| `.FCMacro` | Programový zdroj pro vytvoření dokumentu a exportu |
| `.stl` | Trojúhelníkový model pro slicer; při změně FCStd se sám neobnoví |
| `.png` | Skutečný náhled CAD geometrie; bez fyzického tisku nic nedokazuje o výsledku |
| `.gcode` | Výstup sliceru pro konkrétní tiskovou úlohu a nastavení |
| Kontrolní `.json` | Výsledek kontrol modelu, nikoli certifikace výtisku |

G-code není nutné běžně ukládat do repozitáře. Pokud je důležitý pro reprodukci, nejdřív ověř jeho původ a absenci soukromých dat; jinak stačí přesný záznam parametrů a omezení důkazů v deníku.

## Změny a návaznost

Po změně parametrů přepočítat model a exportovat nový STL z finálního objektu. Udržovat soulad FCStd, makra a náhledu; regenerace ze starého makra by ruční změny dokumentu ztratila. Poznámky modelu mají uvádět zadání, návrhové hodnoty, provedené kontroly a neověřené funkční požadavky.

Stavy zapisovat odděleně: **geometrie ověřena → připraveno ve sliceru → uživatel zahájil tisk → dokončení potvrzeno → fyzický výsledek vyhodnocen**. Poslední dva stavy nelze odvodit z vytvoření STL či odeslání úlohy. Úspěch pro zamýšlený účel může navíc vyžadovat rozměrovou a funkční zkoušku.

Veškeré nové zkušenosti zapisovat do tohoto projektu, do příslušných docs, poznámek modelu a [deníku](denik-tisku.md). Původní soubory mimo checkout jsou zachované kopie, nikoli další místo pro rozvíjení modelu.
