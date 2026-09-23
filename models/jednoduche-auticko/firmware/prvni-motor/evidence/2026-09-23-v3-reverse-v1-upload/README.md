# Upload v3-reverse-v1 — 23. 9. 2026 místního času

**Nahráno a pasivně ověřeno. Fyzická zkouška nové verze ještě není potvrzená.** Zdroj ani BIN se proti [ověřené offline přípravě](../2026-09-22-v3-reverse-v1/README.md) nezměnily; build ani regrese se proto neopakovaly.

Nové potvrzení přišlo z původní hlasové úlohy: otázka „Je Arduino připojené přes USB a napájení motoru i červený vodič serva odpojené?“; odpověď **„ano, servo odpojeno“**. Motor měl podle posledního potvrzení odpojený jeden článek a změna nebyla hlášená. Táhlo se neměnilo. Tyto fyzické údaje jsou uživatelské hlášení, nikoli měření agentem.

- UNO R4 WiFi, USB serial `3CDC75F1A2D4`, VID/PID `2341:1002`, `/dev/ttyACM0`; identita živě ověřena před i po uploadu. Před uploadem byl port volný, cizí proces se neukončoval.
- Zdroj SHA256 `d24a87631fd32a41685baedd7488c425a75ca6f9e300706349c61e09e79fe930`.
- BIN SHA256 `663fbe045211770308dab03aa696c69ea0b61f314b063ae9fc5bf7310c0ae19e`, **86 716 B**; nahráno **22 stran**, exit **0**, 22:09:20–22:09:27 UTC dne 22. 9. (00:09 dne 23. 9. v Praze). Neproběhlo zpětné čtení celé flash.
- Tři automatické diagnostické snapshoty **22:10:07–22:10:19 UTC** potvrdily `build=v3-reverse-v1`, `safety=1`, `drive=0`, `ENread=0 IN1=0 IN2=0`, `watchdog=0`, `steeringReady=1`, `steeringUs=neutralUs=1575`, `rangeUs=300`, nulové expirace a `leaseMs=0`; server byl připravený.
- Zařízení mělo už v prvním snapshotu **HTTP=29 / closed=29 / stopReason=1**; všechny tři počty zůstaly stejné. Čítač počítá přijatá klientská spojení před parsováním, nikoli jen platné povely. Původ dřívějších spojení není určený. Agent při diagnostice zapsal **0 sériových datových bajtů**, poslal **0 HTTP a 0 pohybových povelů**. Tvrzení o nulovém provozu celého zařízení by bylo nesprávné.
- Monitor se po čtení zavřel; následná kontrola portu nezjistila vlastníka. Diagnostika není elektrické měření PWM ani fyzický důkaz pohybu nebo středu.

Původní pomocná kontrola očekávala také HTTP=0 a tato dodatečná domněnka neplatila. Je zachovaná v [prvním výsledku](diagnostics-initial-check.json). [Konečné ověření](diagnostics-result.json) odděluje splněné požadavky na verzi, klidové výstupy, střed/rozsah a server od pozorovaného nenulového provozu. Upload ani aktivní sondování se kvůli tomu neopakovaly.

[Potvrzení a preflight](preflight.json) · [Upload](upload-result.json) · [Log uploadu](upload.txt) · [Pasivní výpisy](serial-after.txt) · [Výsledek diagnostiky](diagnostics-result.json) · [Předchozí ověřovací záznam](verification-before-upload.json).

**Fyzická zkouška couvání čeká na uživatele v původní úloze.** Přijetí neutrální polohy kol na v4 zůstává historickým samostatným výsledkem. Nynější verze zachovává 1575 ±300 µs / 50 Hz; nové couvání používá stejné PWM 128/255 a ochranu změny směru. Předchozí 6,35V zdroj serva byl uživatelem vědomě přijatý pro krátké pokusy bez měniče, nikoli doporučené trvalé napájení.
