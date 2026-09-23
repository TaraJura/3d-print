# Od zadání k výtisku

## Postup

1. **Zadání:** popis dílu, účel, skutečně zadané rozměry v mm. Oddělit měření uživatele od návrhových hodnot. Chybějící údaje potřebné pro uchycení a funkci nepovažovat za ověřené.
2. **Model:** ve `models/<nazev>/` vytvořit nebo upravit parametrický FreeCAD dokument, tabulku parametrů a zdrojové makro. Jiří popisuje změnu; agent modeluje programově podle [postupu pro FreeCAD](software.md#spuštění-makra-ve-freecadu).
3. **Geometrická kontrola:** ověřit požadované rozměry, platnost tělesa a počet solidů (polička má být jeden kus), uzavřenost exportované STL sítě a případné změněné parametrické vazby. Výsledek zaznamenat. Kontrola geometrie nevypovídá o nosnosti ani skutečném fitu.
4. **Náhled a dokument:** uložit finální FCStd, odpovídající STL a náhled z reálné CAD geometrie. Pomocné tvary v dokumentu skrýt. Uživatel otevře FCStd a prohlédne si díl.
5. **Podložky a slicer:** připravit kompletní rozložení podle [postupu níže](#připravené-tiskové-podložky). Uživatel otevře každou připravenou 3MF podložku samostatně jednou v Anycubic Slicer Next, bez ručního rozmisťování nebo kopírování dílů. Vybrat Kobra X 0,4 mm, skutečný materiál a správnou cívku/slot. Samotná barva modelu výběr fyzické cívky nedokazuje.
6. **Nastavení a řezání:** vědomě zvolit výšku vrstvy, teploty, rychlosti, stěny, výplň a podpory; odlišit default od doporučení a skutečné konfigurace. Po řezání zkontrolovat náhled vrstev a drah, varování, případné přesahy a odhady.
7. **Tisk:** spouští uživatel. Agent bez zadání neposílá úlohy ani neprovádí zásahy do tiskárny. V deníku zachytit, co bylo skutečně spuštěno a zda je prokázaná vazba na konkrétní G-code.
8. **Vyhodnocení:** podle uživatelského hlášení, fotografie či měření doplnit první vrstvu, dokončení, vady, rozměry a funkční zkoušku. Upravit model či profil podle výsledku a zaznamenat důvod změny.

## Připravené tiskové podložky

Pro každý nový nebo upravovaný model ulož do `models/<nazev>/rozlozeni/` samostatné podložky 3MF podle skutečné použitelné plochy aktuální tiskárny (nyní Anycubic Kobra X s tryskou 0,4 mm; nezaměňovat s Kobra 3/S1). Počet podložek určuje geometrie a prostor. Zahrň všechny fyzické kopie včetně opakovaných kol, podložek, čepů a pojistek; ověř shodu celé montáže, kusovníku, kopií v kompletním ZIPu a objektů ve všech 3MF, nikoli jen počet různých STL. Zachovej měřítko 100 %, správnou tiskovou orientaci, samostatné objekty a ověřené rozumné rozestupy a okraje.

Přidej stručný přehled názvů podložek a počtů, očíslované náhledy a upozornění, které díly potřebují podpory. Každá podložka se importuje samostatně jednou; uživatel nemá nic ručně přerovnávat ani násobit. Geometry-only 3MF předává geometrii a rozmístění, bez tichého přepsání uživatelových tiskových či materiálových presetů. Ověření rozložení samo nepotvrzuje dosah podpor, hotové řezání ani tisk; skutečné podpory a dráhy je nutné prohlédnout v náhledu vrstev.

## Co znamenají soubory

### Orientace čepů a předání podpor

Pro hřídelky a čepy našeho autíčka je podle Jiřího opakované zkušenosti výchozí orientace nastojato na čele/hlavě, s podélnou osou Z. U krátkých čepů tím odpadne dřík visící nad podložkou kvůli širší hlavě. Nejde o záruku větší pevnosti: vrstvy napříč osou a kmitání vysokého dílu je nutné posoudit zvlášť. Zadní osa může potřebovat lokální podporu i nastojato. Orientaci zaznamenej do reprodukovatelného generátoru a manifestu, aby další export změnu nevrátil.

Podpory připrav skutečně v předávaném nastaveném projektu Next; geometry-only alternativa žádné nastavení podpor nenese. Před předáním proveď místní řezání a kontrolu skutečných vrstev/drah pod převisy, ostrovy, rameny, čepy a v kapsách. Podle geometrie povol podpory na modelu, ne jen z podložky. Zkontroluj také průchodnost funkčních otvorů a možnost podpory odstranit. Brim ověř samostatně jako přilnavost. Automatické zapnutí podpor všude ani textové upozornění kontrolu nenahrazuje. Uveď profil, varování, skutečný rozsah kontroly a odliš jej od dosud neověřeného fyzického tisku. Schváleno Jiřím 20. 9. 2026.

| Soubor | Úloha |
|---|---|
| `.FCStd` | Editovatelný parametrický dokument FreeCADu |
| `.FCMacro` | Programový zdroj pro vytvoření dokumentu a exportu |
| `.stl` | Trojúhelníkový model pro slicer; při změně FCStd se sám neobnoví |
| `.3mf` v `rozlozeni/` | Připravená podložka se všemi kopiemi a jejich rozmístěním; geometry-only soubor není tiskový profil ani G-code |
| `.png` | Skutečný náhled CAD geometrie; bez fyzického tisku nic nedokazuje o výsledku |
| `.gcode` | Výstup sliceru pro konkrétní tiskovou úlohu a nastavení |
| Kontrolní `.json` | Výsledek kontrol modelu, nikoli certifikace výtisku |

G-code není nutné běžně ukládat do repozitáře. Pokud je důležitý pro reprodukci, nejdřív ověř jeho původ a absenci soukromých dat; jinak stačí přesný záznam parametrů a omezení důkazů v deníku.

## Změny a návaznost

Po změně parametrů přepočítat model a exportovat nový STL z finálního objektu. Udržovat soulad FCStd, makra a náhledu; regenerace ze starého makra by ruční změny dokumentu ztratila. Poznámky modelu mají uvádět zadání, návrhové hodnoty, provedené kontroly a neověřené funkční požadavky.

Stavy zapisovat odděleně: **geometrie ověřena → připraveno ve sliceru → uživatel zahájil tisk → dokončení potvrzeno → fyzický výsledek vyhodnocen**. Poslední dva stavy nelze odvodit z vytvoření STL či odeslání úlohy. Úspěch pro zamýšlený účel může navíc vyžadovat rozměrovou a funkční zkoušku.

Veškeré nové zkušenosti zapisovat do tohoto projektu, do příslušných docs, poznámek modelu a [deníku](denik-tisku.md). Původní soubory mimo checkout jsou zachované kopie, nikoli další místo pro rozvíjení modelu.

## Elektronika a vybavení

Zapojení, zkoušky a aktuální stav elektronického projektu patří do [samostatné sekce](../elektronika/README.md); mechanický model na ně odkazuje. U autíčka je výchozí [přehled elektroniky](../elektronika/auticko/README.md), zatímco zdroj programu zůstává u mechanického modelu. Staré cesty elektronických poznámek obsahují jen přesměrování, ne další kopii historie.

Nový nákup zapisovat do [kanonického inventáře](../elektronika/vybaveni.md) s původem potvrzení. Neznámé počty a parametry ponechat neznámé. To, že uživatel vlastní páječku nebo nové baterie, nepotvrzuje zapájené spoje ani výměnu článků v sestavě.

U elektroniky oddělovat návrh a skutečné zapojení, kontrolu zdroje a překlad, upload konkrétní verze a fyzickou zkoušku. Ke zkoušce zaznamenat použitý program, zdroj napájení, podmínky a přesné hlášení uživatele. Novější pracovní zdroj nemusí odpovídat nahranému programu; dřívější fyzický úspěch není důkazem funkce nové verze. Historické podmínky uchovat a aktuální stav uvést zvlášť.
