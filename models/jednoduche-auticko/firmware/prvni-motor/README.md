# Jízda a řízení autíčka — nahrané v3-reverse-v1

**Verze `v3-reverse-v1` s couváním je nahraná; uživatel následně obecně potvrdil funkčnost („Hele, všechno to funguje“).** Motor má kanonický záměr −1/0/1, PWM 128/255 v obou směrech a zaměněné úrovně IN1/IN2 pro couvání. Servo zachovává 1275 / 1575 / 1875 µs při 50 Hz. Překlad pro UNO R4 prošel (86 708 B flash / 9 868 B RAM), stejně jako úplná hostová, JS a Chromium regrese a nezávislá kontrola. Upload **86 716 B / 22 stran / exit 0** a tři pasivní výpisy potvrdily novou verzi a klidové výstupy. Čítače zařízení byly stabilní **HTTP=29 / closed=29**; původ dřívějších požadavků není určený. Agent odeslal 0 sériových dat, 0 HTTP a 0 pohybových povelů; port je zavřený a volný. **Po následné zkoušce uživatel obecně potvrdil funkčnost; agent pohyb ani elektrické měření PWM neprováděl.** [Evidence uploadu](evidence/2026-09-23-v3-reverse-v1-upload/README.md).

**Nové potvrzení před uploadem couvání:** na otázku po USB Arduina a odpojeném napájení motoru i červeném vodiči serva uživatel odpověděl „ano, servo odpojeno“ a upload výslovně autorizoval. Před uploadem byl podle tohoto hlášení servo plus odpojený a motor měl odpojený článek; táhlo se neměnilo. Po pozdější zkoušce uživatel potvrdil dokončení předaného postupu vypnutí („Hotovo“); jednotlivé spoje agent nekontroloval. Jde o uživatelské potvrzení, nikoli elektrické měření.

**Historická předchozí verze `v3-steering-v4`, zdroj SHA256 `0ee42b5512b97240a9d466e833e46a4360a3d4b5a7d112ae647146946781126e`.** Obsahuje druhý trim středu z 1525 rovnou na 1575 µs (+50 µs ve směru Doprava). Rozsah zůstává ±300 µs při 50 Hz: **1275 / 1575 / 1875 µs**. Meziverze se středem 1550 µs nevznikla. Ostatní chování se nemění. **Nahrání je dokončené a potvrzené třemi pasivními USB výpisy**, po novém potvrzení odpojeného servo plusu, motoru bez napájení a UNO na USB; táhlo může zůstat připojené. **Uživatel po tomto druhém trimu s připojeným táhlem a povelem Rovně potvrdil správnou neutrální polohu kol: „Super, takhle to je perfektní“.** Šlo o krátkou zkoušku s koly nad stolem a motorem bez napájení; není to měření úhlu, zkouška všech dorazů, dlouhodobého provozu nebo jízdy. Tehdejší doporučené odpojení serva po úspěchu nebylo potvrzené; nové potvrzení odpojení přišlo před uploadem reverse-v1 výše. Fyzická akceptace v4 se nepřenáší na nový hash.

**Předchozí nahraná `v3-steering-v3`:** první trim na 1525 µs je doložený [uploadem a třemi klidovými výpisy](evidence/2026-09-22-v3-steering-v3/README.md). Uživatel jej poté vyzkoušel s připojeným táhlem a povelem Rovně: změna byla podle něj téměř neznatelná a kola zůstala mírně doleva. Proto žádá další +50 µs. Tato zkouška neprokazuje dorazy, zatížené řízení ani jízdu.

**Předchozí nahraná `v3-steering-v2`:** uživatel po uploadu výslovně potvrdil pohyb volného serva doprava i doleva. Po připojování táhla hlásí mírné natočení kol doleva ve středovém stavu, proto žádá trim. Nejde o úplnou zkoušku krajních poloh se zatížením ani jízdy. [Neměnná evidence v2](evidence/2026-09-22-v3-steering-v2/README.md) a [následná fyzická chronologie](../../../../elektronika/auticko/kontrolni-zapojeni.md#hlasova-zkouska-22-9-2026).

**Předchozí nahraná `v3-steering-v1` (22. 9. 2026):** upload 84 916 B / 21 stran / exit 0 a tři pasivní USB výpisy potvrdily verzi a klidové výstupy. Po opravě chybného připojení mínusu servového zdroje z IOREF na GND uživatel nově potvrdil klidné servo a malý pohyb na směrový povel. Úplná zkouška obou krajních poloh s koly ani jízdy potvrzená není. [Původní upload](evidence/2026-09-22-v3-steering-v1-upload/README.md), [neměnný archiv zdroje a testů v1](../archiv-v3-steering-v1/archiv-manifest.json), [fyzická chronologie](../../../../elektronika/auticko/kontrolni-zapojeni.md#hlasova-zkouska-22-9-2026).

**Poslední úplná fyzická akceptace motorového ovládání patří `hold-to-run-v2`**, SHA256 `1760730b716a6fb281ed900400d533eaac17d96c9b779a6c91e2e99502d69110`. Uživatel u něj potvrdil držení, puštění a další stisk. Jeho úplný zdroj, testy a tehdejší evidence jsou zachované v [přesném archivu v2](../archiv-hold-to-run-v2/README.md) a kontrolované [manifestem](../archiv-hold-to-run-v2/archiv-manifest.json). Historická fyzická akceptace se nevztahuje na nový hash V3.

## Ovládání nahrané v3-reverse-v1

Couvání je nahrané; uživatel po zkoušce obecně potvrdil funkčnost. Následující postup je popis ovládání, nikoli záznam jeho fyzického vyzkoušení.

1. Připojit telefon k Wi-Fi **Auticko-test**, veřejné demo heslo **auticko123**. Po zapnutí trvá příprava AP přibližně 10 sekund.
2. Obnovit starou stránku nebo otevřít **[http://192.168.4.1/](http://192.168.4.1/)**. Načtení zastaví motor a zadá střed serva.
3. Držet **Jízdu vpřed** nebo **Držet pro couvání**. Druhým prstem lze zároveň držet **Doleva** nebo **Doprava**; funguje i opačné pořadí dotyků. Směr kol se při couvání neobrací.
4. Puštění směru vrací řízení na střed, pokud není držený druhý směr. Držená jízda pokračuje. Puštění jízdy vypne motor, i když zatáčení dál držíš.
5. **Rovně** zruší požadavek zatáčení; samotné řízení ani Rovně motor nespustí. Současné držení doleva a doprava zadává střed.
6. Současné vpřed a couvání vyvolá STOP obou ovládání. Předčasná změna směru také zastaví relaci a zobrazí **„Změna směru: pusť ovladače a stiskni znovu.“** Pustit všechny ovladače včetně řízení a potom skutečně znovu stisknout. Dokud některý zůstává držený, nepomůže ani nový stisk jiného ovladače. Také druhý kontakt stejného tlačítka a nově přidané kontakty během zastavování musí být před dalším spuštěním uvolněné.
7. Po chybě ovladače pustit a stisknout znovu. Obnovení sítě, periodický požadavek, opakovaná klávesa ani samotné uplynutí času pohyb neobnoví.

Podporované jsou myš, dva dotyky, klávesy šipka nahoru/dolů/vlevo/vpravo a Space/Enter na zaměřeném tlačítku. Krátké ťuknutí není sekundový pulz a nemusí dokončit přípravu relace. Stav na stránce potvrzuje přijatý příkaz, nikoli měřený pohyb nebo polohu serva.

[Offline náhled](../../../../elektronika/auticko/nahled-ovladani-v3.html) obsahuje skutečné HTML/JS firmwaru s jasně označenou simulací odpovědí a zakázaným síťovým připojením. [Mobilní screenshot](../../../../elektronika/auticko/nahled-ovladani-v3.png) zachycuje skutečné UI sketche v Chromiu proti místní náhradě hardwaru; nejde o stránku skutečného Arduina. Verzi offline náhledu určuje hash zdroje vložený při jeho exportu; screenshot ani náhled nedokazují verzi nahranou do Arduina.

## Zapojení, start a rozsah

Úplný postup, napájecí podmínky a kalibrace jsou v **[řízení V3](../../../../elektronika/auticko/rizeni-v3.md)**. [Motorové zapojení L293D](../../../../elektronika/auticko/zapojeni-l293d.md) zůstává zachované:

| Arduino | Připojení | Výstup |
|---|---|---|
| D5 | L293D pin 1 EN | 490 Hz, ekvivalent PWM 128/255 |
| D7 | L293D pin 2 IN1 | HIGH vpřed, LOW vzad i při vypnutí |
| D8 | L293D pin 7 IN2 | LOW vpřed, HIGH vzad, LOW při vypnutí |
| **D9** | **Signál SG90** | **50 Hz, střed 1575 µs, odchylka ±300 µs** |

`STEER_CENTER_US=1575`, `STEER_OFFSET_US=300`, `STEER_SIGN=1`. Doleva je 1275 µs a doprava 1875 µs. Neutrální polohu kol uživatel přijal na v4; úhel ani převod pulzu na úhel konkrétního kusu nejsou změřené. Tato akceptace se nepřenáší na nový hash couvání. D9 patří přímo k signálu serva, nikoli na L293D.

**Servo dostane středový pulz již při startu a může se pohnout dříve, než se otevře stránka. První vystředění musí proběhnout bez páčky/táhla.** Pohon při startu zůstává vypnutý. Doporučený návrh používá vlastní přímou regulovanou 5V napájecí větev serva a společnou zem, bez propojení externího +5 V s Arduino 5V nebo kladným pólem motorového zdroje. Štítkové režimy powerbanky byly přečtené uživatelem, skutečný vhodný 5V výstup a vyvedení +5 V/GND nejsou ověřené; regulovaná větev není hotová.

**Hlášená zkouška 22. 9. na v1:** po původním chvění a výpadcích uživatel opravil mínus nového servového zdroje z IOREF na správný GND. Následně hlásil 6,35 V bez USB i s USB (plus zdroje proti hnědému serva, nikoli měření zatíženého serva), klid po připojení a první malý pohyb na směrový povel. Proto požádal o dvojnásobnou výchylku. Zdroj není regulovaný a 6,35 V je stále nad uvedeným rozsahem SG90 4,8–6 V; uživatel výslovně přijal riziko krátké zkoušky bez měniče, nejde o doporučené provozní napájení. Před novým uploadem výslovně potvrdil červený servo+ odpojený, motor bez napájení, táhlo odpojené a UNO na USB. [Přesný záznam a původ údajů](../../../../elektronika/auticko/kontrolni-zapojeni.md#hlasova-zkouska-22-9-2026).

Používá se vestavěný `PwmOut`, bez knihovny Servo. V jádru 1.6.0 používá D5 GPT0/A a D9 GPT7/B, následný samostatný časovač kontroly je GPT4. D8 zůstává GPIO, jeho alternativní GPT7/A se nepoužívá. Zápisy PWM se provádějí v krátké kritické sekci nebo přímo v přerušení, bez síťových operací, čekání či alokací v ISR.

## Povolení pohybu a vypnutí

Jedna společná relace řídí motor i servo. Po `POST /session` podle potřeby a `POST /arm` následuje jeden řetězec jednorázových výzev pro `POST /hold`. Prohlížeč nemá dva souběžné řetězce pro dva prsty: každý HOLD nese úplný záměr motor + řízení. Změna během čekání se odešle po odpovědi s novou výzvou; starší odpověď nesmí obnovit ukončený stisk.

Nové hlavičky HOLD jsou vždy obě: `X-Control-Motor: -1|0|1` a `X-Control-Steer: left|center|right`. Neplatná hodnota, duplicita nebo chybějící jedna z dvojice se odmítne. Teprve úplné vynechání obou zachová starý protokol v2 jako motor vpřed / servo střed. Hodnoty motoru znamenají couvání / vypnuto / vpřed; jiné zápisy než přesné `-1`, `0`, `1` nejsou kanonické. Server nadále kontroluje token, číslo stisku, výzvu, Host/Origin, délku a úplnost HTTP.

Před změnou polarity se motorový výstup skutečně vypne: EN=0 a IN1=IN2=LOW. Opačný směr je povolen až po nejméně **250 ms od tohoto OFF**, nikoli od posledního přijatého požadavku. Předčasný HOLD vrátí **`HOLD_REARM` bez nonce**, přejde do IDLE a zahodí výzvu. Původní HOLD/retry ani ARM se stejným číslem stisku relaci neobnoví, ani když 250 ms později uplyne. UI po odpovědi odešle STOP a vyžaduje puštění všech ovladačů a nový skutečný stisk. Příliš brzký nový stisk může být opět odmítnut; z delšího klidu stačí jediné podržení. Žádný časovač sám motor nespouští. **Prodleva není měření mechanického zastavení; motor může dobíhat déle.**

Příprava ARM drží motor vypnutý a servo ve středu nejvýše 3000 ms; první výzva musí být i tak mladší než 500 ms. Platný nový HOLD udělí **500 ms od přijetí**. Přerušení po **5 ms** při vypršení vypne motor a zadá střed. Běží i během běžných blokujících volání Wi-Fi, není však nezávislým watchdogem procesoru.

Při ztraceném STOP může jeden už odeslaný HOLD těsně před vypršením výzvy obnovit povolení naposledy. Konzervativní mez je **až 1 s od zpracování puštění prohlížečem nebo ztráty spojení** do vypnutí motorového výstupu a zadání středu. To platí i při puštění jednoho ovladače, pokud se jeho nový úplný záměr nepodaří doručit. Nový servo pulz se uplatní v následující 20ms periodě, následuje mechanický pohyb. Motor volně dobíhá; skutečná poloha kol ani časy nejsou měřené.

STOP, ztráta focusu, opuštění/skrytí stránky, offline a chyba přeruší povolení pro obě akce. Staré HOLD, starý stisk a pozdní odpovědi nesmějí obnovit vypršenou relaci. Při selhání inicializace PWM nebo časovače se pohon nepovolí. Při selhání PWM serva se D9 nastaví LOW a motor vypne; **v tomto poruchovém stavu nelze garantovat mechanické vystředění**.

## Kontroly a sestavení

[Regresní testy](tests/README.md) spouštějí skutečný sketch proti náhradám hardwaru, skutečný vložený JavaScript a Chromium proti místnímu HTTP serveru napojenému na C++ sketch. Neotevírají USB ani skutečnou Wi-Fi autíčka. Zahrnují dosavadní motorový protokol, nové záměry, samostatné řízení, obě pořadí dvou prstů, nezávislé puštění, Rovně, staré požadavky, chyby PWM a vypnutí během blokujících operací.

Pro `v3-reverse-v1` jsou regrese rozšířené o signed parser, oba směry a vypínání před změnou polarity, REARM bez automatického opakování, konflikty, vlastnictví kontaktů, opožděné odpovědi a skutečné události Chromia. **Úplný běh prošel: 120 parserových + 120 HTTP případů, 42 hostových scénářů, 21 blokujících zkoušek, 46 JS scénářů a 23 skutečných Chromium HTTP scénářů.** Překlad pro UNO R4 prošel (86 708 B flash / 9 868 B RAM), stejně jako úplná hostová, JS a Chromium regrese a nezávislá kontrola. [Přesná evidence a hashe](evidence/2026-09-22-v3-reverse-v1/README.md). Překlad je určený pro `arduino:renesas_uno:unor4wifi`, core 1.6.0; sám neznamená upload.

Historická [evidence v4](evidence/2026-09-22-v3-steering-v4/README.md) má **84 940 B flash / 9 864 B RAM, překlad exit 0**. Při tomto trimu se rozsáhlá regrese neopakovala; tehdejší poslední úplný běh patří [steering-v3](evidence/2026-09-22-v3-steering-v3/). Tyto výsledky nedokazují funkci nového zdroje couvání. Aktuální rozsah evidence rozlišuje [ověřovací záznam](overeni-programu.json).

## Diagnostika a další krok

Poslední pasivně přečtený výpis nahrané verze na 115200 baud obsahoval `build=v3-reverse-v1`, `steeringReady`, `steeringUs`, `neutralUs` a `rangeUs=300`. `drive=RUNNING` znamená aktivní společnou relaci; nově může jít i o zatáčení s vypnutým motorem. Počet přijatých příkazů nebo čtení GPIO není měření proudu či polohy. Znak `?` pouze vyžádá diagnostiku.

Upload **`v3-reverse-v1`, 86 716 B / 22 stran / exit 0** na UNO R4 WiFi `3CDC75F1A2D4`, `/dev/ttyACM0`, je dokončený. Zdroj SHA256 `d24a87631fd32a41685baedd7488c425a75ca6f9e300706349c61e09e79fe930`, BIN SHA256 `663fbe045211770308dab03aa696c69ea0b61f314b063ae9fc5bf7310c0ae19e`. Tři pasivní výpisy **22. 9. 22:10:07–22:10:19 UTC (23. 9. 00:10:07–00:10:19 místně)** potvrdily `build=v3-reverse-v1`, `safety=1`, `drive=0`, EN/IN1/IN2 LOW, `steeringReady=1`, `steeringUs=neutralUs=1575`, `rangeUs=300`, `leaseMs=0` a server=1. **HTTP=29 / closed=29 zůstaly stabilní; nejsou nulové. Původ dřívějších 29 požadavků není určený.** Agent při tomto kroku odeslal **0 sériových dat, 0 HTTP a 0 pohybových povelů**. Port je zavřený a volný. Po následné zkoušce uživatel obecně potvrdil funkčnost; agent pohyb ani elektrické měření PWM neprováděl. [Nová uploadová evidence](evidence/2026-09-23-v3-reverse-v1-upload/README.md) je oddělená od historické offline přípravy a uploadů steering-v4.

**Uživatel po zkoušce řekl „Hele, všechno to funguje“; následně potvrdil dokončení postupu vypnutí („Hotovo“), bez nezávislé kontroly jednotlivých spojů.** Předaný postup počítal s koly nad stolem: Nejdříve krátce zvlášť vpřed a puštění; po pauze a novém stisku vzad a puštění, teprve potom řízení a souběh ovladačů. Předuploadové odpojení bylo potvrzené; následné vypnutí uživatel potvrdil slovem „Hotovo“, bez nezávislé kontroly jednotlivých spojů. Dřívějších 6,35 V a přijetí rizika krátkého pokusu bez měniče zůstávají historickým údajem, nikoli fyzickou akceptací nové verze. [Podrobný plán](../../../../elektronika/auticko/rizeni-v3.md#příští-zkouška-couvání--zatím-neprovedená).

Historické výsledky a nevyřešený těžký rozjezd jsou v [elektronice autíčka](../../../../elektronika/auticko/README.md) a [záznamu potíží](../../../../elektronika/auticko/potize-po-montazi.md). Starší [archiv v1](../archiv-hold-to-run-v1/README.md), [sekundový test](historie-sekundoveho-testu.md) a jeho [evidence](historie-overeni-pulzu.json) se nevztahují k současnému zdroji.
