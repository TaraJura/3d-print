# Hostové regrese ovládání při držení

Z kořene repozitáře:

```bash
python3 models/jednoduche-auticko/firmware/prvni-motor/tests/run_http_tests.py
```

Potřebuje Python 3, g++ a Node.js. Jeden příkaz přeloží **skutečný aktuální sketch** proti hostovým náhradám Arduino/WiFiS3/FspTimer/PwmOut a potom spustí **skutečný JavaScript vyjmutý z jeho HTML**. C++ binárka vzniká v dočasné složce. Testy neotevírají USB port, síť ani hardware, nenahrávají firmware a neroztáčejí skutečný motor. Volba `--source /absolutni/cesta/sketch.ino` umožňuje kontrolu jiné kopie stejného protokolu; starý pulzní protokol `/test` již není podporovaným režimem této sady.

## HTTP a řízení motoru

**82 případů parseru a stejných 82 případů přes skutečný `loop()`** zachovává původních 53 tříd HTTP regresí a přidává nový protokol. Kontroluje mobilní Chrome/Safari hlavičky, fragmentaci, CRLF, syntaxi a zdvojené hlavičky, Host a Origin, nulové tělo, mezní délky **1024 znaků na řádek / 8192 bajtů celkem / 3000 ms příjem**, správný session token, kanonické kladné číslo stisku bez přetečení a formát výzvy. Původní `/test` se odmítne. Samotný GET, ARM, STOP ani nepřipravený HOLD motor nezapne.

**19 navazujících skupin scénářů** kontroluje:

- ARM bez pohybu, první HOLD s čerstvou výzvou, opakované potvrzování držení a STOP.
- STOP, který předběhne ARM nebo HOLD, opakované a opožděné požadavky, obnovu stránky a nový skutečný stisk.
- Vypršení ARM i běžícího motoru, nový HOLD po vypršení, ukotvení limitu k vydání předchozí výzvy (opožděný paket nedostane nových 500 ms).
- Přetečení `millis()` a zákaz přetočení čísla stisku v téže session.
- Přechodné chybové stavy Wi-Fi 255/0/77 a návrat provozu s novou stránkou, nejvýše jeden pokus za sekundu, odmítnutí starého požadavku z fronty; také chybějící modul, neúspěšný start AP nebo serveru.
- Start vždy s vypnutými výstupy, selhání generátoru tokenů, vyčerpání čítače tokenů, selhání každé fáze inicializace PWM/časovače a chybu aktualizace PWM včetně nouzového vypnutí GPIO.

Mock času vykonává přerušení každých 5 ms **i uvnitř simulovaného blokujícího volání**. Sedm dalších scénářů zdrží `WiFi.status`, `connected`, `available`, `read`, odpověď `print`, `stop` a Serial o 1000 ms; kontroluje se vypnutí bez spolupráce hlavní smyčky. Samostatný případ nechá nedokončené HTTP čekat do timeoutu. V testovaných časových fázích proběhne IRQ STOP za **500 ms**; kontrola dovoluje nejvýše 505 ms od okamžitého potvrzení kvůli fázi hostového taktu. Ve zdroji se lease zaokrouhluje dolů a odvozuje od stáří výzvy. Jakékoliv síťové, sériové nebo náhodné I/O přímo v ISR test odmítne. Běžná hlavní smyčka naproti tomu komunikuje i za chodu motoru; právě proto je vypnutí nezávislé na ní.

Odpovědi se kontrolují včetně `Content-Length`; výstupy EN/D7/D8/LED jsou sledované. Mobilní hlavičky jsou realistické testovací vzory, nikoli záznam konkrétního telefonu.

## Ovládání v prohlížeči

**19 scénářů v Node.js** vykonává aktuální inline JavaScript v deterministických náhradách DOM událostí, `fetch`, abortu a časovačů:

- Držení myší a dotykem, řetězec nových výzev po 100 ms, puštění, nový stisk a ignorování cizího pointeru.
- `pointercancel`, ztráta zachycení pointeru, `blur`, `pagehide`, offline a skrytí stránky.
- Opožděná odpověď ARM/HOLD po puštění, i když simulovaný transport ignoruje abort: žádný nový HOLD ani falešný stav „jede“.
- Síťová nebo HTTP chyba, chybná výzva a timeout: STOP bez automatického opakování jízdy. Selhání STOP ponechá ovládání zablokované do obnovení stránky.
- Mezerník/Enter a potlačení opakovaných `keydown`; samotné načtení stránky, `click`, pravé tlačítko či sekundární pointer jízdu nespouští.

Samostatné spuštění pouze JavaScriptu:

```bash
node models/jednoduche-auticko/firmware/prvni-motor/tests/browser_tests.js
```

## Meze ověření

Tyto testy dokazují logiku skutečného zdroje za modelovaných událostí. Náhrady **neověřují skutečnou latenci WiFiS3, běh IRQ na RA4M1, chování fyzického telefonu, napětí, zapojení ani doběh motoru**. Překlad pro UNO R4 WiFi a potvrzený upload jsou další oddělené kroky; držení/puštění a ztrátu spojení na sestaveném autíčku musí potvrdit fyzická zkouška. Odstranění fyzické příčiny dřívějších chyb modemu z hostových regresí neplyne.
