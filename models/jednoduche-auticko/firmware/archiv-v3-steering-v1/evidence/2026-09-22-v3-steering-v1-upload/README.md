# Upload V3 a klidová diagnostika — 22. 9. 2026

**`v3-steering-v1` je nahraný do UNO R4 WiFi a běžící verze je potvrzená USB diagnostikou. Fyzická zkouška pohonu ani serva neproběhla.**

## Přesná verze a zařízení

- Zdroj `prvni-motor.ino`: SHA256 `9f7477c851898e97e7c9fd50ca632104c9214259b415a3fa9996ca6a48d8760c`; shodný ve worktree i kanonickém checkoutu.
- Nahraný BIN: SHA256 `15cd31e1f12aa6f19edcf755ddfd930c05b9e571ff671d6a4faefd02c0b9b6b6`, 84 916 B. ELF: SHA256 `db86354a09207b838d3b9e1a87e0daafd6f33c19d30f0bf356f211bdae93bb93`.
- Použit původní build z 20. 9., jehož BIN i ELF přesně odpovídají tehdejší evidenci. Překlad 84 908 B flash / 9 864 B RAM; žádný nový build ani opakování regresních testů. Velikost uploadovaného BIN se liší od obsazení flash hlášeného překladačem.
- Arduino CLI 1.5.1, jádro `arduino:renesas_uno@1.6.0`, FQBN `arduino:renesas_uno:unor4wifi`.
- USB VID:PID `2341:1002`, serial `3CDC75F1A2D4`, `/dev/ttyACM0`; stejná identita před uploadem a po něm.

[Předběžná kontrola](preflight.json), [USB před](board-before.json), [USB po](board-after.json). Původní artefakty z kanonického projektu byly před uploadem zkopírované do ignorované cache pracovního worktree a znovu ověřené hashem; zdroj nebyl změněný.

## Výsledek uploadu a diagnostiky

[Upload](upload.txt) skončil **exit 0, 84 916 B / 21 stran**. [Strojový záznam](upload-result.json) obsahuje přesný příkaz a UTC časy. Standardní upload provedl 1200baud přechod do bootloaderu a závěrečný reset. Nepoužilo se zpětné přečtení celé flash; úspěch dokládá dokončení uploaderu a běžící verze v následné diagnostice.

[Pasivní monitor po uploadu](serial-after.txt) na 115200 baud s povoleným DTR zachytil tři úplné snapshoty v časech 19:48:23–19:48:33 UTC (21:48:23–21:48:33 Europe/Prague):

```text
build=v3-steering-v1 safety=1 drive=0 ENread=0 IN1=0 IN2=0 watchdog=0
steeringReady=1 steeringUs=1500 neutralUs=1500 rangeUs=150
armExpired=0 runExpired=0 stopReason=0 leaseMs=0
boot=server-started fw=0.4.1 ip=192.168.4.1
ready=1 server=1 HTTP=0 closed=0
```

[Vyhodnocení diagnostiky](diagnostics-result.json): všechny kontroly prošly. `fw=0.4.1` je verze Wi-Fi modemu; verze sketche je `build=v3-steering-v1`. `1500 µs` je hlášený nominální povel, nikoli změřený pulz nebo poloha serva. GPIO výpis není měření proudu motoru.

Monitor neposlal žádná sériová data, ani znak `?`; nevznikl HTTP požadavek nebo testovací povel pro jízdu či zatáčení. Sériový port byl po čtení uzavřený. [Předuploadové pasivní čtení](serial-before.txt) mělo vypnuté DTR a nepřineslo žádný výpis, proto nepotvrzuje tehdejší běžící verzi. V2 je doložená historickou evidencí.

## Fyzické podmínky a další návaznost

Původ fyzických údajů: hlasové hlášení uživatele předané původním taskem `01a0caa4-9807-78f0-9152-893a808ca99a`, nikoli vizuální či elektrická kontrola agentem. Před uploadem uživatel potvrdil USB do počítače, vyjmutí jednoho článku z motorového držáku a nepřipojený druhý zdroj; servo zůstalo podle jeho hlášení nenapájené. Běžné startovní servo PWM připraveného programu bylo očekávané.

Nový odpojený držák čtyř baterií má podle uživatelského měření **6,4 V**; chemie a měření pod zátěží nejsou potvrzené. Nepoužívá se přímo pro SG90. Samostatná regulovaná 5V větev dosud není fyzicky hotová.

Po uploadu uživatel nejprve upřesnil, že zapojení nemá připojené a chce vidět návrh. Koordinátor ukázal schéma s dosud nehotovou regulovanou 5V větví. V navazujícím hlasovém vedení uživatel nyní výslovně potvrdil **oranžový SG90 do UNO D9, následně hnědý do UNO GND a červený ponechaný odpojený**. Jde o nové uživatelské hlášení z 22. 9., nikoli přímé vizuální nebo elektrické ověření.

Následný dotaz na snížení měřených 6,4 V na 5 V a zjištění dostupného napájecího modulu řeší původní hlasový task. Regulované napájení není hotové; agent kvůli tomuto doplnění neotevíral USB ani neposílal pohybové povely. Tento realizační krok neověřuje páčku, táhlo, směr, střed, proud, sílu řízení ani společnou jízdu.

## Historie a návrat

[Záznam před uploadem](verification-before-upload.json) je neměnná kopie původního `overeni-programu.json`; jeho `hardware_uploaded=false` patří přípravě z 20. 9. Aktuální stav je v [souhrnném záznamu](../../overeni-programu.json). Staré testovací manifesty se nepřepisovaly.

Přesný [archiv v2](../../../archiv-hold-to-run-v2/README.md) zůstává zachovaný, včetně 26 souborů ověřených manifestem a zdroje SHA256 `1760730b716a6fb281ed900400d533eaac17d96c9b779a6c91e2e99502d69110`. Návrat by vyžadoval samostatně zadaný upload tohoto zdroje; nyní se neprováděl. Poslední uživatelská fyzická akceptace patří v2.

Při tomto kroku se neměnil firmware, piny, chování, testy, CAD ani tiskové modely; bez commitu a push. Evidence vznikla v `/home/novakj/.codex/worktrees/e339/3d-print`. Přenos úzkých dokumentačních změn do `/home/novakj/3d-print` je doložen samostatným `sync-result.json` po porovnání s původním obsahem.
