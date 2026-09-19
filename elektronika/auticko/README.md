# Elektronika autíčka

První přibližně sekundový rozběh skutečného motoru z telefonu přes UNO R4 WiFi a ST L293D uživatel potvrdil. Následné ovládání při držení v1 bylo přerušované. **Oprava `hold-to-run-v2` je otestovaná a nahraná**; návrat k pulzu uživatel odvolal před uploadem.

## Aktuální stav k 19. 9. 2026

- Požadované chování: souvislé držení udržuje běh, puštění zastaví. Nový stisk po chybě obnoví relaci bez ručního reloadu; nikdy automatické rozjetí.
- V2: 80 504 B flash / 9 792 B RAM; upload 80 512 B, 20 stran, exit 0. USB ověřilo v2 a vypnuté výstupy. Testy i skutečný upload popisuje [firmware](../../models/jednoduche-auticko/firmware/prvni-motor/README.md). Po návratu uživatel obnovil stránku a potvrdil funkční držení, puštění a nový stisk („Jo, funguje to, perfektní“). Fyzická akceptace tohoto základního ovládání je potvrzená uživatelským hlášením; časování a chování při všech síťových poruchách nejsou fyzicky změřené.
- Zapojení a PWM se nemění. Samostatný časovač vypne běh po 500 ms bez platného HOLD; při ztraceném STOP a jednom již odeslaném HOLD je konzervativní hranice až 1 s od puštění. Motor volně dobíhá.
- Neoznačený motor, jeho proud a napětí při rozběhu nejsou změřené. Těžký rozjezd existoval již na starém pulzním programu. [Historie potíží](potize-po-montazi.md) není uzavřená jako fyzicky vyřešená.
- Horní plošinu uživatel vytiskl a nasadil; dosed, vůle a nosnost neověřené. Nářadí, nové baterie a silikonový olej jsou v [inventáři](../vybaveni.md), jejich použití se neodvozuje z nákupu.

## Historie verze při držení tlačítka

Následující popis a kontroly patří dříve nahrané verzi `hold-to-run-v1` (`46cee7f5…`), nikoli nové v2. Po uvolnění, zrušeném dotyku, ztrátě focusu, skrytí stránky nebo offline události prohlížeč ukončuje držení a posílá STOP. Při ztraceném STOP či čekání Wi-Fi hlídá vypnutí samostatné přerušení časovače každých 5 ms: přibližně po 0,5 s od poslední platné výzvy serveru. Skutečné fyzické časování nebylo měřené a tato ochrana neřeší zamrznutí procesoru či dlouho zakázaná přerušení. Po vypršení povolení nebo obnovení spojení se pohon sám neobnoví; je nutný nový stisk.

Překlad má **78 808 B flash / 9 068 B RAM**, úspěšný upload **78 816 B / 20 stran**. Prošlo **82 případů parseru + 82 celého loop**, **19 skupin protokolu, zotavení a selhání**, zkoušky přerušení při **7 blokujících operacích** a **19 scénářů skutečného JavaScriptu v Node**. Jde o hostové simulace. Uživatel nový režim nejprve hodnotil příznivě, nyní ale hlásí neúspěšný rozjezd i s koly ve vzduchu. Těžký rozjezd podle jeho upřesnění existoval už na starém programu; příčina ani regrese nové verze nejsou prokázané. [Návod k aktuálnímu firmwaru](../../models/jednoduche-auticko/firmware/prvni-motor/README.md) a [úplný záznam nahrání](diagnostika-webu.md#historický-upload--ovládání-při-držení-v1) rozlišují rozsah ověření.

## Dokumentace

- **[Aktuální potíže po montáži](potize-po-montazi.md)** — nepravidelný rozjezd, neobvyklý zvuk, použití silikonového oleje a omezení sériové diagnostiky.

- [Zapojení L293D](zapojeni-l293d.md) — piny, napájení a omezení dosavadní zkoušky.
- [První stolní zkouška](prvni-stolni-test.md) — hlášený motorový výsledek, fotografie a opravy během sestavování.
- [Diagnostika a oprava webu](diagnostika-webu.md) — historie Wi-Fi 255, recovery a navazující upload ovládání při držení.
- [Elektronika a historie zprovoznění](elektronika.md) — součástky, USB, původní požadavky a software.
- [Firmware a jeho ověření](../../models/jednoduche-auticko/firmware/prvni-motor/README.md) — zdroj zatím zůstává u modelu.
- [Vybavení](../vybaveni.md), [snímatelná plošina](../../models/jednoduche-auticko/strecha.md) a [deník tisků](../../docs/denik-tisku.md).

Při dalším sestavování postupovat po jednom konkrétním kroku. Zachovat určení řídicích pinů D5 → pin 1, D7 → pin 2 a uživatelem potvrzené propojení D8 → pin 7; barva vodiče nenahrazuje určení pinu. Nákup páječky ani baterií není potvrzením jejich použití.

## Nová mechanická konstrukce

[Autíčko s převodovkou 12:1](../../models/auticko-s-prevodovkou/README.md) je dokončený samostatný model s užitnou elektronickou plochou 170 × 60 mm. [Tiskový ZIP](../../models/auticko-s-prevodovkou/tiskovy-balicek.zip) obsahuje 20 kusů, každý přiložený STL tisknout jednou. Kontroly CAD, exportů a montážních vůlí prošly; fyzický tisk a montáž teprve proběhnou. Piny, výkon PWM a stávající elektronika se kvůli němu nemění. Dva vnější záběry mění výsledný směr oproti původnímu jednomu záběru; při montáži ověřit směr a podle potřeby s odpojeným napájením zaměnit dva motorové vodiče. Převodová redukce není důkazem odstranění neznámého elektrického či mechanického problému.
