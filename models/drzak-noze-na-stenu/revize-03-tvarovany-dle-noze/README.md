# Tvarovaný V držák nože — aktuální revize 03

Revize z 30. 10. 2026 navazuje na otevřený držák V02 a doplňuje Jiřím nově popsaný náběh čepele a rukojeť. Zůstává **jeden tištěný díl, dva vruty a volné vyjmutí shora**. Pod čepelí je šikmé užší V; pod rukojetí vyšší, mírně se rozšiřující sedlo. Mezi nimi zůstává 10 mm volný přechod nad nízkou spojovací patkou, aby pod neznámou záštitou nevznikla vysoká příčka.

[Hlavní skutečný CAD náhled](prehled-navrhu.png) · [boční obrys](nahled-profil.png).

## Rozměry: co je zadání a co výklad

| Údaj | mm | Původ |
|---|---:|---|
| Celková délka nože | 340 | Dřívější zadání |
| Největší výška čepele | 45 | Nově potvrzené zadání |
| Výška čepele o 100 mm směrem ke špičce | 40 | Nové zadání; směr ke špičce plyne z kontextu |
| Délka rukojeti | 105 | Nové zadání |
| Přechod od konce ostří k rukojeti | 10 | Zadání; přesné koncové body nebyly ukázány |
| Max. šířka rukojeti | 25 | Dřívější zadání |
| Výškový odskok spodku rukojeti | 20 | **Pracovní výklad nejasné věty, nikoli potvrzený rozměr v této ose** |
| Délka čepele | 225 | **Odvozený předpoklad:**340 − 105 − 10, pokud jde o celý délkový řetězec |
| Šířka referenční rukojeti u začátku → na konci | 22 → 25 | 22 je návrh; pouze maximum25 je zadáno |
| Výška / průřez referenční rukojeti | 25 / elipsa | Návrh odvozený z nejasného20 mm odskoku a rovného hřbetu |
| Tloušťka referenční čepele | 2 | Ilustrace, nebyla zadána |

Výraz o „dvou centimetrech mínus“ nemá v přepisu jednoznačně určený směr a referenční body. Pro tento návrh je uložen jako parametr `HandleRiseAssumed`: **spodek rukojeti je o20 mm výš než nejnižší bod paty čepele**. Není zaměněn za další změřený podélný segment. Tento výklad je uveden i přímo na hlavním náhledu a lze jej samostatně změnit.

Také **rovný hřbet nože je předpoklad**. Zmenšení výšky 45 → 40 mm na100 mm se proto převádí na vzestup spodní hrany o 5 mm směrem ke špičce. Na dalších45 mm žlabu směrem k jeho levému konci je tento sklon pouze návrhově pokračován; skutečná křivka špičky není známá. Ilustrační obrys před známou stanicí je zjednodušený a neslouží jako měření.

## Geometrie držáku

| Údaj | Hodnota | Původ |
|---|---:|---|
| Délka × výška × hloubka od stěny | 230 × 60 × 42,314 mm | CAD |
| Rozteč dvou vrutů / průchozí otvory | 160 mm / 2×Ø5,5 mm | Návrh, skutečné vruty neznámé |
| Osy vrutů od levého dolního rohu | X35 a195, Y48 mm | CAD |
| Rozevření V pod čepelí | 12 mm | Návrh, skutečná tloušťka čepele neznámá |
| Rozevření V pod podepřenou částí rukojeti | 26 → 28,143 mm | Návrh podle referenčního rozšíření |
| Stěna V v příčném řezu / kořen | 3 mm / R2 mm | Návrh |
| Spojovací patka | 4 mm vysoká ×4 mm široká | Návrh |
| Volný přechod mezi sedly | X145–155 mm | Odvozený návrh; nad patkou zůstává otevřený |

Pata čepele leží v návrhu na X145 mm, začátek rukojeti na X155 mm a konec referenčního nože na X260 mm. Držák končí na X230 mm, takže konec rukojeti přečnívá30 mm; špička přečnívá na druhé straně80 mm. **To není určení těžiště. Špička a přečnívající ostří nejsou kryté.**

Výška sedla rukojeti se nezískala prostým zvednutím dnaV o20 mm. Široká rukojeť ve V sama sedí výše než tenká čepel. Polohy obou sedel jsou odvozeny od celé zvolené referenční geometrie a ověřeny společně. Pro eliptickou rukojeť je teoretický vrchol V odvozen ze vztahu `střed výšky − sqrt(polovýška² + pološířka²)`, s návrhovým digitálním odstupem0,15 mm. Tento odstup není potvrzená tisková kalibrace.

Ouška jsou proti V02 o 5 mm vyšší a osy otvorů jsou na Y48 místo 43 mm, aby nástroj Ø10 mm prošel nad zvýšeným sedlem. Vodorovná rozteč 160 mm zůstává. Spodní patka, stojiny a dvě žebra spojují obě sedla do jednoho dílu. Nejde o dva díly ani o odnímatelný kryt.

## Použití a omezení

Upevnit vodorovně dvěma vruty vhodnými pro skutečnou stěnu a zatížení. Návrhové hlavy Ø10×3 mm a přímý nástroj Ø10 mm mají zkontrolovaný přístup při vyjmutém noži. Nůž položit shora ostřím dolů, rukojeť do širšího sedla; vyjmout přímo nahoru za rukojeť. Žádné víko ani pojistku není nutné rozebírat.

Skutečný profil, tloušťka čepele, tvar přechodu, průřez a rozšíření rukojeti, těžiště, hmotnost a vruty nejsou kompletně změřené. Nůž na obrázcích je **bezkolizní ilustrační příklad podle uvedených bodů**, nikoli přesná kopie konkrétního nože. Barva je návrhová, ne potvrzení fyzické cívky. Kontakt ostří s plastem a jeho opotřebení, otřepy, stabilita, pevnost, kotvení a tisk musí být posouzeny fyzicky. Tiskárna nebyla ovládána.

## Digitální model a tisk

- [drzak.FCStd](drzak.FCStd): parametrický standardní FreeCAD, finální objekt `Holder`; plně omezené skici, výrazy, nativní lofty a booleany, bez Python proxy.
- [drzak.FCMacro](drzak.FCMacro): zdroj a geometrické/parametrické kontroly; nejisté hodnoty jsou samostatné parametry s původem.
- [STL — jeden kus](stl/drzak-tvarovany.stl): již v tiskové orientaci.
- [Nastavená 3MF](rozlozeni/podlozka-01-kobra-x-pla-projekt.3mf) a [dokumentace podložky](rozlozeni/README.md).
- [kontrola-modelu.json](kontrola-modelu.json), [audit-montaze.json](audit-montaze.json), [print-manifest.json](print-manifest.json).

Tisková orientace: instalovaná spodní patka, ouška a žebra na podložce, délka 230 mm leží v rovině podložky. StěnyV vyrůstají ze stojin pod 45°. Podložka obsahuje **1 kus / 300 vrstev**, skutečně **0 segmentů podpor**; odhad sliceru **54,32 g / 3 h 20 min 50 s**. Podložku otevřít jednou jako celý projekt, nemnožit ani nepřerovnávat. Použitý návrhový PLA proces:0,20 mm, 4 stěny,15 %gyroid, tryska 215/205°C, podložka 50°C, brim 3 mm. Fyzická cívka a kalibrace nejsou potvrzené.

Nezávislý montážní audit prošel **26/26 kontrolami** a odpovídá finálnímu SHA-256 dokumentu. Ověřeny platný jeden solid, uzavřená jednokomponentová STL, nativní přepočet změn náběhu a rukojeti, bezkolizní celá rigidní ilustrace a její zdvih60 mm, otevřený10 mm přechod, vruty a přístup nástroje. Parametrický test dočasně změnil výšku stanice 40 → 39 mm, délku rukojeti 105 → 110 mm a předpokládaný odskok 20 → 18 mm a poté obnovil finální stav. Uložení a opětovné otevření FCStd ukazuje jen držák; reference jsou skryté.

U eliptického loftu rukojeti běžný FreeCAD `BoundBox` zahrnuje i volné NURBS meze a vracel širší box. Přesná kontrola používá `optimalBoundingBox` a jemnou tessellaci; referenční obálka je340×45×25 mm. Nejde o změnu rozměru nože.

Kontrola skutečných drah prošla první i všechny další vrstvy, bez nových nepřipojených ostrovů. Vrcholy otvorů uzavírají krátké mosty v Z 51 mm. Nad patkou nepřechází přes 10 mm mezeru žádná extruze. Odhadovaný průběh a mostky nejsou fyzický výsledek. Slicer má dokumentované hlášky o timelapse a exclude triangles; řez není označen jako bezvarovný. Podrobnosti a snímky jsou v [kontrole drah](rozlozeni/kontrola-drah-vizualne.md).

## Regenerace a předchozí varianty

Makro přepisuje pouze vlastní FCStd, STL a JSON vedle sebe. Před spuštěním uložit a zavřít stejnojmenný otevřený dokument. Změny tabulky sladit se zdrojovým makrem; referenční nůž se obnovuje při regeneraci, samotná editace parametrů neobnoví jeho statickou ilustraci ani STL/PNG.

Spustit přes skutečný FreeCAD 1.1.3 (`/home/novakj/.cache/freecad-shelf-1.1.3/runtime/AppRun freecadcmd`) s oddělenými konfiguracemi dle projektové dokumentace. Následně spustit GUI `nahled.FCMacro`, nezávislý `audit-montaze.FCMacro`, `python3 sestavit-nahled.py` a `python3 build_print_projects.py`. Runtime není součástí modelu.

Původní [rovný otevřený držák V02](../revize-02-otevrene-v/README.md) i [uzavřené pouzdro V01](../historie/v01-uzavrene-pouzdro/README.md) zůstávají zachované jako historie.
