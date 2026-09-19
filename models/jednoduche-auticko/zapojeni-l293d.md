# První test motoru — Arduino UNO R4 WiFi a ST L293D

**Stav: návrh vývodů ověřený podle datasheetu, fyzické zapojení a motor dosud neotestované.** Uživatel potvrdil L293D a požádal u neoznačeného samostatného DC motoru **předpokládat rozsah 1–6 V**. Jde o zadaný pracovní předpoklad, nikoli ověřený údaj výrobce. Pro tento předpoklad volíme regulovanou **5V motorovou větev**; skutečný dostupný zdroj a odběr motoru ještě nejsou ověřené. Motorové napájení připojit až po kontrole zdroje a zapojení.

## Co připravit na stole

Arduino UNO R4 WiFi, čip L293D, nepájivé pole, propojovací vodiče, motor. Dále odpor 10 kΩ a dva keramické kondenzátory 100 nF; jejich dostupnost ještě není ověřená. Napájení motoru a případný zásobní elektrolytický kondenzátor doplníme podle skutečného zdroje a odběru. Deska Arduina může být napájená přes datový USB kabel.

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
| **8 — VS, motorová větev** | Plus **samostatného regulovaného 5V zdroje** zvoleného pro předpokládaný motor 1–6 V; konkrétní zdroj zatím není potvrzený |
| **9, 10, 15 — nepoužité řízení** | GND |
| **11, 14 — nepoužité výstupy** | Nezapojovat |

Keramické kondenzátory **100 nF** umístit co nejblíže čipu: jeden mezi pin 16 a GND, druhý mezi pin 8 a GND. Odpor na pinu 1 drží výkonový výstup vypnutý během resetu, kdy se na řízení Arduinem ještě nelze spolehnout.

Pozor na rozdělené napájecí lišty nepájivého pole; jejich skutečné propojení ověřit. Motorový proud nesmí procházet výstupním GPIO Arduina. Arduino a motorový zdroj sdílejí zem; z toho neplyne spojit kladné motorové napájení s 5V pinem Arduina.

## Co musí být určeno před zapnutím motoru

- Označení motoru, jmenovité napětí a proud včetně rozběhu/zablokování, případně způsob omezené zkoušky se známým zdrojem a měřením.
- Typ, napětí a proudové možnosti zdroje. Hodnotu neodvozovat z rozměrů motoru.
- Kontrola zapojení a polarity; při prvním běhu motor nebo kola volně ve vzduchu.

Podle ST musí být **VS nejméně VSS**. Pro zde navrženou logiku 5 V proto volíme VS 5 V, v souladu s uživatelem zadaným předpokladem motoru 1–6 V. Napětí přímo na motoru je nižší o úbytek můstku a závisí na proudu. Při 600 mA jsou úbytky obou větví typicky celkem 2,6 V, maximálně 3,6 V. PWM není náhradou za správně zvolené napájení a proudové dimenzování; 50% PWM neznamená pevné napětí 2,5 V na motoru.

L293D má uvedeno 600 mA na kanál, ale je nutné dodržet teplotní podmínky; to není záruka bezpečného trvalého provozu v nepájivém poli. Špičkových 1,2 A platí pouze pro neopakovaný impuls 100 µs. Čip obsahuje ochranné diody. Při enable LOW jsou výstupy ve vysoké impedanci: motor **volně dobíhá**, aktivně nebrzdí.

Zdroj a kontrola: [ST L293D — datasheet, DIP16 pinout na straně 2, elektrické charakteristiky na straně 3, pravdivostní tabulka na straně 4](https://www.st.com/resource/en/datasheet/l293d.pdf). Nezaměnit s pouzdrem L293DD o 20 vývodech.

## Program a první postup

[Program pro UNO R4 WiFi](firmware/prvni-motor/prvni-motor.ino) a [návod k prvnímu testu](firmware/prvni-motor/README.md). Program vytvoří vlastní Wi-Fi síť a stránku s jedním tlačítkem. Jeden stisk požádá o jediný sekundový impuls vpřed; následuje vypnutí výkonového výstupu. Je to krátký test na stole, ne finální řízení jízdy při držení tlačítka.

Nejprve lze bez připojeného motorového napájení ověřit nahrání, Wi-Fi a ovládací stránku. Skutečný motorový test následuje až po vyřešení napájení výše. Nahrání bylo úspěšné. Uživatel potvrdil Wi-Fi, načtení ovládací stránky a rozsvícení LED po stisku tlačítka; při této zkoušce neměl žádné externí součástky připojené. Fyzický běh motoru dosud potvrzený není.
