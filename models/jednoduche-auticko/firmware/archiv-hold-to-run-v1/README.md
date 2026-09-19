# Neaktivní archiv hold-to-run-v1

Zachovaný přesný zdroj hold-to-run-v1 před opravou přerušované funkce při držení. Požadovaný návrat k jednosekundovému programu uživatel odvolal ještě před uploadem. Aktuálně upravovaný program a skutečný stav uploadu jsou v [prvni-motor](../prvni-motor/README.md). Níže je původní dokumentace a testy této neaktivní verze; její dobové formulace o aktuálním uploadu už neplatí.

# Autíčko — pohon při držení tlačítka

Firmware pro **Arduino UNO R4 WiFi**, core **1.6.0**, a stávající **ST L293D DIP16**. Zadání z 19. 9. 2026 mění webové ovládání ze sekundového pulzu na **běh pouze při držení tlačítka**. Zdroj zůstává v této původní složce; veškerý kontext propojuje [elektronika autíčka](../../../../elektronika/auticko/README.md).

**Stav: přeloženo a úspěšně nahráno do připojené UNO R4 WiFi dne 19. 9. 2026; uživatel následně hlásí nespolehlivý rozběh a bzučení; úspěšné držení a puštění ani jízda nejsou potvrzené.** Přesný výsledek překladu, uploadu a kontrolní součet se zapisují do [ověření programu](overeni-programu.json). Starší úspěšný sekundový test není testem nového držení.

## Použití

1. Po zapnutí je pohon vypnutý. Přístupový bod se připravuje přibližně 10 sekund.
2. Připojit telefon k **Auticko-test**, demonstrační heslo **auticko123**, a otevřít **[http://192.168.4.1/](http://192.168.4.1/)**. Síť nepotřebuje internet, adresa používá HTTP.
3. Podržet **Držet pro jízdu vpřed**. Puštění tlačítka odešle STOP. Funguje dotyk i levé tlačítko myši; na zaměřeném tlačítku také mezerník a Enter.
4. Ztráta zachycení prstu, zrušený dotyk, odchod ze stránky, skrytí stránky, ztráta focusu nebo offline událost ukončí držení. Po obnovení spojení se jízda sama neobnoví; vyžaduje nový stisk. Při nepotvrzeném STOP stránka další stisk nepovolí a vyžádá obnovení stránky.

Výstup je stále **D5 PWM 128/255**, **D7 HIGH**, **D8 LOW** při pohonu. STOP nastaví PWM na nulu a oba směrové vstupy LOW; kola mohou volně dobíhat. Slovo „vpřed“ označuje dosavadní elektrický směr. Fyzický směr jízdy kompletního autíčka ještě není ověřený.

| Arduino | Pin L293D | Úloha |
|---|---|---|
| D5 | 1 | EN1,2 — PWM |
| D7 | 2 | IN1 |
| D8 | 7 | IN2 |

Zapojení se nemění. Kompletní napájení, země a výstupy motoru jsou v [tabulce L293D](../../../../elektronika/auticko/zapojeni-l293d.md). Parametry neoznačeného motoru nejsou změřené; údaj 1–6 V je uživatelský pracovní předpoklad.

## Vypnutí při výpadku

Prohlížeč posílá další potvrzení držení **100 ms po úspěšné odpovědi** na předchozí, vždy nejvýše jedno nevyřízené potvrzení. Povolující interval je **500 ms**, kontrolovaný přerušením samostatného časovače každých **5 ms**. Obnovení intervalu je navázané na čas vydání předchozí jednorázové výzvy serveru, nikoli na pozdní přijetí paketu. Zpožděný paket proto neposune vypnutí o dalších 500 ms od svého přijetí.

Při běžném spojení STOP vypne výstup po přijetí. Když se STOP ztratí nebo hlavní program čeká uvnitř WiFiS3, přerušení vypne pohon při konci povoleného intervalu, nejpozději přibližně do půl sekundy od poslední ověřené výzvy. Po expiraci už starý heartbeat pohon neobnoví. To je ochrana proti běžnému síťovému čekání, **nikoli nezávislý hardwarový watchdog při zamrznutí procesoru nebo dlouho zakázaných přerušeních**. Skutečné fyzické časování a doběh nebyly měřené.

PWM se inicializuje před výběrem volného časovače; nepřebírá se časovač rezervovaný jinou funkcí. Inicializace každého kroku se kontroluje. Pokud PWM nebo hlídací časovač není připraven, rozběh se nepovolí. Přerušení nevolá síť, Serial ani alokaci paměti; mění pouze stav, GPIO a již připravené PWM. Implementace vychází z místně ověřeného [Arduino core 1.6.0 — FspTimer](https://github.com/arduino/ArduinoCore-renesas/blob/1.6.0/cores/arduino/FspTimer.h) a [PwmOut](https://github.com/arduino/ArduinoCore-renesas/blob/1.6.0/cores/arduino/pwm.cpp).

## Ochrana proti starým povelům

- `GET /` vždy vypne pohon a vytvoří nový token stránky. Obnovení stránky samo nespouští motor a zneplatní předchozí stránku.
- `POST /arm` vyžaduje token a vyšší číslo nového stisku. Pouze připraví krátce platnou jednorázovou výzvu; motor ještě stojí.
- `POST /hold` vyžaduje stejnou stránku, číslo stisku a aktuální jednorázovou výzvu. Teprve platné potvrzení zapne nebo udržuje pohon. Výzva se při použití spotřebuje; opakování ji neobnoví.
- `POST /stop` vypne pohon a zapamatuje číslo ukončeného stisku. Funguje i tehdy, když předběhne čekající ARM nebo HOLD. Starý start stejného stisku už nemůže uspět.
- Ztráta Wi-Fi, chyba požadavku a expirace vypnou pohon. Zotavení Wi-Fi zachovává předchozí opravu opakovaného dotazování po chybě 255; vyžaduje znovunačtení stránky a nový stisk. Původní `POST /test` je odmítaný.
- JavaScript ruší čekající fetch a používá číslo generace stisku: pozdě dokončená odpověď po puštění nebo ze starého stisku nemůže naplánovat další HOLD. Žádný automatický retry START/HOLD.

POST musí mít správné `Host`, právě jeden `Content-Length: 0`, `X-Motor-Control: 1`, `X-Motor-Token` a kladné kanonické `X-Motor-Press`; HOLD navíc `X-Motor-Challenge`. Kontroluje se Origin, CRLF a duplicity řídicích hlaviček. Povoleno je nejvýše **1024 znaků na řádek**, **8192 B požadavku** a **3000 ms** aplikační doby příjmu. `Transfer-Encoding`, `Expect`, jiná cesta nebo metoda se odmítají. Tokeny jsou ochrana proti nechtěným a starým povelům, nikoli autentizace vůči jinému uživateli připojenému ke stejné Wi-Fi.

## Ověření a diagnostika

Finální zdroj má SHA256 `46cee7f55931e12fe802de19b01724e76f8e1184860f316b5da6176acbc7e631`. Překlad Arduino CLI **1.5.1**, core **1.6.0**, FQBN `arduino:renesas_uno:unor4wifi`: **78 808 B flash / 9 068 B RAM**. Na USB desku se serialem `3CDC75F1A2D4` se zapsalo **78 816 B, 20 stran, 100 %, exit 0**, port `/dev/ttyACM0`. [Log překladu](evidence/2026-09-19-hold-to-run/compile.txt), [log uploadu](evidence/2026-09-19-hold-to-run/upload.txt), [USB výpis po uploadu](evidence/2026-09-19-hold-to-run/serial.txt).

Živý výpis čtyřikrát potvrdil správný build, `safety=1`, `drive=0`, čtení EN/IN1/IN2 LOW, připravený server a IP `192.168.4.1`. Agent poslal pouze znak `?` pro diagnostiku, žádný požadavek pro pohyb. Kontrolní součet je z lokálního zdroje a binárky použité k uploadu; firmware se z desky nečetl zpět.

Pro tento zdroj prošlo **82 parserových + 82 integračních HTTP případů**, **19 skupin protokolu/recovery/chyb**, **7 simulovaných blokací I/O** a **19 scénářů vloženého JavaScriptu**. Zdroj zkontroloval i nezávislý reviewer; drobná následná úprava pouze zpřesnila text „přibližně 0,5 sekundy“.

[Hostové testy](tests/README.md) spouštějí skutečný sketch s náhradami Arduino/Wi-Fi a simulovaným přerušením, plus skutečný vložený JavaScript v Node harnessu. Testují parser i chování při držení, uvolnění, pořadí STOP/ARM/HOLD, expiraci, blokujících síťových voláních, chybách inicializace a zotavení. Nejde o fyzické měření.

```bash
python3 models/jednoduche-auticko/firmware/prvni-motor/tests/run_http_tests.py
```

USB diagnostika běží při **115200 baud**, každých 5 sekund, případně po znaku `?`. Hlásí `build=hold-to-run-v1`, stav časovače `safety`, `drive` (0 vypnuto, 1 připraveno, 2 běží), čtené logické úrovně EN/IN1/IN2, počet timeoutů a stav Wi-Fi/serveru. Logické čtení pinů neověřuje elektrické napětí, zapojení ani pohyb motoru. Žádné čekání na otevřený sériový monitor.

Pro ruční zkoušku této verze zbývá potvrdit z telefonu: běh při držení, vypnutí po puštění, zrušený dotyk/skrytí stránky a výpadek spojení. U krátkého výpadku se výstup nemá sám znovu zapnout. Agent tyto motorové příkazy živě neposílá.

Historie zůstává v [archivu sekundového programu](historie-sekundoveho-testu.md), [první fyzické zkoušce](../../../../elektronika/auticko/prvni-stolni-test.md) a [diagnostice Wi-Fi](../../../../elektronika/auticko/diagnostika-webu.md). Nákup nových baterií a páječky je v [inventáři](../../../../elektronika/vybaveni.md); nepotvrzuje výměnu článků ani zapájení kontaktů.

## Navazující problém při rozjezdu

Uživatel dodatečně upřesnil časovou osu: těžký rozjezd zaznamenal už na starém pulzním programu; nový držící režim zpočátku vnímal jako perfektně funkční. Následně po montáži hlásil bzučení a jen občasný rozběh. Nejnovější zkouška s koly ve vzduchu podle něj skončila bez rozběhu i bez zátěže. Mazání hřídelek silikonovým olejem podle něj výrazně nepomohlo. To je **hlášení neúspěšného nebo nespolehlivého fyzického pokusu**, nikoli úspěšná zkouška řízení nebo určení příčiny.

Následných 30 sekund pouze čtecího USB sledování bez resetu a bez motorových povelů zachytilo `watchdog=4 → 5` a `HTTP=35 → 36`, po celou dobu dokončené požadavky, `drive=0`, `safety=1`, Wi-Fi stav 8 a plynulý uptime. [Původní výpis](evidence/2026-09-19-hold-to-run/serial-symptom.txt). Čítač zahrnuje expiraci **ARMED i RUNNING**, nelze z něj sám o sobě odvodit počet fyzických zastavení. Výpis neobsahuje konkrétní stáří heartbeatů ani důvod STOP každého požadavku.

Půlsekundová lhůta může při vyšší latenci přerušit přípravu nebo běh; příliš pozdní HOLD už se správně neobnoví. Není tím prokázáno, že je to jediná příčina symptomu. Nezměřené napájení, úbytek L293D, dočasné kontakty a mechanický odpor zůstávají otevřené. Zkoušku s koly ve vzduchu už uživatel provedl a hlásí neúspěch. Zbývá sladit konkrétní stisk s LED, textem stránky a USB stavem; na zkoušku bez zátěže se znovu neptat. Po tomto hlášení se program neměnil ani znovu nenahrával.

**Konkrétní odvození z logu a zdroje:** mezi uptime 221 025 a 226 033 ms přibyl z výchozího IDLE právě jeden dokončený požadavek a jedna expirace. V tomto programu může jediný požadavek z IDLE pouze úspěšně připravit ARM; běh potřebuje další HOLD. Tento konkrétní pokus tedy vypršel už při čekání v ARMED. Není to přímý záznam URL a neukazuje, zda telefon další HOLD odeslal, nebo zůstal čekat na síti. Nelze tento nález bez dalšího přenést na všechny pokusy s bzučením.

**Druhé sledování 13:25:10–13:25:54:** existující nemotorový znak `?` vyžádal výpis přibližně každých 1,1 s, bez resetu. [Záznam](evidence/2026-09-19-hold-to-run/serial-unloaded.txt) po celou dobu ukazuje `drive=0`, EN/IN1/IN2 LOW, `safety=1`, server připravený a Wi-Fi 8. Počet HTTP zůstal 6/6 a watchdog 2; **v tomto okně nedorazil žádný nový požadavek**. Není proto potvrzeno, že některý aktuální stisk z telefonu doputoval k řízení motoru. Nižší uptime proti prvnímu sledování ukazuje restart mezi okny, jeho příčina či ruční provedení neznámé; agent reset neprovedl.

Přesný další rozlišovací údaj je text a stav tlačítka na telefonu při neúspěšném pokusu. Po nepotvrzeném STOP může zůstat disabled a vyžaduje obnovu stránky. Z kódu také plyne přísná rezerva: dva navazující intervaly HOLD se musí vejít do 500 ms; při čekání 100 ms po odpovědi to v ustáleném modelu ponechává přibližně 150 ms na síťovou/obslužnou odezvu jednoho cyklu. To je odvozená vlastnost protokolu, nikoli měření telefonu. Zdroj WiFiS3 používá blokující modemové transakce pro stav, dostupnost, odeslání a uzavření; aktuální USB výpis jejich délku neudává. Bez tohoto rozlišení se PWM ani bezpečnostní limit nezvyšují.

Ohraničené navazující sledování do 13:29:59 rovněž nepřijalo nový HTTP požadavek; monitor byl ukončen. Hostový experiment navíc reprodukoval omezenou rezervu intervalů HOLD 250–300 ms, ale neměří skutečnou Wi-Fi. Úplná časová osa, výsledky a navržený další diagnostický krok jsou v [záznamu potíží](../../../../elektronika/auticko/potize-po-montazi.md). Firmware zůstává na stejném hashi, bez dalšího uploadu.
