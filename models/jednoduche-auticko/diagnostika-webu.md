# Načítání stránky po restartu — 19. 9. 2026

**Nejnovější stav: USB diagnostika prokázala trvalé zablokování obsluhy (`ready=0`) po chybovém výsledku Wi-Fi 255. Oprava zotavení je připravená ve zdroji a prošla hostovými regresemi; její překlad pro desku probíhá. Nová verze dosud nebyla nahraná ani fyzicky ověřená. Důvod samotného výsledku 255 ještě známý není.** Poslední uživatelské potvrzení „celý setup funguje super“ a zachycený HTTP TEST patří předchozí diagnostické verzi, nikoli opravě.

Po dříve úspěšném stolním motorovém testu uživatel hlásil opakované nekončící načítání stránky po vypnutí a zapnutí Arduina. Potvrdil připojení telefonu k `Auticko-test`, adresu `http://192.168.4.1/` i použití výslovného HTTP odkazu. Jednou po zavření a otevření prohlížeče oznámil úspěch, potom problém znovu potvrdil. Při tomto prvním hlášení ještě nebyla příčina určená; následná reprodukce níže doložila zablokování programu, nikoli původ chybového stavu modulu.

Arduino bylo následně připojeno datovým USB kabelem do počítače. Systém a Arduino CLI potvrdily UNO R4 WiFi na `/dev/ttyACM0`, přístup pro čtení/zápis a volný port. Motorový držák má podle pokynu zůstat s jednou baterií vyjmutou; agent motorový požadavek neposílal. Počítač má Ethernet, nikoli dostupný Wi-Fi adaptér, proto se požadavky telefonu sledují přes sériový výpis Arduina.

## Diagnostická verze

Do [firmwaru](firmware/prvni-motor/prvni-motor.ino) byl přidán výpis při 115200 baud: stav startu AP a serveru, uložená verze Wi-Fi firmwaru a IP, změny stavu Wi-Fi, přijetí a klasifikace HTTP požadavku, návrat z odpovědi a ukončení klienta. Snapshot se opakuje po pěti sekundách; znak `?` jej vyžádá nejvýše jednou za sekundu. Zprávy neobsahují hesla ani obsah požadavků.

UNO R4 WiFi používá pro `Serial` UART přes ESP bridge. Výpis nečeká na otevření monitoru; krátký UART přenos je synchronní. **Uvnitř motorového pulzu není žádná síťová ani sériová komunikace.** V této diagnostické verzi zůstaly parser, motorové piny, délka pulzu, `server.available()` i dosavadní zablokování po chybě Wi-Fi beze změny: šlo o diagnostiku, nikoli opravu výpadku.

- Zdroj SHA256: `8a3eeb5f802b223b4b6cdb6bba02b40d513150aacf55e07026dd09c9dad99cad`.
- Prošlo 53 případů parseru a 53 celého loop, plus nové testy diagnostiky, limitování výpisu a zachování vypnutí při chybě Wi-Fi.
- Překlad pro UNO R4 WiFi / Renesas 1.6.0: flash 69 400 B, globální RAM 8 688 B.
- Upload dokončen bez chyby: 69 408 B, 17 stran, 100 %. Program nebyl čten zpět. Při samotném uploadu agent motorový pulz nevyvolal; pozdější uživatelská zkouška této verze je zaznamenaná níže.
- Původní verze s již potvrzeným motorovým rozběhem měla SHA256 `04429d8c23b01743c1ef7d769c449e56ffee600d4a31bb5141314fc96dc30209`. Její [fyzický výsledek](prvni-stolni-test.md) zůstává platný jako historie, ne jako nový test změněného programu.

## První skutečně načtený stav desky

Po tomto uploadu USB výpis potvrdil:

```text
boot=server-started fw=0.4.1 ip=192.168.4.1
ready=1 server=1 APstart=7 statusLast=7 HTTP=0 closed=0
```

Server se při tomto startu vytvořil a adresa je správná. V prvních zachycených snímcích nebyl přijatý HTTP požadavek. Po opětovném připojení telefonu se stav změnil na 8 (`WL_AP_CONNECTED`). **Uživatel potvrdil zobrazení stránky** a USB log zachytil dvě úplné sekvence `HTTP PAGE → response-returned → closed`. Poslední snapshot v této fázi měl `ready=1 server=1 HTTP=4 closed=4`; další dva požadavky nemají kvůli omezení frekvence detailní klasifikaci. Hodnota `server=1` sama znamená pouze vytvořený socket; zde ji doplňuje skutečná obsluha požadavků a potvrzení zobrazení uživatelem.

Výsledek je úspěšné načítání po diagnostickém uploadu, **nikoli prokázaná oprava občasného výpadku**. Uživatel byl požádán jednou stisknout RESET pro opakování startu. Potvrzení tohoto kroku nedodal; místo něj v souvislosti s baterií a další zkouškou oznámil „Funguje to super“ a požádal diagnostiku ukončit a pokračovat dál. **Diagnostika tím byla na jeho žádost ukončena.** Přesný průběh dalšího motorového pulzu, provedení RESET ani poslední stav bateriového držáku z tohoto hlášení nelze určit; starší vyjmutou baterii nepovažovat automaticky za aktuální stav.

V závěru této první fáze zůstala nahraná diagnostická verze; opravný zásah do řízení serveru ani ESP firmwaru tehdy neproběhl. Následný návrat závady a obnovené práce jsou zaznamenané níže.

## Možnosti zvažované před reprodukcí

- Jediný neplatný výsledek `WiFi.status()` v původním i diagnostickém loop nastavoval `ready=false` až do restartu. Instalovaná WiFiS3 může vrátit 0 při selhání dotazu na modem. Pozdější hardwarové pozorování níže zachytilo hodnotu 255; příčinu této konkrétní hodnoty neurčilo.
- `server.begin()` nevrací výsledek a původní program po něm nastavuje `ready=true` bez ověření socketu. Diagnostika nově pouze zaznamenává `bool(server)`; při tomto pozorovaném startu byl výsledek 1.
- Předotevřená TCP spojení a chování `available()` vyžadují ověření proti skutečnému Wi-Fi firmwaru. Na desce je nyní zjištěná verze 0.4.1; automatická výměna za `accept()` ani aktualizace ESP firmwaru neproběhla.
- Aplikační třísekundový příjem není tvrdý limit všech volání: knihovna může čekat na odpověď modemu déle. Z diagnostiky je potřeba určit poslední dokončený krok, než se začne měnit řízení serveru.

Úplný pracovní log z tohoto běhu je mimo repozitář v `/home/novakj/.cache/auticko-arduino-test/network-diagnostics-serial.log`; není přenositelným projektovým artefaktem. Výsledky podstatné pro další postup patří sem. Žádný commit ani push při diagnostice neproběhl.

## Návrat závady a potvrzený mechanismus

Po ukončení předchozího pokusu uživatel znovu odpojil a zapojil Arduino a hlásil nekončící načítání stránky. Potvrdil USB do počítače. Deska byla skutečně na `/dev/ttyACM0`; monitor byl otevřený při 115200 baud **bez uploadu či restartu**, aby zůstal zachovaný nefunkční stav.

```text
DIAG 100843 boot=server-started fw=0.4.1 ip=192.168.4.1
DIAG ready=0 server=1 APstart=7 statusLast=255 ageMs=90190 HTTP=0 closed=0
```

V této reprodukci server při startu vznikl a IP byla správná. Asi 90 sekund před přečtením snapshotu se stav Wi-Fi změnil na chybnou hodnotu 255, načež náš program vypnul motorové výstupy a trvale zakázal další obsluhu. Nepřijal žádný HTTP požadavek. To dokládá bezprostřední důvod neobsloužené stránky; protože při `ready=false` původní loop už `WiFi.status()` nevolá, nevíme, zda problém modemu přetrvával, nebo šlo o přechodnou chybu.

## Další úspěšný start diagnostické verze

Během přípravy opravy uživatel znovu odpojil a připojil USB. Monitor zachytil nový start se zdravým `ready=1`, `server=1` a stavem 8, dvě obsluhy `HTTP PAGE` a poté `HTTP TEST 5 → response-returned → closed` v 10:46:46. Požadavek TEST vyvolal uživatel, nikoli agent. Uživatel následně řekl **„celý setup funguje super“**; hlasová relace skončila, ale uživatel tím nezrušil rozpracovanou opravu známé chyby.

Tento úspěch stále patří diagnostickému zdroji **`8a3eeb5f…`**. Dokládá úspěšnou uživatelskou zkoušku této verze; samotný USB log potvrzuje obsluhu příkazu a návrat z odpovědi, nikoli fyzické měření pohybu nebo elektrických parametrů motoru. Jedním funkčním startem se nevyvrací dříve zachycené trvalé zablokování při chybě 255.

## Připravená oprava — dosud nenahraná

Aktuální [zdroj programu](firmware/prvni-motor/prvni-motor.ino) má SHA256 **`772cd12f0e3c1ead271666b5d80e7a291e4f2ef341c526692404f2b24ac74b48`**. Následující změny jsou ověřené v hostových testech, ne na desce:

- Chybný stav Wi-Fi vypne motorové výstupy, zneplatní token a pozastaví obsluhu. Kontrola se během čekání opakuje s odstupem alespoň **1 s**; po návratu stavu 7 nebo 8 se obsluha může obnovit. Chybějící modul při startu už nevede k trvalému návratu ze setup bez dalšího pokusu.
- Po `server.begin()` se kontroluje `bool(server)`. Při neúspěchu zůstává motor vypnutý a start serveru se později zopakuje. Po přechodné chybě se existující server ani AP zbytečně nerestartují.
- Nové načtení stránky vydá **jednorázový token**, který musí platný POST předat v hlavičce `X-Motor-Token`. Token se spotřebuje před motorovým pulzem; chyba Wi-Fi jej zneplatní. Starý nebo zopakovaný POST proto po zotavení motor nespustí. Nové načtení stránky zneplatní také token předchozí stránky. Token používá hardwarový generátor náhodných hodnot dostupný přes `random()` v instalovaném UNO R4 core a čítač; při chybě generátoru se nové povolení nevydá.
- Po STOP úspěšná odpověď vrátí nový token a tlačítko dovolí **další vědomý stisk**. Prohlížeč neposílá automatický motorový pokus ani retry. Po chybě či nejednoznačném výsledku zůstává tlačítko vypnuté a stránku je nutné znovu načíst.
- Po přijetí a ověření POST se stav Wi-Fi kontroluje ještě jednou. Bezprostředně před pulzem musí být stáří aktuální obsluhy, měřené od začátku jejího loop před síťovými dotazy, **menší než 3 s**. Zdržení následným AT dotazem tak nemůže obejít samotný timeout parseru a spustit opožděný pulz.
- Funkce `motorPulse()` zůstala beze změny: D5 PWM 128/255, D7 HIGH, D8 LOW, `delay(1000)`, potom vypnutí enable a obou směrových vstupů. Uvnitř pulzu stále není Wi-Fi ani Serial I/O. Původní limity HTTP a ostatní validace zůstaly zachované; POST navíc vyžaduje token.

Ochrana tokenem je nutná i při obnově serveru: [ESP bridge 0.4.1 v obsluze SERVEREND](https://github.com/arduino/uno-r4-wifi-usb-bridge/blob/0.4.1/UNOR4USBBridge/cmds_wifi_netif.h#L597) výslovně nečistí přijaté klienty. Nelze předpokládat, že pouhé ukončení serveru odstranilo všechny staré požadavky. Oprava proto na takový předpoklad nespoléhá a nepřepíná `available()` na `accept()`.

**Provedené kontroly:** původních 53 případů parseru a 53 celého loop; navíc odmítnutí neplatných tokenů, spotřeba před pulzem, nový token po STOP, opakovaný vědomý stisk, odmítnutí replay a selhání generátoru. Osm scénářů zotavení pokrývá jednotlivé chybné stavy 255/0/77, chybu 255 až po parseru, zpoždění druhého dotazu o 4000 ms a počáteční selhání modulu, AP či serveru. Starý POST zůstával ve frontě testové náhrady a po zotavení byl odmítnut; nový GET a nový POST následně prošly. Prošel také kontrolní běh původního parseru, syntaxe vloženého JavaScriptu a `git diff --check`. [Spuštění a rozsah regresí](firmware/prvni-motor/tests/README.md).

**Omezení:** jde o obnovu obsluhy po přechodném chybném stavu, ne o prokázanou opravu příčiny výpadku ESP. `bool(server)` kontroluje místní identifikátor socketu a nezaručuje, že listener přežil skutečný restart modulu. Po již úspěšném založení AP tato oprava AP znovu nezakládá. Jednosekundový interval není horní doba zotavení: jednotlivá volání WiFiS3 mohou čekat na modem až 10 s. Třísekundová podmínka před pulzem takové čekání nepřeruší, pouze zabrání následnému zapnutí motoru; není měřením času od uživatelova stisku ani fyzickou zárukou síťové odezvy.

**Hardware stav této opravy: nenahraná, fyzický výsledek zatím není.** Výsledek překladu, uploadu a nové zkoušky se doplní samostatně; úspěch diagnostické verze se na tento hash nepřenáší.
