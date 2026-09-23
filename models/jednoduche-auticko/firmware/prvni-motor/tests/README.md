# Regrese motoru a řízení SG90 — v3-reverse-v1

**Úplná regrese `v3-reverse-v1` prošla: 120 parserových + 120 HTTP případů, 42 hostových scénářů, 21 blokujících zkoušek, 46 JS scénářů a 23 skutečných Chromium HTTP scénářů.** Překlad UNO R4 prošel: 86 708 B flash / 9 868 B RAM. [Evidence a přesný hash](../evidence/2026-09-22-v3-reverse-v1/README.md). Stejný zdroj `d24a87631fd32a41685baedd7488c425a75ca6f9e300706349c61e09e79fe930` byl následně [nahrán jako v3-reverse-v1](../evidence/2026-09-23-v3-reverse-v1-upload/README.md): 86 716 B / 22 stran / exit 0, tři pasivní klidové výpisy. Čítače zařízení byly stabilní HTTP=29 / closed=29 s neurčeným původem dřívějších požadavků; agent odeslal 0 sériových dat, 0 HTTP a 0 pohybových povelů. **Fyzická zkouška nové verze ani měření PWM neproběhly.** Historická steering-v4 a její uživatelem přijatá neutrální poloha kol mají samostatnou [evidenci](../evidence/2026-09-22-v3-steering-v4/README.md), která není fyzickou akceptací couvání. Níže je popis testované logiky, nikoli tvrzení o skutečném hardwaru.

Z kořene projektu spusť:

```bash
python3 models/jednoduche-auticko/firmware/prvni-motor/tests/run_http_tests.py
```

Python 3, g++ a Node.js přeloží skutečný aktuální sketch proti hostovým náhradám Arduino/WiFiS3/FspTimer/PwmOut a vykonají jeho skutečný vložený JavaScript. Dočasné binárky vznikají v ignorované `.cache/` vedle firmwaru. Tyto testy neotevírají USB ani sériová zařízení, nenahrávají firmware a neovládají hardware. Volba `--source /absolutni/cesta/sketch.ino` vybírá jiný kompatibilní zdroj. Přesná původní v2 má vlastní nezměněné testy v [archivu](../../archiv-hold-to-run-v2/).

## Hostový firmware

- **Parser a úplný HTTP loop:** původní motorové požadavky, mobilní hlavičky, délkové a časové meze, nonce, tokeny, čísla stisku a nový společný motorový/řídicí úmysl. Částečné, duplicitní či neplatné `X-Control-Motor` / `X-Control-Steer` se odmítají; nikdy nepřejdou na výchozí motorový povel.
- **Stavové scénáře:** ARM bez pohybu, motorová v2 kompatibilita, jednorázové výzvy, STOP před ARM/HOLD, staré a duplicitní pakety, vypršení, obnova relace, síťové chyby, přetečení času a čítačů, chyby RNG, PWM a bezpečnostního časovače. Steer-only HOLD nezapne motor; změna úmyslu může ponechat řízení a vypnout motor nebo zachovat motor a centrovat řízení.
- **7 původních + 7 společných + 7 reverzních blokujících zkoušek:** status, connected, available, read, write, stop a Serial zablokované na 1000 ms. Simulovaný IRQ vypne motor a vydá 1575µs neutrál i bez hlavní smyčky. Mez je 505 ms od posledního přijatého HOLD kvůli fázi 5ms taktu, naměřeno v simulaci 500 ms. Zvlášť se kontroluje neúplné HTTP čekající do timeoutu.
- D5 zůstává na 490 Hz a 128/255 v obou směrech; vpřed D7 HIGH / D8 LOW, vzad D7 LOW / D8 HIGH, vypnuto EN=0 a oba vstupy LOW. Servo D9 má 50 Hz a povely 1275 / 1575 / 1875 µs. Chyba servového PWM vypne motor, zablokuje další povely a přepne signál serva na LOW; test tento stav nevydává za dosažený fyzický střed.

Rozšíření couvání kontroluje přesné motorové hodnoty `-1`, `0`, `1`, odmítnutí nekanonických či neúplných hlaviček a zachování legacy motor vpřed / servo střed pouze při vynechání obou záměrů. Kontroluje opačné IN1/IN2, skutečné OFF před změnou směru a nejméně 250 ms od něj. Předčasný opačný HOLD musí vrátit `HOLD_REARM` bez nonce, ukončit sekvenci a ponechat výstupy vypnuté. Ani čas, starý HOLD/retry nebo ARM se stejným číslem stisku nesmějí běh obnovit. Časové měření v mocku neprokazuje mechanické zastavení motoru.

Časovač v mocku běží i uvnitř blokujícího I/O. Jakékoliv sériové, síťové nebo náhodné I/O uvnitř ISR je chyba. Nová rozšíření zachovávají motorovou v2 regresi při intervalech 200–400 ms i konzervativní hranici až 1000 ms při ztraceném STOP a posledním opožděném HOLD. Toto jsou modelové testy, nikoli měření skutečného telefonu, MCU, serva nebo mechanického doběhu.

## Skutečný vložený JavaScript

Scénáře v Node.js s deterministickou náhradou DOM, fetch, abortu a časovačů zachovávají původní ovládání a kontrolují:

- Řízení bez motoru; dva dotyky v obou pořadích, včetně sekundárního dotyku na motoru, také při couvání.
- Couvání myší, dotykem, ArrowDown a Space/Enter; signed záměr a oddělené indikátory běhu vpřed/vzad. Řízení se při couvání neobrací.
- Evidence všech fyzických kontaktů, včetně odmítnutých během západky či STOP a druhého dotyku stejného tlačítka; žádné předání řízení zbývajícímu dotyku.
- Konflikt vpřed/vzad, STOP a povinné puštění všech kontaktů/kláves včetně nových kontaktů během čekání na STOP, kontaktů odmítnutých za povinného puštění a druhého dotyku stejného tlačítka. Po `HOLD_REARM` nesmí opakovaný HOLD, klávesa, puštění ani čas vyvolat nový běh; potřeba nového skutečného stisku.
- Nezávislé puštění motoru či směru, protichůdné směry, explicitní Rovně a kombinace šipek na klávesnici.
- Jeden rozpracovaný ARM/HOLD a jednorázové nonce; změna úmyslu čeká na odpověď předchozího HOLD.
- Puštění nebo chyba během čekání, ignorovaný abort transportem, opožděné odpovědi, blur, skrytí stránky, offline a pointercancel. Staré odpovědi neobnoví UI ani pohyb; nový běh vyžaduje nový skutečný stisk.

```bash
node models/jednoduche-auticko/firmware/prvni-motor/tests/browser_tests.js
```

## Skutečný Chromium přes lokální HTTP

```bash
python3 models/jednoduche-auticko/firmware/prvni-motor/tests/run_http_tests.py --browser
```

Vyžaduje Playwright a Chromium; lze nastavit `PLAYWRIGHT_MODULE` a `PLAYWRIGHT_CHROMIUM_EXECUTABLE`. Testovací HTTP server naslouchá pouze na `127.0.0.1` a předává požadavky skutečnému C++ sketchi v trvalém hostovém procesu. IP/Origin se v tomto bridge přepíší na očekávané hlavičky Arduina; žádné skutečné Arduino se nekontaktuje.

Sada zachovává původních devět síťových regresí (200/300/400ms odezvy, jitter, ztracené odpovědi a staré pakety), skutečné dotykové události dvěma prsty v obou pořadích, nezávislé puštění, kombinaci šipek, Rovně, ztrátu focusu, společný timeout a mobilní rozvržení. Rozšíření ověřuje couvání přes `motorDirection` a skutečné mockované IN1/IN2, obě pořadí dotyků s nezměněným natočením kol, konflikty a nové skutečné stisky. Po 250 ms opakuje původní odmítnutý HOLD i ARM a vyžaduje stále motor OFF; zkouší i puštění před opožděnou odpovědí REARM se ztraceným STOP. Native pointerdown na disabled tlačítku během 1000ms čekání na STOP je skutečně vyvolaný přes CDP a ověřený; další kontakt se neztratí ani po puštění původních prstů. Samotné PWM 128 nestačí jako důkaz směru. Skutečné CDP dotyky kontrolují také doručení pointerdown na disabled tlačítku během čekání na STOP a uchování všech těchto kontaktů až do jejich puštění. Snímek mobilního UI 390 × 844 je uložen přímo do [elektroniky](../../../../../elektronika/auticko/nahled-ovladani-v3.png). Volitelný `TEST_MATCH` slouží jen k diagnostice jedné skupiny; filtrovaný běh nenahrazuje úplnou regresi.

## Offline náhled

```bash
python3 models/jednoduche-auticko/firmware/prvni-motor/tests/export_preview.py
```

[Náhled](../../../../../elektronika/auticko/nahled-ovladani-v3.html) zachovává vložené UI a doplňuje viditelné označení simulace, náhradu fetch a CSP `connect-src 'none'`. Nemůže ovládat hardware ani posílat síťové požadavky. Obsahuje hash zdrojového sketche.

Historické úplné výsledky steering-v3 jsou v [evidence/2026-09-22-v3-steering-v3](../evidence/2026-09-22-v3-steering-v3/). Při následujícím trimu v4 se upravila jen očekávání pulzů bez opakování celé sady; aktuální couvání už přidává nové regresní scénáře. Nový výsledek je samostatně doložený pro přesný zdroj v odkazu výše. Původní v1 má zachované [testy a manifest](../../archiv-v3-steering-v1/archiv-manifest.json). Překlad ani hostové/browserové testy neznamenají upload nebo fyzickou zkoušku nové verze.
