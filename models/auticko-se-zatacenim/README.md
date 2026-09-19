# Autíčko s převodem 12:1 a předním řízením SG90

**Pracovní CAD prototyp. Ještě neoznačeno jako balík připravený k tisku — probíhá kontrola pohybu a montážních vůlí.** Původní dvě varianty zůstávají beze změny. Firmware se při této mechanické úpravě nemění.

Nová přední kola se otáčejí samostatně na osičkách těhlic. Svislé čepy jsou podepřené rámem i horní odnímatelnou čelistí. Servo přenáší pouze sílu táhla, nikoli hmotnost kol. Jednoduchý rovnoběžník natáčí obě kola stejným úhlem; není to Ackermannovo řízení, takže v zatáčce očekáváme smýkání pneumatik. Skutečnou sílu potřebnou k zatáčení a schopnost SG90 zatáčet pod zatížením neznáme.

[Parametrický model](auticko-se-zatacenim.FCStd) · [Generátor](auticko-se-zatacenim.FCMacro) · [Geometrická kontrola](kontrola-modelu.json) · [Původní varianta 12:1](../auticko-s-prevodovkou/README.md) · [Elektronika](../../elektronika/auticko/README.md) · [Inventář](../../elektronika/vybaveni.md)

## Skutečně známé údaje a návrh

- Jiří identifikoval Tower Pro Micro Servo 9g SG-90. Má originální jednoramennou páčku s vnitřním ozubením a středový šroubek. Vzdálenost středu osy ke středu posledního malého otvoru **výslovně změřil 15 mm**. Starší nejednoznačné údaje 20/19 mm tento rozměr nenahrazují.
- Nominální výkres výrobce: tělo 22,7 × 12,2 mm, výška těla 27 mm, celková výška včetně výstupu 30,3 mm, délka přes uši 32,3 mm, spodek → spodní rovina uší 17 mm. Přesný posun osy po délce těla a výška skutečné páčky nejsou kótované. Analogová/digitální varianta se nerozlišila; nepředpokládáme rozsah 180°.
- Rozměry těla, malý otvor páčky a výška páčky **nejsou fyzicky ověřené**. `CaseAxisOffset=5 mm` a tloušťka páčky 2,5 mm jsou označené návrhové hodnoty, nikoli měření. Páskové lože umožňuje posunout servo; před finálním utažením vyrovnat skutečnou osu a klouby do modelových poloh.
- Původní DC motor: uživatelsky změřený válec Ø22,5 × 26 mm, hřídel délky 6 mm. Nominální tištěný otvor pastorku 2,2 mm uživatel nasadil; skutečný průměr hřídele, moment a zatížitelnost nejsou změřené.
- Střed řízení X154, Y±44, Z24; kola Ø80, středy při rovné jízdě X150,3, Y±57. Zadní náprava X32. Přední rozchod 114 mm je širší než zadní 88 mm. Konstrukční mechanické dorazy ±24°, zamýšlený provozní rozsah maximálně ±20° před fyzickou kalibrací.
- Servoosa X184/Y0, páčka v nule dozadu; čep páčky X169/Y0. Ramena těhlic délky20, jejich konce X174/Y±44. Příčné táhlo mezi osami88, servotáhlo mezi osami√(44²+5²)=44,283 mm. Celá vazba se přepočítává z tabulky `Steering`.
- Horní plošina má nezměněnou souvislou užitnou plochu **170 × 60 mm**. Je to stejný díl jako u V2, s dosedy X32/150 a Y±18. Zadní kontakty motoru zůstávají přístupné po sejmutí plošiny.

Primární zdroje: [TowerPro SG90 analog](https://towerpro.com.tw/product/sg90-analog/), [TowerPro SG90 digital](https://towerpro.com.tw/product/sg90-7/). Nominální údaje nepotvrzují skutečný rozměr uživatelova kusu ani zatížitelnost celého mechanismu.

## Opětovné použití z V2

Přebírané STL jsou přesné bajtové kopie z `auticko-s-prevodovkou/stl`, jejich SHA jsou v kontrolním JSON. Beze změny lze použít plošinu, čtyři kola, pastorek, mezikolo, zadní hlavní osu, meziosu, zadní levou rozpěrku8,6, jednu dlouhou rozpěrku17,6 a dvě krátké1,6. Z šesti velkých C pojistek se tři dají převzít z kompletního V2 a tři je třeba dotisknout.

Nový rám nahrazuje rám V2. Dřívější přední dlouhá osa a dvě dlouhé přední rozpěrky se nepoužijí. Nové jsou dvě těhlice s krátkou osičkou, dvě horní čelisti, dva svislé čepy, příčné táhlo, servotáhlo, dva malé kloubové čepy, dvě malé pojistky a hornový distanční váleček. Úplný kusovník bude v počtovaném balíčku po dokončení kontrol.

## Spoje a montážní omezení

Tištěná osička kola má Ø8, kruhový otvor kola Ø8,6; svislé čepy Ø8 proti otvorům8,6; klouby táhel Ø6 proti otvorům6,5. Vůle jsou návrhové. Jemný tisk, odstranění otřepů a skutečná volnost chodu se musí ověřit. Netvrdit ověřený press-fit ani nosnost tištěných os/pojistek.

Originální páčku upevňuje její dodaný středový šroubek. Pro poslední malý otvor je navržen **1× šroub M2×16, 2× podložka M2 a 1× pojistná matice M2**; vlastnictví tohoto materiálu není potvrzené. Tištěné servotáhlo má otvor2,3. Před montáží ověřit otvor v originální páčce, tloušťku páčky a průchodnost šroubu; nevnucovat šroub do menší díry. Případnou úpravu otvoru provést až po ověření zbývající stěny a uchycení. Spoj musí zůstat otočný, nesmí být sevřený. Délka šroubu a výška distančního válečku se ověří podle skutečné páčky; nevhodný spoj nenahrazovat násilným utažením.

Servo se uchytí dvěma malými stahovacími páskami přes otevřené lože; potřebný materiál navíc k dvěma páskům motoru. Otvory jsou pro návrhovou šířku pásku maximálně2,5 mm, vlastnictví/typ nepotvrzen. Udržet kabel mimo táhla, ozubení a kola. Vyjímatelná plošina potřebuje podle uživatelem zvoleného zatížení vlastní zajištění; těsný fit a nosnost nepovažovat za potvrzené.

Před spojováním odpojit motorové napájení. Nejdříve sestavit a ručně projít celý podvozek bez servotáhla. Vložit těhlice mezi čelisti, nasadit horní čelisti klíčem do registru, svislé čepy shora a C pojistky zespodu. Potom nasadit přední kola a jejich C pojistky. Připojit příčné táhlo, malé čepy a pojistky. Nakonec nastavit servo do neutrálu a připojit originální páčku a servotáhlo bez předpětí. Dorazy chrání geometrii, **nejsou příkazem pro servo, aby do nich tlačilo**.

Řízení potřebuje samostatné budoucí ovládání/napájení serva. V této etapě se na Arduino nic nenahrálo, servo nepřipojovalo a nezkoušelo. Moment SG90, tření kol a napájecí stabilita se z CAD neprokazují. Dříve hlášený těžký rozjezd existoval i se starým pulzním firmwarem; silikonový olej podle uživatele moc nepomohl. Převod ani servo nejsou prokázanou opravou jeho příčiny.
