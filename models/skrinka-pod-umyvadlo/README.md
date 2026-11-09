# Černá skříňka pod umyvadlo

Návrh z 5. 10. 2026 podle tří Jiřího fotografií a zadání „délka umyvadla 37, šířka 18, výška skříňky 55 cm“. Černý závěsný kryt rozvodů má **vnější rozměry 370 × 180 × 550 mm**, dvoje přední dveře, šest integrovaných pantů a otevřená záda, vršek i střed dna. Nasazuje se kolem stávajícího odpadu a přívodů; nevyžaduje jejich odpojení. Nemá středový sloupek ani police u ventilů.

**Jde o geometricky ověřený tiskový prototyp.** Zadaná šířka a hloubka patří umyvadlu; použití stejných rozměrů pro kryt je návrhová volba. Fotografie nejsou měřením potrubí ani stěny. Skříňka nenese umyvadlo a navržené lepené spoje, čepy, kotvení a fyzický tisk zatím nejsou vyzkoušené.

## Soubory

- [skrinka.FCStd](skrinka.FCStd) – editovatelný FreeCAD s tabulkou parametrů, běžnými Part objekty, výrazy a 54 kopiemi dílů v sestavě.
- [skrinka.FCMacro](skrinka.FCMacro) – zdroj; regenerace přepíše zdejší FCStd, STL, kusovník a geometrický kontrolní JSON. Nativní přepočet uloženého dokumentu makro nepotřebuje.
- [nahled.FCMacro](nahled.FCMacro) – skutečné CAD náhledy zavřených a otevřených dveří. Umyvadlo v kontextovém náhledu je pouze schematická reference, nikoli přesný model keramiky z fotografií.
- [stl](stl/) a [dily.json](dily.json) – 13 typů v tiskové orientaci, dohromady **54 fyzických kusů**.
- [Připravené podložky](rozlozeni/README.md) – každou nastavenou 3MF otevřít jednou jako celý projekt. Počty se už nenásobí.
- [kontrola-modelu.json](kontrola-modelu.json), [kontrola-nahledu.json](kontrola-nahledu.json), [nezavisly-audit.json](nezavisly-audit.json) – provedené CAD a render kontroly.

## Rozměry a konstrukce

| Údaj | Hodnota | Původ |
|---|---:|---|
| Šířka / hloubka umyvadla | 370 / 180 mm | Přímé zadání Jiřího, převedeno z cm |
| Vnější šířka / hloubka krytu | 370 / 180 mm | Návrh podle rozměrů umyvadla |
| Výška krytu | 550 mm | Přímé zadání Jiřího |
| Panely | 4 mm | Návrh pro tisk |
| Boční segmenty | 183 mm × 176,5 mm; výztuha vystupuje dovnitř do 20 mm | CAD |
| Plocha jedněch dveří | 164 × 546 mm včetně dvou 0,5mm spár | CAD; šířka včetně lokálního pantu je větší |
| Spáry | 2 mm nahoře, dole a mezi dveřmi; 0,5 mm ve dvou vodorovných švech | Návrh |
| Panty | 3 na každých dveřích, čep Ø4 mm, kruhová část otvoru Ø4,6 mm | Návrh; teardrop otvor pro tisk bez podpor |
| Montážní otvory | 4, kruhová část Ø5,5 mm; X = 30 / 340, Z = 6 / 544 mm | Návrh; skutečné šrouby nejsou zadané |

Přední hrana je v Y = 180 mm, zadní montážní rovina Y = 0. Vnitřní volná hloubka před plochou dveří je nejvýše 176 mm; u příček, pantů, spojek a zapuštěných bočních lišt je menší. Otevřená záda dovolují obejít stávající nástěnné rozvody. Horní a spodní obvod zpevňují příčky; uprostřed dna není plošná deska.

Obě dveře se v tabulce otevírají parametry `LeftOpening` a `RightOpening` v rozsahu **0–90°**. CAD zkontroloval jejich průběh po 15°. Model nemá samostatný fyzický doraz ani magnetickou západku; na místě nepřetáčet pravé dveře do boční stěny. Volná šířka mezi bočními panely je 362 mm, místně ji zmenšují pouzdra pantů a spoje.

## Kusovník

| Díly | Kusů |
|---|---:|
| Boční segment, společný soubor | 6 |
| Levé dveře: dolní / střední / horní s úchopem | 1 + 1 + 1 |
| Pravé dveře: dolní / střední / horní s úchopem | 1 + 1 + 1 |
| Poloviny předních příček | 4 |
| Poloviny zadních příček s montážním otvorem | 4 |
| Spojky panelů 80 × 20 × 4 mm | 16 |
| Spojky příček 50 × 12 × 4 mm | 4 |
| Rohové úhelníky | 8 |
| Čepy pantů | 6 |
| **Celkem** | **54** |

## Montážní návrh

1. Před celým tiskem ověř největší vyložení ventilů/hadic od zadní zdi, šířku celého jejich obrysu, výšku od spodní roviny keramiky pod nejnižší bod sifonu a místo pro dveře u WC. Hodnota 180 mm sama neprokazuje, že všechny rozvody vejdou dovnitř. Kryt posadit pod keramiku s malou mezerou; výška této mezery není změřená.
2. Každý bok vytvoř ze tří segmentů se dvěma 0,5mm spárami. Přes každý šev použij dvě spojky: zadní na vnitřním boku v pásu Y = 24–44 mm; přední otočenou o 90° kolem Z za zapuštěnou lištou (levá X = 4–24 mm, Y = 158–162 mm, pravá zrcadlově). Přední spojka současně zakryje průhled švem a přilepí se na zadní plochy obou lišt. Pro pravý bok otoč stejné boční výtisky o 180° kolem podélné osy Y; souměrná horní/dolní pouzdra si vymění pozice. Pouhé přesunutí levého segmentu napravo nestačí.
3. Každé dveře sestav ze správných tří levých nebo pravých segmentů. Na zadní straně dej dvě spojky přes každý šev, na levých dveřích X = 45–65 a 140–160 mm; pravé zrcadlově. Horní segmenty mají uprostřed půlkruhové úchopy.
4. Každou ze čtyř obvodových příček sestav ze dvou polovin. Vnitřní spojku umísti přes středový spoj, poté příčky spoj s boky a osmi rohovými úhelníky. Otvory pro kotvení patří na zadní příčky.
5. Konstrukce počítá s lepením panelových a rámových spojů. Použít lepidlo vhodné pro skutečně zvolený filament a koupelnové prostředí, připravit povrchy dle jeho výrobce. Konkrétní lepidlo ani únosnost lepení nejsou potvrzené. Čepy a funkční pantové mezery nelepit; nejdřív sestavit nasucho a vyzkoušet vzájemné dosednutí.
6. Dveře vlož mezi pevná pouzdra. V každém pantu zůstane nad i pod prostředním pouzdrem nominálně 2 mm axiální mezera. Šest čepů vlož hlavou shora; zůstávají vyjímatelné. Vyzkoušej pohyb a vůle před lepením celé sestavy. Čepy se tisknou nastojato na Ø7mm hlavě, ne naležato na dříku.
7. Celý lehký kryt upevni nezávisle do skutečné stěny přes čtyři otvory. Kotvy a šrouby vybrat podle podkladu a skutečného vedení instalací. Typ podkladu, kotvy ani vrtací místa nejsou ověřené. Horní čepy je vhodné vložit ještě před montáží pod keramiku.

Žádný bod není potvrzenou fyzickou montáží. Spáry a pantové vůle mohou po tisku potřebovat úpravu. Příčky nejsou police a skříňka nebyla navržena pro další zatížení.

## Kontroly a tisk

Geometrický generátor ověřil jednotlivé validní solidy, uzavřenost STL, obálku 370 × 180 × 550 mm, skutečných 54 kopií, změnu šířky 370 → 380 → 370 mm a pohyb obou dveří po 15° od 0 do 90° bez objemové kolize s korpusem. Nezávislé otevření finálního FCStd navíc ověřilo nulové objemové průniky mezi všemi 54 fyzickými kusy, pohyb dveří po 5° i nesouměrné otevření a radiální mezeru čep/pouzdra 0,300 mm. Všech 28 spojek/úhelníků má plošný kontakt s nejméně dvěma příslušnými díly; přední krycí spojky mají nominálně 603 mm² s každým sousedním segmentem. Plocha kontaktu není změřená pevnost lepení. Audit zaznamenává hash makra a geometrickou obálku/objem každé kopie; GUI následně pouze ukládá viditelnost a kameru. Konfigurace a kontroly sliceru jsou v [přehledu podložek](rozlozeni/README.md).

Používá se Kobra X 0,4 mm a návrhový černý PLA Basic. Tento prototyp ani profil nejsou fyzicky kalibrované. Barva modelu nenastavuje skutečnou cívku. Všechny místní počítačové kontroly se vztahují k této geometrii; nezakládají potvrzení, že kryt sedí kolem skutečného potrubí, že lepení drží, že se dveře nekříží s WC, ani že tisk proběhl úspěšně.

Původ fotografií: `/home/novakj/Downloads/20261005_155821.jpg`, `20261005_155825.jpg`, `20261005_155830.jpg`. Jde o uživatelem dodané obrazové reference bez měřítka pro polohu jednotlivých trubek. Zdrojové fotografie nebyly upravovány.
