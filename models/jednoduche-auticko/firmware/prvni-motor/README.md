# První sekundový test motoru

Jednoduchý zkušební firmware pro **Arduino UNO R4 WiFi** a **ST L293D DIP16**. Uživatel úspěšně nahrál první verzi motorového programu a připojil telefon k jeho Wi-Fi. Web odpověděl chybou neplatného/neúplného požadavku. Aktuální zdroj opravuje příliš krátké limity pro hlavičky mobilních prohlížečů; agent jej po kontrole úspěšně nahrál do desky. Uživatel potvrdil otevření opravené stránky na telefonu a rozsvícení LED Arduina po stisku tlačítka; externí součástky zatím připojené nemá. Motor zatím nebyl fyzicky vyzkoušen. Uživatel pro návrh výslovně dovolil předpokládat motor **1–6 V**; nejde o ověřený údaj skutečného motoru. Návrh počítá se samostatnou regulovanou 5V větví, ale skutečný zdroj a odběr motoru zatím nejsou potvrzené, takže fyzické zapnutí zůstává otevřeným bodem. Konkrétní zapojení je v [návodu pro L293D](../../zapojeni-l293d.md), širší kontext v [elektronice modelu](../../elektronika.md).

## Co udělá

Po startu drží motor vypnutý a vytvoří vlastní Wi-Fi síť **Auticko-test**, heslo **auticko123**. Jde o veřejné demonstrační heslo, nikoli údaj k domácí Wi-Fi. Příprava přístupového bodu trvá přibližně 10 sekund. Po připojení k této síti se stránka otevírá na [192.168.4.1](http://192.168.4.1).

Stránka má jediné tlačítko **Test motoru na 1 sekundu**. Platný POST vyvolá jeden pulz: IN1 HIGH, IN2 LOW a osmibitové PWM EN **128/255**. Po `delay(1000)` se EN nastaví na nulu a oba směrové vstupy na LOW. Motor může volně dobíhat; nejde o aktivní brzdu. Skutečný směr závisí na zapojení vývodů motoru.

**Puštění tlačítka, zavření stránky ani odpojení prohlížeče pulz okamžitě nezkrátí.** Jde o konečný sekundový test, nikoli finální řízení autíčka. Během zapnutého pulzu se nevolá Wi-Fi ani Serial; odpověď prohlížeči se posílá až po vypnutí výstupu. Časování je softwarové, nikoli nezávislá hardwarová pojistka.

Během čekání je tlačítko vypnuté. Potvrzená odpověď dovolí další vědomé kliknutí. Při chybě nebo šestisekundovém síťovém timeoutu stránka ohlásí nejistý výsledek, tlačítko ponechá vypnuté a nic automaticky neopakuje. Po chybě nejprve ověřit skutečný stav, teprve potom stránku znovu otevřít. Obnovení stránky samo motor nespouští.

## Řídicí piny

| Arduino | L293D DIP16 | Význam |
|---|---|---|
| D5, PWM | 1 — EN1,2 | Povolení výstupů první dvojice |
| D7 | 2 — IN1 | První směrový vstup |
| D8 | 7 — IN2 | Druhý směrový vstup |

Program navíc používá pouze `LED_BUILTIN` jako indikaci pulzu. Tabulka uvádí řídicí propojení, nikoli celé elektrické zapojení. Za běhu chybný stav Wi-Fi vypne výstupy a další testy zablokuje až do nového startu; automatický restart ani opakování pulzu neexistují.

## Jednoduchý HTTP protokol

- `GET / HTTP/1.1` vrátí stránku a nikdy nespustí motor. Favicon, jiné cesty, jiné metody a neúplné požadavky motor nespouštějí.
- Motor spouští pouze přesné `POST /test HTTP/1.1` po kompletním zakončení hlaviček `CRLF CRLF`, s `Host: 192.168.4.1` (případně `:80`), právě jedním `Content-Length: 0` a `X-Motor-Test: 1`.
- JavaScript posílá prázdné tělo; `Content-Length: 0` doplňuje prohlížeč. Skript nenastavuje tuto pro JavaScript zakázanou hlavičku ručně.
- Vlastní hlavička a nepovolené CORS brání běžnému nechtěnému vyvolání cizí webovou stránkou. Pokud je přítomný `Origin`, musí odpovídat místní stránce. Nejde o samostatné přihlašování; zařízení připojené k této testovací síti může správný požadavek vytvořit.
- Příjem má aplikační limit **3 sekundy**, nejvýše **8192 bajtů** celého požadavku a **1024 znaků** na řádek. Dřívější limit 128 znaků odmítal běžné dlouhé mobilní hlavičky. Statické pole řádku používá 1025 B RAM mimo zásobník; celý požadavek se v paměti nehromadí. Server zpracovává vždy pouze jedno spojení. Kontrolují se CRLF, názvy hlaviček, nulové tělo, duplicity kritických hlaviček; `Transfer-Encoding` a `Expect` se odmítají. Podkladové Wi-Fi volání není tvrdý real-time časovač; během příjmu je motor vypnutý.
- Po jedné odpovědi se spojení uzavře. Pro další pulz musí přijít nový úplný platný POST. Požadavek neobsahuje volitelnou délku, směr ani výkon.

## Zdroj a ověření

[prvni-motor.ino](prvni-motor.ino) používá přibalenou knihovnu `WiFiS3`. Vytvoření AP vychází z [oficiálního příkladu Arduino AP_SimpleWebServer](https://github.com/arduino/ArduinoCore-renesas/blob/main/libraries/WiFiS3/examples/AP_SimpleWebServer/AP_SimpleWebServer.ino); IP je výslovně nastavená přes `WiFi.config(IPAddress(192,168,4,1))`. Odpovídající API popisuje [WiFi.h v oficiálním Arduino core](https://github.com/arduino/ArduinoCore-renesas/blob/main/libraries/WiFiS3/src/WiFi.h).

Hostová kontrola skutečného zdrojového kódu s náhradami Arduino/Wi-Fi API prošla pro **53 případů parseru a stejných 53 případů celého `loop()`**: platné požadavky, neúplné/chybné hlavičky, jiné metody a cesty, duplicity, cizí Host/Origin, nenulové tělo, CRLF, délku řádku i celkový limit a pomalý příjem. Parsování nezapisovalo motorové piny. Simulovaný pulz trval přesně 1000 ms, během něj nebylo síťové I/O a skončil vypnutým EN i směrovými vstupy. Start bez Wi-Fi modulu ponechal výstupy vypnuté. Testy běžely pouze na počítači a neověřují chování fyzického motoru.

Kompilace byla samostatně ověřena **Arduino CLI 1.5.1**, deska `arduino:renesas_uno:unor4wifi`, core **1.6.0**: úspěch, flash **67 804 / 262 144 B**, RAM **8 604 / 32 768 B** po přesunu bufferu do statické paměti. Vložený JavaScript prošel také `node --check`.

Arduino IDE **2.3.10** má nainstalovanou podporu Renesas **1.6.0**. Po výměně kabelu se UNO R4 WiFi skutečně detekovalo na **`/dev/ttyACM0`** a následně byla opravena oprávnění portu. Jeho existence i přístup pro čtení/zápis byly znovu ověřené. Původní stav „USB nedetekováno“ už neplatí.

Uživatel potvrdil **úspěšný upload 51 824 B**. Lokální kontrola posledního `sketch_sep19a.ino` potvrdila jen prázdné `setup()` a `loop()` s výchozími komentáři. Jde o úspěšné nahrání prázdného sketche; **tehdy ještě nešlo o motorový program**. Nebyl proveden read-back firmware z desky; zdrojem informace je uživatelské hlášení a kontrola lokálního sketche.

Motorový sketch byl otevřený příkazem níže v novém okně stávajícího IDE, bez uploadu:

```bash
/home/novakj/Downloads/arduino-ide_2.3.10_Linux_64bit.AppImage \
  /home/novakj/3d-print/models/jednoduche-auticko/firmware/prvni-motor/prvni-motor.ino
```

Otevření bylo ověřené názvem nového okna **`prvni-motor | Arduino IDE 2.3.10`**; současně zůstalo otevřené původní **`sketch_sep19a | Arduino IDE 2.3.10`** ve stejném procesu IDE. Oba `.ino` soubory mají shodné SHA256 před a po otevření. Příkaz pouze otevírá zdroj, nenahrává jej. Kontrola kódu, otevřené okno ani úspěšná kompilace nepotvrzují elektrickou vhodnost zapojení či rozběh motoru.

**Následný upload motorového programu:** uživatel dodal dokončený log překladu **67 820 B flash / 7 580 B RAM** a zápisu **67 828 B, 17 stran, 100 %**, bez chyby. Nejnovější lokální `build.options.json` ukazuje zdejší `prvni-motor` a správné FQBN UNO R4 WiFi; odpovídající `.bin` má 67 828 B a zdroj má nezměněný kontrolní součet. Tím je doložen úspěšný uživatelský upload motorového programu, nikoli zatím funkce Wi-Fi nebo motoru. Starší samostatný překlad CLI výše měl 67 804 B; údaje obou běhů nejsou zaměňované. Firmware z desky nebyl čten zpět.

### Oprava mobilního prohlížeče

Uživatel po úspěšném uploadu viděl Wi-Fi `Auticko-test`, připojil telefon a při otevření místní HTTP adresy obdržel text „Neplatny nebo neuplny pozadavek.“. To dokládá spojení a HTTP odpověď, nikoli funkční ovládací stránku. Původní parser omezoval každý řádek na 128 znaků a celý požadavek na 1024 B. Aktuální změna zvyšuje tyto limity na 1024 znaků / 8192 B a aplikační čas příjmu na 3 s; striktní validace spouštěcího POST, Host, Origin a nulového těla i sekundový motorový pulz zůstávají zachované. Konkrétní síťový požadavek uživatelova telefonu nebyl zachycen.

**Ověření opravy a nahrání:** reprezentativní mobilní GET/POST prošly, GET a neplatný POST neaktivují motor; zkoušky obou limitů a třísekundového deadline prošly. [Regresní testy](tests/README.md) běží proti skutečnému zdroji. Buffer řádku je statický, protože konfigurace UNO R4 rezervuje pro hlavní zásobník pouze 0x400 B. Finální zdroj byl přeložen (67 804 B flash, 8 604 B statická RAM) a agent jej úspěšně nahrál na potvrzenou UNO R4 WiFi: 67 812 B, 17 stran, 100 %, návratový kód 0. Motorový test agent nevyvolal. Uživatel následně potvrdil úspěšné načtení opravené stránky a reakci LED na tlačítko. Při této zkoušce nejsou k Arduinu připojené žádné externí součástky; nejde o ověření skutečného motoru ani měření délky pulzu.
