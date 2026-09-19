# Potíže s rozjezdem — 19. 9. 2026

**Aktuálně je v2 dokončená a nahraná; uživatel po návratu potvrdil funkční držení, puštění a nový stisk.** Následující záznam zachovává potíže a diagnostiku před touto akceptací. Uživatel výslovně odvolal návrat k sekundovému pulzu ještě před jeho uploadem. Příčina původního těžkého rozjezdu nebyla určená: první hlášení v této etapě přišlo po nasazení střechy a nahrání v1, ale uživatel upřesnil, že těžký rozjezd měl už na starém pulzním programu.

Časová osa podle upřesnění uživatele:

1. Těžký rozjezd se objevoval už se starým sekundovým programem.
2. Nový režim při držení tlačítka zpočátku vnímal jako perfektně funkční.
3. Následně hlásil bzučení / divný zvuk a jen občasné rozjetí.
4. V této etapě zkusil kola ve vzduchu a hlásí, že se autíčko nerozjede ani tak.

Počáteční příznivé hodnocení nového režimu je uživatelská zkušenost, nikoli změřená odezva nebo systematická zkouška STOP a timeoutu. Tento tehdejší pokus byl neúspěšný. **Zvednutí kol samo nevylučuje mechanické odpory soukolí a uložení, elektrické napájení, kontakty ani problém řízení.** Předchozí úspěšný sekundový stolní test patří staršímu programu a jiným podmínkám. [Aktuální firmware](../../models/jednoduche-auticko/firmware/prvni-motor/README.md), [jeho nahrání a testy](diagnostika-webu.md#historický-upload--ovládání-při-držení-v1) a [mechanický model](../../models/jednoduche-auticko/README.md) zůstávají oddělenými záznamy.

## Co uživatel potvrdil

- [Střecha](../../models/jednoduche-auticko/strecha.md) je vytištěná a uživatel ji nasadil. Tím nejsou potvrzené správný dosed, provozní vůle, nosnost ani volný chod sestavy pod zatížením.
- Má **silikonový olej** a namazal jím hřídelky se záměrem snížit odpor. Podle jeho hlášení to **moc nepomohlo**. Výrobek, složení, množství a přesná místa aplikace nejsou známé; odpor ani přínos nebyly změřené. Použití oleje nevylučuje mechanickou příčinu. Vlastnictví a použití jsou doplněné do [inventáře](../vybaveni.md).
- Před opravou v2 po fázi nepravidelného rozjezdu a neobvyklého zvuku uživatel hlásil neúspěšný rozjezd i s koly ve vzduchu. Není doloženo, kde zvuk vznikal nebo zda se při jednotlivých neúspěšných pokusech točil samotný motor. Následné pozitivní hlášení v2 je zaznamenané na konci této časové osy.

## Průběžná USB diagnostika — uložené čtení 13:20:32–13:21:02

Při diagnostice se pouze četl sériový výpis; agent nevyvolal pohon ani nenahrál nový firmware. Uložená evidence: [30sekundový sériový záznam](../../models/jednoduche-auticko/firmware/prvni-motor/evidence/2026-09-19-hold-to-run/serial-symptom.txt). Čas je místní pro Europe/Prague.

| Údaj ve výpisu | Pozorování |
|---|---|
| `watchdog` | Zvýšení z 4 na 5 |
| HTTP / closed | Zvýšení z 35 / 35 na 36 / 36 |
| `drive`, `safety` | Ve všech úplných snapshotech `drive=0`, `safety=1` |
| ENread / IN1 / IN2 | Ve všech úplných snapshotech 0 / 0 / 0 |
| Síť | `ready=1`, `server=1`, stav Wi-Fi 8 |
| Uptime prvního a posledního snapshotu | 206 011 → 231 038 ms; v záznamu nebyl pozorován reset ani chybný stav Wi-Fi |

**Čítač zahrnuje vypršení povolení ve stavech ARMED i RUNNING. Hodnota 4 ani její nárůst na 5 proto samy neznamenají čtyři či pět vypnutí běžícího motoru.** Snapshot s `drive=0` ukazuje klidový stav v daném okamžiku, nikoli celý průběh mezi snímky. Výpis nezaznamenává stáří každého potvrzení držení ani konkrétní důvod ukončení; samotný čítač příčinu obtíží neurčuje.

### Závěr odvozený z logu a zdrojového kódu

Mezi snapshoty v uptime **221 025 ms** (`IDLE`, HTTP 35 / closed 35, watchdog 4) a **226 033 ms** (`IDLE`, HTTP 36 / closed 36, watchdog 5) přibyl jediný HTTP požadavek. Podle kontroly kódu mohl jediný požadavek ze stavu IDLE vést k tomuto zvýšení čítače úspěšným ARM; přechod do RUNNING by potřeboval ještě další HOLD požadavek. **Tato konkrétní událost tedy odpovídá expiraci ARMED bez navazujícího HOLD, nikoli vypnutí běžícího motoru.**

Jde o odvození z čítačů, stavů a zdrojového kódu, potvrzené nezávislým zdrojovým review; není to přímý záznam obsahu HTTP požadavku. Není známo, zda telefon HOLD vůbec odeslal, nebo zda zůstal čekat v síti. Souvislost této události s uživatelem hlášeným zvukem a nepravidelným rozjezdem není prokázaná. Tento závěr také nevysvětluje všechny předchozí hodnoty čítače.

## Druhé čtení USB 13:25:10–13:25:54

Při rozšířeném čtení se posílal jen diagnostický znak `?` přibližně každých 1,1 s; žádné motorové příkazy, upload ani reset. Evidence: [sériový záznam po hlášení zkoušky s koly ve vzduchu](../../models/jednoduche-auticko/firmware/prvni-motor/evidence/2026-09-19-hold-to-run/serial-unloaded.txt).

Po celou zachycenou dobu zůstalo HTTP 6 / closed 6, `watchdog=2`, `drive=0`, `safety=1`, ENread/IN1/IN2 na nule, Wi-Fi 8 a server i ready zapnuté. **Nebyl zaznamenán žádný nový HTTP požadavek.** Tento úsek proto neukazuje reakci na nový přijatý povel k jízdě a sám nerozlišuje problém prohlížeče od síťového čekání nebo fyzického problému pohonu.

Uptime byl **138 183 → 182 156 ms**, tedy nižší než v prvním okně. Z toho plyne restart mezi oběma okny; v tomto čtení jej agent nevyvolal a jeho příčina není známá. Čítače obou oken patří různým běhům programu, proto je nelze spojovat do jedné nepřerušené řady.

V této etapě byl jako další údaj navržen text a stav tlačítka v telefonu. Tento dotaz už není čekajícím krokem: následná hlášení a následná změna zadání jsou níže. Zkoušku s koly ve vzduchu není potřeba opakovaně vyžadovat.

## Dosud neznámé

- Přesný průběh neúspěšné zkoušky s koly ve vzduchu: fyzické veličiny a samostatný chod motoru bez mechanického převodu nebyly doložené.
- Skutečné mechanické odpory, kontakt střechy či rozpěrek s pohyblivými díly, záběr soukolí, přenos momentu a zatížení.
- Aktuální články v držáku, napětí při rozběhu, proud motoru a spolehlivost spojů. Nákup nových baterií ani páječky nepotvrzuje jejich použití.
- Průběh a latence konkrétního držení tlačítka, chování samotného motoru a časová souvislost potíží s expirací povolení.

Příčinu ani úspěšné vyřešení zatím neuzavírat. Výše uvedená čtení zachycují tehdejší průběh; pozdější uživatelské změny zadání jsou zaznamenané na konci. Staré telefonní dotazy už další postup neblokují.

## Ohraničené sledování dalšího obnovení stránky

Na navazující pokyn se četlo ještě nejvýše **120 sekund**, přibližně **13:28:01–13:29:59**. Použitý byl pouze existující nemotorový diagnostický znak `?`, bez resetu, dalšího uploadu nebo příkazu k pohybu. [Celý výpis](../../models/jednoduche-auticko/firmware/prvni-motor/evidence/2026-09-19-hold-to-run/serial-refresh.txt). Monitor byl po limitu ukončen.

Po celou dobu zůstaly HTTP i closed na **6**, watchdog na **2**, drive **0**, safety **1**, čtené EN/IN1/IN2 **LOW**, server připravený a Wi-Fi ve stavu **8**. Uptime plynule vzrostl **309 080 → 427 436 ms**. **V tomto okně se nepodařilo zachytit žádné nové načtení stránky ani povel z telefonu.** Uživatel následně uvedl, že byl během sledování pryč; nepřítomnost HTTP při monitorování tak není důkazem selhání ovládání při aktivním stisku. Není z toho možné odvodit zapnutý motor pod zátěží nebo selhání jeho napájení.

## Reprodukovaná citlivost časování — simulace

Další hostový experiment vykonal skutečný nahraný zdroj `46cee7f5…` s existujícími mocky a přidal uplynulý čas mezi HTTP kroky. Neměnil firmware ani nepoužíval hardware. [Původní výsledky](../../models/jednoduche-auticko/firmware/prvni-motor/evidence/2026-09-19-hold-to-run/latency-simulation.txt):

| Simulovaný průběh | Výsledek skutečné řídicí logiky |
|---|---|
| HOLD každých 200 ms | Chod pokračuje |
| HOLD každých 250 nebo 300 ms | Vypnutí při 500 ms, další HOLD odmítnut |
| Odpověď ARM opožděná o 400 ms | První HOLD dovolí pouze 100 ms běhu; další po 200 ms už ne |
| Odpověď ARM opožděná o 500–600 ms | První HOLD odmítnut, motor vůbec nenastartuje |

Povolení běhu končí 500 ms od vydání spotřebované předchozí výzvy. Dva sousední intervaly HOLD se proto musí vejít do tohoto okna; při čekání JavaScriptu 100 ms po odpovědi zbývá v ustáleném modelu přibližně **méně než 150 ms na síťovou/obslužnou odezvu jednoho cyklu**. Simulace potvrzuje tuto vlastnost kódu, **neměří skutečnou latenci telefonu**. WiFiS3 v core 1.6.0 používá blokující modemová volání pro stav, příjem, odpověď i ukončení klienta.

## Tehdy navržený rozlišovací krok — historický

Zjistit přesný text a stav tlačítka na telefonu při neúspěšném pokusu: „Připravuji jízdu…“, „Pohon vpřed“, nebo chybové hlášení. Po nepotvrzeném STOP je tlačítko záměrně neaktivní až do obnovení stránky. Zkouška kol ve vzduchu už má neúspěšný výsledek; znovu se na ni neptat. Pro řízení a elektrický pohon je zásadní, zda při konkrétním stisku skutečně vznikne RUNNING / trvale svítící LED, nebo se nedokončí ARM/HOLD.

Tehdy byl pouze navržen podrobnější výpis typu požadavku, doby příjmu/odpovědi, stáří výzvy a oddělených čítačů vypršení ARM a RUNNING. **Tehdy tato změna nebyla provedena ani nahrána. Uživatel krátce zvolil návrat k sekundovému pulzu, ale vzápětí výslovně zadal dokončit opravu držení.** Historický návrh není aktuální úkol.

## Poslední pokusy a požadavek návratu k pulzu

Uživatel později upřesnil, že byl během monitorování pryč; chybějící nové HTTP v těchto oknech proto nespojujeme s potvrzeným aktivním stiskem. Po návratu hlásil nejprve, že nesvítí LED, potom dva funkční pokusy a následně „zas nefunguje“.

Přiznal, že předtím tlačítko krátce ťukal místo držení. Potom ale skutečně zkusil souvislé držení: pohon se spustil a zastavil, přestože tlačítko dál držel; někdy se nespustil vůbec. Krátké ťukání tedy nevysvětluje všechny následné pokusy. Konkrétní síťová příčina není doložená a simulace časování není měřením jeho telefonu. Dřívější těžký mechanický rozjezd na pulzním programu je samostatné hlášení, nikoli důkaz stejné příčiny.

Uživatel nejprve požádal o návrat k přesné sekundové verzi `772cd12f…`. Zdroj byl lokálně obnoven a ověřena shoda se zálohou a verzí Git; **tento rollback se do Arduina nenahrál**. Uživatel zadání výslovně zrušil: požaduje souvislou jízdu během držení a STOP po puštění, opravu i upload autonomně během své schůzky. Původní v1 je archivovaná v [samostatné složce](../../models/jednoduche-auticko/firmware/archiv-hold-to-run-v1/README.md).

## Oprava v2 — práce a rozsah důkazu

V2 odstranila požadavek součtu dvou komunikačních intervalů pod 500 ms, slučuje krátkou odpověď do jednoho zápisu, zkracuje prodlevu browseru na 20 ms a umožňuje obnovit relaci při novém skutečném stisku po chybě. Běžný limit povolení běhu zůstává 500 ms. Při ztrátě STOP a jednom již odeslaném HOLD je konzervativní hranice do vypnutí výstupu až 1 s od puštění; nejde o změřené fyzické zabrzdění. Přidává oddělené údaje ARM/RUN, důvody vypnutí a časy komunikace.

Aktuální dokončení překladu, testů a uploadu uvádí [firmwarový návod](../../models/jednoduche-auticko/firmware/prvni-motor/README.md) a [strojová evidence](../../models/jednoduche-auticko/firmware/prvni-motor/overeni-programu.json). Uživatelská fyzická akceptace základního ovládání v2 následně proběhla, viz závěrečný záznam níže. Oprava komunikační logiky nedokazuje odstranění mechanických či elektrických příčin těžkého rozjezdu.

**Technické dokončení v2:** finální zdroj `1760730b…` prošel hostovými regresními testy a skutečným Chromium přes lokální HTTP, byl přeložen a nahrán. USB po startu potvrdilo v2 a vypnuté výstupy; nebyl zaslán žádný motorový povel. Následnou fyzickou zkoušku držení/puštění a nového stisku uživatel potvrdil, viz níže. Starší mechanické a napájecí potíže tím nejsou automaticky uzavřené.

## Uživatelská akceptace v2 po návratu — 19. 9. 2026

Jiří po návratu obnovil ovládací stránku a na pokyn vyzkoušet držení, puštění a nový stisk opakovaně hlásil „Jo, funguje to, perfektní“. Tento výsledek patří nahrané verzi `hold-to-run-v2`, SHA256 `1760730b716a6fb281ed900400d533eaac17d96c9b779a6c91e2e99502d69110`. Potvrzuje základní funkci ovládání podle uživatele. Agent další upload ani motorový povel neprovedl. Přesná délka držení, doběh, maximální zátěž, elektrické parametry a všechny druhy výpadků sítě nejsou změřené. Zpětně tím nemažeme historii těžkého rozjezdu ani z něj neodvozujeme příčinu.
