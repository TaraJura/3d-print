# v3-steering-v4 — druhý trim středu, 22. 9. 2026

Uživatel na předchozí v3 s připojeným táhlem a povelem Rovně hlásil téměř neznatelnou změnu a kola stále mírně doleva. Nový požadovaný krok je **1525 → 1575 µs (+50 ve směru Doprava)**; **žádná meziverze 1550 nevznikla**. Zachováno ±300 µs a 50 Hz, povely **1275 / 1575 / 1875 µs**. [Chronologie fyzických hlášení](../../../../../../elektronika/auticko/kontrolni-zapojeni.md#hlasova-zkouska-22-9-2026) odlišuje funkční volné servo v2, první nedostatečný trim v3 a tento dosud nevyhodnocený druhý trim.

## Kontrola a překlad

[Úzký diff a meze](static-review.json) i nezávislé review potvrdily pouze BUILD_ID a střed; motor, směrová logika, WiFi, bezpečnostní řízení a všechny ostatní bajty sketche jsou zachované. Right=+1 a STEER_SIGN=1, duty6,375/7,875/9,375 %. To jsou nominální povely, nikoli měřené úhly či polohová zpětná vazba.

- Zdroj SHA256 `0ee42b5512b97240a9d466e833e46a4360a3d4b5a7d112ae647146946781126e`.
- BIN SHA256 `cf654176b45a0880b17133fe6d0b54f44d77e2e4ddcf530dcc0910d7eb841bae`, **84 948 B**.
- ELF SHA256 `63f8f315da47578c1a5bc48c86a1812b96655de4fa8b963844a8000b117bf8fe`.
- [Překlad](arduino-compile.txt), Arduino CLI1.5.1/core1.6.0/UNO R4 WiFi: **exit0, 84 940 B flash / 9 864 B RAM**. Varování Arduino jádra/knihoven.
- Na výslovné zadání se **neopakovala úplná browserová/síťová regrese** stejného funkčního kódu. Poslední úplný běh patří [v3](../2026-09-22-v3-steering-v3/host-and-browser-tests.txt). Existující očekávání pulzů aktualizována; timeouty nezměněny, žádné nové testy.
- Zachován [přesný předchozí zdroj v3](previous-v3.ino), jeho build a veškerá předchozí evidence; žádný další rozsáhlý archiv nevznikl.

## Upload a pasivní ověření

[Nové potvrzení před uploadem](preflight.json): uživatel po poslední fyzické zkoušce odpověděl „Ano“ na pokyn odpojit červený servo+, ponechat UNO na USB a motor bez napájení. Táhlo mohlo zůstat připojené. Jde o uživatelské hlášení, nikoli elektrické měření agentem.

[USB před](board-before.json) i [po](board-after.json): UNO R4 WiFi, VID:PID2341:1002, serial`3CDC75F1A2D4`, `/dev/ttyACM0`; port neměl jiného vlastníka. [Upload přesného BIN](upload-result.json) dokončen **84 948 B / 21 stran / exit0**, se standardním bootloaderovým přechodem a resetem, bez zpětného čtení celé flash.

[Tři pasivní snapshoty](serial-after.txt), 21:42:01–21:42:13 UTC, na115200baud sDTR zapnutým [prošly kontrolami](diagnostics-result.json): `build=v3-steering-v4`, `steeringReady=1 steeringUs=1575 neutralUs=1575 rangeUs=300`, `safety=1 drive=0 ENread=0 IN1=0 IN2=0 watchdog=0`, `leaseMs=0`, běžící server a `HTTP=0 closed=0`.

Monitor uzavřen; žádná sériová data, HTTP ani pohybové povely nebyly poslané. Fyzické srovnání druhého trimu, dorazy, zatížení a jízda nejsou tímto potvrzené. [Příprava před uploadem](verification-before-upload.json) a [aktuální souhrn](../../overeni-programu.json) přesně rozlišují fáze.
