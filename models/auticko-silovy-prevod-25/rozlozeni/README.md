# V3 25:1 — aktuální tiskové podložky

**Další připravený tisk je [kombinovaná03,26 kusů na jedné podložce](kombinovana-03-2026-09-20/README.md).** Otevři [nastavený projekt](kombinovana-03-2026-09-20/auticko-25-kombinovana-03-nastaveny-projekt.3mf) jako celý projekt v Anycubic Slicer Next. Nic nemnož ani automaticky nerozmísťuj. Měřítko100 %, Kobra X0,4mm; proces a skutečné podpory jsou uložené a ověřené řezem.

26 = **13 dosud netištěných původní03 +7 oprav první várky +6 oprav druhé**. Tato jedna podložka nahrazuje samostatnou03 a všechny tři původní opravné podložky. Odhad19h37min17s /120,09g; není to fyzicky naměřený výsledek.

Fotografie druhé várky již dorazily. Nově se nahrazuje levá těhlice a pět čepů; pravá těhlice už je v prvních sedmi. **Na detail rámu a potvrzení víka objímky a obou motorových klínků se čeká.** Nejsou přidané bez důkazu, takže26 samo neuzavírá celý inventář. [Podrobný inventář](kombinovana-03-2026-09-20/inventar-druhe-varky.json).

## Přehled variant

| Varianta | Kusů | Význam |
|---|---:|---|
| [Kombinovaná03 — hotový Next projekt](kombinovana-03-2026-09-20/auticko-25-kombinovana-03-nastaveny-projekt.3mf) |26|Aktuální jedna podložka k pokračování |
| [Samostatná původní03](stojate-cepy-2026-09-20/README.md) |13|Pouze alternativa; její díly už jsou v kombinované26 |
| [Samostatná oprava první várky](dotisk-prvni-varky-2026-09-20/README.md) |7 ve3 úlohách|Pouze alternativa; všechny její díly už jsou v kombinované26 |
| [Původní01](auticko-25-podlozka-01.3mf) |26|Historický záznam částečně vadného tisku; neopakovat beze změny procesu |
| [Původní02](auticko-25-podlozka-02.3mf) |27|Historický záznam druhé částečně vadné várky; neopakovat beze změny procesu |

[Úplný kusovník původních66 kopií](kusovnik-podlozek.md), [montáž](../montaz.md). Kusovník celé konstrukce je zachovaný; kombinovaná26 nepřidává nové konstrukční typy.

## Ověření a omezení

Skutečný společný řez obsahuje všech26 modelů do plné výšky a podporu plošiny, osy a obou těhlic. Obálky všech extruzí včetně podpor, brimu a poloviny šířky čáry mají nejmenší mezeru3,56mm a okraj4,39mm. [Report](kombinovana-03-2026-09-20/overeni.json), [skutečné dráhy](kombinovana-03-2026-09-20/evidence/drahy-a-odstupy.png), [kritické vrstvy](kombinovana-03-2026-09-20/evidence/kriticke-vrstvy.png).

Plošina má2 stěny a15 % výplně, ostatních25 dílů4 stěny a100 %. Proces0,12mm se systémovým Anycubic PLA není kalibrací fyzické cívky Alzament. Projekt ukládá nastavení, geometry-only alternativa je neobsahuje. Přesné hodnoty, zaznamenaná varování a čištění podpor jsou v [návodu](kombinovana-03-2026-09-20/README.md). Fyzická stabilita150,6mm vysoké osy, pevnost, odstranitelnost podpor a montáž nebyly tímto výpočtem ověřeny. Tiskárna nebyla oslovena.

## Původní soubory a regenerace

Kanonický CAD, STL a ZIP zůstávají beze změny. Původní01 byla už dříve uložená jako Next projekt s vypnutými podporami a je zachovaná bitově. Původní02 má nově také podobu celého Next projektu (mtime20.9.2026 19:24:56) s vrstvou0,20mm a vypnutými podporami. Její hash je jiný než starší geometry-only soubor; všech27 meshů a rozmístění ale odpovídá kanonickému manifestu do0,00002mm. Kdo soubor uložil a jaký G-code byl opravdu tištěný, z toho nevyvozujeme. Aktuální02 nebyla přepsána ani vrácena. [Přesné hashe a kontrola](kombinovana-03-2026-09-20/overeni-zachovani.json).

Původní03 byla již dříve nahrazena variantou se stojatými čepy až po [archivaci staré03, manifestu i opravné sady](../historie/pred-stojatou-orientaci-2026-09-20/README-ARCHIV.md). Její aktuální geometrie a standalone projekt zůstávají alternativou, nikoli další úlohou navíc.

Kombinované rozložení vlastní [pripravit.py](kombinovana-03-2026-09-20/pripravit.py), proces [projekt.py](kombinovana-03-2026-09-20/projekt.py) a audit [overit.py](kombinovana-03-2026-09-20/overit.py). [Přesná reprodukce](kombinovana-03-2026-09-20/README.md#reprodukce). Starší kořenové reporty `overeni-3mf.json`, `overeni-rozlozeni.json` a `overeni-importu.json` popisují historické revize, nikoli kombinovanou26. XY-only nástroje záměrně odmítnou plné3D transformace; generický export nesmí přepsat kanonický adresář. Žádná regenerace nepřepisuje uživatelovy původní01/02.

![Aktuální26kusové rozložení](kombinovana-03-2026-09-20/podlozka.png)
