# v3-steering-v3 — první trim středu, 22. 9. 2026

Na Jiřího žádost posunut střed **1500 → 1525 µs směrem povelu Doprava**. Ověřený parser používá right=+1 a STEER_SIGN=1. Rozsah zůstává **±300 µs při 50 Hz**, tedy **1225 / 1525 / 1825 µs**. Motor, WiFi, protokol a bezpečnostní logika beze změny. Jde o první nenaměřený kalibrační krok; neprokazuje vyrovnaná kola ani přesný úhel.

Uživatel před úpravou výslovně potvrdil, že volné servo na předchozí v2 funguje doprava i doleva. Po práci na připojení táhla hlásil kola v neutrálu mírně doleva. Tato hlášení neznamenají zkoušku dorazů, zatíženého řízení ani jízdy. [Fyzická chronologie](../../../../../../elektronika/auticko/kontrolni-zapojeni.md#hlasova-zkouska-22-9-2026).

## Překlad a kontroly

- Finální zdroj SHA256 `0e56dfc88e022d18fcf4b8d33e511c5f99cc0671d2a23572686be4324a19dbb3`.
- BIN SHA256 `de8a2cec4fdbcb5964f5de09e3f6ffff767a263dd92e09b27f684d8a51e52dc0`, **84 948 B**.
- ELF SHA256 `d3ad5de650f309ace411eef680a0e86130f5b2d1b83d9032a97d3780c565ec89`.
- Arduino CLI1.5.1, Renesas UNO core1.6.0, `arduino:renesas_uno:unor4wifi`.
- [Překlad finálního zdroje](arduino-compile.txt): exit0, **84 940 B flash / 9 864 B RAM**, varování Arduino jádra/knihoven.
- [Existující regrese](host-and-browser-tests.txt): **109 parser + 109 HTTP, 34 stavových skupin, 14 IRQ, 33 JS a 14 Chromium**, exit0. Změnila se pouze očekávání servových pulzů; timeouty testů zachované, nové scénáře nepřibyly.
- Po testech byl opraven pouze starý komentář o1500µs a finální zdroj znovu přeložen. [Přesný testovaný vstup](tested-source.ino) a [doklad jediné komentářové změny](comment-only-followup.json) rozlišují testovaný a finální hash; výkonný kód je shodný. Testy se kvůli komentáři neopakovaly.
- Nezávislé review potvrdilo směr trimu, zachování±300/50Hz a úzký diff. [Čtyři předchozí soubory v2](previous-v2/) zachovávají zdroj, měněné testy a tehdejší souhrn; staré uploadové evidence se nepřepisovaly.

## Skutečné nahrání a klidový stav

[Předuploadové potvrzení](preflight.json): uživatel na otázku obsahující odpojené servo+, motor bez napájení a UNO na USB odpověděl „Červenej vodič serva odpojen. Ano, potvrzuji, můžeš to nahrát.“ Táhlo mohlo zůstat nasazené. Jde o hlášení uživatele, nikoli měření agentem.

[USB před](board-before.json) a [USB po](board-after.json) potvrzují UNO R4 WiFi `2341:1002`, serial `3CDC75F1A2D4`, `/dev/ttyACM0`; port před operacemi neměl vlastníka. [Upload](upload-result.json) přesného BIN skončil **84 948 B / 21 stran / exit0**, včetně běžného bootloaderového přechodu a resetu. Celá flash se zpětně nečetla.

[Tři pasivní snapshoty](serial-after.txt) na115200baud sDTR zapnutým, **21:36:23–21:36:34 UTC**, prošly [kontrolami](diagnostics-result.json): `build=v3-steering-v3 safety=1 drive=0 ENread=0 IN1=0 IN2=0 watchdog=0`, `steeringReady=1 steeringUs=1525 neutralUs=1525 rangeUs=300`, `leaseMs=0`, běžící server a `HTTP=0 closed=0`.

Monitor je uzavřený. Žádná sériová data, HTTP ani pohybové povely nebyly poslané; fyzická zkouška trimu a elektrické měření pulzů neproběhly. [Předuploadový záznam](verification-before-upload.json) zůstává historickým bodem přípravy, [aktuální souhrn](../../overeni-programu.json) uvádí skutečně provedený upload. Mechanické vyrovnání musí potvrdit uživatel.
