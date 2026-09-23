# Regrese motoru a řízení SG90 — v3-steering-v1

Z kořene projektu spusť:

```bash
python3 models/jednoduche-auticko/firmware/prvni-motor/tests/run_http_tests.py
```

Python 3, g++ a Node.js přeloží skutečný aktuální sketch proti hostovým náhradám Arduino/WiFiS3/FspTimer/PwmOut a vykonají jeho skutečný vložený JavaScript. Dočasné binárky vznikají v ignorované `.cache/` vedle firmwaru. Tyto testy neotevírají USB ani sériová zařízení, nenahrávají firmware a neovládají hardware. Volba `--source /absolutni/cesta/sketch.ino` vybírá jiný kompatibilní zdroj. Přesná původní v2 má vlastní nezměněné testy v [archivu](../../archiv-hold-to-run-v2/).

## Hostový firmware

- **109 případů parseru a 109 průchodů úplným HTTP loopem:** původní motorové požadavky, mobilní hlavičky, délkové a časové meze, nonce, tokeny, čísla stisku a nový společný motorový/řídicí úmysl. Částečné, duplicitní či neplatné `X-Control-Motor` / `X-Control-Steer` se odmítají; nikdy nepřejdou na výchozí motorový povel.
- **34 skupin stavových scénářů:** ARM bez pohybu, motorová v2 kompatibilita, jednorázové výzvy, STOP před ARM/HOLD, staré a duplicitní pakety, vypršení, obnova relace, síťové chyby, přetečení času a čítačů, chyby RNG, PWM a bezpečnostního časovače. Steer-only HOLD nezapne motor; změna úmyslu může ponechat řízení a vypnout motor nebo zachovat motor a centrovat řízení.
- **7 původních + 7 společných blokujících zkoušek:** status, connected, available, read, write, stop a Serial zablokované na 1000 ms. Simulovaný IRQ vypne motor a vydá 1500µs neutrál i bez hlavní smyčky. Mez je 505 ms od posledního přijatého HOLD kvůli fázi 5ms taktu, naměřeno v simulaci 500 ms. Zvlášť se kontroluje neúplné HTTP čekající do timeoutu.
- D5 zůstává na 490 Hz a 128/255, D7 HIGH / D8 LOW při chodu. Servo D9 má 50 Hz a povely 1350 / 1500 / 1650 µs. Chyba servového PWM vypne motor, zablokuje další povely a přepne signál serva na LOW; test tento stav nevydává za dosažený fyzický střed.

Časovač v mocku běží i uvnitř blokujícího I/O. Jakékoliv sériové, síťové nebo náhodné I/O uvnitř ISR je chyba. Nová rozšíření zachovávají motorovou v2 regresi při intervalech 200–400 ms i konzervativní hranici až 1000 ms při ztraceném STOP a posledním opožděném HOLD. Toto jsou modelové testy, nikoli měření skutečného telefonu, MCU, serva nebo mechanického doběhu.

## Skutečný vložený JavaScript

**33 scénářů v Node.js** s deterministickou náhradou DOM, fetch, abortu a časovačů kontroluje původní v2 ovládání a navíc:

- Řízení bez motoru; dva dotyky v obou pořadích, včetně sekundárního dotyku na motoru.
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

**14 scénářů** pokrývá původních devět síťových regresí (200/300/400ms odezvy, jitter, ztracené odpovědi a staré pakety), skutečné dotykové události dvěma prsty v obou pořadích, nezávislé puštění, kombinaci šipek, Rovně, ztrátu focusu, společný timeout a mobilní rozvržení. Snímek mobilního UI 390 × 844 je uložen přímo do [elektroniky](../../../../../elektronika/auticko/nahled-ovladani-v3.png). Volitelný `TEST_MATCH` slouží jen k diagnostice jedné skupiny; filtrovaný běh nenahrazuje úplnou regresi.

## Offline náhled

```bash
python3 models/jednoduche-auticko/firmware/prvni-motor/tests/export_preview.py
```

[Náhled](../../../../../elektronika/auticko/nahled-ovladani-v3.html) zachovává vložené UI a doplňuje viditelné označení simulace, náhradu fetch a CSP `connect-src 'none'`. Nemůže ovládat hardware ani posílat síťové požadavky. Obsahuje hash zdrojového sketche.

Finální výsledky a logy jsou v [evidence/2026-09-20-v3-steering-v1](../evidence/2026-09-20-v3-steering-v1/). Překlad ani hostové/browserové testy neznamenají upload nebo fyzickou zkoušku nové verze.
