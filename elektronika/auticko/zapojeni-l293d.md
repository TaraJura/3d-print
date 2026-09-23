# První test motoru — Arduino UNO R4 WiFi a ST L293D

**Stav k 19. 9. 2026: uživatel sestavil obvod a potvrdil první přibližně sekundový rozběh motoru tlačítkem z telefonu.** [Záznam skutečné zkoušky](prvni-stolni-test.md) rozlišuje potvrzené kroky, částečnou fotografickou kontrolu a neověřené parametry. Tabulka níže je referenční zapojení; každý spoj nebyl nezávisle proměřen.

U neoznačeného samostatného DC motoru uživatel zadal **předpoklad 1–6 V**, nikoli ověřený údaj výrobce. Místo původně navrhované regulované 5V motorové větve se při pokusu použil sériový držák čtyř AA se směsí Ni-MH 1,2 V a běžných článků. Skutečné celkové napětí a odběr nebyly měřené. Tato provizorní směs není návrhem pro další běžný provoz. Arduino bylo napájené samostatně z USB powerbanky. Pozdější nákup nových 1,5V baterií je potvrzen v [inventáři](../vybaveni.md); jejich vložení do držáku, typ a počet zatím potvrzené nejsou.

## Co připravit na stole

Použité součásti: Arduino UNO R4 WiFi, ST L293D, nepájivé pole, vodiče, motor, odpor 10 kΩ a bateriový držák. Odpor je mezi enable a GND. **Dva navržené keramické kondenzátory 100 nF při prvním pokusu chyběly**, protože je uživatel neměl. Doplnění odrušení, vhodného napájení a pevných motorových spojů zůstává otevřené. Arduino se programuje datovým USB kabelem z počítače; při stolním pokusu používalo USB-C powerbanku.

Zapojovat s odpojeným USB i napájením motoru. Čip vložit přes středovou mezeru nepájivého pole, aby se protilehlé nožičky nespojily.

## Orientace čipu a vývody

Pohled **shora na nápis**, výřez otočený nahoru. Pin 1 je vlevo nahoře, číslování pokračuje dolů po levé straně a nahoru po pravé:

```text
                 výřez
              ┌───∪───┐
 EN 1,2     1 │       │ 16  VSS — logika
 vstup 1    2 │ L293D │ 15  vstup 4
 výstup 1   3 │       │ 14  výstup 4
 GND        4 │       │ 13  GND
 GND        5 │       │ 12  GND
 výstup 2   6 │       │ 11  výstup 3
 vstup 2    7 │       │ 10  vstup 3
 VS         8 │       │  9  EN 3,4
              └───────┘
```

| Pin L293D | Připojení v tomto návrhu |
|---|---|
| **1 — enable** | Arduino **D5**, současně **10 kΩ na GND** |
| **2 — vstup 1** | Arduino **D7** |
| **7 — vstup 2** | Arduino **D8** |
| **3 a 6 — výstupy** | Dva kontakty motoru; jejich pořadí určí fyzický směr |
| **4, 5, 12, 13 — zem** | Všechny propojit se **společnou GND** Arduina a mínusem motorového zdroje |
| **16 — VSS, logika** | **5 V z Arduina** |
| **8 — VS, motorová větev** | Plus **samostatného motorového zdroje**; při popsané zkoušce červený vodič držáku AA, nikoli 5V lišta Arduina |
| **9, 10, 15 — nepoužité řízení** | GND |
| **11, 14 — nepoužité výstupy** | Nezapojovat |

Pokud je při pohledu shora výřez otočený **vlevo**, spodní řada se čte zleva **1, 2, 3, 4, 5, 6, 7, 8** a horní zleva **16, 15, 14, 13, 12, 11, 10, 9**. Takto byl čip orientovaný při skládání. D5 je digitální pin mezi D4 a D6 na Arduinu, nikoli analogový A5. Žlutý vodič D8 → pin 7 uživatel výslovně zkontroloval.

Pro stabilní sestavu doplnit keramické kondenzátory **100 nF** co nejblíže čipu: jeden mezi pin 16 a GND, druhý mezi pin 8 a GND. Nejsou součástí již provedené zkoušky. Odpor na pinu 1 drží výkonový výstup vypnutý během resetu, kdy se na řízení Arduinem ještě nelze spolehnout. Vybraný odpor 10 kΩ má pět proužků hnědá–černá–černá–červená–hnědá; v uživatelské fotografii šlo o prostřední pás v průhledném sáčku.

Pozor na rozdělené napájecí lišty nepájivého pole; jejich skutečné propojení ověřit. Motorový proud nesmí procházet výstupním GPIO Arduina. Arduino a motorový zdroj sdílejí zem; z toho neplyne spojit kladné motorové napájení s 5V pinem Arduina.

## Co krátký rozběh ještě neověřil

- Označení motoru, jmenovité napětí a proud včetně rozběhu/zablokování, případně způsob omezené zkoušky se známým zdrojem a měřením.
- Typ, napětí a proudové možnosti zdroje. Hodnotu neodvozovat z rozměrů motoru.
- Úplná kontrola zapojení a polarity, odrušení, spolehlivost provizorních kontaktů a chování při mechanické zátěži.

Podle ST musí být **VS nejméně VSS**. Při zde použité logice z 5V pinu Arduina je potřeba tuto podmínku ověřit i pro motorový zdroj při zatížení. Čtyři články označené 1,2 V mají součet jmenovitých hodnot 4,8 V, čtyři 1,5V články 6 V; skutečné napětí se mění podle stavu a zatížení. To není ověření skutečné smíšené sady ani důvod články míchat. Úspěšný rozběh neprokazuje provoz v podmínkách datasheetu.

Napětí přímo na motoru je nižší o úbytek můstku a závisí na proudu. Při 600 mA jsou úbytky obou větví typicky celkem 2,6 V, maximálně 3,6 V. PWM není náhradou za správně zvolené napájení a proudové dimenzování; 50% PWM neznamená pevné napětí 2,5 V na motoru.

L293D má uvedeno 600 mA na kanál, ale je nutné dodržet teplotní podmínky; to není záruka bezpečného trvalého provozu v nepájivém poli. Špičkových 1,2 A platí pouze pro neopakovaný impuls 100 µs. Čip obsahuje ochranné diody. Při enable LOW jsou výstupy ve vysoké impedanci: motor **volně dobíhá**, aktivně nebrzdí.

Zdroj a kontrola: [ST L293D — datasheet, DIP16 pinout na straně 2, elektrické charakteristiky na straně 3, pravdivostní tabulka na straně 4](https://www.st.com/resource/en/datasheet/l293d.pdf). Nezaměnit s pouzdrem L293DD o 20 vývodech.

## Program a první postup

**Verze `v3-reverse-v1` je nahraná, uživatel následně obecně potvrdil funkčnost („Hele, všechno to funguje“).** Upload **86 716 B / 22 stran / exit 0** a tři pasivní výpisy potvrdily novou verzi a klidové výstupy. Čítače zařízení byly stabilní **HTTP=29 / closed=29**; původ dřívějších požadavků není určený. Agent odeslal 0 sériových dat, 0 HTTP a 0 pohybových povelů; port je zavřený a volný. **Po následné zkoušce uživatel obecně potvrdil funkčnost; agent pohyb ani elektrické měření PWM neprováděl.** [Evidence uploadu](../../models/jednoduche-auticko/firmware/prvni-motor/evidence/2026-09-23-v3-reverse-v1-upload/README.md). **Nové potvrzení před uploadem couvání:** na otázku po USB Arduina a odpojeném napájení motoru i červeném vodiči serva uživatel odpověděl „ano, servo odpojeno“ a upload výslovně autorizoval. Před uploadem byl podle tohoto hlášení servo plus odpojený a motor měl odpojený článek; táhlo se neměnilo. Aktuální připojení po pozdější zkoušce není potvrzené. Jde o uživatelské potvrzení, nikoli elektrické měření. Couvání nevyžaduje přepojovat D5 → EN, D7 → IN1 ani D8 → IN2. Při vpřed jsou IN1 HIGH / IN2 LOW, při couvání IN1 LOW / IN2 HIGH; EN má v obou směrech stejných 490 Hz a PWM 128/255. Při vypnutí a před změnou polarity se EN nastaví na 0 a oba vstupy na LOW. Opačný směr vyžaduje nejméně 250 ms od skutečného OFF. Předčasný požadavek zruší relaci, vyžádá puštění všech ovladačů a nový stisk; čas ani opakovaný HOLD motor samy nerozjedou. Tato prodleva není měření zastavení motoru. Servo i jeho směry zůstávají beze změny. [Ovládání a plán příští zkoušky](rizeni-v3.md#příští-zkouška-couvání--zatím-neprovedená) navazují v původní úloze; nejprve zvlášť vpřed/vzad a puštění, s koly nad stolem, teprve potom řízení. Překlad a úplná offline regrese prošly; upload už nečeká na potvrzení.

Předchozí uploady v1, v2 a v3 zachovávají svoji [evidenci](../../models/jednoduche-auticko/firmware/prvni-motor/README.md). Po uživatelem potvrzeném pohybu volného serva v2 oběma směry první trim v3 na 1525 µs s připojeným táhlem podle hlášení ponechal kola mírně doleva. Předchozí [verze `v3-steering-v4`](../../models/jednoduche-auticko/firmware/prvni-motor/evidence/2026-09-22-v3-steering-v4/README.md), zdroj SHA256 `0ee42b5512b97240a9d466e833e46a4360a3d4b5a7d112ae647146946781126e`, byla nahraná: **střed 1575 µs, ±300 µs / 50 Hz**, přímo +50 µs od v3 bez mezikroku. [Upload 84 948 B / 21 stran / exit 0 a tři klidové výpisy](../../models/jednoduche-auticko/firmware/prvni-motor/evidence/2026-09-22-v3-steering-v4/README.md) potvrdily tuto verzi a nominální střed 1575 µs; uživatel následně s připojeným táhlem a povelem Rovně potvrdil správnou neutrální polohu kol („Super, takhle to je perfektní“). Tehdejší stav před uploadem byl uživatelsky potvrzený: servo plus odpojený, motor bez napájení, UNO na USB; při závěrečné zkoušce zůstalo táhlo připojené a kola byla nad stolem. Odpojení serva po této historické zkoušce tehdy nepotvrdil; nové potvrzení přišlo před uploadem couvání výše. Neutrální poloha v4 není fyzická akceptace nové verze. [Chronologie](kontrolni-zapojeni.md#hlasova-zkouska-22-9-2026) a [řízení V3](rizeni-v3.md) odlišují upload od fyzického výsledku. V uvedených trimových verzích zůstaly piny D5/D7/D8/D9, motorové PWM 128/255 a ovládací protokol stejné; nahrané rozšíření couvání výše mění motorový záměr na −1/0/1. Poslední úplná akceptace motorového ovládání patří historickému hold-to-run-v2; dorazy, zatížení a jízda V3 nejsou fyzicky přijaté.

Nejprve uživatel bez externích součástek ověřil nahrání, Wi-Fi, stránku a reakci LED. Později sestavil obvod a nejprve jej zapnul jen přes USB s jednou baterií mimo držák. Po vložení poslední baterie motor zůstal stát a po stisku tlačítka se podle uživatele přibližně na sekundu rozběhl. Následné vyjmutí jednoho článku motorový obvod přerušilo a další rozběh nenastal. Tento výsledek je uložený v [záznamu stolního testu](prvni-stolni-test.md); nenahrazuje chybějící měření nebo zkoušku jízdy.
