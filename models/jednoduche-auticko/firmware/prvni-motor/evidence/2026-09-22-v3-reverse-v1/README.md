# Offline příprava v3-reverse-v1 — 22.–23. 9. 2026

**Připravené a ověřené, dosud nenahrané.** V Arduinu je podle poslední doložené evidence stále `v3-steering-v4`; jeho uživatelské přijetí neutrální polohy kol se nepřenáší na nový hash. Během přípravy couvání se neotevíralo USB/sériové zařízení, neprováděla se enumerace desky, HTTP k Arduinu ani pohyb.

- Zdroj SHA256 `d24a87631fd32a41685baedd7488c425a75ca6f9e300706349c61e09e79fe930`.
- BIN SHA256 `663fbe045211770308dab03aa696c69ea0b61f314b063ae9fc5bf7310c0ae19e`; 86 716 B.
- Arduino UNO R4 WiFi, `arduino:renesas_uno:unor4wifi`, core 1.6.0, CLI 1.5.1. Překlad exit 0: 86 708 B flash / 9 868 B RAM. Varování jsou v jádru/knihovnách, žádné na řádku sketche.
- Úplný běh exit 0: 120 parserových + 120 HTTP případů, 42 hostových scénářů, 21 blokujících zkoušek, 46 vložených JS scénářů a 23 skutečných Chromium HTTP scénářů. Hardware je ve všech těchto testech nahrazený.
- Nezávislá revize finálního zdroje bez dalšího nálezu. Nalezená chyba evidence odmítnutých kontaktů byla opravena a ověřena v mocku i nativním CDP dotyku na disabled tlačítku při čekajícím STOP.

Couvání má samostatné české tlačítko a ArrowDown, opačné IN1/IN2 a stejné PWM 128/255. Servo zůstává 1275/1575/1875 µs při 50 Hz a při couvání se neobrací. Před změnou polarity se vypne EN a oba vstupy; protější směr vyžaduje nejméně 250 ms od vypnutí. Předčasný povel vrací `HOLD_REARM` bez nonce a ruší celou sekvenci. Ani čas, periodic HOLD, retry či starý ARM ji neoživí; je nutné pustit všechny kontakty a nově stisknout. 250 ms je softwarově hlídaný interval, nikoli elektrické měření nebo důkaz mechanického zastavení.

[Build](compile-result.json) · [Log překladu](compile.log) · [Výsledky testů](test-result.json) · [Úplný testovací log](host-and-browser-tests.txt) · [Nezávislá revize](independent-review.json) · [Aktuální přehled](../../overeni-programu.json). Dva malé soubory [původní zdroj v4](previous-uploaded-v4.ino) a [původní ověřovací záznam](previous-verification-v4.json) zachovávají bod před změnou; další rozsáhlý archiv se nevytvářel. Starší evidence a archiv v1 zůstaly bajtově beze změny.

Další krok řídí původní hlasová úloha po **novém výslovném potvrzení hardwarové připravenosti**. Pak teprve upload přesného BIN a samostatná diagnostika; první fyzická zkouška s koly nad stolem, zvlášť vpřed/vzad a puštění, s pauzou a novým stiskem. Žádný takový krok v této přípravě neproběhl. Poslední odpojení servo plusu nebylo potvrzené.
