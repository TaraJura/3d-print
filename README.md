# 3D tisk a elektronika

Osobní projekt Jiřího Nováka: parametrické modely, 3D tisk, elektronika a zkušenosti ze sestavování. Znalosti i nové modely patří sem, aby šlo v další úloze pokračovat bez opakovaného vysvětlování. Nejde o firemní TechTools projekt ani o TechTools Brain.

Jiří popíše požadovaný díl nebo změnu běžným jazykem. Agent připraví model programově ve FreeCADu a Jiří si výsledek prohlédne.

[Sekce elektroniky](elektronika/README.md) je určená také pro všechny další osobní elektronické projekty bez vazby na 3D tisk. Nový projekt patří do `elektronika/<nazev>/` a do tamního indexu; jeho úplný propojený kontext zůstává v tomto repozitáři. Firmware existujícího autíčka má výjimku kvůli zachování původní cesty u modelu.

## Kde začít

- [AGENTS.md](AGENTS.md) — pravidla pro další práci agentů.
- [Tiskárna](docs/tiskarna.md) — Anycubic Kobra X, ověřené údaje a neznámé.
- [Software](docs/software.md) — FreeCAD, Anycubic Slicer Next a spuštění makra.
- [Materiály a profily](docs/materialy.md) — Alzament PLA Basic, defaulty a startovací doporučení.
- [Postup práce](docs/workflow.md) — od zadání přes model a slicer k vyhodnocení tisku.
- [Deník tisků](docs/denik-tisku.md) — skutečně hlášený průběh a výsledky.
- [Modely](models/README.md) — přehled všech dílů a jejich zdrojů.
- [Elektronika](elektronika/README.md) — zapojení, zkoušky a aktuální stav projektů.
- [Vybavení a materiál](elektronika/vybaveni.md) — kanonický inventář včetně potvrzeného nákupu v Hornbachu.

## Aktuální stav k 19. 9. 2026

Tiskárna je **Anycubic Kobra X s tryskou 0,4 mm**. K dispozici je bílý a černý **Alzament PLA Basic 1,75 mm**. Uživatel potvrdil spuštění FreeCADu a Anycubic Slicer Next na Ubuntu 26.04.1 LTS.

První model je [polička na zárubeň 90 × 50 mm](models/policka-na-zaruben/README.md). Její geometrie byla ověřena a uživatel model otevřel i importoval do sliceru. Uživatel oznámil zahájení prvního tisku; **fyzický výsledek ani první vrstva zatím nejsou potvrzené**. U zkontrolovaného lokálního G-code není jednoznačně doloženo, že jde právě o úlohu běžící na tiskárně. Podrobnosti jsou v [deníku](docs/denik-tisku.md).

Další model je [jednoduché autíčko s jedním motorem](models/jednoduche-auticko/README.md): čtyři kola, společná zadní náprava a ozubený převod. První FCStd a jednotlivé STL jsou vytvořené a geometricky zkontrolované. **Uživatel na vytištěném vzorku zvolil otvor 2,2 mm a následně potvrdil dobré nasazení hotového [pastorku](models/jednoduche-auticko/stl/pastorek.stl).** Tisk zbývajících 13 kusů zadal s odhadem sliceru 3 h 15 min; dokončení zatím nepotvrdil. **První sekundový rozběh samostatného motoru tlačítkem z telefonu přes UNO R4 WiFi a L293D uživatel potvrdil.** [Záznam sestavování, zapojení a posledního stavu](elektronika/auticko/prvni-stolni-test.md) obsahuje i provizorní napájení a otevřené body. Fyzická montáž podvozku a jízda ještě ověřené nejsou.

Autíčko nově doplňuje **[snímatelná plošina s užitnou plochou 170 × 60 mm](models/jednoduche-auticko/strecha.md)**. Nasazuje se na čtyři existující výstupky u kol; původní rám se nemusí tisknout znovu. **Uživatel potvrdil dokončení tisku a nasazení.** Správný dosed, provozní vůle, nosnost a stabilita nejsou potvrzené.

[Elektronika autíčka](elektronika/auticko/README.md) soustřeďuje zapojení a historii motorových zkoušek. **Opravené ovládání při držení `hold-to-run-v2` je přeložené, otestované a nahrané.** Předchozí požadavek na návrat k sekundovému pulzu uživatel odvolal před uploadem. [Firmwarový návod](models/jednoduche-auticko/firmware/prvni-motor/README.md) uvádí skutečný stav testů a nahrání. [Záznam potíží](elektronika/auticko/potize-po-montazi.md) odlišuje těžký rozjezd již na starém programu od přerušování při skutečném držení. Po návratu uživatel obnovil stránku a opakovaně potvrdil funkční držení, puštění a další stisk („Jo, funguje to, perfektní“). Jde o jeho fyzickou zkoušku v2, nikoli měření doběhu či zatížení. Nákup nářadí a baterií i použití silikonového oleje jsou v [inventáři](elektronika/vybaveni.md); vlastnictví neznamená potvrzené zapojení.

Dokončený je nový model [samostatného autíčka s převodovkou 12:1](models/auticko-s-prevodovkou/README.md), koly Ø80 a užitnou plošinou 170 × 60 mm pro stávající elektroniku. Vůči původnímu převodu 3:1 s koly Ø60 je ideální tažná síla 3× a rychlost 1/3, před ztrátami. [Balíček pro tisk](models/auticko-s-prevodovkou/tiskovy-balicek.zip) obsahuje 20 kusů ze 13 typů STL, každý soubor tisknout jednou. Hotové jsou parametrický FCStd, náhledy a montážní návod; prošly kontroly těles, STL, kolizí, soukolí i montážních vůlí. Původní modelové soubory zůstaly beze změny. Nová konstrukce je zatím fyzicky nevyzkoušený prototyp, bez G-code a bez odeslaného tisku.

**Rozpracovaná je třetí samostatná varianta s předním zatáčením přes SG90.** Navazuje na převodovku 12:1 a plošinu 170 × 60 mm; oba předchozí modely zůstávají zachované. První pracovní FCStd a STL již existují, po náhledu ale uživatel zadal širší a menší kola se skutečným tištěným dezénem. Nová návrhová volba je Ø76 × 12 mm s drážkami hlubokými 1 mm; kontrola a finální balíček ještě nejsou dokončené. Potvrzené servo, páčky, středový šroubek a měření účinného poloměru páčky 15 mm jsou v [inventáři](elektronika/vybaveni.md). Práce nyní zahrnuje pouze mechaniku; firmware se kvůli zatáčení nemění.

## Jak zapisovat poznatky

U nového údaje uvést původ: zadání uživatele, fyzické měření, údaj výrobce, kontrola souboru, návrhová hodnota nebo doporučení. Zadané rozměry nejsou automaticky měřením skutečného předmětu. Doporučení není potvrzené nastavení a kontrola modelu není důkaz úspěšného výtisku.

Nové parametry a změny modelů zapisovat do příslušné složky modelu; elektroniku do `elektronika/<projekt>/` a vybavení do [inventáře](elektronika/vybaveni.md). Po tisku doplnit deník podle skutečného výsledku. **Vytvoření STL, úspěšné řezání ani odeslání úlohy nestačí k označení tisku za úspěšný.** Upload programu sám není potvrzením fyzického výsledku.

## Projekt a Git

Aktuální místní checkout je `/home/novakj/3d-print`; osobní repozitář je [TaraJura/3d-print](https://github.com/TaraJura/3d-print). Git příkazy spouštět v tomto checkoutu: domovský adresář `/home/novakj` má vlastní, odlišný repozitář. Zdejší obsah se přípravou dokumentace automaticky necommituje ani nepublikuje.

Malé záměrné soubory FCStd, STL a PNG patří k modelu a jsou verzovatelné. Instalátory, runtime, přístupové údaje, cache a automatické zálohy do projektu nepatří. Původní kopie poličky v `Documents/3D-models` zůstala zachovaná kvůli otevřeným souborům; další práci ukládat sem.
