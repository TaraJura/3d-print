# Zdobené červené pouzdro na nůž — aktuální revize 05

Revize z 2.–3. 11. 2026. Jiří odmítl design V04 a chce nové pouzdro, do kterého se nůž jen podélně zasune. Potvrdil čepel 200 × 45 × 3 mm a montáž **na stěnu se zasouváním shora**. Jeden díl, dva vruty, při zasouvání se nic neotevírá. Celá čepel i špička jsou kryté, rukojeť zůstává venku.

**Preferovaný tisk od 3. 11. 2026: [naležato s podporami](rozlozeni/nalezato-s-podporami/README.md).** Jiří hlásí, že ručně otočený tisk naležato bez podpor „propadal na visícím přechodu“ a že svisle „to nevyšlo“. Příčina svislého neúspěchu ani skutečně tištěný G-code nejsou známé. Geometrie se nemění: [STL naležato](stl/pouzdro-zdobene-nalezato.stl) je tuhé otočení svislého STL z [generátoru](build_nalezato.py). Nová varianta je jen digitálně ověřená.

[Hlavní skutečný CAD náhled](prehled-navrhu.png) · [čelo](nahled-cad-celo.png) · [šikmo se stěnou](nahled-cad-iso.png) · [s referenčním nožem](nahled-cad-s-nozem.png) · [řez](nahled-cad-rez.png) · [ústí](nahled-cad-usti.png) · [zadní strana](nahled-cad-zadni.png)

## Rozměry

| Údaj | mm | Původ |
|---|---:|---|
| Čepel: délka × výška × tloušťka | 200 × 45 × 3 | Zadání Jiřího, není naše měření |
| Přechod ostří / rukojeť | 10 | Dřívější zadání |
| Rukojeť: délka, největší šířka | 105, 25 | Dřívější zadání |
| Dutina: délka × šířka × tloušťka | 218 × 47 × 4,4 | Návrh: 200 + 10 + rezerva 8; vůle 1 a 0,7 mm na stranu |
| Náběh v ústí | 51,4 × 8,8, délka 12 | Návrh |
| Rovina čepele před stěnou | 24 | Návrh: za rukojetí 25 mm zůstává 11,5 mm |
| Stěna pod dekorem | 2,4 | Návrh |
| Dno dutiny nad spodkem dílu | 16 | Návrh |
| Reliéf nad čelem | 1,2 / 2 / 2,2 / 3,2 | Návrh: lemování, šikmé pásy, prstenec, střed emblému |
| Horní pás límce nad čelem | 4,2 | Návrh |
| Celý díl | 78 × 33,8 × 248 | CAD |

Všechny hodnoty jsou v tabulce `Parameters` s původem. Délka čepele zůstává 200 mm; delší dutina je funkční rezerva.

## Konstrukce a vlastní rozhodnutí

- **Doraz:** nůž se zastaví širší rukojetí o límec. Krček 10 mm může projít ústím, špička pak zůstává 8 mm nade dnem. Širší krček zastaví nůž dřív, čepel je pořád krytá a rezerva se zvětší až na 18 mm. Dutina je rovná, tvar špičky do ní nezasahuje.
- **Odsazení:** rukojeť široká 25 mm by při tunelu přímo na stěně narazila. Tělo proto drží střední žebro a plochá zadní deska 4 mm. Prostor za tělem je otevřený, nejsou v něm žádné plovoucí díly ani uvězněné podpory.
- **Dva vruty:** Ø5,5 mm, vpravo nahoře nad ústím (X +32, Z 241) a vlevo dole (X −32, Z 7), vzdálenost 242,6 mm. Jsou mimo dutinu i mimo rukojeť. Nástroj Ø11 má z místnosti přímou cestu, hlava Ø10 sedí na desce. Další dva rohy desky jen opírají díl o stěnu. Díry lze označit přes přiložený díl. Skutečné vruty a stěna nejsou známé.
- **Místo na stěně:** nad ústím musí zůstat volných nejméně 315 mm pro vytažení nože (210 + 105).
- **Dekor:** skutečná CAD geometrie, žádná textura. Výrazný dvoustupňový límec s výstupky, tři lomené pásy nad i pod emblémem, boční lemování, šestiúhelníkový emblém s paprsky a štítek na koncovce. Dekor jen přidává materiál. Mělký příkop v emblému ubírá pouze stupeň prstence, stěny se nedotýká. Bez tenkých hrotů.
- **Tisk:** svisle ústím nahoru, tedy stejně jako po montáži. Dutina je shora otevřená, takže uvnitř nevzniká strop ani podpora. Patka desky a blok žebra dávají půdorys 78 × 31,6 mm, k tomu brim 8 mm.

## Soubory

- [pouzdro.FCStd](pouzdro.FCStd): parametrický PartDesign, viditelné je jen červené `Scabbard`. Referenční nůž je skrytý a je to ilustrace.
- [pouzdro.FCMacro](pouzdro.FCMacro): zdroj celé revize, 22 plně vázaných skic a výrazy, bez Python proxy.
- [STL — jeden kus](stl/pouzdro-zdobene.stl), už v tiskové orientaci.
- **[Preferovaný projekt naležato s podporami](rozlozeni/nalezato-s-podporami/pouzdro-nalezato-kobra-x-pla-projekt.3mf)** a [jeho přehled](rozlozeni/nalezato-s-podporami/README.md).
- [Starší svislý projekt Kobra X](rozlozeni/podlozka-01-kobra-x-pla-projekt.3mf) a [jeho přehled](rozlozeni/README.md). `podlozka-01-geometrie.3mf` je jen alternativa bez procesu; má už před variantou naležato jiný hash než starý manifest a nebyl obnoven.
- [audit-pouzdra.json](audit-pouzdra.json), [kontrola-modelu.json](kontrola-modelu.json), [kontrola-nahledu.json](kontrola-nahledu.json), [kontrola drah](rozlozeni/kontrola-drah-vizualne.md), [predani.json](predani.json), [predani.sha256](predani.sha256).

## Provedené kontroly

Audit znovu otevřel uložený FCStd a prošel **48/48 kontrol** vázaných na SHA-256 FCStd a STL. Kontrola příznaku samoprůniku byla po opravě přepočítaná samostatně, ostatní výsledky jsou z celého běhu na stejných souborech.

- **Těleso:** platný 1 solid, 174 543,36 mm³; zadní strana je jedna rovná plocha v rovině stěny.
- **Dutina:** naměřeno 47 × 4,4 mm po celé délce, dno v Z 16, plná deska pod dutinou Z 10–16.
- **Zasouvání:** přímý pohyb obálky 200 × 45 × 3 mm od dosednutí až nad ústí bez kolize, nejmenší odstup 0,7 mm, rezerva pod špičkou 8 mm. Širší nebo hlubší obálka v kontrolních případech narazí.
- **Celý referenční nůž, oběma směry:** bez kolize s límcem, oušky i hlavami vrutů; za rukojetí 11,5 mm; rukojeť je skutečný doraz.
- **Stěny:** nejméně 2,4 mm kolem rovné dutiny, 3,2 mm u rohů dna, 3,9 mm kolem náběhu. Dekor má od dráhy čepele nejméně 2,4 mm.
- **STL:** uzavřená, jedna komponenta, jednotná orientace, 8396 trojúhelníků; vrcholy nejvýše 0,00001 mm od CAD.
- **Přepočet:** tloušťka čepele 4,5, délka 190, 2 pásy a osa 22 mm od stěny přepočítají platný model s volnou dráhou. Hodnoty obnoveny, soubor nezměněn.
- **Náhled:** obrys čelního renderu se shoduje s průmětem STL, IoU 0,995.

**Dvě výhrady z auditu:**

- Ne všechny dolní plochy mají nejvýše 45°. Čtyři přechody dolních křídel límce mají lokálně až cca 49,2° podle STL, nad 45,5° je to asi 31 mm². Řez je bez nových ostrovů a slicer tam nevytvořil převisovou stěnu, geometrie se kvůli tomu neměnila. Kvalitu těchto míst ukáže až tisk.
- FreeCAD Mesh hlásí samoprůniky (surový příznak zůstává v protokolu jako varování). Všech 41 dvojic z 56 záznamů je ale oddělených rovinou jednoho z trojúhelníků, nejmenší mezera 0,000035 mm. Jde o téměř se dotýkající facety na přechodech křídel a slicer nepotřeboval žádnou opravu sítě.

## Starší svislý tisk

Tato část popisuje svislý projekt, který podle hlášení Jiřího nevyšel. Tisknout se má [varianta naležato](rozlozeni/nalezato-s-podporami/README.md).

Projekt otevřít jednou jako celek, 1 kus, nepřerovnávat. Kobra X 0,4 mm, návrhový nekalibrovaný červený PLA: 0,20 mm, 4 stěny, 15 % gyroid, tryska 215/205 °C, podložka 50 °C, brim 8 mm, max. průtok 8 mm³/s, bez podpor. Nový řez: **1240 vrstev, 0 nových ostrovů, 0 segmentů podpor, odhad 160,35 g / 10 h 26 min 37 s.** Podrobnosti jsou v [kontrole drah](rozlozeni/kontrola-drah-vizualne.md).

Červená je jen barva v projektu. [Sklad](../../../docs/materialy.md) eviduje Elegoo PLA Red 14.0007.203, ale zavedení do tiskárny, vstup ani kalibrace nejsou potvrzené. Při odeslání vybrat skutečnou cívku.

## Před tiskem změřit na noži

Vzdálenost **od špičky k začátku širší rukojeti**. Návrh počítá s 210 mm, do dutiny se vejde nejvýše 218 mm. Dřívější celková délka 340 mm by při čepeli 200 a rukojeti 105 nechala mezi nimi 35 mm, ne 10 mm. Kdyby byl úsek opravdu tak dlouhý a tenký, špička by dosedla na dno dřív než rukojeť. Začátek rukojeti také musí být širší než 8,8 mm, jinak by neměl o co dosednout.

## Regenerace

Makro přepisuje jen vlastní FCStd, STL a JSON v této složce. Před spuštěním uložit a zavřít stejnojmenný dokument. Změny tabulky sladit s makrem; statická ilustrace nože a STL/PNG se samotnou editací parametrů neobnoví.

Přes FreeCAD 1.1.3 (`/home/novakj/.cache/freecad-shelf-1.1.3/runtime/AppRun`, s oddělenými konfiguracemi dle [projektové dokumentace](../../../docs/software.md)): `pouzdro.FCMacro`, pak v GUI `nahled.FCMacro` (potřebuje `from pivy import coin`), pak `audit-pouzdra.FCMacro`. Následně `python3 sestavit-nahled.py` a `python3 build_print_projects.py`. Runtime není součástí modelu. Nový běh změní hashe, předání je pak nutné obnovit.

## Neověřeno

Fyzický tisk, přilnavost a stabilita vysokého dílu při tisku, první vrstva, kvalita lokálních převisů, skutečný fit nože, opotřebení ostřím, pevnost, vruty a kotvení ve stěně. Tvar špičky, krčku a rukojeti v referenci je ilustrace. Otevření projektu v GUI sliceru nebylo zkoušeno. Tiskárna nebyla ovládána.

Předchozí [V04](../revize-04-zrcadlovy/README.md) (design Jiří odmítl), [V03](../revize-03-tvarovany-dle-noze/README.md), [V02](../revize-02-otevrene-v/README.md) a [V01](../historie/v01-uzavrene-pouzdro/README.md) zůstávají beze změny jako historie.
