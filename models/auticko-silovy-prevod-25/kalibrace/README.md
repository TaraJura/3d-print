# Kalibrace tištěných uložení a klíče

Malé samostatné vzorky pro chystané silové autíčko. **Návrhové rozměry, zatím bez fyzického tisku a měření.** Kalibrace pomůže vybrat otvor; nepotvrzuje souosost celého rámu, pevnost dlouhé osy, nosnost ani přenos momentu.

- [Balíček 8 kusů](kalibracni-dily.zip): každý STL vytisknout jednou, jednotky mm, měřítko **100 %**.
- [Editovatelný FreeCAD](kalibrace.FCStd), [zdrojové makro](kalibrace.FCMacro), [skutečný CAD náhled](nahled.png).
- [Geometrická kontrola](kontrola-kalibrace.json), [kontrola exportů](overeni-exportu.json), [ověřovací skript](overit-exporty.py).

## Které díly použít

| STL | Otvory / rozměr | Význam |
|---|---|---|
| [otvory-8-svisle](stl/otvory-8-svisle.stl) | 8,1 / 8,2 / 8,3 / 8,4 / 8,6 mm | otvory nábojů mezikol, při tisku osa Z |
| [otvory-8-vodorovne](stl/otvory-8-vodorovne.stl) | stejné | vodorovné otvory podpěr čepu, osa Y |
| [otvory-12-svisle](stl/otvory-12-svisle.stl) | 12,1 / 12,2 / 12,3 / 12,4 / 12,6 mm | otvor velkého kola/náboje, osa Z |
| [otvory-12-vodorovne](stl/otvory-12-vodorovne.stl) | stejné | pracovní uložení zadní osy v rámu, osa Y |
| [otvory-4-svisle](stl/otvory-4-svisle.stl) | 4,1 / 4,2 / 4,3 mm | základní fit příčného klíče; nenahrazuje zkoušku skutečného příčného otvoru v ose |
| [čep 8](stl/cep-8-kulaty-nalezato.stl) | Ø8 × 24 mm | plně kruhový referenční čep |
| [čep 12](stl/cep-12-kulaty-nalezato.stl) | Ø12 × 24 mm | plně kruhový referenční čep |
| [čep 4](stl/cep-4-kulaty-nalezato.stl) | Ø4 × 24 mm | vzorek klíče |

Hloubka každého otvoru je **8 mm**. Stěny hlavních bloků mají nominálně nejméně **2,7 mm**; každý blok včetně orientačního výstupku je jediný solid. Na dílech nejsou vyražená čísla: malý plochý výstupek na jednom konci vždy označuje začátek řady, tedy **nejmenší otvor**. Otvory počítej od výstupku; otočení destičky z druhé strany pořadí nemění.

```text
výstupek →  1     2     3     4     5
Ø8 řada:   8,1   8,2   8,3   8,4   8,6
Ø12 řada: 12,1  12,2  12,3  12,4  12,6
Ø4 řada:   4,1   4,2   4,3
```

## Tisk a vyhodnocení

STL už mají zamýšlenou orientaci na Z0. Nepoužívat automatickou orientaci ani měnit měřítko. Zvol stejný materiál, vrstvy, kompenzaci otvorů a další nastavení jako u skutečných dílů. Svislé a vodorovné otvory se vyhodnocují zvlášť; jejich výsledek nepřenášet automaticky mezi orientacemi.

**Všechny tři čepy se tisknou naležato jako úplné válce a potřebují podpory spodního oblouku.** Není na nich pracovní D ploška. Před tiskem ověř podporu ve vrstveném náhledu, po tisku ji pečlivě odstraň bez poškození kluzného povrchu. Stopy podpor i případné broušení ovlivňují výsledek; zapiš je a totéž zpracování zopakuj u konečné osy. Vodorovné otvory mají klenutý strop, který může po tisku klesnout; pokud pro ně použiješ podpory či jiné opracování, postup musí odpovídat finálnímu rámu. Tento balíček neobsahuje slicerový profil ani G-code a neslibuje tisk bez úpravy podpor.

1. Odstranit volné otřepy a podpory. Pokud máš měřidlo, zapsat skutečný průměr čepu v několika směrech; nominální Ø8 nebo Ø12 není změřený výsledek.
2. Pro rotující kluzné uložení vybrat nejmenší otvor, ve kterém čistý čep projde celou hloubkou a lehce se otočí po celé otáčce bez tlačení. Nepoužívat lepidlo ani olej k zakrytí špatného fitu.
3. Pevný čep v podpoře může potřebovat jiný fit než rotující mezikolo. Zajištění pevného čepu a příčného klíče musí řešit konstrukce; samotná těsná dírka není důkazem přenosu momentu.
4. Zapsat pro každou destičku číslo otvoru, skutečný chod, boční vůli a způsob očištění. Podle výsledku upravit odpovídající parametr hlavního modelu; nesnížit automaticky všechny vůle současně.

Po vytištění vzorků ještě musí následovat zkouška skutečné délky osy, obou souosých podpor, čelních stohů a převodu bez motoru. Krátký vzorek se může otáčet lehce i při chybě souososti celého rámu.

## Reprodukce a rozsah kontroly

[Makro](kalibrace.FCMacro) vytváří běžné objekty Part, výrazy a tabulku Parameters; přepisuje výhradně soubory této kalibrační složky. [Náhledové makro](nahled.FCMacro) nastaví viditelnost osmi dílů, uloží skutečný PNG a model znovu otevře. Rozložení v náhledu je přehled dílů, **nikoli hotová tisková podložka**.

Provedené kontroly: 8 platných jednodílných těles, 23 průchozích otvorů s materiálem za jejich obvodem, uzavřené orientované STL, minimum Z0, shodné kopie v ZIP a opětovné otevření FCStd. Tyto kontroly nevytvářejí fyzicky ověřené tiskové tolerance.
