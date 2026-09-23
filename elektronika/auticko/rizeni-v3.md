# Řízení V3 — SG90 a ovládání z telefonu

**Couvání `v3-reverse-v1` je nahrané; uživatel následně obecně potvrdil funkčnost („Hele, všechno to funguje“).** Nová verze přidává Držet pro couvání / ArrowDown, zachovává PWM 128/255 a servo 1275 / 1575 / 1875 µs při 50 Hz. Řídicí vodiče L293D se nepřepojují; software pro couvání zamění úrovně IN1/IN2. Doleva a Doprava nadále znamenají stejný směr natočení kol i při couvání. Překlad pro UNO R4 prošel (86 708 B flash / 9 868 B RAM), stejně jako úplná hostová, JS a Chromium regrese a nezávislá kontrola. Zdroj SHA256 `d24a87631fd32a41685baedd7488c425a75ca6f9e300706349c61e09e79fe930`. Upload **86 716 B / 22 stran / exit 0** a tři pasivní výpisy potvrdily novou verzi a klidové výstupy. Čítače zařízení byly stabilní **HTTP=29 / closed=29**; původ dřívějších požadavků není určený. Agent odeslal 0 sériových dat, 0 HTTP a 0 pohybových povelů; port je zavřený a volný. **Po následné zkoušce uživatel obecně potvrdil funkčnost; agent pohyb ani elektrické měření PWM neprováděl.** [Evidence nového uploadu](../../models/jednoduche-auticko/firmware/prvni-motor/evidence/2026-09-23-v3-reverse-v1-upload/README.md). Následující evidence neutrální polohy patří předchozí v4; není akceptací couvání.

Historicky byl nahraný **`v3-steering-v4`: střed 1575 µs, zachované ±300 µs a 50 Hz (1275 / 1575 / 1875 µs)**. Upload **84 948 B / 21 stran / exit 0** a tři pasivní USB výpisy potvrdily novou verzi, klid motoru, `steeringUs=neutralUs=1575` a `rangeUs=300`. **Uživatel následně s připojeným táhlem, koly nad stolem, motorem bez napájení a povelem Rovně potvrdil správnou neutrální polohu kol: „Super, takhle to je perfektní“.** Jde přímo o +50 µs od v3 ve směru Doprava, bez mezikroku 1550 µs. Uživatel na v3 s připojeným táhlem a povelem Rovně stále hlásil kola mírně doleva; první +25µs trim byl podle něj skoro neznatelný. Potvrzení se týká neutrální polohy kol při krátké zkoušce; nejde o měření úhlu, ověření všech dorazů, dlouhodobého provozu ani jízdy.

**Nové potvrzení před uploadem couvání:** na otázku po USB Arduina a odpojeném napájení motoru i červeném vodiči serva uživatel odpověděl „ano, servo odpojeno“ a upload výslovně autorizoval. Před uploadem byl podle tohoto hlášení servo plus odpojený a motor měl odpojený článek; táhlo se neměnilo. Po pozdější zkoušce uživatel potvrdil dokončení předaného postupu vypnutí („Hotovo“); jednotlivé spoje agent nekontroloval. Jde o uživatelské potvrzení, nikoli elektrické měření.

Zdroj v4 SHA256 `0ee42b5512b97240a9d466e833e46a4360a3d4b5a7d112ae647146946781126e`; překlad 84 940 B flash / 9 864 B RAM. Tři pasivní snapshoty v **21:42:01–21:42:13 UTC** potvrdily `build=v3-steering-v4`, `steeringReady=1`, `steeringUs=neutralUs=1575`, `rangeUs=300`, `safety=1`, `drive=0`, EN/IN1/IN2 LOW, `leaseMs=0`, `watchdog=0`, server=1 a HTTP=0. Port je uzavřen; žádná sériová data, HTTP ani pohybové povely nebyly odeslány. [Evidence uploadu v4](../../models/jednoduche-auticko/firmware/prvni-motor/evidence/2026-09-22-v3-steering-v4/README.md).

**Předchozí nahraný `v3-steering-v3`: nominální střed 1525 µs (+25 µs ve směru Doprava při `STEER_SIGN=1`), zachované ±300 µs a 50 Hz, tedy 1225 / 1525 / 1825 µs.** Zdroj SHA256 `0e56dfc88e022d18fcf4b8d33e511c5f99cc0671d2a23572686be4324a19dbb3`; build 84 940 B flash / 9 864 B RAM, upload **84 948 B / 21 stran / exit 0**. Tři pasivní USB snapshoty v 21:36:23–21:36:34 UTC potvrdily novou verzi, `steeringReady=1`, `steeringUs=neutralUs=1525`, `rangeUs=300`, vypnutý motor, `leaseMs=0` a připravený server s HTTP=0. Port je uzavřen; agent neposlal sériová data, HTTP ani pohybové povely. [Evidence uploadu v3](../../models/jednoduche-auticko/firmware/prvni-motor/evidence/2026-09-22-v3-steering-v3/README.md). Uživatel po potvrzeném pohybu volného serva v2 oběma směry a pokynech k připojení táhla hlásil mírné natočení kol doleva při Rovně. První trim byl následně uživatelem vyzkoušen s připojeným táhlem: při Rovně zůstala kola mírně doleva a změna byla skoro neznatelná. Dorazy, zatížení a jízda nejsou přijaté.

**Předchozí nahraný `v3-steering-v2`: ±300 µs místo ±150 µs, tedy 1200 / 1500 / 1800 µs při stejných 50 Hz.** Zdroj SHA256 `fcefad5f61f703e3294ac1464206d1022e72fcf85fc7acea3f634947d1b8a5b6`; build 84 940 B flash / 9 864 B RAM, upload 84 948 B / 21 stran / exit 0. Tři pasivní USB snapshoty v 21:26:15–21:26:26 UTC potvrdily `build=v3-steering-v2`, `safety=1`, `drive=0`, EN/IN1/IN2 LOW, `steeringReady=1`, střed 1500 µs, `rangeUs=300`, `leaseMs=0` a připravený server s HTTP=0. Port byl uzavřen; žádná sériová data, HTTP ani pohybové povely nebyly odeslány. **Uživatel následně potvrdil, že se volné servo na v2 hezky pohybuje doprava i doleva.** [Evidence uploadu v2](../../models/jednoduche-auticko/firmware/prvni-motor/evidence/2026-09-22-v3-steering-v2/README.md). Piny, střed, motorové PWM, ovládací protokol a časové limity se nemění. Dvojnásobný rozdíl pulzu není naměřeným dvojnásobkem úhlu konkrétního serva či kol.

Historický upload z **22. 9. 2026**: předchozí `v3-steering-v1` byl **nahrán do Arduino UNO R4 WiFi** (USB serial `3CDC75F1A2D4`, `/dev/ttyACM0`). Upload 84 916 B / 21 stran skončil exit 0; tři pasivní USB výpisy potvrdily správnou verzi, vypnutý motor, `steeringReady=1`, nominální střed 1500 µs, rozsah ±150 µs, `leaseMs=0` a připravený server. Při tomto ověření agent neposlal pohybové ani HTTP povely. **Po pozdější opravě mínusu servo zdroje z IOREF do GND uživatel poprvé hlásí klidné servo a malý pohyb na směrové tlačítko.** To není úplná fyzická akceptace řízení ani jízdy. [Evidence uploadu v1](../../models/jednoduche-auticko/firmware/prvni-motor/evidence/2026-09-22-v3-steering-v1-upload/README.md) a [ověřovací záznam](../../models/jednoduche-auticko/firmware/prvni-motor/overeni-programu.json) rozlišují jednotlivé kroky.

**Před uploadem trimu v4:** Pro upload v4 uživatel nově odpověděl „Ano“ na dotaz zahrnující odpojení servo plusu, ponechání UNO na USB a motor bez napájení. Táhlo smí zůstat připojené a před novým odpojením je hlásil připojené. Jde o nové uživatelské hlášení, nikoli přímou elektrickou kontrolu agentem. [Pinout a přesná chronologie](kontrolni-zapojeni.md); původní [SVG](kontrolni-zapojeni.svg) zachovává starší stavové popisky.

[Otevřít offline ovládání — pouze simulace](nahled-ovladani-v3.html) · [Mobilní náhled skutečného UI](nahled-ovladani-v3.png)

Mechanická návaznost je [V3 s převodovkou 25:1](../../models/auticko-silovy-prevod-25/README.md). Tato elektronická změna nemění CAD ani tiskové soubory. [Inventář](../vybaveni.md) je jediný seznam skutečně potvrzeného vybavení. Nic se nenakupovalo.

## Fyzická připravenost a následné upřesnění — 22. 9. 2026

Původ všech fyzických údajů je hlášení uživatele; uvedené fotografie vyhodnotil původní task a jeho audit. [Podrobná časová posloupnost](kontrolni-zapojeni.md#hlasova-zkouska-22-9-2026) zachovává původní neúspěšnou zkoušku, doplnění UNO GND → mínusová lišta, kontrolu obou směrů v UI při odpojeném servo plusu i pozdější opravu jiného spoje: mínusu nového zdroje z **IOREF do správného GND**. Krátké „Připravuji ovládání“ samo odpovídá přípravě relace; dřívější podezření na reset nebylo potvrzené logem.

Uživatel po opravě naměřil **6,35 V bez USB a pak stále 6,35 V s USB** mezi volným plusem servo zdroje a hnědým kontaktem serva; měření nebylo pod zátěží. Následně při odpojeném táhle, volné páčce a motoru bez napájení hlásil klidné servo a první malý pohyb na směrové tlačítko ve `v3-steering-v1`. Nejde o úplnou zkoušku krajních poloh, návratu, zatížení nebo jízdy ani důkaz příčiny všech předchozích potíží.

Nový čtyřčlánkový zdroj je podle uživatele nerozebiratelný; měnič nemá a výslovně přijal riziko přímého pokusu. **Původních 6,4 V i nynějších 6,35 V je nad uváděnými 4,8–6 V pro SG90; regulovaná 5V větev není hotová.** Přijetí rizika nepředstavuje doporučení provozního napájení ani záruku bez poškození. Starý motorový držák má podle posledního potvrzení jen tři zapojené články a čtvrtý odpojený.

**Historické potvrzení před uploadem `v3-steering-v2`:** uživatel výslovně potvrdil červený plus serva odpojený, motor bez napájení, táhlo od kol odpojené a UNO na USB. Upload v2 je dokončený a doložený výše; uživatel potom potvrdil pěkný pohyb volného serva oběma směry. Po pokynech Rovně, odpojit servo plus a USB, srovnat kola a připojit táhlo bez násilí hlásil mírné natočení kol doleva ve středu. Malý trim v3 byl následně nahraný; před jeho uploadem uživatel nově potvrdil odpojený servo plus a upload v předuploadovém stavu motor bez napájení / UNO na USB. Přesné hlášení a jeho meze jsou v [chronologii](kontrolni-zapojeni.md#hlasova-zkouska-22-9-2026).

## Historické sestavování — hlasové hlášení 20. 9. 2026

Původ evidence: **slovní potvrzení uživatele**, nikoli přímá vizuální nebo elektrická kontrola. Autíčko přinesl na stůl a chce pokračovat zapojením SG90 a nahráním V3. Tento záznam není provedení ani pokyn k uploadu: neproběhlo nové připojení USB k hostu, upload, ovládání zařízení ani pohyb serva. Připravený zdroj má SHA256 `9f7477c851898e97e7c9fd50ca632104c9214259b415a3fa9996ca6a48d8760c`; k tomuto historickému záznamu byla poslední nahraná a přijatá verze v2.

| Oblast | Potvrzené hlášení a jeho meze |
|---|---|
| Příprava | Před sestavováním potvrdil odpojení USB a přerušení bateriového napájení. To nepotvrzuje pozdější odpojení obou vodičů držáku |
| Servo | Přečetl oranžový, červený uprostřed a hnědý vodič. Potvrdil **oranžový přímo do UNO D9**, **hnědý do UNO GND**. Červený zůstal podle instrukcí volný; připojení napájení nepotvrdil |
| Mechanika a motor | Nasazení či odpojení páčky/táhla nepotvrdil. Motorové propojení se mělo zachovat, jeho aktuální stav nebyl zkontrolovaný |
| Multimetr | Nově potvrzené vlastnictví. Hlásil černou šňůru v COM a červenou ve V/Ω; přepis obsahoval i ampér, přesné označení společné zdířky není vizuálně ověřené. Před USB měřením výslovně potvrdil rozsah **20 V DC**. Pozdější návrh přepnout odpojené měření na kontinuitu a spojit hroty už nepotvrdil; dnešní poloha přepínače ani pípnutí nejsou známé |
| Bateriový držák | Uživatel uvedl články označené **1,5 V** a ptal se na napájení serva z držáku čtyř článků. Typ, stav, aktuální složení, úplné osazení, skutečné napětí a proudová rezerva nejsou ověřené; nepředpokládat historickou směs ani novou shodnou sadu |

**Powerbanka:** uživatel ji označil jako **AlzaPower Vision** (původní přepis „Vision All“); přesný model a kapacita nejsou určené. Nejprve četl 22,5 W, potom štítek USB-C1/C2: 5 V / 3 A, 9 V / 3 A, 12 V / 3 A, 15 V / 3 A a později 28 V / 5 A, 140 W max. Mezilehlé údaje pro 20 V jsou nejasné. U USB-A přečetl 5 V / 3 A, 9 V / 2 A a 10 V s nejasným proudem „2,… A“. Jde o **přečtené štítkové režimy, nikoli naměřené výstupy**. Celkový sdílený limit není potvrzený; produktové ID z těchto údajů neodvozovat.

**Dva upravované náhradní USB kabely:** uživatel chtěl místo adaptéru využít vlastní kabel; dostal pokyn stříhat vždy odpojený kabel. U prvního s červeným a černým vodičem až při pokusu o měření upřesnil USB-C na straně powerbanky. Řekl „nic mi to nehlásí“ — není zaznamenaná přesná číselná hodnota ani měření pod zátěží. Chybějící rozpoznání odběratele přes CC po úpravě zaznělo pouze jako **hypotéza**, nikoli potvrzená závada nebo poškození powerbanky; bylo doporučeno kabel odpojit. Potom potvrdil rozstřižení dalšího kabelu s velkým USB-A konektorem. Uvnitř popsal stříbrný obal (pravděpodobně stínění), zelený, červený a **dva bílé vodiče**. Napájecí dvojice není identifikovaná, žádný bílý nelze automaticky označit za GND. Připojení kabelu k servu nepotvrdil.

**Navazující hlasové hlášení k článkům:** při přípravě druhého bateriového zdroje uživatel přiznal pokus pájet přímo na póly článků 1,5 V; cín podle něj nedržel. U jednoho hlásil možné vytečení, případně zbytek tavidla/plastů; přepis je nejasný a únik není potvrzený. Dostal pokyn články dál nezahřívat a podezřelý nepoužívat. Poté opakovaně potvrdil úplné vychladnutí, uvedl, že podezřelý článek vyhodil/zlikvidoval a nahrazuje jiným. Způsob likvidace, stav dalších zahřívaných článků a složení nové sady nejsou ověřené. Na jeho výslovné přání je tento incident uzavřený pro další vedení; neopakovat otázky na teplotu ani další rady k němu. Jde pouze o uživatelské hlášení.

### Kde hovor skončil a jak navázat

**Aktualizace 23. 9.:** `v3-reverse-v1` je nahraná a potvrzená klidovou diagnostikou. Uživatel před uploadem nově potvrdil odpojené servo v dotazu zahrnujícím USB Arduina a motor bez napájení. První fyzická zkouška couvání čeká v původní úloze. Historická akceptace neutrální polohy kol na v4 se nepřenáší na nový hash. [Chronologie](kontrolni-zapojeni.md#hlasova-zkouska-22-9-2026) rozlišuje výsledky jednotlivých verzí. Následující odstavce zachovávají historický hovor z 20. 9., nikoli dnešní bod pokračování.

Poslední jasný pokyn uživatele je: **„ten zdroj napětí vyřešíme potom, pojďme teď zapojovat servo“**. Napájení serva zůstává **nevyřešené a vědomě odložené**. Dřívější plán samostatně změřit bateriový držák i identifikovat USB-A vodiče tím přestal být následujícím krokem; nic z toho neběží na pozadí. Předchozí odpojení obou přívodů držáku ani nové měření nebyly potvrzené. Znovu probíraná samostatná 5V větev USB-A pro servo a USB-C pro Arduino nebyla dokončená; napájecí vodiče ani pípnutí při zkoušce kontinuity nejsou potvrzené.

Platí dříve hlasově potvrzené **oranžový SG90 → UNO D9**, **hnědý → UNO GND**. Červený napájecí vodič má podle instrukce zůstat volný a oddělený; jeho připojení potvrzené není. Stav páčky/táhla zůstává neověřený.

**Poslední zadaný fyzický krok:** při odpojeném bateriovém napájení **motoru** a volném odděleném červeném vodiči **serva** připojit UNO R4 WiFi datovým USB k **počítači**. Uživatel splnění tohoto kroku před koncem hovoru **nepotvrdil**. Další živé vedení naváže potvrzením této připravenosti; teprve následná samostatně zadaná realizační úloha může ověřit desku a nahrát přesný připravený `v3-steering-v1`. Uživatel si nový program přeje a obecný souhlas už vyslovil, není třeba znovu zjišťovat jeho cíl. To však není potvrzení fyzické připravenosti ani provedeného uploadu. V tomto dokumentačním předání neproběhlo nové měření, připojení k PC, upload ani pohyb serva; poslední doložená nahraná a přijatá verze je nadále `hold-to-run-v2`.

## Ovládání nahrané v3-reverse-v1 — fyzická zkouška čeká

Následující ovládání je v nahrané verzi; uživatel po zkoušce obecně potvrdil funkčnost. Telefon se připojí ke stávající síti **Auticko-test** a otevře **http://192.168.4.1/**. Při startu trvá příprava přístupového bodu přibližně 10 sekund. Starou stránku po změně firmwaru obnovit.

| Ovladač | Chování |
|---|---|
| Držet pro jízdu vpřed | Při držení motor vpřed, PWM 128/255 |
| Držet pro couvání | Při držení opačná polarita motoru, stejné PWM 128/255 |
| Vpřed i couvání současně | STOP obou ovládání; pustit všechny ovladače a potom nově stisknout |
| Doleva / Doprava | Při držení zadává malou výchylku serva; samotné zatáčení motor nezapne |
| Puštění směru | Pokud není držený druhý směr, zadá se střed; držená jízda pokračuje |
| Puštění jízdy při drženém směru | Vypne se motor, řízení zůstane ve zvoleném směru |
| Rovně | Zruší požadavek zatáčení; držená jízda pokračuje. Samostatné stisknutí motor nespustí |
| Doleva i doprava současně | Povel na střed |
| Puštění všech ovladačů, opuštění stránky nebo chyba | Vypnutí motoru a povel na střed serva |

Jízda a zatáčení se ovládají dvěma prsty v libovolném pořadí. Na klávesnici fungují šipky nahoru (vpřed), dolů (couvání), vlevo a vpravo; na zaměřeném tlačítku také mezerník nebo Enter. Po chybě je potřeba ovladače pustit a stisknout znovu. Obnovení sítě samo jízdu ani zatáčení nezahájí.

Před změnou polarity software nejprve nastaví EN=0 a oba vstupy IN1/IN2 na LOW. Opačný směr je dovolen až po nejméně **250 ms skutečně vypnutého motorového výstupu**. Předčasný požadavek vrátí `HOLD_REARM` bez nové výzvy a zruší relaci. UI zobrazí „Změna směru: pusť ovladače a stiskni znovu.“; dokud nejsou uvolněné všechny evidované ovladače včetně řízení, blokuje i nové stisky. Eviduje také další kontakty stejného tlačítka a kontakty přidané během čekání na STOP nebo povinného puštění; i ty je nutné uvolnit. Teprve nový skutečný stisk může založit další relaci; pokud je stále příliš brzy, opět skončí požadavkem na puštění. Z delšího klidu stačí jediné podržení. Žádný periodický HOLD, opakování klávesy nebo uplynutí času pohon po tomto zastavení samo neobnoví. **250 ms není potvrzení fyzického zastavení motoru.**

Povel na střed není měření polohy: SG90 nemá v tomto zapojení zpětnou vazbu do Arduina. Motor při vypnutí volně dobíhá. Sdílené povolení řízení platí 500 ms od přijetí platného HOLD; kontroluje je přerušení po 5 ms. Při ztraceném STOP a jednom už odeslaném HOLD je konzervativní mez **až 1 s od zpracování puštění prohlížečem** do vypnutí motorového výstupu a zadání středu. Nový servo pulz se projeví nejpozději v následující 20ms periodě, potom teprve následuje mechanický pohyb. Skutečné časy na hardwaru nebyly měřené. Ochrana závisí na běžících přerušeních, nepokrývá zamrznutí procesoru.

## Zapojení

Motorové propojení [L293D](zapojeni-l293d.md) zůstává stejné. Nový je pouze signál SG90 na **digitálním D9** a jeho samostatná napájecí větev. Nezaměnit D9 s pinem 9 čipu L293D; pin 9 L293D zůstává nepoužité enable připojené na GND.

| Vodič / pin | Kam patří |
|---|---|
| UNO D5 | L293D pin 1 EN; odpor 10 kΩ mezi EN a GND zůstává |
| UNO D7 | L293D pin 2 IN1 |
| UNO D8 | L293D pin 7 IN2 |
| **UNO D9** | **Signál SG90**, obvykle oranžový nebo žlutý vodič; před zapojením ověřit konkrétní konektor |
| SG90 GND | Společná zem UNO, L293D, mínusu motorového zdroje a zdroje serva; obvykle hnědý nebo černý vodič |
| SG90 napájení | Samostatná **regulovaná 5V větev** přímo ze zdroje, obvykle červený vodič |
| UNO USB-C | USB napájení Arduina jako dosud |
| L293D pin 16 | 5V logika z Arduina jako dosud |
| L293D pin 8 | Plus zdroje motoru z držáku AA jako dosud; s napájením serva nespojovat |

Barva vodiče je pomůcka, ne důkaz polarity konkrétního kusu. Nepropojovat kladný pól AA, externí 5V větev serva a 5V pin Arduina. Společná je **GND**. Napájecí proud serva vést přímo ze zdroje, nikoli přes GPIO nebo regulátor Arduina. Tento princip odpovídá [návodu Arduino pro externí napájení serv](https://support.arduino.cc/hc/en-us/articles/360017053760-Troubleshoot-servo-motors). Pro zapojování odpojit všechny zdroje; pro kontrolu serva nechat motorový držák rozpojený.

### Napájení z dostupného vybavení

Původní podmíněný návrh používá jeden USB výstup powerbanky → USB-C Arduina, druhý **5V výstup → servo** a společnou zem. Následně uživatel přečetl štítkové režimy včetně 5 V / 3 A; konkrétní model, skutečný výstup, společný proudový limit a použitelná napájecí dvojice upraveného kabelu zůstávají neověřené. Úplný průběh je v [hlasovém záznamu výše](#historické-sestavování--hlasové-hlášení-20-9-2026). Nejde o hotové zapojení. Uživatel tehdy řešení zdroje výslovně odložil. Upload v1 bez napájení motoru a serva již proběhl 22. 9.; přímý pokus s novým zdrojem, opravu IOREF → GND, následných 6,35 V a historické odpojení servo plusu před uploadem v2 popisuje záznam výše; nové potvrzení pro trim v3 je uvedené výše.

Neoznačený nebo nedostupný modul MB102 není součástí návrhu. Katalog sady neprokazuje jeho vlastnictví a uživatel uvedl, že snižující měnič nemá. Přímé napájení SG90 z nového čtyřčlánkového zdroje 6,4 V bylo 22. 9. hlášené jako uskutečněný rizikový pokus po výslovném přijetí rizika uživatelem; **není doporučením pro provoz ani důkazem správného napájení**. Nový servo zdroj je oddělený od starého motorového držáku. Historická směs Ni-MH a běžných článků se nepřebírá jako doporučené ani aktuálně potvrzené napájení; nákup nových baterií ani hlášená náhrada jednoho článku nepotvrzují dnešní složení a stav celé sady.

Dostupnost odrušovacích kondenzátorů stále není potvrzená. Jejich absence nesmí být v dokumentaci zaměněná za ověřené stabilní napájení. Případné restarty, cukání nebo pokles napětí se musí při zkoušce posoudit jako hardwarový problém, ne automaticky jako chyba webu. Rezerva zdroje při rozběhu a zatížení konkrétního SG90 není změřená.

<a id="příští-zkouška-couvání--zatím-neprovedená"></a>
## Zkouška couvání — obecné potvrzení uživatele

**23. 9. 2026 — Jiří po zkoušce aktuální `v3-reverse-v1` řekl: „Hele, všechno to funguje“.** Jde o obecnou uživatelskou fyzickou akceptaci po předání postupu jízdy vpřed a couvání, nikoli samostatně doložené měření proudu, průběh změny směru nebo dlouhodobou zkoušku. Následně potvrdil „Hotovo“ po postupu úplného vypnutí: pustit ovladače, zastavit kola, vyjmout jeden článek motorového zdroje, odpojit plus servo zdroje od červeného vodiče serva, zaizolovat volný plus a odpojit USB. Jde o uživatelské potvrzení dokončení postupu, nikoli nezávislou kontrolu jednotlivých spojů.

Upload je dokončený po novém výslovném potvrzení uživatele. První fyzická zkouška couvání má nyní obecné uživatelské potvrzení funkčnosti. Servo plus je podle posledního potvrzení odpojený, motor má nadále odpojený článek a táhlo se neměnilo. Dřívější krátký pokus s 6,35 V bez regulátoru byl uživatelem přijatým rizikem; není doporučením provozního napájení ani fyzickou akceptací nové verze.

Po potvrzené přípravě a ověření skutečně nahrané verze ponechat kola nad stolem. Nejdříve zvlášť krátce ověřit vpřed a puštění, potom po pauze a novém stisku couvání a puštění. Směry nepřepínat proti běžícímu motoru; po výzvě k opakování pustit všechny ovladače. Až poté ověřit řízení a souběh dvou prstů, stále s koly ve vzduchu. Výsledek zaznamenat pro konkrétní hash, napájení a podmínky; toto je plán, žádná nová fyzická zkouška se neprovedla.

## Původní plán prvního nastavení — po ověření zapojení a napájení

Při živém vedení podávat vždy **jen jeden krok** a čekat na potvrzení. Následující seznam zachovává obecný plán prvního sestavování, nikoli záznam provedených úkonů ani aktuální pořadí zkoušky couvání uvedené výše.

1. S odpojeným napájením nechat motorový držák rozpojený. Servo nastavit nejprve **bez páčky a táhla**, aby se při prvním vystředění neopřelo o doraz.
2. Ověřit tři vodiče SG90 a napájecí větev, společnou zem a D9. Při tomto historickém nastavování byl nahraný druhý trim `v3-steering-v4`; jeho neutrální polohu kol uživatel přijal samostatně od předchozího pohybu volného serva v2. Před fyzickou zkouškou ověřit skutečně nahranou verzi a dnešní propojení.
3. Zapnout ověřené napájení Arduina a serva. **Trim v4 i současná reverse-v1 už při startu vysílají 1575 µs (v3 měl 1525 µs, v2 1500 µs): servo se může pohnout do nominálního středu ještě před otevřením stránky.** Směr ani geometrický střed tohoto kusu tím nejsou změřené.
4. Vyzkoušet samotné Doleva, puštění, Doprava a Rovně. Motor zůstává bez napájení. Ve v4 i současné reverse-v1 je při `STEER_SIGN=1` levý směr 1275 µs a pravý 1875 µs kolem středu 1575 µs; předchozí v2 měl 1200 / 1500 / 1800 µs. Předchozí v1 používal 1350 µs a 1650 µs. Ověřit, zda fyzický směr odpovídá popisu; případně změnit `STEER_SIGN` a znovu sestavit před dalším uploadem.
5. Při povelu Rovně odpojit napájení, nasadit původní jednoramennou páčku co nejblíže středové orientaci a zajistit původním šroubkem. Využít uživatelem naměřený účinný poloměr **15 mm**. Kola nastavit rovně, teprve potom spojit táhlo.
6. Opakovat malý rozsah s odpojeným pohonem a koly bez zátěže. Pokud servo tlačí do dorazu, bzučí nebo mechanismus drhne, odpojit napájení a opravit geometrii či snížit rozsah. Neukládat hodnotu 1500 µs jako fyzicky ověřený střed bez této kontroly.
7. Teprve po úspěchu ověřit společnou jízdu a řízení, oba pořadí dvou prstů, puštění každého ovladače zvlášť, ztrátu spojení a opětovné zapnutí. U zaznamenané zkoušky uvést hash programu, zdroje, podmínky a výsledek.

Předchozí v2 má `STEER_CENTER_US=1500` a `STEER_OFFSET_US=300`. První trim v3 měl střed `1525`; dřívější druhý trim v4 změnil pouze střed na `1575`, zachovává rozsah `300` a 50 Hz. Jde o rozdíly pulzu, **ne změřené úhly**; uživatelem potvrzený pohyb volného serva v2 je samostatný výsledek; neutrální polohu kol po druhém trimu v4 uživatel nyní také přijal. Nominální CAD má pracovní zatáčení kol ±25° a mechanické dorazy ±27°; plný pracovní rozsah by podle kinematiky vyžadoval přibližně +33,51° / −35,10° serva. To neopravňuje zadat neověřenému SG90 celý rozsah 0–180°. Nejprve musí sedět neutrální poloha, směr a skutečný převod pulz → poloha. Servo se nepoužívá k tlačení na mechanický doraz.

## Implementace a ověřitelné meze

- V3 zachovává motorové D5/D7/D8, 490Hz PWM a ekvivalent 128/255. Neřeší automaticky dřívější těžký rozjezd ani mechanické zasekávání V2.
- SG90 dostává 50Hz hardwarové PWM přes `PwmOut` na D9. Nepřidává se závislost na knihovně Servo.
- Ve skutečně instalovaném jádru `arduino:renesas_uno@1.6.0` je D5 = GPT0/A, D9 = GPT7/B. D8 může používat GPT7/A, zde ale zůstává obyčejným GPIO; nepřidávat na něj další PWM s jinou frekvencí. Motor a servo se inicializují před výběrem volného 5ms časovače (v této konfiguraci GPT4).
- Po startu je motor vypnutý a servo má povel na nominální střed. Při selhání inicializace nebo změny PWM se pohon nepovolí. Pokud selže periférie serva a D9 přejde na LOW, **fyzické vystředění se negarantuje**.
- Zápisy PWM při přijatém HOLD i vypnutí probíhají v krátké kritické sekci nebo v přerušení. V přerušení nejsou síťová volání, Serial, alokace ani čekání. Nový opožděný požadavek nesmí obnovit již vypršené povolení.
- Nahrané couvání používá kanonický motorový záměr −1/0/1. Předčasná změna polarity ruší sekvenci přes `HOLD_REARM`; další HOLD původního držení ani nové ARM se stejným číslem stisku ji neobnoví.
- Jedna společná relace posílá vždy úplný záměr motor + řízení. Neúplné či neplatné nové hlavičky se odmítnou; nesmějí se přeložit na starý příkaz „motor zapnout“. Starý úplný protokol v2 zůstává kompatibilní jako motor vpřed / servo střed.

Podklady kontroly z 20. 9. 2026: místní jádro 1.6.0, odpovídající [mapování pinů UNO R4 WiFi](https://github.com/arduino/ArduinoCore-renesas/blob/1.6.0/variants/UNOWIFIR4/pinmux.inc), [implementace PwmOut](https://github.com/arduino/ArduinoCore-renesas/blob/1.6.0/cores/arduino/pwm.cpp) a [aktualizace duty v Renesas FSP 4.0](https://raw.githubusercontent.com/renesas/fsp/v4.0.0/ra/fsp/src/r_gpt/r_gpt.c). [TowerPro SG90](https://towerpro.com.tw/product/sg90-7/) uvádí 4,8 V a v odpovědi výrobce rozsah 4,8–6 V, orientační proud 0,5–2 A a běžný rozsah 0–150°. Tyto údaje nejsou měřením konkrétního kusu; právě proto zůstává ověření proudové rezervy zdroje a rozsahu otevřené.

Poslední fyzicky přijatá motorová verze `hold-to-run-v2` je uložená přesně v [archivu](../../models/jednoduche-auticko/firmware/archiv-hold-to-run-v2/README.md), včetně zdroje, testů a tehdejší evidence. Pro V3 platí samostatná evidence; první hlášený malý pohyb v1 po opravě země není úplná fyzická akceptace řízení a jízdy. V2 má doložený upload, klidovou USB diagnostiku a uživatelské potvrzení pohybu volného serva oběma směry. V3 podle hlášení s připojeným táhlem ponechala mírný levý odklon. Druhý trim v4 má doložený upload, klidovou diagnostiku a uživatelskou akceptaci neutrální polohy kol; dorazy, zatížení a jízda nejsou přijaté. Nové couvání `v3-reverse-v1` má doložený upload a klidovou diagnostiku, uživatel následně obecně potvrdil funkčnost („Hele, všechno to funguje“).
