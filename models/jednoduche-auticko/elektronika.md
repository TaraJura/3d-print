# Elektronika a ovládání autíčka

Stav k 19. 9. 2026: budič ST L293D potvrzený, [zapojení navržené](zapojeni-l293d.md), [první firmware](firmware/prvni-motor/README.md) vytvořený a přeložený pro UNO R4 WiFi. Po původním prázdném sketche uživatel doložil **úspěšné nahrání motorového programu**: 67 820 B při překladu, 67 828 B zapsáno, 100 % a dokončeno bez chyby. Uživatel po opravě potvrdil stránku v telefonu a reakci LED Arduina na tlačítko. Externí součástky zatím připojené nejsou; fyzické zapojení, ovládání skutečného motoru a jízda zůstávají neověřené.

## Potvrzené údaje a požadavek

- Uživatel vlastní **Arduino UNO R4 WiFi**.
- Uživatel oznámil otevření Arduino IDE. Původně napájel desku přes USB adaptér. Po připojení k počítači změna portu nepomohla, ale **výměna kabelu přinesla skutečnou detekci UNO R4 WiFi** v USB i Arduino CLI na **`/dev/ttyACM0`**. První pokus uživatele o upload potom selhal na oprávněních; ta byla opravena a čtení i zápis portu pro účet novakj ověřeny. Uživatel následně potvrdil **úspěšný upload 51 824 B**. Kontrola posledního sketche `sketch_sep19a.ino` našla pouze prázdné `setup()` a `loop()` s výchozími komentáři. Tento úspěch tedy dokládá uživatelský upload prázdného sketche, nikoli nahrání našeho motorového programu o přeložené velikosti 67 804 B.
- Původně chtěl ovládání z webového prohlížeče šipkami vpřed a vzad. **Nejnovější změna zadání: pro první verzi stačí jediné tlačítko a jízda pouze dopředu.** Zpětný chod už není podmínkou prvního testu; původní požadavek prohlížeče nebyl odvolán.
- Mechanika má jeden motor a společnou zadní nápravu, bez řízení zatáčení. Rozměry motoru jsou v [README modelu](README.md). Uživatel potvrdil, že **na motoru není žádný nápis** a **není z uvedené sady**. Výslovně požádal pro návrh předpokládat klasický dvouvodičový kartáčový DC motor **1–6 V**. Tento rozsah je pracovní předpoklad uživatele, nikoli identifikovaný typ či ověřené jmenovité napětí; proud zůstává neznámý.

## Princip

Prohlížeč → Wi-Fi → Arduino → výkonový spínač / motorový budič → motor. Pro nový požadavek jednoho směru není H-můstek nezbytný; pro případnou pozdější reverzaci by potřeba byl.

UNO R4 WiFi už obsahuje Wi-Fi modul. Arduino má pro tuto desku [oficiální příklad jednoduchého webového serveru s vlastní Wi-Fi sítí](https://github.com/arduino/ArduinoCore-renesas/blob/main/libraries/WiFiS3/examples/AP_SimpleWebServer/AP_SimpleWebServer.ino). Náš připravený motorový program používá vlastní síť `Auticko-test` na `192.168.4.1`; její vznik a připojení telefonu uživatel potvrdil; první pokus o stránku však vrátil HTTP chybu. Původní prázdný sketch tuto síť nevytvářel; nyní je doložen následný upload motorového programu. Další krok je ověřit síť a stránku s odpojeným motorovým napájením.

H-můstek je výkonový elektronický obvod, který u běžného dvouvodičového stejnosměrného motoru umožní obrátit polaritu a tím směr otáčení. Arduino poskytuje řídicí signály; proud pro motor dodává napájení přes budič. [Příklad řízení směru a rychlosti v dokumentaci Arduino](https://docs.arduino.cc/hardware/motor-shield-rev3) není doporučením konkrétního shieldu pro tento zatím neidentifikovaný motor.

## Co zbývá určit

- Vhodnost potvrzeného ST L293D pro skutečný motor a dostupné napájení.
- Typ nebo označení motoru, vhodné napětí a potřebný proud včetně rozběhu. Rozměry těla ani hřídelky elektrické parametry neurčují.
- Dostupný zdroj nebo baterie, vodiče, konektory a případný multimetr.

Konkrétní budič a napájení vybrat až podle těchto údajů. Zapojení pinů nevymýšlet bez znalosti modulu. Hlavní I/O UNO R4 WiFi pracují s 5V logikou; přímé vývody jeho ESP32-S3 mají jinou napěťovou úroveň, proto je nezaměňovat. Zdroj: [oficiální datasheet desky](https://github.com/arduino/docs-content/blob/main/content/hardware/02.uno/boards/uno-r4-wifi/datasheet/datasheet.md).

## Dostupná sada a fotografie součástek

Uživatel dodal přímo [odkaz na sadu LaskaKit MAXI RFID](https://www.laskakit.cz/laskkit-arduino-maxi-starter-kit--rfid/); konkrétní varianta dodané Arduino desky v sadě není určená. Její zveřejněný seznam uvádí řadič ULN2003, krokový motor 28BYJ-48, servo a jednokanálové relé; L293D ani samostatný dvouvodičový DC motorek v seznamu nejsou. Skutečné vlastnictví L293D však potvrdil uživatel a fotografie níže, proto se existence čipu nepopírá podle obsahu katalogu. Odkaz neurčuje elektrické parametry jeho samostatného motoru.

Na první uživatelské fotografii je vlevo od LCD zelená deska s černým čipem, bílým konektorem a čtyřmi LED. **Následný detail `20260919_012402.jpg` potvrdil čitelné označení TI ULN2003AN.** Jde tedy o skutečně dostupný modul s tranzistorovými spínači, nikoli potvrzený H-můstek. V horní průhledné krabici jsou další volné čipy, jejichž označení nelze přečíst. Z fotografií proto nelze potvrdit konkrétní H-můstek ani dokázat, že jej uživatel nemá.

[ULN2003A podle výrobce TI](https://www.ti.com/product/ULN2003A) obsahuje nízkostranné tranzistorové spínače; sám není H-můstkem pro reverzaci dvouvodičového DC motoru. Pro vizuální porovnání jsme uživateli otevřeli [samostatný L293D na Drátku](https://dratek.cz/arduino-platforma/1128-io-l293d-pro-rizeni-motoru.html). Není to potvrzení jeho vlastnictví ani konečný výběr pro neidentifikovaný motor. [Parametry L293D u výrobce](https://www.ti.com/product/L293D).

**Oprava předchozího kategorického tvrzení v hlasovém rozhovoru:** ULN2003 lze za vhodných elektrických podmínek použít i jako spínač dvouvodičového DC motoru pro jeden směr. Není omezený výhradně na krokové motory. Vhodnost konkrétního modulu pro uživatelův motor stále není potvrzena: chybí napětí, proud včetně rozběhu/zablokování a ověření zapojení napájení a ochranných diod modulu. Bez těchto údajů nedávat návod k zapnutí motoru ani automaticky spojovat výstupy.

Uživatel následně poslal detail samostatného čipu `20260919_012729.jpg` a výslovně **potvrdil celé označení L293D**. Máme tedy ST L293D v pouzdru DIP16. [Oficiální stránka ST L293D](https://www.st.com/en/motor-drivers/l293d.html) potvrzuje řízení DC motorů dvojicemi kanálů jako H-můstky; jmenovitě 600 mA na kanál, špičkový údaj 1,2 A není trvalý dovolený proud. Identifikace čipu nepotvrzuje jeho stav ani odběr motoru. [Návrh konkrétního zapojení](zapojeni-l293d.md) má vývody ověřené dle ST a pro uživatelem předpokládaný motor 1–6 V volí samostatnou regulovanou 5V motorovou větev. Skutečný dostupný zdroj a vhodnost z hlediska proudu zbývá ověřit.

## První program a další ovládání

[První program](firmware/prvni-motor/prvni-motor.ino) vytvoří vlastní Wi-Fi síť a nabídne jediné tlačítko pro **sekundový test vpřed**. Po startu je motor vypnutý. Platný požadavek vyvolá 1s pulz s PWM 128/255, potom se výkonový výstup vypne; síťová odpověď se posílá až po vypnutí. Jde o test na stole, nikoli nepřetržité řízení autíčka. Uvolnění tlačítka tento krátký pulz okamžitě nezkrátí. Při chybných/neúplných požadavcích ani obnovení stránky se motor nespouští.

Zdroj prošel překladem skutečným Arduino CLI pro UNO R4 WiFi a knihovnu WiFiS3 v core Renesas 1.6.0; to nepotvrzuje funkci na desce. Podpora Arduino UNO R4 Boards 1.6.0 byla doplněna také do místního Arduino IDE. USB detekce i oprávnění portu jsou nyní ověřené a uživatel potvrdil úspěšný upload prázdného sketche. **Motorový program `prvni-motor.ino` byl otevřený v samostatném okně stejného Arduino IDE 2.3.10 a následně jej uživatel úspěšně nahrál.** Původní okno `sketch_sep19a` zůstalo zachované; kontrolní součty obou `.ino` se při otevření nezměnily. Otevření okna není upload ani zkouška motoru. Nový log uživatele potvrzuje překlad 67 820 B, RAM 7 580 B a úspěšný zápis 67 828 B. Lokální poslední build ukazuje správný zdroj i UNO R4 WiFi a velikost jeho `.bin` odpovídá. Obsah desky nebyl čten zpět. Další krok je síť a stránka; fyzické zapnutí motoru vyžaduje ověření zapojení a napájení.

### Oprava Linux USB oprávnění

Uživatelův log po výměně kabelu skončil chybou `1200-bps touch ... Permission denied`. Účet novakj původně neměl oprávnění pro čtení ani zápis `/dev/ttyACM0`. Na jeho žádost a s ověřeným sudo přístupem bylo vytvořeno `/etc/udev/rules.d/71-arduino-uno-r4-wifi-uaccess.rules`: pravidlo pro USB výrobce `2341`, modely `1002|006d` přidává `TAG+="uaccess"`. Tyto identity vycházejí z instalovaného `boards.txt` pro UNO R4 WiFi.

Pravidlo prošlo `udevadm verify`, bylo načtené a aplikované na aktuální tty zařízení. `getfacl` následně potvrdilo `user:novakj:rw-` a kontrola jako běžný uživatel potvrdila čtení i zápis. Skupiny uživatele ani oprávnění pro všechny uživatele nebyly rozšířené. Pravidlo umožňuje přístup aktivnímu místnímu uživateli a použije se také při dalším rozpoznání odpovídající desky. Samotnou opravou práv se žádný firmware nenahrával.

Pro pozdější skutečnou jízdu zůstává návrh ovládání při držení tlačítka se zastavením při uvolnění/ztrátě pravidelných povelů. Uživatel zatím přesnou interakci nezvolil a tento průběžný režim v prvním sekundovém testu implementovaný není.

Uživatel následně potvrdil, že v nabídce Wi-Fi vidí síť **Auticko-test**. Následně potvrdil také připojení telefonu a HTTP odpověď s chybou neplatného/neúplného požadavku. Aktuální oprava zvětšuje omezení HTTP hlaviček pro mobilní prohlížeče. Později uživatel potvrdil úspěšné načtení stránky po opravě a reakci LED. Motor dosud připojený není.

**Oprava telefonu nahrána agentem:** limit řádku zvýšen ze 128 na 1024 znaků, součet na 8192 B, čas příjmu na 3 s; buffer je statický. Původní chybu reprodukovaly testovací mobilní hlavičky. Aktuální zdroj prošel 53 testy parseru a 53 testy celého loop, kompilací a uploadem 67 812 B / 17 stran / 100 % na ověřenou UNO R4 WiFi. Motorový pulz nebyl na hardwaru spuštěn. Uživatel následně potvrdil stránku a reakci LED na tlačítko bez připojených externích součástek. Další krok: fyzické zapojení L293D a volba dostupného motorového zdroje.
