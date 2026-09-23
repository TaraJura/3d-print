# Revize po fyzické kalibraci 20. 9. 2026

**Nejnovější zadání:** předat kompletní tiskový prototyp na třech podložkách bez dalších povinných vzorků. Zachovat původní 20° profil a nominální rozteče, zapracovat fitové otvory 8,6 / 12,6 a oddělené pevné spoje. Nominální geometrie a úplnost jsou ověřené; scénář celé nominální CAD vůle jako skutečné provozní vůle zůstane explicitně nepokrytý. Historické poznámky o čekání na vzorek níže tím byly nahrazené.

**Aktuální předání:** celá sada 34 typů / 66 kusů je regenerovaná s původním 20° ozubením a novými otvory. [Tři podložky 26 / 27 / 13 kusů](rozlozeni/README.md), [aktuální zdroj a rozsah ověření](README.md). Dřívější kompletní CAD je zachovaný v [archivu](historie/pred-kalibraci-8_6-12_6-2026-09-20/README.md). Předává se pouze v projektu; staré kopie na ploše se dále nemění. Následující oddíly zachycují chronologii včetně později překonaných návrhů, nikoli další podmínky předání.

## Co uživatel skutečně potvrdil

| Vzorek | Uživatelské hlášení | Vazba na zmrazený návrh |
|---|---|---|
| Největší čep | Hezky se vejde jen do největší díry; další menší díra jej nepřijme. Přepis pořadí menší díry není jednoznačný. | Referenční čep Ø12; největší otvor řady je 12,6 mm. |
| Střední čep | „Úplně to samý, ta největší díra.“ | Referenční čep Ø8; největší otvor řady je 8,6 mm. |
| Nejmenší čep | Volné otáčení se nepodařilo v žádném otvoru, ani v největším. | Referenční čep Ø4; původní řada končí 4,3 mm. |

Čísla jsou nominální rozměry skutečně předaných kalibračních modelů, nikoli posuvným měřítkem změřené výtisky. V pozdějším hlasovém doplnění uživatel u Ø8 výslovně potvrdil „Otáčí se, otáčí se“. Otáčení Ø8 čepu v největším otvoru 8,6 je tedy potvrzené. Velikost bočního viklání tím jednoznačně zodpovězená není. U Ø12 zůstává potvrzené subjektivně vyhovující nasazení. Neznáme orientaci zkoušené destičky (svislá/vodorovná), způsob očištění, stopy podpor ani přesné skutečné průměry. Výsledek z jedné orientace není automaticky měřením druhé.

Výrok o „zmenšení“ u nevyhovujícího Ø4 se nepoužije k dalšímu zmenšení otvoru. Záměr je odstranit příliš těsný fit; průměr nosného čepu se zatím nesnižuje.

## Původní postup před konečným upřesněním

- Navrhnout provozní uložení Ø12 podle otvoru 12,6 a Ø8 podle 8,6; jde o nominální návrhovou volbu vycházející z uživatelova testu, nikoli potvrzení funkce celé osy.
- Oddělit rotační uložení, pevná sedla čepů, spoj výstupního kola s osou, D spoje kol a západkové pojistky. Neměnit všechny díry stejným přírůstkem.
- Přepočítat společně vůli náboje na čepu a čepu v rámu, výstupního kola na ose a osy v rámu. Ukládání neřešit lepidlem ani předpokladem, že se opotřebení samo vymezí.
- Ověřit nejmenší i největší rozteče zubů, šířku aktivního záběru a řízení celé V3. Zachovat tři stupně a poměr 25:1, čtyři kola, SG90 a dvě 5mm hladká vodicí pásma s odlehčeným středem. Nové mechanické díly pouze tištěné.
- Připravit nový samostatný doplňkový vzorek Ø4 s většími otvory 4,4 / 4,6 / 4,8 a jasnými popisky. Jeho rozměry nejsou fyzicky ověřené. U montážního klíče je důležitá průchodnost a zachycení momentu, nikoli požadavek na volné otáčení.

## Výchozí problém větších vůlí

Při prosté změně kluzných otvorů 8,2→8,6 a 12,2→12,6 by s původními pevnými sedly 8,1 vznikl maximální modelový posuv každého mezikola ±0,35 mm. Sdílený původní parametr zadního ložiska a otvoru výstupního kola by dal na výstupu až ±0,60 mm. Příčný klínek neposkytuje bezvůlové vystředění ve směru vlastní osy.

Při původním předpokladu posuvu motoru ±0,15 mm jsou konzervativní relativní radiální posuvy stupňů 0,50 / 0,70 / 0,95 mm. Původní přirážka roztečí 0,40 mm tedy nestačí. Zvětšení přirážky zase snižuje kontaktní poměr při největším oddálení; je nutné řešit vedení a ozubení společně. Tyto mezivýsledky nejsou finálními rozměry nové revize.

## Pozdější výslovná volba podle funkce

Uživatel následně upřesnil: pro volné otáčení použít největší hodnotu kalibrační řady, pro pevné spoje nejmenší. Jde o autorizaci návrhových hodnot; průchodnost či bezpečné lisování nejmenších otvorů nepotvrdil. Auto ani nosné čepy se nemají globálně zmenšovat. V tomto bodě uživatel čekal na revizi; konečné zadání výše následně přijalo tisk celé sady.

| Funkce | Nová návrhová volba | Co tato volba nepotvrzuje |
|---|---|---|
| Mezikolo volně na Ø8 čepu | Otvor 8,6; dvě 5mm vodicí pásma | Souosost dlouhého uložení, skutečné vůle a volnou celou otáčku |
| Pevný Ø8 čep v rámu | Sedlo 8,1; tvarové zajištění hlavy zůstává | Bezpečné nasunutí / nalisování konkrétního výtisku |
| Zadní Ø12 osa otáčející se v rámu | Otvor 12,6 | Výsledek vodorovného otvoru, pokud uživatel zkoušel jinou orientaci |
| Výstupní kolo pevně na Ø12 ose | Samostatný parametr otvoru 12,1; moment nadále přenáší příčný klíč | Nulové radiální vůle či únosnost klíče |
| Zadní kolo pevně na D konci | Posoudit kruhovou část 12,1 a plošku odděleně | Fit D profilu zkouškou obyčejného kruhového otvoru |
| Ø4 montážní čepy a klíč | Těsná návrhová hodnota 4,1 podle funkce, bez změny nosného průměru | Bezpečné násilné vtlačení; volné otáčení zde není obecné kritérium |

S odděleným výstupním otvorem 12,1 klesne nominální součet radiálních posuvů výstupu na 0,35 mm (0,30 osa/rám +0,05 kolo/osa). Relativní rozsahy stupňů potom jsou 0,50 /0,70 /0,70 mm; ani tak původní profil s přirážkou rozteče 0,40 nevyhovuje. Tyto konzervativní CAD rozsahy byly použity k hledání robustnějšího ozubení. Samy nepopisují skutečně změřený výtisk a nejsou důvodem požadovat změnu potvrzeného funkčního rozdělení spojů. Skutečná vůle může být jiná, protože část přídavku může kompenzovat tiskové zmenšení otvoru; bez měření ji nebudeme zaměňovat za prokázané provozní vymezení.

Zmrazené kalibrační podklady, původní V2/V3 a firmware se nemění. Není objednaný ani spuštěný nový tisk, vytvořený G-code či ovládané zařízení.

## Připravený doplňkový vzorek Ø4

[Podložka Ø4 V2](kalibrace-4-v2/kalibrace-4-v2-podlozka-01.3mf) obsahuje dva bloky Z/Y, každý s otvory 4,4 / 4,6 / 4,8 mm o pracovní délce 8 mm. Používá původní Ø4 čep; neztenčuje jej. [Návod a kontroly](kalibrace-4-v2/README.md) rozlišují CAD/STL/3MF kontrolu od dosud neprovedené fyzické zkoušky. Původní zmrazená kalibrace zůstává zachovaná.

## Historický mezistav: geometrické hledání a návrh další zkoušky

V tomto dřívějším mezistavu celá revidovaná sada ještě nebyla připravená a hlavní exporty byly předkalibrační. Pozdější výslovné zadání přijalo původní 20° nominální prototyp s novými fit otvory; aktuální regenerované soubory a jejich rozsah kontroly jsou odkazované nahoře. Tento odstavec není zákazem tisku současné sady.

U profilu s modulem 1,1, úhlem 14°, hlavami 1,31m / 1,59m a patou 1,7m se zkoušely přirážky rozteče 0,80 / 0,85 / 0,90 mm. Poslední varianta při kontrole nosného boku prvního páru 18→54 prokázala skutečný střet kořene: rozteč 40,0 mm, fáze velkého kola 1,666667°, objem průniku 0,002991016 mm³ při tloušťce 1 mm. Průnik zasahuje poloměr malého kola 9,20082 mm, tedy pod bázovou kružnici 9,60593 mm i pod skutečný začátek evolventního segmentu 9,62546 mm. Po malém vrácení o ekvivalent 0,007 mm zůstává průnik 0,000838750 mm³. Nejde tedy jen o mikroskopickou aproximaci evolventy Bézierovými křivkami. Tento profil se nepředává k tisku celé sestavy. [Důkazy, zdroj zkoušek a přesný rozsah](revize-fitu-diagnostika/README.md) jsou uložené v projektu.

Geometrický důkaz neprokazuje chybu stávajícího fyzického otvoru 8,6. Část jeho přídavku může vyrovnávat nepřesnost tisku. K rozhodnutí je hotová a exportně ověřená [ruční zkouška převodu](zkouska-prevodu/README.md): původní 20° dvojkola A/B při rozteči 39,4 mm, jejich skutečné pevné čepy a pojistky, zachované obě podpěry i axiální dorazy ve zkráceném rámu. Otáčivé náboje mají Ø8,6 se dvěma 5mm vodicími pásmy, pevná sedla Ø8,1 podle výslovného zadání. Celkem sedm kusů.

Zkouška se dělá bez motoru, s rámem drženým nad stolem nebo podepřeným pouze po stranách tak, aby se zuby ničeho nedotýkaly. B60 zasahuje 3,2 mm pod dno rámu; přitlačení dnem na stůl by vytvořilo falešné zadření. Nejprve zasunutí pevných čepů bez násilí, pak jednotlivá kola na čepech a nakonec alespoň tři celé otáčky mezikola B v obou směrech, také s lehkým odporem prstů. Zaznamenat neprůchodnost, tvrdé místo, kývání či přeskakování. Výsledek rozhodne o skutečném chodu tohoto stupně; neověří automaticky Ø12 zadní osu, její pevný náboj ani celé řízení. Tato praktická zkouška nahrazuje opakované dotazování na neznámý skutečný průměr, nikoli zkoušku celého auta.


## Hotové předání zkoušek

- **[Ruční zkouška 18→60: jedna podložka, 7 kusů](zkouska-prevodu/zkouska-prevodu-podlozka-01.3mf)**. CAD, zachování původní geometrie mimo otvory, přepočet, GUI save/reopen, STL, kusovník a import/export Next CLI prošly. [Skutečný náhled](zkouska-prevodu/nahled.png) a [krátký návod](zkouska-prevodu/README-3MF.md). 3MF SHA-256: `2d001c67b6299568b6544d4fbd94c75e0eff9888868929b3398d1b26894981a6`.
- **[Ø4 V2: jedna podložka, 2 bloky](kalibrace-4-v2/kalibrace-4-v2-podlozka-01.3mf)**. Použít původní Ø4 čep; otvory 4,4 / 4,6 / 4,8. 3MF SHA-256: `e9ff259b1f6a3ac4e2155896c951eed0a3a265532c4a9591f1172c26d930fa21`.

Každá podložka je samostatná zkouška. Nejde o hlavní sadu auta; objekty se již nenásobí. Oba soubory obsahují geometrii, nikoli profil nebo G-code. Před tiskem zbývá ve sliceru zkontrolovat skutečné podpory a vrstvy. Zkoušky zatím nebyly fyzicky vytištěné ani vyhodnocené. Následně uživatel povinnou zkoušku odmítl a zvolil celou hlavní sadu. Oba zdejší doplňkové výtisky proto zůstávají pouze volitelné; podmínkou aktuálního předání nejsou.


## Konečné předání celé sady

Aktuální zdroj, FCStd, 34 STL typů, kompletní ZIP a tři podložky **26 + 27 + 13 = 66 kusů / čtyři kola** jsou synchronizované. Původní 20° / m1 ozubení a rozteče zůstaly; kluzná uložení jsou 8,6 / 12,6, oddělené pevné spoje 8,1 / 12,1 / 4,1 podle funkce a D ploška 4,05 proti ose 4,00 mm. Finální FCStd SHA-256: `68ea656115ca166e95adf049ba3347167bbedb6a44fdd77c22d8aef21761e6e9`.

Aktuální kontroly: 2345 nominálních párů bez průniku, 16 společných axiálních kombinací (plná poslední šířka 8 mm s rezervou 1,5 mm), šest nezměněných ozubených obrysů, 24 krajních párů u změněných otvorů objímky a 10 změnových parametrických zkoušek včetně navrácení. GUI uložená/znovu otevřená sestava má doloženou vazbu na předchozí geometrický snapshot. Historické pohybové kontroly nezměněných částí jsou převzaté s původem a hashem, neoznačené za nové spuštění.

**`nominal_cad_validation_pass=true`; `full_nominal_radial_clearance_scenario_pass=false`.** Plný konzervativní radiální scénář zůstává nepokrytý. Doplňkové vzorky nejsou vyžadované. Fyzický tisk, fit celé sestavy, zatížení ani jízda nejsou potvrzené. [Aktuální předání](README.md), [stav a hashe](stav-revize.json), [exportní kontrola](overeni-exportu.json).

Všechny předávané soubory jsou v projektu. Již existující kopie na ploše se podle posledního pokynu dále nemění; dřívější návrh jejich aktualizace je zrušený. Kritické pravidlo je v kořenovém `AGENTS.md`. Žádný nový tisk, G-code, změna presetů, firmware, ovládání zařízení, commit nebo push nebyly součástí tohoto předání.
