# Hostové HTTP regrese

Z kořene projektu spustit:

```bash
python3 models/jednoduche-auticko/firmware/prvni-motor/tests/run_http_tests.py
```

Je potřeba Python 3 a g++. Test se překládá v dočasné složce a používá skutečný `.ino` s náhradami Arduino/Wi-Fi API. Neotevírá USB port, síť ani hardware. Nenahrává program a neověřuje motor ani skutečné časování WiFiS3.

Obsahuje původních 38 tříd HTTP případů s novými hranicemi 1024 znaků na řádek, 8192 bajtů a 3000 ms; navíc reprezentativní Chrome Android a Safari iOS hlavičky, fragmentaci a další chybné požadavky. Každý případ se zkouší samotným parserem i skutečnou funkcí `loop()`. Kontroluje se absence spuštění motoru pro GET a chybný POST, 1000ms simulovaný pulz pouze pro platný POST, odpověď po vypnutí a nulové síťové I/O během pulzu.

Mobilní hlavičky jsou realistické testovací vzory, nikoli zachycené požadavky uživatelova telefonu. Původní parser odmítal i 408bajtový Chrome GET (`Accept` 143 znaků) a 360bajtový Safari GET (`User-Agent` 147 znaků), protože překročily původní limit 128 znaků na řádek.

Pro reprodukci původní chyby lze použít zachovaný soubor mimo projekt:

```bash
python3 models/jednoduche-auticko/firmware/prvni-motor/tests/run_http_tests.py \
  --legacy --source /home/novakj/.cache/auticko-arduino-test/before-phone-fix.ino
```

Legacy režim očekává odmítnutí těchto mobilních požadavků a původní hranice 128/1024/1000. Cache nemusí zůstat dostupná; výchozí test vždy kontroluje aktuální projektový zdroj.
