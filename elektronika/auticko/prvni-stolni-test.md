# První stolní zkouška motoru — 19. 9. 2026

**Výsledek podle uživatele: tlačítko v telefonu roztočilo skutečný motor přibližně na jednu sekundu. Po vyjmutí jednoho článku motor už neběžel.** Tím je poprvé potvrzený celý řetězec telefon → Wi-Fi → Arduino UNO R4 WiFi → ST L293D → motor. Jde o krátkou stolní zkoušku; sestavené autíčko, převod pod zátěží ani trvalý provoz ověřené nejsou.

Záznam shrnuje hlasové sestavování a hlášené výsledky. Zapojení bylo kontrolováno jen částečně z fotografií, nikoli proměřeno. Přibližná sekunda je pozorování uživatele; přesné časování, napětí, proud a teplota nebyly fyzicky měřeny. Původní uložení tohoto záznamu neměnilo firmware ani geometrii. **Následnou diagnostiku a upload opravy webu sleduje [samostatný záznam](diagnostika-webu.md); zdejší motorový test patří k dřívější verzi programu.**

## Sestavený obvod a napájení

- **Arduino UNO R4 WiFi:** při stolní zkoušce napájené přes USB-C z powerbanky. Její druhý USB výstup byl zvažován pro motor, ale nakonec se nepoužil; chyběl adaptér pro vyvedení napájecích vodičů.
- **Budič:** uživatelem potvrzený ST L293D DIP16, přes středovou mezeru nepájivého pole. [Úplná tabulka zapojení](zapojeni-l293d.md) odpovídá řídicím pinům [programu](../../models/jednoduche-auticko/firmware/prvni-motor/prvni-motor.ino).
- **Řízení:** Arduino D5 → pin 1, D7 → pin 2, D8 → pin 7. Žlutý vodič **D8 → pin 7** uživatel výslovně zkontroloval na obou koncích. Barva vodiče sama funkci neurčuje.
- **Motor:** dva vodiče na výstupy 3 a 6. Tělo Ø 22,5 × 26 mm a vyčnívající hřídel 6 mm jsou dřívější ruční údaje. Motor nemá označení a není z LaskaKit sady. Rozsah 1–6 V je pouze uživatelem zadaný předpoklad, proud včetně rozběhu není známý. Uživatel před sestavením potvrdil také přímý rozběh při přidržení bateriových vodičů na kontaktech; použitý zdroj tehdy nebyl přesně určen.
- **Zem:** piny 4, 5, 12, 13, Arduino GND a černý vodič držáku na společném nepřerušeném úseku modré lišty. Nepoužité řízení 9, 10, 15 má podle postupu patřit na GND; výstupy 11 a 14 zůstávají volné. Celý obvod nebyl vizuálně potvrzen pin po pinu.
- **Logika:** pin 16 na červenou lištu připojenou k 5 V Arduina.
- **Motorové napájení:** červený vodič sériového držáku čtyř AA přímo do propojené pětice pinu 8. Kladná větev držáku se nespojuje s červenou 5V lištou Arduina.

V konkrétní poloze při skládání byl výřez čipu **vlevo**, směrem dovnitř pole. Při pohledu shora je spodní řada zleva **1–8** a horní zleva **16–9**. Volný otvor u nožičky musí patřit do stejné propojené pětice; u napájecí lišty rozhoduje stejný nepřerušený úsek. Polohu v otvoru nelze spolehlivě odvozovat jen z horního konce vysokého plastového konektoru na šikmé fotografii.

### Skutečné články při zkoušce

V držáku byly **smíšené nabíjecí Ni-MH a běžné články**. Na šedém článku bylo ve fotografii čitelné Ni-MH a uživatel později potvrdil údaj **1,2 V**; vedle byl článek VARTA LONGLIFE MAX POWER. Původní tvrzení o čtyřech běžných 1,5V článcích bylo tímto opravené. Úplné složení po vložení posledního článku, stav nabití ani napětí celého držáku nebyly ověřeny. Skutečný zdroj proto **neoznačovat jako změřených 6 V**.

Uživatel na krátkém pokusu s dostupnými články trval; byl upozorněn, že tato směs není řešení pro běžný provoz. Záznam úspěšného rozběhu není doporučením tento způsob napájení opakovat. Pro další provoz použít sadu odpovídajících článků stejného typu a obdobného stavu, ověřit napětí a proudové možnosti vůči budiči i motoru. [Pokyny výrobce baterií k nemíchání typů a starých/nových článků](https://energizer.com/about-batteries/battery-care/).

**Vyjmutí jedné baterie z tohoto sériového držáku přeruší celý obvod.** Není to zkouška motoru na napětí zbývajících tří článků. Arduino může dál běžet z oddělené USB powerbanky a reagovat LED, zatímco motor nemá uzavřený napájecí obvod.

### Odpor, kondenzátory a dočasné kontakty

- Pro odpor **10 kΩ mezi pinem 1 a GND** byl na fotografii `20260919_030519.jpg` vybraný prostřední pás v průhledném sáčku: pět proužků **hnědá–černá–černá–červená–hnědá**, tedy 10 kΩ ±1 %. Uživatel potvrdil zapojení. D5 zůstává připojený přímo k pinu 1; odpor není v sérii se signálem. Orientace odporu nerozhoduje.
- Návrh obsahuje dva keramické **100 nF** u napájení čipu, 16–GND a 8–GND. **Při této zkoušce nebyl osazen žádný kondenzátor**, protože je uživatel neměl a chtěl pokračovat. Jeden úspěšný pulz neověřuje odolnost proti rušení, poklesům napětí či resetům; pro stabilní sestavu odrušení doplnit.
- Součástka s označením **SW-520D** je kuličkový náklonový spínač, ne kondenzátor. Do místa kondenzátoru nepatří.
- Při této první zkoušce uživatel neměl páječku, cín ani malé krokosvorky. Později potvrdil nákup páječky, pájky a dalších pomůcek v Hornbachu, viz [inventář](../vybaveni.md); zapájení kontaktů dosud nepotvrdil. Odizolované konce obou vodičů protáhl otvory motorových kontaktů a zahnul kolem plíšků. Jde o **dočasný mechanický kontakt bez pájení**, nikoli hotový spoj pro jízdu. Holé části mají zůstat oddělené od sebe a kovového pláště; před mechanickou montáží je potřeba spolehlivé připojení a odlehčení tahu.

## Průběh zkoušky

| Krok | Hlášený výsledek a co dokládá |
|---|---|
| Sestavování bez USB a s jednou AA mimo držák | Vodiče byly připojované bez napájení. Jednotlivé kroky potvrzoval uživatel. |
| Připojení pouze USB powerbanky, AA stále mimo držák | Rozsvítila se kontrolka napájení Arduina; motorová větev zůstala přerušená. |
| Telefon v síti `Auticko-test`, stránka se nejprve nenačetla | Po otevření výslovného odkazu **[http://192.168.4.1/](http://192.168.4.1/)** uživatel potvrdil funkční stránku. Záměna HTTP/HTTPS byla možnost, nikoli zachycená a prokázaná příčina. |
| Tlačítko „Test motoru na 1 sekundu“ bez motorového napájení | LED Arduina podle uživatele svítila asi sekundu; to samo ještě nebyl běh motoru. |
| Vložení poslední AA, tlačítko zatím nestisknuté | Motor podle uživatele zůstal stát. |
| Jeden vědomý stisk tlačítka | Uživatel oznámil, že se motor na sekundu rozběhl. První fyzický motorový test přes L293D vyšel. |
| Následné vyjmutí jedné AA a další zkouška | Uživatel potvrdil, že motor už nefunguje; držák má přerušený sériový obvod. |

Test byl vedený jako krátký stolní pokus s volným motorem, bez ověření pohonu kol. Program dává jeden pulz s PWM **128/255**, potom výstup vypne a motor může dobíhat; nejde o aktivní brzdu. Uvolnění tlačítka délku pulzu nezkracuje. Přesný směr budoucí jízdy z tohoto testu neplyne, závisí na zapojení kontaktů a orientaci motoru v sestavě.

**Stav na konci této první zkoušky:** jedna baterie vyjmutá, motorový zdroj přerušený, Arduino na USB powerbance. Později uživatel napájení přepojoval a motor zkoušel znovu; aktuální stav držáku nelze odvodit z tohoto historického zápisu. Navazující diagnostika probíhala přes USB počítače.

## Fotografie a opravy během sestavování

Uživatel poskytl archiv `Photos-1-001.zip` se snímky `20260919_033207.jpg`, `20260919_033204.jpg` a `20260919_033158.jpg`. Místní originál je `/home/novakj/Downloads/Photos-1-001.zip`; fotografie odporů je `/home/novakj/Downloads/20260919_030519.jpg`. Originály zůstávají mimo repozitář, odkazy na tato jména jsou evidence původu, nikoli přenositelná fotopříloha. Rozbalená pracovní kopie v cache není kanonický projektový záznam.

Na dodaných snímcích byly vidět odpojené USB, jedna chybějící baterie a čip přes mezeru pole. Některé nožičky, orientační značku a řady otvorů zakrývaly konektory. **Celé zapojení tedy nebylo z fotografií potvrzeno.** Uživatel požádal kontrolovat až na konci a potom postupovat podle jeho kontroly zapojení.

- Předchozí hlasový pokyn **pin 8 → GND byl chybný**. Byl odvolán a uživatel potvrdil odpojení tohoto vodiče; konečné určení pinu 8 je plus motorového zdroje.
- Podezření z šikmé fotografie, že žlutý vodič končí na D7, bylo odvoláno. Uživatel přímo potvrdil **D8 na Arduinu → pin 7 čipu**. Není doloženo, že zde skutečně byla chyba nebo proběhlo přepojení.
- První zjištěný modul **ULN2003AN** není reverzační H-můstek, ale za odpovídajících elektrických podmínek umí spínat DC motor jedním směrem. Tvrzení, že je výhradně pro krokové motory, bylo opraveno. Pro tuto sestavu se nakonec použil potvrzený **ST L293D**.

## Mechanika a další pokračování

Uživatel už potvrdil, že vytištěný **pastorek s nominálním CAD otvorem 2,2 mm dobře pasuje na motor**. Zkouška vzorku ani nasazení nejsou měřením skutečného průměru hřídelky. Přenos momentu pastorkem a záběr soukolí pod zátěží zůstávají neověřené.

Tisk zbývajících **13 kusů z devíti typů STL** uživatel oznámil jako zadaný; slicer ukázal **3 h 15 min**. Dokončení, skutečný čas, profil a cívka ještě potvrzené nejsou. Počty a montážní pořadí jsou v [README modelu](../../models/jednoduche-auticko/README.md), tisková historie v [deníku](../../docs/denik-tisku.md).

Pro další pokračování zbývá:

1. Potvrdit dokončení ostatních dílů a jejich mechanický fit, volné osy, zajištění kol, uchycení motoru a soukolí.
2. Dokončit spolehlivé motorové spoje a odrušení, vyřešit odpovídající napájení bez směsi článků a ověřit skutečné elektrické parametry. První pulz nepotvrzuje rezervu proudu ani teplotní chování L293D.
3. Teprve potom ověřit pohon celé sestavy a jízdu. Tehdejší firmware i pozdější recovery verze prováděly sekundový test. Následně byl nahrán chod při držení tlačítka `hold-to-run-v1`; uživatel jej nejprve hodnotil příznivě, poté ale hlásil [potíže a neúspěšný rozjezd i s koly ve vzduchu](potize-po-montazi.md). Tento historický sekundový rozběh neověřuje nové řízení ani příčinu nynějších potíží. Aktuální použití a časové limity jsou v [návodu k firmwaru](../../models/jednoduche-auticko/firmware/prvni-motor/README.md). Reverzace součástí nového režimu není.

Při dalším vedení montáže chce uživatel **jeden konkrétní krok najednou**. Hotové zapojení nepřestavovat jen podle barev vodičů; vycházet z pinů, uživatelského potvrzení a případného měření.
