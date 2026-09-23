# Regrese ovládání při držení — v2

Z kořene repozitáře:

```bash
python3 models/jednoduche-auticko/firmware/prvni-motor/tests/run_http_tests.py
```

Potřebuje Python 3, g++ a Node.js. Jeden příkaz přeloží **skutečný aktuální sketch** proti hostovým náhradám Arduino/WiFiS3/FspTimer/PwmOut a potom spustí **skutečný JavaScript vyjmutý z jeho HTML**. C++ binárka vzniká v dočasné složce. Tyto dvě sady neotevírají USB port ani síť, nenahrávají firmware a neroztáčejí skutečný motor. Volba `--source /absolutni/cesta/sketch.ino` umožňuje kontrolu jiné kopie stejného protokolu; původní pulzní `/test` se již musí odmítat.

## HTTP a řízení motoru

**90 případů parseru a stejných 90 případů přes skutečný `loop()`** zachovává původních 53 tříd HTTP regresí a přidává nový protokol. Kontroluje mobilní Chrome/Safari hlavičky, fragmentaci, CRLF, syntaxi a zdvojené hlavičky, Host a Origin, nulové tělo, mezní délky **1024 znaků na řádek / 8192 bajtů celkem / 3000 ms příjem**, správný session token, kanonické kladné číslo stisku bez přetečení a formát výzvy. Samotný GET, SESSION, ARM, STOP ani nepřipravený HOLD motor nezapne. `/session` přijímá pouze POST s předepsanými hlavičkami.

**28 navazujících skupin scénářů** kontroluje:

- ARM bez pohybu, první HOLD s čerstvou výzvou, opakované potvrzování držení a STOP.
- STOP, který předběhne ARM nebo HOLD, opakované a opožděné požadavky, obnovu stránky a nový skutečný stisk. Starší STOP/ARM/HOLD novější jízdu nepřeruší ani neprodlouží.
- Vypršení ARM i běžícího motoru, HOLD po vypršení a přetečení `millis()`. ARM zůstává bez pohybu nejvýše 3000 ms; první i další výzva pro HOLD přesto platí méně než 500 ms.
- Opravu dvojí závislosti na síťové latenci: platný HOLD dostane celých 500 ms od přijetí. Dvacet cyklů při každém z intervalů 200/250/300/400 ms udrží chod; původní v1 při 250 ms a více předčasně vypínala.
- Ztracený STOP a jeden opožděný HOLD: i tento případ skončí nejpozději do 1000 ms od simulovaného puštění. Duplicitní paket dobu neprodlužuje.
- Obnovu session po novém stisku, opakování po ztracené odpovědi, odmítnutí starší session, vyčištění obnovovacího záznamu novou stránkou a obnovu po startu desky. Opakovaný požadavek předchozí session vrací již vytvořený token, aniž by zastavoval nový běh.
- Přechodné stavy Wi-Fi 255/0/77 a návrat provozu s novou session, nejvýše jeden pokus za sekundu, odmítnutí starého požadavku z fronty; také chybějící modul, neúspěšný start AP nebo serveru.
- Start s vypnutými výstupy, selhání generátoru tokenů a session, vyčerpání čítačů, selhání každé fáze inicializace PWM/časovače a chybu aktualizace PWM včetně nouzového vypnutí GPIO.

Mock času vykonává přerušení každých 5 ms **i uvnitř simulovaného blokujícího volání**. Sedm dalších scénářů zdrží `WiFi.status`, `connected`, `available`, `read`, odpověď `write`, `stop` a Serial o 1000 ms; kontroluje se vypnutí bez spolupráce hlavní smyčky. Samostatný případ nechá nedokončené HTTP čekat do timeoutu. V testovaných časových fázích proběhne IRQ STOP za **500 ms** od posledního přijetí HOLD; assertion dovoluje nejvýše 505 ms kvůli fázi hostového taktu. To je simulované časování, nikoli měření MCU. Jakékoliv síťové, sériové nebo náhodné I/O přímo v ISR test odmítne. Hlavní smyčka komunikuje i za chodu motoru, proto na ní vypnutí nezávisí.

Odpovědi se kontrolují včetně `Content-Length`; všechny krátké odpovědi na POST používají **jediné `write()` a žádné `print()`**, aby nevytvářely řadu AT přenosů. Výstupy EN/D7/D8/LED jsou sledované. Mobilní hlavičky jsou realistické testovací vzory, nikoli záznam konkrétního telefonu.

## Ovládání v náhradě prohlížeče

**21 scénářů v Node.js** vykonává aktuální inline JavaScript v deterministických náhradách DOM událostí, `fetch`, abortu a časovačů:

- Držení myší a dotykem, řetězec nových výzev po **20 ms od odpovědi**, puštění, nový stisk a ignorování cizího pointeru.
- `pointercancel`, ztráta zachycení pointeru, `blur`, `pagehide`, offline a skrytí stránky.
- Opožděná odpověď ARM/HOLD po puštění, i když transport ignoruje abort: žádný nový HOLD ani falešný stav „jede“.
- Síťová nebo HTTP chyba, chybná výzva a timeout: STOP bez automatického opakování jízdy. Stále držený pointer nový pokus nespustí; je nutné pustit a nově stisknout.
- Neúspěšný STOP nezablokuje tlačítko navždy. Nový stisk nejprve obnoví session, potom teprve ARM/HOLD. Puštění při čekání na session nesmí spustit ARM.
- Mezerník/Enter a potlačení opakovaných `keydown`; samotné načtení stránky, `click`, pravé tlačítko či sekundární pointer jízdu nespouští.

Samostatné spuštění JavaScriptu:

```bash
node models/jednoduche-auticko/firmware/prvni-motor/tests/browser_tests.js
```

## Skutečný Chromium a HTTP

Doplňková integrační sada vyžaduje Playwright a lokální Chromium:

```bash
python3 models/jednoduche-auticko/firmware/prvni-motor/tests/run_http_tests.py --browser
```

Případně samostatně:

```bash
node models/jednoduche-auticko/firmware/prvni-motor/tests/browser_http_tests.js
```

Pokud Playwright není ve standardní cestě Node, nastavit `NODE_PATH` na adresář dostupných balíčků nebo `PLAYWRIGHT_MODULE` na modul. Volitelné `PLAYWRIGHT_CHROMIUM_EXECUTABLE` určuje již instalovanou binárku Chromium; test nic automaticky neinstaluje.

**9 scénářů** používá headless Chromium, skutečný DOM, myš/dotyk, `fetch`, HTTP a skutečný JavaScript stránky. Místní server je vázaný pouze na `127.0.0.1`; posílá požadavky do dlouho žijícího C++ procesu se skutečným `.ino`. Zachovává hlavičky prohlížeče, ale překládá místní Host/Origin na adresu očekávanou firmwarem. Timer běží v hostové náhradě i během prodlev HTTP. Nikdy se nespojuje s Arduinem, telefonem ani skutečnou sítí autíčka.

Kontroluje držení přes dvě sekundy při simulovaných round-trip prodlevách **200/300/400 ms**, proměnlivé prodlevy a dotyk, puštění během ARM odpovědi, ztracený STOP, ztrátu HOLD, obnovu až po novém stisku, ztracenou odpověď na obnovu session a opožděné příkazy starší jízdy. Krátké odpovědi a nové časování tak procházejí celým řetězcem prohlížeč → HTTP → parser → skutečná logika řízení.

## Meze ověření

Testy dokazují logiku skutečného zdroje za modelovaných událostí. Ani Chromium sada **neověřuje skutečnou latenci WiFiS3, běh IRQ na RA4M1, konkrétní telefon, napětí, zapojení ani doběh motoru**. Překlad pro UNO R4 WiFi a potvrzený upload jsou další oddělené kroky; držení/puštění a ztrátu spojení na sestaveném autíčku musí potvrdit fyzická zkouška. Odstranění fyzické příčiny dřívějších chyb modemu nebo slabého rozběhu z těchto regresí neplyne.

## Uložený běh finálního zdroje

Pro verzi v2 z 19. 9. 2026 jsou uloženy [hostové a JavaScriptové výsledky](../evidence/2026-09-19-hold-to-run-v2/host-tests.txt) a [Chromium HTTP výsledky](../evidence/2026-09-19-hold-to-run-v2/browser-http.txt). Oba soubory uvádějí SHA-256 testovaného sketchu a exit status. Nejsou důkazem nahrání na desku ani fyzické zkoušky motoru.
