# Konstrukce tiskového prototypu 25:1 se SG90

Aktuální revize 20. 9. 2026 zachovává původní profil 20° / modul 1, rozteče a vnější tvar sestavy. Mění otvory podle výsledků kalibrace a odděluje kluzná uložení od pevných spojů. Celá sada se předává na výslovné zadání jako nominálně ověřený tiskový prototyp bez dalších povinných vzorků. [Soubory a kusovník](README.md), [montáž](montaz.md), [historie rozhodnutí](revize-fitu-2026-09-20.md).

## Převod a uspořádání

| Stupeň | Zuby | Poměr | Osová vzdálenost | Pracovní šířky v ose Y |
|---|---|---:|---:|---|
| Motor → A | 18 → 54 | 3 | 36,4 mm | Motor: 14,5…19,5; A54: 12…20 mm |
| A → B | 18 → 60 | 10/3 | 39,4 mm | A18: 0…8; B60: −2…10 mm |
| B → zadní osa | 22 → 55 | 2,5 | 38,9 mm | B22: −16…−8; výstup55: −18…−6 mm |

Součin je **25:1**. Hlavy malých kol mají 1,1m, velkých 1,2m, paty 1,25m a posunutí profilu je nulové. Osy mají společnou výšku Z28; zadní osa je X35, B73,9, A113,3 a motor149,7 mm. Tři vnější záběry obracejí směr vůči motoru.

Proti 12:1 je ideální moment na stejné ose 2,083× a rychlost 48 %, před ztrátami. Volba 25:1 proti zvažovaným 16:1 a 36:1 ponechává hrubší modul 1, poslední 22zubý pastorek a nominální světlost ozubení 6,8 mm při kolech Ø76. Při hypotetickém dosedu na kořen dezénu Ø74 je světlost 5,8 mm. Varianta 36:1 s věncem Ø74 by při stejných kolech měla jen 1 mm. Toto je geometrické porovnání, nikoli naměřená síla, účinnost či nosnost. Původní úplné porovnání je zachované v [archivu](historie/pred-kalibraci-8_6-12_6-2026-09-20/README.md).

Volba 22→55 u posledního stupně ponechává 1,7 mm nominálního odstupu mezi obálkou 60zubého kola a zadní Ø12 osou. Příčný klínek leží mimo rovinu B60: výstupní náboj pokračuje k Y−28 a klínek je v Y−23. Výstup55 leží v Y−18…−6.

## Uložení podle funkce

| Parametr | Hodnota | Funkce |
|---|---:|---|
| `RunningBore` | 8,6 mm | Mezikola na pevných Ø8 čepech |
| `FixedSeatBore` | 8,1 mm | Pevné čepy v obou podpěrách rámu |
| `RearBearingBore` | 12,6 mm | Otáčení zadní Ø12 osy v rámu |
| `OutputBore` | 12,1 mm | Vedení pevného výstupního náboje na ose |
| `DriveBore` / `DriveFlat` | 12,1 / 4,05 mm | D spoj zadních kol; ploška osy je 4,00 mm od středu |
| `StaticLockBore` | 4,1 mm | Statické Ø4 zajišťovací čepy a příčný klíč |
| `DeckSocketBore` | 8,1 mm | Sedla plošiny |

Průměry samotných čepů a os zůstávají. Přední otočné Ø8 spoje mají nadále 8,6mm otvory, Ø6 klouby 6,5mm otvory, původní západkové pojistky se nemění. Zadní rozpěrky 17,6 mm zůstávají s 12,6mm průchodem.

Každý 30mm náboj A/B má dvě skutečně kruhová 5mm vodicí pásma a odlehčený 20mm střed Ø9. Menší kontaktní plocha sama o sobě nezaručuje nižší tření. Odlehčený střed nesmí být považován za náhradní vedení po opotřebení pásů. Hlavy pevných čepů se tvarově zajišťují mimo kluznou část. Zadní náboj přenáší moment příčným klínkem, zadní kola D ploškami; pojistky pouze určují axiální polohu.

Otáčení Ø8 v kalibračním otvoru 8,6 a subjektivně vyhovující nasazení Ø12 do 12,6 potvrdil uživatel. Skutečné průměry, radiální vůle, orientace a očištění konkrétního vzorku nejsou změřené. Pevné 8,1 / 12,1 / 4,1 jsou požadované návrhové hodnoty, nikoli fyzicky potvrzené lisované spoje.

## Nominální kontrola a radiální omezení

[Kontrola revize](kontrola-revize-fitu.json) porovnává šest skutečných obrysů ozubení se zachovaným archivem pomocí symetrického rozdílu 1mm extruzí. Obrysy jsou shodné; rozteče, fáze a kinematika se nemění. Proto lze s uvedeným původem převzít **nominální** část původních 65fázových kontrol záběru. Nově se kontroluje celá statická nominální sestava a změněné otvory. Nepřebírá se původní PASS pro jiné radiální vůle.

Pokud by se celý nominální přídavek otvoru choval jako skutečná provozní vůle, připadá na každé mezikolo ±0,35 mm (0,30 náboj/čep + 0,05 čep/rám). Výstup by měl ±0,35 mm (0,30 osa/rám + 0,05 náboj/osa), motor předpokládaných ±0,15 mm. Z toho vychází:

| Stupeň | Konzervativní relativní rozsah | Minimum / nominál / maximum rozteče | Ideální kontaktní poměr při maximu |
|---|---:|---|---:|
| 18→54 | ±0,50 mm | 35,90 / 36,40 / 36,90 mm | 1,04751 |
| 18→60 | ±0,70 mm | 38,70 / 39,40 / 40,10 mm | 0,88519 |
| 22→55 | ±0,70 mm | 38,20 / 38,90 / 39,60 mm | 0,90558 |

Druhý a třetí stupeň mají při maximálním oddálení kontaktní poměr pod 1; celý rozsah nelze prohlásit za souvislý záběr. Při minimálním přiblížení navíc hrozí střet profilu. **`full_nominal_radial_clearance_scenario_pass=false`.** Část přídavku může kompenzovat tiskové zmenšení otvoru, ale to není měření skutečné provozní vůle. Uživatel zvolil nominální tiskový prototyp s tímto omezením; scénář není vydáván za vyřešený ani použit jako podmínka dalšího vzorku.

Nepoužitý kandidát 14° / modul 1,1 skutečně neprošel kontrolou kořene. Jeho [diagnostika](revize-fitu-diagnostika/README.md) zůstává historickým důkazem, v současných dílech není.

## Axiální šířka záběru

Kontrola zahrnuje 16 společných krajních poloh A±0,2 / B±0,2 / výstup±0,3 / motor0…+0,4 mm. Výstupní rozsah zahrnuje posuv osy ±0,2 a vůli obou 4,1mm otvorů příčného klíče ±0,1 mm. Celý 8mm pastorek posledního stupně zůstává uvnitř 12mm věnce s nejmenší boční rezervou **1,5 mm**. První motorový záběr může poklesnout z 5 na 4,9 mm. [Výsledek skutečné CAD kontroly](kontrola-revize-fitu.json).

Tato axiální kontrola je oddělená od nepokrytého radiálního scénáře. Nevydává fyzický výtisk, pružnost ani opotřebení za známé.

## Řízení, podvozek a motor

Rám má délku 236 a šířku 112 mm, přední příčník 160 mm. Kingpiny jsou X190 / Y±72, ramena 20, spojnice 144 mm a osa SG90 X220 mm. V přímé poloze mají přední kola středy X186,3 / Y±87 a celkovou vnější šířku 186 mm. Plošina zachovává užitnou plochu 170 × 60 mm.

Řízení je rovnoběžníkové, nikoli Ackermannovo. Návrhový pracovní rozsah je ±25°, dorazy ±27°; smýkání při zatáčení a momentová rezerva serva nebyly fyzicky změřené. Originální páčka má potvrzený účinný poloměr 15 mm, servotáhlo délku 72,1734 mm. Originální drážkování a středový šroubek se zachovávají, tištěná objímka má vlastní Ø8 otočný čep. Podložka 1,8 mm nechává axiální volnost nejméně 0,4 mm. Konkrétní šířka a tloušťka páčky a tělo serva nejsou změřené.

Kinematika, rozmístění a vnější obálky řízení zůstaly shodné. Historické kontroly pohybu jsou v [nezávislém auditu revize](nezavisla-kontrola-revize.json) označené původním souborem, hashem a rozsahem, nikoli jako znovu spuštěná kontrola. Aktuální kontrola zahrnuje i 24 krajních párů u změněných otvorů objímky.

Motor je podle uživatele válcový Ø22,5 × 26 mm s 6mm hřídelkou; nový pastorek používá původní návrhový otvor 2,2 mm. Hřídelka nebyla přesně změřená, starý úspěšný pastorek nepotvrzuje nový výtisk. Dvě sedla, dva můstky a dva dlouhé společné čepy drží motor bez nově kupovaných spojů. Oba dlouhé čepy je třeba zasunout před mezikolem A. Zadní kontakty zůstávají přístupné.

## Co předání dokládá

34 typů STL tvoří 66 skutečných montážních instancí, včetně dvou předních a dvou zadních kol. Kontrola vede od uložené sestavy přes kusovník a 66 kopií v ZIPu ke třem 3MF s 26 / 27 / 13 objekty. Nový tisk, složení, skutečná vůle, zatížení a jízda této revize nejsou potvrzené. Soubory jsou geometrické podklady, nikoli G-code nebo nastavení podpor.
