# Hostové HTTP regrese

Z kořene projektu spustit:

```bash
python3 models/jednoduche-auticko/firmware/prvni-motor/tests/run_http_tests.py
```

Je potřeba Python 3 a g++. Test se překládá v dočasné složce a používá skutečný `.ino` s náhradami Arduino/Wi-Fi API. Neotevírá USB port, síť ani hardware. Nenahrává program a neověřuje motor ani skutečné časování WiFiS3.

Obsahuje původních 38 tříd HTTP případů s novými hranicemi 1024 znaků na řádek, 8192 bajtů a 3000 ms; navíc reprezentativní Chrome Android a Safari iOS hlavičky, fragmentaci a další chybné požadavky. Celkem 53 případů se zkouší samotným parserem i skutečnou funkcí `loop()`. Platné POST mají aktuální jednorázový token. Kontroluje se absence spuštění motoru pro GET a chybný POST, 1000ms simulovaný pulz pouze pro platný POST, odpověď po vypnutí a nulové síťové I/O během pulzu.

Navazující případy kontrolují chybějící, prázdný, nesprávný či zdvojený `X-Motor-Token`, spotřebu tokenu ještě před zapnutím motoru, nový token v odpovědi po STOP, odmítnutí opakovaného požadavku i možnost dalšího výslovného testu s novým tokenem. Nové načtení stránky zneplatní předchozí token. Selhání každého ze tří volání generátoru a vyčerpání čítače nevydá nový token. Kontroluje se skutečný `Content-Length` odpovědí včetně HTML s vloženým tokenem.

Recovery regrese simulují osm scénářů: jednotlivý stav 255, 0 nebo 77; 255 po přijetí platného POST; úspěšný, ale o 4000 ms zpožděný druhý dotaz na stav; chybějící modul při startu; neúspěšný start serveru; neúspěšný start AP. Ověřují nejvýše jeden pokus za sekundu během čekání, návrat webu bez zbytečného restartu AP/serveru a STOP při chybě i opožděné odpovědi. Původní POST zůstává ve frontě mocku, aby se prokázalo jeho odmítnutí po návratu Wi-Fi; nové načtení stránky a nový POST pak dovolí právě jeden pulz. Mock používá skutečné hodnoty stavů WiFiS3: AP naslouchá 7, klient připojen 8, modul nenalezen 255.

Diagnostika ověřuje nulové Serial I/O během pulzu, uložené startovní údaje v pozdějším snapshotu, vyžádaný výpis znakem `?`, omezení frekvence a délky vstupu a hlášení obnovy spojení. Snapshot nedělá další dotazy na Wi-Fi: `statusLast` a `ageMs` označují poslední dotázaný stav a jeho stáří. Hostové testy neprokazují odstranění fyzické příčiny výpadků modulu; ověřují reakci skutečného programu na simulované návratové hodnoty a zpoždění.

Pro UNO R4 WiFi v instalovaném core 1.6.0 je `Serial` UART přes ESP bridge, nikoli přímo USB CDC. `operator bool()` zde vrací vždy true a `availableForWrite()` není implementováno; test proto nepředstírá detekci připojeného monitoru ani dostupnou velikost TX bufferu. Krátké řádky při 115200 se přenášejí synchronně, bez čekání na monitor a bez `flush()`. Snapshot přijde každých 5 s; `?` jej vyžádá nejvýše jednou za sekundu. Hostová náhrada neověřuje skutečné trvání UART přenosu nebo stav ESP bridge.

Mobilní hlavičky jsou realistické testovací vzory, nikoli zachycené požadavky uživatelova telefonu. Původní parser odmítal i 408bajtový Chrome GET (`Accept` 143 znaků) a 360bajtový Safari GET (`User-Agent` 147 znaků), protože překročily původní limit 128 znaků na řádek.

Pro reprodukci původní chyby lze použít zachovaný soubor mimo projekt:

```bash
python3 models/jednoduche-auticko/firmware/prvni-motor/tests/run_http_tests.py \
  --legacy --source /home/novakj/.cache/auticko-arduino-test/before-phone-fix.ino
```

Legacy režim očekává odmítnutí těchto mobilních požadavků a původní hranice 128/1024/1000. Cache nemusí zůstat dostupná; výchozí test vždy kontroluje aktuální projektový zdroj.
