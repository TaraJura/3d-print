# V02 bez wipe – kandidát pro další zkoušku TPU

[**Nastavená podložka V02**](podlozka-01-v02-bez-wipe-kobra-x-alzament-tpu95a.3mf) je samostatný projekt s pěti vzorky, profily a G-code. **Jde o kandidáta pro další test až po ověření průchodnosti podávání a určení fáze původního zastavení. Oprava chyby 11833 není potvrzená.** Původní V01 a její soubory zůstaly zachované; nic nebylo odesláno tiskárně.

Změny proti V01 jsou úmyslně úzké:

- **Wipe při retrakci vypnutý.** V01 obsahovala záporné E během velmi krátkých XY pohybů, s vysokou odvozenou rychlostí filamentu.
- Délka retrakce zůstává **0,8 mm**; retrakce i návrat filamentu jsou výslovně nastavené na **20 mm/s**.
- Samostatný požadavek na retrakci při změně vrstvy je vypnutý. Retrakce při potřebných přejezdech zůstávají.
- Název exportovaného G-code nově obsahuje **`V02-bez-wipe`**.

Geometrie, rozmístění, tiskárna, teploty **225/60 °C**, startovací makro a mapování zůstávají stejné. Odhad sliceru je **1 h 21 min 51 s / 9,79 g**. Teplotní varování při 60 °C a rozpor technického listu s produktovou stránkou přetrvávají, viz [původní dokumentace](../README.md#zachované-teplotní-varování).

[Oficiální průvodce Kobra X pro TPU](https://wiki.anycubic.com/en/fdm-3d-printer/anycubic-kobra-x/tpu-printing-guide), ověřený 24. 10. 2026, doporučuje vypnout „Wipe While Retracting“; uvádí retrakci 1,2 mm při 30 mm/s. **Našich 0,8 mm při 20 mm/s je konzervativní návrh, nikoli převzatá hodnota výrobce nebo fyzická kalibrace Alzamentu.**

## Ověření a jeho hranice

Projekt byl nativně exportovaný, znovu načtený a nařezaný. [Kontrola V02](kontrola-v02.json) dokládá zachování všech pěti geometrií a poloh, 60 vrstev kroužků, úplnost tenkých obvodových drah a přesný seznam změněných nastavení. Náhledy rozmístění a modelových drah jsou po bajtech shodné s ověřenou V01.

Audit zpracoval **54 524 explicitních pohybů s E**, včetně kladných, záporných a samostatných E pohybů. Výsledek: **0 záporných E spojených s pohybem XYZ, žádné značky wipe**, všech 493 samostatných retrakcí a 492 návratů má délku 0,8 mm a rychlost 20 mm/s. Samostatně je zaznamenaný jeden úsek s XYZ zaokrouhleným na stejný bod, kladným E 0,00001 mm a zachovaným modelovým posuvem 25 mm/s; nebyl z auditu vynechán. Modelový posuv zůstává nejvýše 25 mm/s.

Start stále volá **`G9111 bedTemp=60 extruderTemp=225`**. Jeho vnitřní ohřev, čekání, purge, rychlost zavádění a kontrola zaseknutí jsou ve firmwaru a **tento audit je neověřuje**. Vypnutí wipe nemůže samo prokázat nápravu zastavení, které nastalo ještě uvnitř tohoto makra. Skutečné motorové rychlosti, průchodnost, první vrstva a výsledek V02 dosud nejsou fyzicky ověřené.

## Soubory

- [Projekt V02](podlozka-01-v02-bez-wipe-kobra-x-alzament-tpu95a.3mf) – otevřít jednou jako celý projekt, pět kusů již připravených.
- [Geometry-only alternativa](podlozka-01-v02-geometrie.3mf) – bez profilů a G-code; nepřidávat jako dalších pět kusů.
- [Číslovaný náhled](podlozka-01.png), [vrstvy](podlozka-01-vrstvy.png), [detail kroužků](krouzky-detail-drah.png).
- [Generátor V02](pripravit-v02.py), [proces](proces-v02-kobra-x-tpu.json), [filament](filament-v02-alzament-tpu95a.json), [kontrola rozmístění](kontrola-rozlozeni-v02.json).

Generátor čte zachované vstupy V01 a její kontrolní funkce, zapisuje jen do této podsložky a nikdy nekomunikuje s tiskárnou. Lokální mezisoubory jsou v ignorované `.cache/`.
