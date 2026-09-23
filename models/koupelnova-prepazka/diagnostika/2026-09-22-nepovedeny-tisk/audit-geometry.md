# Nezávislý audit zachované geometrie přepážky

Čteny přímo vrcholy, trojúhelníky, komponenty a build transformace všech 3MF; staré kontrolní JSON nebyly zdrojem výsledků.
Evidence: 84 souborů; SHA-256 všech souborů před a po auditu shodné.

| 3MF | Nastavený projekt / vložený G-code | Počet dílů | Rozměry výsledných dílů mm | Z po všech transformacích mm |
|---|---|---:|---|---|
| `revize-02-8mm/historie/reference-10mm/rozlozeni/EXPERIMENT-prepazka-B-Alzament-TPU95A.3mf` | ano / ano | 3 | 196.000000 × 20.000000 × 9.999418; 202.000000 × 20.000000 × 9.999418; 196.000000 × 20.000000 × 9.999418 | 0.00000000–9.99941826; 0.00000000–9.99941826; 0.00000000–9.99941826 |
| `revize-02-8mm/historie/reference-10mm/rozlozeni/prepazka-B-pracovni-geometrie.3mf` | ne / ne | 3 | 196.000000 × 20.000000 × 9.999418; 202.000000 × 20.000000 × 9.999418; 196.000000 × 20.000000 × 9.999418 | 0.00000000–9.99941826; 0.00000000–9.99941826; 0.00000000–9.99941826 |
| `revize-02-8mm/rozlozeni/EXPERIMENT-prepazka-B-Alzament-TPU95A.3mf` | ano / ano | 3 | 193.000000 × 20.000000 × 7.999606; 200.000000 × 20.000000 × 7.999606; 193.000000 × 20.000000 × 7.999606 | 0.00000000–7.99960614; 0.00000000–7.99960614; 0.00000000–7.99960614 |
| `revize-02-8mm/rozlozeni/TEST-EXPERIMENT-spoj-Alzament-TPU95A.3mf` | ano / ano | 2 | 30.000000 × 20.000000 × 7.999606; 30.000000 × 20.000000 × 7.999606 | 0.00000000–7.99960614; 0.00000000–7.99960614 |
| `revize-02-8mm/rozlozeni/TEST-spoj-pracovni-geometrie.3mf` | ne / ne | 2 | 30.000000 × 20.000000 × 7.999606; 30.000000 × 20.000000 × 7.999606 | 0.00000000–7.99960613; 0.00000000–7.99960613 |
| `revize-02-8mm/rozlozeni/prepazka-B-pracovni-geometrie.3mf` | ne / ne | 3 | 193.000000 × 20.000000 × 7.999606; 200.000000 × 20.000000 × 7.999606; 193.000000 × 20.000000 × 7.999606 | 0.00000000–7.99960613; 0.00000000–7.99960613; 0.00000000–7.99960613 |

## Výsledek geometrické kontroly

- Všechny 3MF mají explicitní jednotku millimeter. Lineární části všech component/build transformací jsou jednotkové: žádné zmenšení, zploštění ani rotace.
- Všechny vložené mesh objekty jsou type=model. V nastavených projektech jsou díly subtype=normal_part, extruder=1 a build printable=1. Žádné lepidlo, negativní objem ani modifikátor.
- Každá výsledná síť je jedna souvislá uzavřená orientovaná komponenta, s nenulovým kladným objemem, bez hran s jiným počtem než dva sousední trojúhelníky a bez degenerovaných trojúhelníků.
- Všechny build díly dosedají na Z=0, s kladnou plochou spodního rovinného dosedu. U nastavených projektů jsou raw sítě centrované kolem nuly; build posun o polovinu výšky je správný, není to odsazení nad podložku.
- Všechny výsledné mesh odpovídají příslušným uloženým STL po odstranění posunu a kvantizaci 0,00001 mm. Žádné 3MF neobsahuje pouze 2mm lepicí lože.
- TEST má dva díly 30 × 20 × 7,99960614 mm. Aktuální velký projekt má 193/200/193 × 20 × 7,99960614 mm. Historický projekt má 196/202/196 × 20 × 9,99941826 mm.

## Co tento audit neprokazuje

Skutečně tištěný soubor a úprava při kopírování dílu z jiného projektu nejsou identifikovány. Z těchto původních souborů nelze dovodit zachování jejich nastavení po kopírování/importu. Import geometrie může použít nastavení cílového projektu; zde se ověřuje uložená geometrie, nikoli konkrétní uživatelský postup.
Audit nevysvětluje chování extruze ani nepotvrzuje vhodnost dalšího tisku. G-code posuzuje samostatný audit. Není proveden úplný test samoprůniků trojúhelníků ani přepočet CAD BREP.

## Zachování důkazů

Nebylo spuštěno FreeCAD makro, FreeCAD, slicer ani ovládání tiskárny. Zápis pouze audit-geometry.py/json/md v této diagnostické složce mimo evidence/.
Podrobný strojově čitelný výsledek, všechny transformace, příznaky, objemy, počty trojúhelníků, parametry FCStd a SHA-256 jsou v audit-geometry.json.
