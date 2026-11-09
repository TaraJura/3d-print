# Nástěnný kryt pro tři zesilovače

**Aktuální je [V03 — PCB položené na otevřené podpěry](revize-03-volne-polozeni/README.md).** Jiří 22. 10. 2026 upřesnil, že kondenzátory dosahují k horním hranám PCB: horní lemy PCB drážek jsou odstraněné, desky se položí na spodní opěry. PCB zůstává přesně **78 × 108 mm**, čelo se stále nasouvá shora a jistí M3 šroubem.

[FreeCAD V03](revize-03-volne-polozeni/kryt.FCStd) · [Detail položení PCB](revize-03-volne-polozeni/detail-polozeni-pcb.png) · [Podpěry v těle](revize-03-volne-polozeni/nahled-podpory.png) · [Tiskové podložky](revize-03-volne-polozeni/rozlozeni/README.md)

**Výška osazení zůstává nezměřená.** Hodnota 38 mm nad PCB je zástupná; před tiskem celé sady je potřeba doplnit skutečné měření. Tělo má 88,4 × 134 × 157,2 mm. Fyzický fit, chlazení a vhodnost materiálu nejsou ověřené. [V02 s původními PCB drážkami](revize-02-posuvne-celo/README.md) zůstává historickou variantou, kterou V03 nahrazuje.

## Historický koncept v01 — 21. 10. 2026


Zadání Jiřího 21. 10. 2026: společný hezký kryt pro tři vyfotografované zesilovače, montáž na stěnu, pohodlné ovládání hlasitosti a zadní průchod kabeláže.

**Historický stav v01: rozpracovaný prostorový koncept, čekal na rozměry. Není připravený k výrobě ani k osazení elektronikou.** Fotografie nemají měřítko; žádný mechanický rozměr desek, otvorů, ovladačů ani konektorů není potvrzený.

## Návrh

Tři vodorovné desky nad sebou. Ovladače a přístup k RCA směřují dopředu, svorky do zadního kabelového prostoru. Boční a horní větrání, snímatelné čelo a vršek, tři vyjímatelné nosné rámečky. Zesílená záda se čtyřmi místy pro montáž na stěnu. Uvnitř za deskami je návrhová rezerva pro vedení kabelů a záda mají průchody; vnější odstup od zdi a odlehčení tahu se ještě musí doplnit podle kabeláže.

První koncept ponechává RCA přístupné vpředu. Případné skrytí a vyvedení RCA dozadu potřebuje rozměry skutečných zástrček, jejich ohybu a způsobu prodloužení. Polohy otvorů v čele jsou jen prostorové zástupné hodnoty.

## Co je doloženo

- Uživatel požaduje kryt pro **3 zesilovače**; fotografie ukazuje tři podobně osazené moduly.
- Na fotografiích jsou ventilátory, chladiče, dvě RCA na hraně s ovladačem a na opačné hraně svorky označené L+/L−, VCC/GND a R−/R+.
- Přesný model, výkon, napájecí napětí, ztrátové teplo a shodnost rozměrů všech tří modulů nebyly ověřeny. Starší záznam pravděpodobného PAM8403 v inventáři se s těmito deskami neztotožňuje.
- „2 kabely a 2×2 kabely“ zatím není potvrzené jako počet pro každý modul nebo pro celek; pravděpodobné rozlišení napájení a reproduktorových výstupů čeká na uživatele.

## Potřebná měření

1. Šířka a délka samotné PCB; nejvyšší součástka nad PCB a přesah pájení pod ní.
2. Rozteče a průměr montážních otvorů, vzdálenosti krajních otvorů od hran.
3. Poloha osy potenciometru a obou RCA vůči okraji desky; průměr a přesah knoflíku.
4. Obrys připojených RCA zástrček, vnější průměry kabelů a směr jejich vyvedení; potvrdit zadní RCA ano/ne.
5. Hmotnost tří modulů a vhodné vruty/kotvy podle skutečné stěny.

## Soubory a ověření konceptu v01

- [Editovatelný FreeCAD](koncept-v01/kryt.FCStd), [zdrojové makro](koncept-v01/kryt.FCMacro), [makro náhledů](koncept-v01/nahled.FCMacro).
- [Pohled zepředu](koncept-v01/nahled-zpredu.png), [vnitřní uspořádání](koncept-v01/nahled-vnitrek.png), [zadní průchody](koncept-v01/nahled-zezadu.png).
- [Kontrolní JSON](koncept-v01/kontrola-modelu.json), [předběžné geometrické podložky](koncept-v01/rozlozeni/README.md).
- 6 konstrukčních těles je validních, každé STL je uzavřená jedna komponenta; mezi těmito šesti tělesy není objemová kolize. Dokument byl po uložení znovu otevřen, pomocné konstrukční objekty jsou skryté. Barevné zástupné desky a ovladače zůstávají viditelné jako vysvětlení sestavy, netisknou se.
- Navržená skříňka má zatím **132 × 189,2 × 208 mm (šířka × hloubka × výška)**, bez předního přesahu knoflíků a bez budoucího odstupu od zdi. Tyto hodnoty nejsou odměřené z fotografií. Obálka jedné PCB 100 × 140 mm a výška 38 mm jsou pouze pracovní zástupné hodnoty.
- Chybí skutečné sloupky/otvory PCB, zajištění rámečků a spojení snímatelného čela/vršku, odstup od zdi a odlehčení tahu kabelů. Rámečky jsou zobrazené v zamýšlených polohách, zatím bez mechanického zachycení. Geometricky validní koncept proto **ještě nemůže držet zesilovače**.
- [Nedestruktivní kontrola parametrů](koncept-v01/kontrola-parametru.json): po změně šířky PCB, rozteče pater a výšky osazení přepočet nativních objektů proběhl a všech 6 dílů zůstalo jedním validním tělesem. Zkušební změny nebyly uloženy do předávaného CAD.
- Chlazení, materiál, provozní teplota, zatížení, montáž, slicer a fyzický tisk nebyly ověřeny.

## Návaznost

Pozorování elektroniky a nejasnosti kabeláže jsou v [projektu tří zesilovačů](../../elektronika/tri-zesilovace/README.md).


První variantu ukládáme odděleně do [koncept-v01](koncept-v01/). Hodnoty v tabulce CAD jsou výhradně **návrhové zástupné hodnoty**, nikoli měření z fotografií. Ověření uzavřenosti geometrie nenahrazuje ověření fitu, montáže, chlazení a materiálu. Připravený tiskový projekt se správným materiálem a kontrolou podpor vznikne až po doplnění rozhodných rozměrů. Případné 3MF označené KONCEPT obsahují pouze geometrii bez tiskového procesu a nejsou pokynem k tisku.

Zdrojové fotografie z uživatelského zadání: `/home/novakj/Downloads/9d49d0b2-5d10-4e9b-9f47-ca59e29a1755.jpeg`, `aa1b5d69-cac6-4a19-b158-470bd6cb148c.jpeg`, `dd6b0c7b-18c7-444e-a92b-b65dd134c36e.jpeg`, `e1978808-ed28-464d-a12b-e5cdae325d97.jpeg`. Fotografie nejsou rozměrový výkres.
