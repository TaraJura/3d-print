# v3-steering-v2 — dvojnásobná výchylka, 22. 9. 2026

Na Jiřího žádost změněna pouze výchylka z ±150 na **±300 µs** a identifikace buildu: **1200 / 1500 / 1800 µs, 50 Hz**, stejný střed a směrová logika. Motor, síť a bezpečnostní logika se nemění. Délky pulzů nejsou měřené mechanické úhly.

## Identita a kontroly

- Zdroj SHA256 `fcefad5f61f703e3294ac1464206d1022e72fcf85fc7acea3f634947d1b8a5b6`.
- BIN SHA256 `a015d71e247945f736a7966f95ef7d5980a644abacebab28e493f74620a22591`, 84948 B.
- ELF SHA256 `ecfa0b0362fcf171934d5ead24c70e55b8c1a1f10ee7055d01b79f696bcf67e8`.
- Arduino CLI 1.5.1, Renesas UNO core 1.6.0, `arduino:renesas_uno:unor4wifi`.
- [Překlad](arduino-compile.txt): exit 0, **84 940 B flash / 9 864 B RAM**. Varování jádra/knihoven, žádná diagnostika u řádku aktuálního sketche.
- [Existující regrese](host-and-browser-tests.txt): **109 parser + 109 HTTP, 34 stavových skupin, 14 IRQ, 33 JS, 14 Chromium**. Jen očekávání krajních pulzů byla upravena; nové testy nepřibyly. Hostové testy pracují s náhradami hardwaru a lokálním HTTP, nikoli s deskou.
- Nezávislé review potvrdilo úzký diff a beze změn všech 40 souborů [archivu v1](../../../archiv-v3-steering-v1/archiv-manifest.json), včetně původních manifestů. Historická evidence se nepřepisovala.

## Upload a pasivní diagnostika

[Předběžná kontrola](preflight.json) zachycuje výslovné potvrzení uživatele předané původním taskem: červený servo+ odpojen, motor bez napájení, táhlo odpojeno a UNO na USB. Není to elektrické měření agentem. [USB před](board-before.json) a [USB po](board-after.json): UNO R4 WiFi, VID:PID `2341:1002`, serial `3CDC75F1A2D4`, `/dev/ttyACM0`; port před operací neměl vlastníka.

[Upload](upload-result.json) přesného ověřeného BIN skončil **exit 0, 84 948 B / 21 stran**. [Úplný výpis](upload.txt) zachycuje standardní bootloaderový přechod a reset. Celá flash se zpětně nečetla.

[Pasivní diagnostika](serial-after.txt), 115200 baud a DTR zapnuté, zachytila **tři úplné snapshoty**, všechny [kontroly prošly](diagnostics-result.json):

- `build=v3-steering-v2 safety=1 drive=0 ENread=0 IN1=0 IN2=0 watchdog=0`
- `steeringReady=1 steeringUs=1500 neutralUs=1500 rangeUs=300`
- `armExpired=0 runExpired=0 stopReason=0 leaseMs=0`
- `boot=server-started fw=0.4.1 ip=192.168.4.1`, `ready=1 server=1 HTTP=0 closed=0`.

Monitor neposlal žádná sériová data, znak `?`, HTTP ani pohybový povel a je uzavřený. Úspěšný upload a hlášený klid nejsou elektrickým měřením pulzů ani fyzickou zkouškou větší výchylky. Tu uživatel dosud nepotvrdil.

## Fyzická historie a aktuální záznam

První malý pohyb po opravě servo mínusu z IOREF na GND se týká **předchozí v1**; nepřenáší se na nový hash. [Přesná chronologie, měření 6,35 V a přijaté riziko krátkého pokusu](../../../../../../elektronika/auticko/kontrolni-zapojeni.md#hlasova-zkouska-22-9-2026) rozlišuje hlášení, fotografie a nezměřené hodnoty. [Záznam před uploadem](verification-before-upload.json) zůstává historickým bodem přípravy; [aktuální souhrn](../../overeni-programu.json) obsahuje skutečně provedený upload.
