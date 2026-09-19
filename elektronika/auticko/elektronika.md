# Elektronika a ovládání autíčka

Stav k 19. 9. 2026: **první stolní rozběh skutečného motoru přes telefon, Arduino UNO R4 WiFi a ST L293D uživatel potvrdil.** Po stisku tlačítka motor běžel přibližně sekundu. Po vyjmutí jedné baterie už neběžel; přerušil se celý sériový bateriový obvod. [Souhrnný záznam dnešního sestavování a výsledků](prvni-stolni-test.md) je výchozí bod pro pokračování. [Zapojení](zapojeni-l293d.md) a [firmware](../../models/jednoduche-auticko/firmware/prvni-motor/README.md) jsou uložené zde. Jízda celého autíčka a provoz pod zátěží zůstávají neověřené.

Arduino bylo při zkoušce na USB powerbance; motorová větev používala držák čtyř AA se **směsí Ni-MH 1,2 V a běžných článků**, bez změřeného celkového napětí. Kondenzátory nebyly osazené, vodiče motoru jsou dočasně zahnuté kolem kontaktů bez pájení. Tyto podmínky popisují provedený pokus, nejsou hotovým řešením pro provoz autíčka. Jedna AA byla vyjmutá na konci první zkoušky; později uživatel napájení přepojoval. Aktuální obsazení držáku ani stav USB z této historie neplynou. Pozdější nákup nových 1,5V baterií, páječky a dalších pomůcek je v [inventáři](../vybaveni.md); jejich použití zatím potvrzené není.

**Následná oprava webu:** USB diagnostika prokázala trvalé zablokování obsluhy po výsledku Wi-Fi 255. Agent nahrál recovery verzi `772cd12f…`, která obnovovala obsluhu po návratu platného stavu a odmítala staré či opožděné požadavky; tehdejší sekundový pulz zůstal stejný. Uživatelské potvrzení funkční sestavy před tímto uploadem patří diagnostické verzi `8a3eeb5f…`; fyzická zkouška recovery nebyla potvrzená. Důvod samotného chybového výsledku modemu zůstává neznámý. [Historie diagnostiky](diagnostika-webu.md).

**Aktuálně je nahraná oprava `hold-to-run-v2` (`1760730b…`).** Uživatel krátký požadavek návratu k sekundové verzi odvolal před jejím uploadem. Dokončená oprava prošla testy a překladem; upload má 80 512 B / 20 stran a USB po startu potvrdilo v2 s vypnutými výstupy. Po návratu uživatel potvrdil funkční držení, puštění a nový stisk; jde o jeho hlášení, nikoli měření elektrických či mechanických parametrů. [Aktuální stav](README.md) a [firmwarové README](../../models/jednoduche-auticko/firmware/prvni-motor/README.md) mají přednost před historickými popisy níže.

**Historicky nahraná verze při držení:** `hold-to-run-v1` (`46cee7f5…`) změnila ovládání na chod při držení tlačítka, STOP při uvolnění a 500ms platnost povolení hlídanou časovačem. Překlad, upload a hostové testy uspěly; USB výpis zachytil připravený server a vypnuté výstupy. Nový režim uživatel zpočátku hodnotil jako perfektně funkční, potom ale hlásil [bzučení a neúspěšný rozjezd i s koly ve vzduchu](potize-po-montazi.md). Těžký rozjezd existoval už na starém programu; příčina ani regrese nového režimu nejsou prokázané. [Aktuální přehled](README.md) a [návod k firmwaru](../../models/jednoduche-auticko/firmware/prvni-motor/README.md) popisují použití a omezení. Následující sekundové testy zůstávají historií starších verzí.

## Potvrzené údaje a požadavek

- Uživatel vlastní **Arduino UNO R4 WiFi**.
- Uživatel oznámil otevření Arduino IDE. Původně napájel desku přes USB adaptér. Po připojení k počítači změna portu nepomohla, ale **výměna kabelu přinesla skutečnou detekci UNO R4 WiFi** v USB i Arduino CLI na **`/dev/ttyACM0`**. První pokus uživatele o upload potom selhal na oprávněních; ta byla opravena a čtení i zápis portu pro účet novakj ověřeny. Uživatel následně potvrdil **úspěšný upload 51 824 B**. Kontrola posledního sketche `sketch_sep19a.ino` našla pouze prázdné `setup()` a `loop()` s výchozími komentáři. Tento úspěch tedy dokládá uživatelský upload prázdného sketche, nikoli nahrání našeho motorového programu o přeložené velikosti 67 804 B.
- Původně chtěl ovládání z webového prohlížeče šipkami vpřed a vzad. **Pro první stolní verzi zadal jediné tlačítko a jízdu pouze dopředu.** Nyní na to navazuje požadavek chodu pouze při držení tlačítka. Zpětný chod už není podmínkou prvního testu; původní požadavek prohlížeče nebyl odvolán.
- Mechanika má jeden motor a společnou zadní nápravu, bez řízení zatáčení. Rozměry motoru jsou v [README modelu](../../models/jednoduche-auticko/README.md). Uživatel potvrdil, že **na motoru není žádný nápis** a **není z uvedené sady**. Výslovně požádal pro návrh předpokládat klasický dvouvodičový kartáčový DC motor **1–6 V**. Tento rozsah je pracovní předpoklad uživatele, nikoli identifikovaný typ či ověřené jmenovité napětí; proud zůstává neznámý.

## Princip

Prohlížeč → Wi-Fi → Arduino → výkonový spínač / motorový budič → motor. Pro nový požadavek jednoho směru není H-můstek nezbytný; pro případnou pozdější reverzaci by potřeba byl.

UNO R4 WiFi už obsahuje Wi-Fi modul. Arduino má pro tuto desku [oficiální příklad jednoduchého webového serveru s vlastní Wi-Fi sítí](https://github.com/arduino/ArduinoCore-renesas/blob/main/libraries/WiFiS3/examples/AP_SimpleWebServer/AP_SimpleWebServer.ino). Náš motorový program používá síť `Auticko-test` a stránku **[http://192.168.4.1/](http://192.168.4.1/)**. Původní prázdný sketch tuto síť nevytvářel. Po uploadu motorového programu a opravě limitů HTTP hlaviček uživatel potvrdil připojení telefonu, stránku, LED a později také běh motoru. Server používá HTTP, nikoli HTTPS.

H-můstek je výkonový elektronický obvod, který u běžného dvouvodičového stejnosměrného motoru umožní obrátit polaritu a tím směr otáčení. Arduino poskytuje řídicí signály; proud pro motor dodává napájení přes budič. [Příklad řízení směru a rychlosti v dokumentaci Arduino](https://docs.arduino.cc/hardware/motor-shield-rev3) není doporučením konkrétního shieldu pro tento zatím neidentifikovaný motor.

## Co zbývá určit

- Vhodnost potvrzeného ST L293D pro motor při rozběhu pod zátěží a při delším provozu; úspěšný sekundový pulz tyto rezervy neověřuje.
- Typ nebo označení motoru, vhodné napětí a potřebný proud včetně rozběhu. Rozměry těla ani hřídelky elektrické parametry neurčují.
- Vhodné trvalejší napájení místo použité směsi článků, skutečné napětí a proud, spolehlivé konektory, odrušení a dostupnost multimetru.

Zvolený budič i další napájení posoudit podle těchto údajů. Hlavní I/O UNO R4 WiFi pracují s 5V logikou; přímé vývody jeho ESP32-S3 mají jinou napěťovou úroveň, proto je nezaměňovat. Zdroj: [oficiální datasheet desky](https://github.com/arduino/docs-content/blob/main/content/hardware/02.uno/boards/uno-r4-wifi/datasheet/datasheet.md).

## Dostupná sada a fotografie součástek

Uživatel dodal přímo [odkaz na sadu LaskaKit MAXI RFID](https://www.laskakit.cz/laskkit-arduino-maxi-starter-kit--rfid/); konkrétní varianta dodané Arduino desky v sadě není určená. Její zveřejněný seznam uvádí řadič ULN2003, krokový motor 28BYJ-48, servo a jednokanálové relé; L293D ani samostatný dvouvodičový DC motorek v seznamu nejsou. Skutečné vlastnictví L293D však potvrdil uživatel a fotografie níže, proto se existence čipu nepopírá podle obsahu katalogu. Odkaz neurčuje elektrické parametry jeho samostatného motoru.

Na první uživatelské fotografii je vlevo od LCD zelená deska s černým čipem, bílým konektorem a čtyřmi LED. **Následný detail `20260919_012402.jpg` potvrdil čitelné označení TI ULN2003AN.** Jde o modul s tranzistorovými spínači, nikoli H-můstek. V horní průhledné krabici byly další volné čipy s nečitelnými nápisy. Z těchto prvních snímků nebylo možné určit H-můstek; až další detail a uživatelské potvrzení určily ST L293D.

[ULN2003A podle výrobce TI](https://www.ti.com/product/ULN2003A) obsahuje nízkostranné tranzistorové spínače; sám není H-můstkem pro reverzaci dvouvodičového DC motoru. Pro vizuální porovnání jsme uživateli otevřeli [samostatný L293D na Drátku](https://dratek.cz/arduino-platforma/1128-io-l293d-pro-rizeni-motoru.html). Samotný katalog nebyl potvrzením vlastnictví; to doložil až následující detail čipu.

**Oprava předchozího kategorického tvrzení v hlasovém rozhovoru:** ULN2003 lze za vhodných elektrických podmínek použít i jako spínač dvouvodičového DC motoru pro jeden směr. Není omezený výhradně na krokové motory. Vhodnost konkrétního modulu pro uživatelův motor stále není potvrzena: chybí napětí, proud včetně rozběhu/zablokování a ověření zapojení napájení a ochranných diod modulu. Bez těchto údajů nedávat návod k zapnutí motoru ani automaticky spojovat výstupy.

Uživatel následně poslal detail samostatného čipu `20260919_012729.jpg` a výslovně **potvrdil celé označení L293D**. Máme tedy ST L293D v pouzdru DIP16. [Oficiální stránka ST L293D](https://www.st.com/en/motor-drivers/l293d.html) potvrzuje řízení DC motorů dvojicemi kanálů jako H-můstky; jmenovitě 600 mA na kanál, špičkový údaj 1,2 A není trvalý dovolený proud. Identifikace čipu nepotvrzuje odběr motoru. [Zapojení](zapojeni-l293d.md) má vývody ověřené dle ST. Původně zvažovanou regulovanou 5V motorovou větev při skutečné zkoušce nahradil výše popsaný držák AA; jeho parametry nebyly měřené.

## První program a další ovládání

Historická první testovací verze vytvářela vlastní Wi-Fi síť a nabízela jediné tlačítko pro **sekundový test vpřed**. Následující popis patří tehdejšímu programu; [aktuální firmware](../../models/jednoduche-auticko/firmware/prvni-motor/README.md) už používá držení tlačítka. Po startu je motor vypnutý. Platný požadavek vyvolá 1s pulz s PWM 128/255, potom se výkonový výstup vypne; síťová odpověď se posílá až po vypnutí. Jde o test na stole, nikoli nepřetržité řízení autíčka. Uvolnění tlačítka tento krátký pulz okamžitě nezkrátí. Při chybných/neúplných požadavcích ani obnovení stránky se motor nespouští.

Zdroj prošel překladem skutečným Arduino CLI pro UNO R4 WiFi a knihovnu WiFiS3 v core Renesas 1.6.0; samotný překlad nepotvrzuje funkci na desce. Podpora Arduino UNO R4 Boards 1.6.0 byla doplněna také do místního Arduino IDE. Po opravě USB uživatel nejprve úspěšně nahrál prázdný sketch. **Motorový program `prvni-motor.ino` byl potom otevřený v samostatném okně stejného Arduino IDE 2.3.10 a následně jej uživatel úspěšně nahrál.** Původní okno `sketch_sep19a` zůstalo zachované; kontrolní součty obou `.ino` se při otevření nezměnily. Otevření okna není upload ani zkouška motoru. Log tohoto uživatelského uploadu uvádí překlad 67 820 B, RAM 7 580 B a úspěšný zápis 67 828 B. Tehdejší lokální build ukazoval správný zdroj i UNO R4 WiFi a velikost jeho `.bin` odpovídala. Následovala oprava mobilního HTTP popsaná níže; velikosti různých verzí nezaměňovat. Obsah desky nebyl čten zpět.

### Oprava Linux USB oprávnění

Uživatelův log po výměně kabelu skončil chybou `1200-bps touch ... Permission denied`. Účet novakj původně neměl oprávnění pro čtení ani zápis `/dev/ttyACM0`. Na jeho žádost a s ověřeným sudo přístupem bylo vytvořeno `/etc/udev/rules.d/71-arduino-uno-r4-wifi-uaccess.rules`: pravidlo pro USB výrobce `2341`, modely `1002|006d` přidává `TAG+="uaccess"`. Tyto identity vycházejí z instalovaného `boards.txt` pro UNO R4 WiFi.

Pravidlo prošlo `udevadm verify`, bylo načtené a aplikované na aktuální tty zařízení. `getfacl` následně potvrdilo `user:novakj:rw-` a kontrola jako běžný uživatel potvrdila čtení i zápis. Skupiny uživatele ani oprávnění pro všechny uživatele nebyly rozšířené. Pravidlo umožňuje přístup aktivnímu místnímu uživateli a použije se také při dalším rozpoznání odpovídající desky. Samotnou opravou práv se žádný firmware nenahrával.

Uživatel zvolil držení tlačítka se zastavením po uvolnění. Po potížích v1 krátce požádal rollback, ale ještě před uploadem jej zrušil. Opravená `hold-to-run-v2` je otestovaná a nahraná; přesný stav testů a uploadu je v [přehledu](README.md) a [firmwaru](../../models/jednoduche-auticko/firmware/prvni-motor/README.md). Uživatel následně po obnovení stránky opakovaně potvrdil funkční držení, puštění a nový stisk („Jo, funguje to, perfektní“).

Uživatel následně potvrdil, že v nabídce Wi-Fi vidí síť **Auticko-test**, připojení telefonu a HTTP odpověď s chybou neplatného/neúplného požadavku. Oprava zvětšila limity HTTP hlaviček pro mobilní prohlížeče. Později uživatel potvrdil úspěšné načtení stránky po opravě a reakci LED; v této první fázi byl motor ještě odpojený.

**Oprava telefonu nahrána agentem:** limit řádku zvýšen ze 128 na 1024 znaků, součet na 8192 B, čas příjmu na 3 s; buffer je statický. Původní chybu reprodukovaly testovací mobilní hlavičky. Tehdejší zdroj prošel 53 testy parseru a 53 testy celého loop, kompilací a uploadem 67 812 B / 17 stran / 100 % na ověřenou UNO R4 WiFi. Agent při uploadu motorový pulz nevyvolal. Uživatel nejprve potvrdil stránku a reakci LED bez externích součástek; **po sestavení L293D, napájení a motoru sám potvrdil i skutečný sekundový rozběh**. Podrobnosti a omezení tohoto pozdějšího pokusu jsou v [záznamu prvního stolního testu](prvni-stolni-test.md).
