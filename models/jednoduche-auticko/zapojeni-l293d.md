# První test motoru — Arduino UNO R4 WiFi a ST L293D

**Stav k 19. 9. 2026: uživatel sestavil obvod a potvrdil první přibližně sekundový rozběh motoru tlačítkem z telefonu.** [Záznam skutečné zkoušky](prvni-stolni-test.md) rozlišuje potvrzené kroky, částečnou fotografickou kontrolu a neověřené parametry. Tabulka níže je referenční zapojení; každý spoj nebyl nezávisle proměřen.

U neoznačeného samostatného DC motoru uživatel zadal **předpoklad 1–6 V**, nikoli ověřený údaj výrobce. Místo původně navrhované regulované 5V motorové větve se při pokusu použil sériový držák čtyř AA se směsí Ni-MH 1,2 V a běžných článků. Skutečné celkové napětí a odběr nebyly měřené. Tato provizorní směs není návrhem pro další běžný provoz. Arduino bylo napájené samostatně z USB powerbanky.

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

[Program pro UNO R4 WiFi](firmware/prvni-motor/prvni-motor.ino) a [návod k prvnímu testu](firmware/prvni-motor/README.md). Program vytvoří vlastní Wi-Fi síť a stránku s jedním tlačítkem. Jeden stisk požádá o jediný sekundový impuls vpřed; následuje vypnutí výkonového výstupu. Je to krátký test na stole, ne finální řízení jízdy při držení tlačítka.

Nejprve uživatel bez externích součástek ověřil nahrání, Wi-Fi, stránku a reakci LED. Později sestavil obvod a nejprve jej zapnul jen přes USB s jednou baterií mimo držák. Po vložení poslední baterie motor zůstal stát a po stisku tlačítka se podle uživatele přibližně na sekundu rozběhl. Následné vyjmutí jednoho článku motorový obvod přerušilo a další rozběh nenastal. Tento výsledek je uložený v [záznamu stolního testu](prvni-stolni-test.md); nenahrazuje chybějící měření nebo zkoušku jízdy.
