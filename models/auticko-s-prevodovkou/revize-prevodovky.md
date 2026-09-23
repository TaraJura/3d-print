# Revize převodovky V2 po hlášeném zasekávání

Stav 19. 9. 2026: **technický audit a návrh dalšího směru, nikoli hotová nová převodovka**. Původní FCStd, makro, STL, ZIP, V3 ani firmware se touto revizí nemění.

**Volba uživatele je uzavřená: všechny nové mechanické díly mají být tištěné, bez nákupu kovových os, ložisek, pouzder nebo dalšího spojovacího materiálu.** Původní doporučení 16:1 níže bylo prvním porovnáním v obálce V2, nikoli limitem zadání. Jiří chce větší praktický tah a dovoluje změnit celou konstrukci, výšku, půdorys i počet stupňů. Navazuje samostatný návrh [silové převodovky 25:1](../auticko-silovy-prevod-25/architektura.md). Prioritu má lehký chod a zachování záběru; vyšší redukce ani nulové vůle samy zadírání neřeší.

## Nová fyzická evidence

Jiří hlásí, že sestava **V2 12:1 se opakovaně zasekává** a její odpor podle něj převyšuje přínos převodu. Uvedl použití sekundového lepidla a následně oleje; přesná místa, množství, výrobky a časový vztah k jednotlivým závadám neznáme. Potom vyslovil podezření na rozpěrku na nesprávné straně a slíbil přestavbu. **Výsledek přestavby ani mechanická zkouška oddělená od motoru zatím nejsou potvrzené.** Tiskový profil, skutečné rozměry, zatížení a motorové parametry nebyly změřené. Jde o uživatelské hlášení, ne o nezávislé určení příčiny. Historické označení „fyzicky netestovaný“ uvnitř původních exportů popisuje stav při jejich vytvoření; tento zápis je novější.

**Doplňující uživatelské hlášení:** první záběr motor→převodovka podle Jiřího přenáší dobře; druhý záběr převodovka→zadní kolo zabírá „jenom tak na půl zubu“. Upřesnil, že myslí nevyužitou **šířku** ozubení. Jde o fyzický odhad, nikoli změřených 50 % ani nový údaj v mm. Nová revize má využít celou pracovní šířku užšího výstupního pastorku i při povolených axiálních posuvech.

## Co současná konstrukce skutečně obsahuje

Zdrojem jsou [makro](auticko-s-prevodovkou.FCMacro), [montážní stohy](README.md#montážní-stohy-a-vůle), [geometrická evidence](kontrola-modelu.json) a [exportní kontrola](overeni-exportu.json). Zdrojové hashe a následující vlastní výpočty jsou v [revize-prevodovky-vypocty.json](revize-prevodovky-vypocty.json).

- Dva vnější evolventní záběry **18→54 a 18→72**, modul 0,9 mm, úhel 20°, poměr 12:1. Motor a zadní osa se otáčejí stejným směrem. Osy jsou na X32 / 72,7 / 105,3, Z24; rozteče 40,7 / 32,6 mm, vždy 0,2 mm nad standardní osovou vzdáleností. Kola zůstávají Ø80 a užitná plošina 170 × 60 mm.
- Každá tištěná osa Ø8 má souvislou D plošku i v kluzných uloženích. Dvě uložení jsou dlouhá 8 mm, jejich středy vzdálené 36 mm. Střed zadního ozubení je 17,5 mm a střed zadního kola 26 mm vně středu bližšího uložení; malé mezikolo je vyložené 14,5 mm. To je páka pro průhyb, nikoli jeho změřená velikost.
- Bloky stojí na 4mm desce; kolem otvoru je po stranách X a nahoře nominálně jen 2,7 mm materiálu. Meziosové bloky nemají horní propojení sloupky plošiny. Tuhost rámu a souosost je nutné řešit i při doplnění ložisek.
- Motor Ø22,5 × 26, délka hřídele 6 mm jsou uživatelská měření s neznámou přesností. Otvor pastorku 2,2 mm byl nasazen, ale přenos momentu, skutečný průměr hřídele, proud a moment motoru tím změřené nejsou.

### Rozpěrky a šířka záběru

Y− je strana ozubení, Y+ druhá strana. Jde o CAD polohy, nikoli odečet aktuálního výtisku.

| Prvek | Rozsah Y [mm] |
|---|---:|
| Ozubení zadního kola 72z | −40 až −31 |
| Krátká zadní rozpěrka 8,6 | −30,8 až −22,2 |
| Levé / pravé uložení rámu | −22 až −14 / 14 až 22 |
| Dlouhá zadní rozpěrka 17,6 | 22,2 až 39,8 |
| Malé mezikolo 18z / velké 54z | −36 až −29 / −29 až −24 |
| Pastorek motoru | −29 až −23,5 |

**Oba záběry mají nominálně jen 5 mm společné šířky.** U druhého stupně se tedy nevyužívá celých 7 mm malého ani 9 mm velkého ozubení. Z rozšířených axiálních mezí původní kontroly vychází druhé překrytí 3,5–6,4 mm. Mezi velkým mezikolem a motorem je 1 mm, mezi pastorkem a čelem motoru 0,5 mm. Zadní ozubení míjí podpěrný disk mezikola o 2 mm; tuto oddělovací rezervu nelze bez nového stohu smazat.

**Při prohození zadních rozpěrek 8,6 ↔ 17,6 mm** a zachování návaznosti čel na rám se zadní osa s koly posune přibližně o −9 mm. Součet délek se nezmění, pojistka tedy může stále zapadnout. Zadní zuby pak leží Y−49..−40 a malé mezikolo Y−36..−29: překrytí je 0 a mezera 4 mm. To je konkrétní geometrické vysvětlení, proč stojí za to nejprve zkontrolovat uživatelovo podezření. **Nedokazuje, že tak jeho sestava opravdu vypadá.**

### Tři vůle, které se nesmějí zaměnit

| Druh | Současný návrh | Důsledek pro revizi |
|---|---|---|
| Zubová vůle | Přirážka os 0,2 mm; ideální obvodová vůle asi 0,150 / 0,149 mm, nikoli přímo 0,2 mm mezi boky zubů | Kalibrovat boky a rozteč spolu; nepřitlačit osy „na nulu“ |
| Radiální vůle uložení | Ø8,6 proti Ø8: rozdíl průměrů 0,6 mm, na kruhové části 0,3 mm na stranu | Ve zjednodušeném kruhovém modelu se dva posuny mohou složit na 0,6 mm změny osové vzdálenosti, více než přirážka 0,2 mm. D profil a naklopení situaci dále ovlivňují |
| Axiální volnost | Hlavní stoh 1,2 mm, mezistoh 1,1 mm, pojistka navíc 0,2 mm v drážce | Zmenšit neřízené cestování po ose, ale nepředepnout rotující čela proti rámu |

Samostatná čtvrtá věc je vůle **spoje pro přenos momentu**: D otvor Ø8,3 a ploška 3,0 proti ose Ø8 a plošce 2,8 mm. Není to ložisko ani zubová vůle. Přesný kruhový kluzný čep a tvarové zajištění náboje mají v revizi rozdílné funkce.

Původní CAD testy kontrolují nominální středy, 25 úhlových poloh a zvolené axiální posuny. **Neověřují radiální posun, naklopení, deformaci, drsnost a tření skutečného výtisku.** Rozteč a backlash jsou provázané; výrobce KHK popisuje přidání vůle změnou osové vzdálenosti nebo ztenčením zubů. [KHK: vůle ozubení](https://khkgears.net/new/gear_knowledge/gear_technical_reference/gear_backlash.html)

## Praktické varianty redukce

Všechny hodnoty níže ponechávají modul 0,9, 18zubé pastorky, přirážku os 0,2, zadní osu X32/Z24 a kola Ø80. Čísla jsou vlastní analytický přepočet, **ne kolizně ověřený nový CAD**. Pro roztečný průměr platí d=m·z, pro hlavový da=m·(z+2), nominální osová vzdálenost je polovina součtu roztečných průměrů. [KHK: výpočet ozubení](https://khkgears.net/new/gear_knowledge/gear_technical_reference/calculation_gear_dimensions.html)

| Varianta | Stupně | Velké hlavové průměry [mm] | Rozteče 1. / 2. [mm] | X meziosy / motoru [mm] | Nejmenší světlost [mm] | Ideální síla / rychlost vůči 12:1 |
|---|---|---|---|---|---:|---|
| 12:1, opravené uložení | 18→54; 18→72 | 50,4 / 66,6 | 32,6 / 40,7 | 72,7 / 105,3 | 6,7 | 1× / 1× |
| **16:1, první dvoustupňový kandidát** | **18→72; 18→72** | **66,6 / 66,6** | **40,7 / 40,7** | **72,7 / 113,4** | **6,7** | **1,333× / 0,75×** |
| 20:1, prostorově těsnější | 18→80; 18→81 | 73,8 / 74,7 | 44,3 / 44,75 | 76,75 / 121,05 | 2,65 | 1,667× / 0,60× |

Přímé 18→90 a 18→72 by také dalo 20:1, ale 90z kolo Ø82,8 by při současné výšce os zasahovalo **1,4 mm pod rovinu země**. Proto tuto prostou záměnu nedoporučuji. Dvacetinásobná redukce přes 80/81 zubů sice zůstane nad zemí, ale vyžaduje také nové zadní ozubené kolo a přesun meziosy; malá světlost je nevýhoda. Pro 16:1 zůstává druhý stupeň i poloha zadní/meziosy, posune se motor o 8,1 mm a změní mezikolo na 72/18.

**16:1 ještě vyžaduje nový rám/sedlo a kompletní kontrolu.** Pevné odlehčovací okno X128..138 by se střetlo s posunutým pravým otvorem motorového pásku X127,9..130,9. Okna a trasy pásků se musejí upravit společně. Pevný vnitřní poloměr odlehčení mezikola 18 mm by po zvětšení zbytečně zesílil prstenec ke kořeni zubů z 5,175 na 13,275 mm; odlehčení a příčky se musí přepočítat. Změny vedení os mohou vyžadovat i další nové díly. Plošina 170 × 60 a kola Ø80 se automaticky nemění.

Síla při ustáleném chodu přibližně odpovídá F≈i·η·Mmotor/R, rychlost v≈ωmotor·R/i. Účinnost η ani skutečný moment nejsou změřené a při rozběhu nelze pevnou účinnost předpokládat. Vyšší poměr neodstraní tvrdé sevření; větší přenesený moment může přetížit tištěný zub, osu, pojistku či pastorek. Tah je navíc omezený přilnavostí a zatížením poháněných kol. Bez údajů motoru, nákladu a požadované rychlosti neslibujeme tažnou sílu v N ani nosnost v kg.

## Změny pro navazující plně tištěný návrh

1. **Souosé vedení blíže záběrům:** vyztužit bočnice/žebra a zkrátit vyložení zejména mezikola; přednostně uložit převod mezi dvěma blízkými podporami. Vnější podpěru nelze jen přilepit do dnešních mezer: kolizi s kolem, přírubou, motorem a přístup k montáži ověří nový CAD.
2. **Kruhové čepy, oddělený náboj:** v kluzném uložení plný hladký kruh. D ploška nebo jiný tvarový klíč jen tam, kde přenáší moment; oddělený náboj musí stále jít navléknout a zajistit. U kovové osy navrhnout odpovídající sevření/tvarový spoj, nikoli volný kulatý otvor držený lepidlem.
3. **Jednoznačné axiální stohy:** označení rozpěrek přímo na dílech, strany L/P, stupňové dorazy a tenké vymezovací podložky. Cílem k ověření je celková volnost přibližně 0,3–0,5 mm na stoh místo nynějších více než 1 mm; není to předepsaná tolerance neznámého výtisku. Nezmenšit ochrannou mezeru čel bez přepočtu celého stohu.
4. **Šířka skutečného záběru:** v nové konstrukci vystředit 8mm výstupní pastorek do 12mm věnce a zachovat celých 8 mm i v nejhorší společné axiální poloze; doložit rezervy vůči sousedním diskům a motoru. Pouhé přidání šířky zubům bez nastavení Y rovin nic neřeší. Nevytvářet axiální sevření pro omezení viklání.
5. **Kalibrace před dlouhým tiskem:** malý vzorek stejných orientací/vrstev jako díly — kruhový čep Ø8 a 8mm dlouhé uložení s nominálními otvory 8,1 / 8,2 / 8,3 / 8,4 / 8,6; zvolit nejmenší skutečně volně otočné uložení po očištění. Samostatně párový zubový vzorek s přirážkami os 0,10 / 0,20 / 0,30 mm a kontrola celé otáčky, nikoli jediného zubu. Neaplikovat plošné škálování celého auta. Tyto vzorky jsou zatím návrh, nevytvořené STL.
6. **Lepidlo mimo pohyblivé plochy:** tvarové a axiální zajištění navrhnout mechanicky. Nezalévat uložení ani zuby; neověřeným olejem nekompenzovat kolizi nebo sevření. U současné sestavy nejdřív zjistit skutečné místo kontaktu a slepení, netvrdit je bez prohlídky.

Kovové osy a kupovaná pouzdra/ložiska byly posouzené jako alternativa, ale **nejsou součástí zvolené cesty**. Přesnost, tuhost a tření průmyslových ložisek nelze vydávat za vlastnosti tištěných dílů. Pracovní fit se musí zvolit podle skutečných vzorků.

## Další krok a hranice této revize

Materiálová volba již není blokátor. V samostatné složce se připravuje celý nový CAD a tiskové podklady; původní modely zůstávají zachované. Kromě nominálních kolizí se kontrolují axiální stohy, skutečná šířka záběru a obálka radiálních vůlí. Výpočty nepokrývají pružné deformace, drsnost ani skutečné tření. Zadrhávání, lepidlo, tiskové chyby, motor a napájení zůstávají možné oddělené příčiny; audit žádnou z nich neprokazuje. Nová konstrukce nebyla fyzicky vytištěná ani změřená.
