# Jízda a řízení autíčka — v3-steering-v1

**`v3-steering-v1` je od 22. 9. 2026 nahraný do UNO R4 WiFi a potvrzený klidovou USB diagnostikou.** Přidává servo SG90 na D9 a ovládání dvěma prsty. Nahrál se původní testovaný BIN se shodným hashem; zdroj ani piny a chování se neměnily. Upload: **84 916 B / 21 stran / exit 0**. Tři výpisy potvrdily V3, motorové výstupy LOW, `leaseMs=0`, připravené řízení a nominální střed 1500 µs. **Následná uživatelem hlášená zkouška serva nepotvrdila samostatný návrat na střed; V3 nemá fyzickou akceptaci.** [Evidence uploadu](evidence/2026-09-22-v3-steering-v1-upload/README.md), [souhrnný ověřovací záznam](overeni-programu.json), [hlasová zkouška a kontrolní zapojení](../../../../elektronika/auticko/kontrolni-zapojeni.md#hlasova-zkouska-22-9-2026).

**Předchozí upload a poslední fyzická akceptace patří `hold-to-run-v2`**, SHA256 `1760730b716a6fb281ed900400d533eaac17d96c9b779a6c91e2e99502d69110`. Uživatel u něj potvrdil držení, puštění a další stisk. Jeho úplný zdroj, testy a tehdejší evidence jsou zachované v [přesném archivu v2](../archiv-hold-to-run-v2/README.md) a kontrolované [manifestem](../archiv-hold-to-run-v2/archiv-manifest.json). Historická fyzická akceptace se nevztahuje na nový hash V3.

## Ovládání nahrané V3 — po dokončení fyzického zapojení

1. Připojit telefon k Wi-Fi **Auticko-test**, veřejné demo heslo **auticko123**. Po zapnutí trvá příprava AP přibližně 10 sekund.
2. Obnovit starou stránku nebo otevřít **[http://192.168.4.1/](http://192.168.4.1/)**. Načtení zastaví motor a zadá střed serva.
3. Držet **Jízdu vpřed**. Druhým prstem lze zároveň držet **Doleva** nebo **Doprava**; funguje i opačné pořadí dotyků.
4. Puštění směru vrací řízení na střed, pokud není držený druhý směr. Držená jízda pokračuje. Puštění jízdy vypne motor, i když zatáčení dál držíš.
5. **Rovně** zruší požadavek zatáčení; samotné řízení ani Rovně motor nespustí. Současné držení doleva a doprava zadává střed.
6. Po chybě ovladače pustit a stisknout znovu. Nový skutečný stisk obnoví relaci; obnovení sítě samo pohyb nezahájí.

Podporované jsou myš, dva dotyky, klávesy šipka nahoru/vlevo/vpravo a Space/Enter na zaměřeném tlačítku. Krátké ťuknutí není sekundový pulz a nemusí dokončit přípravu relace. Stav na stránce potvrzuje přijatý příkaz, nikoli měřený pohyb nebo polohu serva.

[Offline náhled](../../../../elektronika/auticko/nahled-ovladani-v3.html) obsahuje skutečné HTML/JS firmwaru s jasně označenou simulací odpovědí a zakázaným síťovým připojením. [Mobilní screenshot](../../../../elektronika/auticko/nahled-ovladani-v3.png) zachycuje skutečné UI sketche v Chromiu proti místní náhradě hardwaru; nejde o stránku skutečného Arduina.

## Zapojení, start a rozsah

Úplný postup, napájecí podmínky a kalibrace jsou v **[řízení V3](../../../../elektronika/auticko/rizeni-v3.md)**. [Motorové zapojení L293D](../../../../elektronika/auticko/zapojeni-l293d.md) zůstává zachované:

| Arduino | Připojení | Výstup |
|---|---|---|
| D5 | L293D pin 1 EN | 490 Hz, ekvivalent PWM 128/255 |
| D7 | L293D pin 2 IN1 | HIGH při jízdě |
| D8 | L293D pin 7 IN2 | LOW |
| **D9** | **Signál SG90** | **50 Hz, střed 1500 µs, počáteční odchylka ±150 µs** |

`STEER_CENTER_US=1500`, `STEER_OFFSET_US=150`, `STEER_SIGN=1`. Doleva je 1350 µs a doprava 1650 µs. Směr, střed ani převod na úhel konkrétního kusu nebyly změřené. D9 patří přímo k signálu serva, nikoli na L293D.

**Servo dostane středový pulz již při startu a může se pohnout dříve, než se otevře stránka. První vystředění musí proběhnout bez páčky/táhla.** Pohon při startu zůstává vypnutý. Doporučený návrh používá vlastní přímou regulovanou 5V napájecí větev serva a společnou zem, bez propojení externího +5 V s Arduino 5V nebo kladným pólem motorového zdroje. Štítkové režimy powerbanky byly přečtené uživatelem, skutečný vhodný 5V výstup a vyvedení +5 V/GND nejsou ověřené; regulovaná větev není hotová.

**Hlášený pokus 22. 9.:** uživatel nemá měnič a po upozornění na rozsah SG90 4,8–6 V přijal riziko přímých naměřených 6,4 V z nového samostatného čtyřčlánkového zdroje. Potvrdil oranžový SG90 → UNO D9, hnědý → GND, mínus nového zdroje → volný GND Arduina a pro krátké zkoušky plus přímo na červený vodič. Táhlo od kol odpojil, páčka zůstala. Načetl skutečné UI V3 v telefonu; ve středu servo hlásil klidné, mimo střed chvění/bzučení s nutností pomoci rukou. Nejde o úspěšné samostatné ustavení ani doporučené napájení. Zkoušku směrových tlačítek či jízdy nepotvrdil. **Poslední odpojení plusu serva i USB není potvrzené; stav napájení je nejistý.** Volný modrý vodič z mínusové lišty ani neověřené propojení této lišty s UNO GND neprokazují příčinu. Jde výhradně o hlasové hlášení, nikoli přímou kontrolu; [úplný nákres a seznam spojů](../../../../elektronika/auticko/kontrolni-zapojeni.md) slouží k další kontrole.

Používá se vestavěný `PwmOut`, bez knihovny Servo. V jádru 1.6.0 používá D5 GPT0/A a D9 GPT7/B, následný samostatný časovač kontroly je GPT4. D8 zůstává GPIO, jeho alternativní GPT7/A se nepoužívá. Zápisy PWM se provádějí v krátké kritické sekci nebo přímo v přerušení, bez síťových operací, čekání či alokací v ISR.

## Povolení pohybu a vypnutí

Jedna společná relace řídí motor i servo. Po `POST /session` podle potřeby a `POST /arm` následuje jeden řetězec jednorázových výzev pro `POST /hold`. Prohlížeč nemá dva souběžné řetězce pro dva prsty: každý HOLD nese úplný záměr motor + řízení. Změna během čekání se odešle po odpovědi s novou výzvou; starší odpověď nesmí obnovit ukončený stisk.

Nové hlavičky HOLD jsou vždy obě: `X-Control-Motor: 0|1` a `X-Control-Steer: left|center|right`. Neplatná hodnota, duplicita nebo chybějící jedna z dvojice se odmítne. Teprve úplné vynechání obou zachová starý protokol v2 jako motor vpřed / servo střed. Server nadále kontroluje token, číslo stisku, výzvu, Host/Origin, délku a úplnost HTTP.

Příprava ARM drží motor vypnutý a servo ve středu nejvýše 3000 ms; první výzva musí být i tak mladší než 500 ms. Platný nový HOLD udělí **500 ms od přijetí**. Přerušení po **5 ms** při vypršení vypne motor a zadá střed. Běží i během běžných blokujících volání Wi-Fi, není však nezávislým watchdogem procesoru.

Při ztraceném STOP může jeden už odeslaný HOLD těsně před vypršením výzvy obnovit povolení naposledy. Konzervativní mez je **až 1 s od zpracování puštění prohlížečem nebo ztráty spojení** do vypnutí motorového výstupu a zadání středu. To platí i při puštění jednoho ovladače, pokud se jeho nový úplný záměr nepodaří doručit. Nový servo pulz se uplatní v následující 20ms periodě, následuje mechanický pohyb. Motor volně dobíhá; skutečná poloha kol ani časy nejsou měřené.

STOP, ztráta focusu, opuštění/skrytí stránky, offline a chyba přeruší povolení pro obě akce. Staré HOLD, starý stisk a pozdní odpovědi nesmějí obnovit vypršenou relaci. Při selhání inicializace PWM nebo časovače se pohon nepovolí. Při selhání PWM serva se D9 nastaví LOW a motor vypne; **v tomto poruchovém stavu nelze garantovat mechanické vystředění**.

## Kontroly a sestavení

[Regresní testy](tests/README.md) spouštějí skutečný sketch proti náhradám hardwaru, skutečný vložený JavaScript a Chromium proti místnímu HTTP serveru napojenému na C++ sketch. Neotevírají USB ani skutečnou Wi-Fi autíčka. Zahrnují dosavadní motorový protokol, nové záměry, samostatné řízení, obě pořadí dvou prstů, nezávislé puštění, Rovně, staré požadavky, chyby PWM a vypnutí během blokujících operací.

Sestavení pro `arduino:renesas_uno:unor4wifi`, jádro `arduino:renesas_uno@1.6.0`, prošlo: **84 908 B flash / 9 864 B RAM**. Finální SHA256: `9f7477c851898e97e7c9fd50ca632104c9214259b415a3fa9996ca6a48d8760c`. Prošlo **109 parserových + 109 HTTP případů, 34 stavových skupin, 14 blokujících IRQ zkoušek, 33 JS a 14 skutečných Chromium scénářů**. [Ověřovací záznam](overeni-programu.json) a [výpisy](evidence/2026-09-20-v3-steering-v1/) patří tomuto hashi. Překladač hlásí varování v Arduino jádru a knihovnách, žádné v aktuálním sketchi. Úspěšná simulace a překlad nepotvrzují skutečnou latenci WiFiS3, elektrické pulzy, proudové rezervy, sílu řízení ani chování pod zátěží.

## Diagnostika a další krok

Výpis na 115200 baud přidává `build=v3-steering-v1`, `steeringReady`, `steeringUs`, `neutralUs` a `rangeUs`. `drive=RUNNING` znamená aktivní společnou relaci; nově může jít i o zatáčení s vypnutým motorem. Počet přijatých příkazů nebo čtení GPIO není měření proudu či polohy. Znak `?` pouze vyžádá diagnostiku.

Upload a pasivní diagnostika jsou dokončené; sériový monitor je uzavřený. Agent během ověření neposlal žádná sériová data ani HTTP či pohybové povely. Předuploadové pasivní čtení s DTR vypnutým nepřineslo diagnostiku, proto nepotvrzuje tehdejší běžící verzi; v2 zůstává doložená historickou evidencí. Po uploadu bylo DTR zapnuté pro příjem CDC na 115200 baud. Další fyzické vedení po hlášené neúspěšné zkoušce serva zůstává původnímu tasku podle [kontrolního přehledu](../../../../elektronika/auticko/kontrolni-zapojeni.md) a [návodu V3](../../../../elektronika/auticko/rizeni-v3.md). Toto dokumentační doplnění nepřidává hardwarovou operaci ani nové softwarové testy. Zpětné přečtení celé flash ani elektrické měření PWM se neprovádělo; doložený je upload a diagnostikou hlášený klid v době ověření.

Historické výsledky a nevyřešený těžký rozjezd jsou v [elektronice autíčka](../../../../elektronika/auticko/README.md) a [záznamu potíží](../../../../elektronika/auticko/potize-po-montazi.md). Starší [archiv v1](../archiv-hold-to-run-v1/README.md), [sekundový test](historie-sekundoveho-testu.md) a jeho [evidence](historie-overeni-pulzu.json) se nevztahují k současnému zdroji.
