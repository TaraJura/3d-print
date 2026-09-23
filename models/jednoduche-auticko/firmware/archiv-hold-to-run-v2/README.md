# Ovládání autíčka při držení tlačítka

**`hold-to-run-v2` je přeložený a skutečně nahraný do UNO R4 WiFi.** SHA256 `1760730b716a6fb281ed900400d533eaac17d96c9b779a6c91e2e99502d69110`; překlad **80 504 B flash / 9 792 B RAM**, upload **80 512 B / 20 stran / exit 0**. USB po uploadu potvrdilo `build=hold-to-run-v2`, `safety=1`, `drive=0`, EN/IN1/IN2 LOW, připravený server a HTTP0. Monitor je ukončený; agent neposlal žádný povel k fyzickému pohybu. [Úplná evidence](overeni-programu.json). **Jirka po návratu obnovil stránku a opakovaně potvrdil funkční držení, puštění a nový stisk: „Jo, funguje to, perfektní“.** To je fyzická akceptace základního ovládání podle uživatelského hlášení; nejde o měření doběhu, zátěže nebo všech síťových poruch.

Požadavek na návrat k sekundovému testu uživatel výslovně odvolal ještě před uploadem. Zdroj byl krátce lokálně obnoven z přesné zálohy `772cd12f…`, ale do desky nahraný nebyl. [Archiv v1](../archiv-hold-to-run-v1/README.md) uchovává přesný neaktivní zdroj, testy a diagnostiku před touto opravou. [Historie původního pulzu](historie-sekundoveho-testu.md) a [historický ověřovací záznam](historie-overeni-pulzu.json) se nevztahují k současnému zdroji.

## Použití po nahrání

1. Připojit telefon k Wi-Fi **Auticko-test**, demo heslo **auticko123**. Příprava AP po zapnutí trvá přibližně 10 sekund.
2. Jednou zavřít starou stránku a otevřít **[http://192.168.4.1/](http://192.168.4.1/)**. Načtení stránky motor nespouští.
3. **Držet** tlačítko „Držet pro jízdu vpřed“. Po navázání ovládání běží pohon, dokud přicházejí platná potvrzení držení.
4. Puštění posílá STOP. Totéž dělá zrušený dotyk, ztráta focusu, skrytí stránky nebo ztráta spojení. Motor se vypíná do volného doběhu, nejde o aktivní brzdu.
5. Po chybě tlačítko pustit a stisknout znovu. Nový skutečný stisk obnoví potřebnou relaci bez ručního reloadu. Chyba sama nesmí vyvolat nový rozběh.

Podporované je držení myší, primárním dotykem a klávesou Space/Enter. Krátké ťuknutí nemusí dokončit přípravu a není režimem jednosekundového pulzu.

## Co oprava mění

V1 omezovala konec běhu okamžikem vydání předchozí výzvy. Dva sousední intervaly komunikace se musely vejít do 500 ms; simulace reprodukovala vypnutí už při pravidelných 250–300 ms. V2 přidělí plných **500 ms od přijetí každého nového platného HOLD**. Každá serverová výzva zůstává jednorázová a nejvýše 500 ms stará. Už neplatí limit součtu dvou intervalů.

Prohlížeč čeká po odpovědi pouze **20 ms** místo 100 ms. Krátká odpověď HTTP včetně hlaviček se odesílá jedním zápisem do modemu. Stav Wi-Fi se za normálního provozu kontroluje nejvýše každých 100 ms místo před každým těsným průchodem smyčky. Zotavení po chybě Wi-Fi a odmítání starých povelů zůstávají zachované.

Příprava `ARMED` při vypnutém motoru má samostatný limit 3000 ms. **První HOLD přesto musí použít výzvu mladší než 500 ms**; třísekundová příprava nedovoluje opožděný rozběh. Odezva překračující tento limit se odmítne a další pokus vyžaduje nový stisk. Je to vymezený provozní limit, nikoli záruka chodu přes libovolně pomalou síť.

## Vypnutí a ochrana proti starým povelům

Přerušení `FspTimer` každých **5 ms** vypne EN a oba směrové vstupy při vypršení 500ms povolení. Časovač běží i během běžných blokujících volání Wi-Fi. Není to nezávislý hardwarový watchdog procesoru; zamrznutí CPU či dlouho zakázaná přerušení tato ochrana nepokrývá.

**Hranice při ztraceném STOP je konzervativně až 1 sekunda od zpracování puštění v prohlížeči nebo od ztráty spojení.** Jeden již odeslaný HOLD může dorazit těsně před vypršením své 500ms výzvy a přidat posledních 500 ms. Prohlížeč neposílá více HOLD souběžně. Při běžně doručeném STOP se výstup vypne při jeho zpracování. Uvedené limity se týkají elektrického výstupu; kola mohou mechanicky dobíhat. Zpoždění samotného doručení události v prohlížeči do tohoto limitu nezahrnujeme. Skutečné časování na fyzickém pohonu zatím není změřené.

STOP si pamatuje číslo stisku i tehdy, když předběhne ARM. Po STOP nebo vypršení nesmí pozdější HOLD obnovit pohyb. Staré tokeny, duplicitní výzvy a starší stisky se odmítají bez prodloužení povolení i bez shození novější jízdy. Ani starý STOP jiného, dřívějšího stisku nesmí vypnout novější stisk.

Po chybě získá až nový stisk relaci přes `POST /session`. Obnova motor vypne a zneplatní předchozí token. Opakování stejné obnovy po ztracené odpovědi vrací tutéž relaci bez dalšího vypnutí; opožděná obnova tak neshodí novější jízdu. Po restartu nebo síťové invalidaci je také nutná nová relace a nový stisk. Stránka neopakuje jízdu automaticky.

## Zapojení a výkon

| Arduino | ST L293D DIP16 | Funkce |
|---|---|---|
| D5 | 1 | EN, PWM 490 Hz, ekvivalent 128/255 |
| D7 | 2 | IN1, při chodu HIGH |
| D8 | 7 | IN2, při chodu LOW |

Motor je mezi piny 3 a 6, logika má 5 V na pinu 16, motorové napájení patří na pin 8, společná zem na 4/5/12/13. [Úplný návod](../../../../elektronika/auticko/zapojeni-l293d.md) rozlišuje návrh a uživatelem potvrzené propojení. PWM, směr a výkon se touto opravou nezvyšují. Neznámý proud motoru, napájení, mechanické odpory a těžký rozjezd dříve hlášený i na sekundovém programu nejsou opravou webu vyřešené.

## Výsledek testů

Finální zdroj prošel **90 parserových + 90 úplných HTTP případů**, **28 stavovými skupinami**, **7 blokujícími operacemi s kontrolou časovače**, **21 JS scénáři** a **9 scénáři skutečného Chromium přes HTTP proti skutečnému C++ sketchi s náhradami hardwaru**. Testy udržely běh při odezvách 200, 300 a 400 ms, ověřily jitter, dotyk, puštění během ARM, ztracený STOP/HOLD/odpověď obnovy i návrat sítě při stále drženém tlačítku bez automatického rozběhu. Nejde o fyzické měření telefonu, modemu, motoru ani brzdné dráhy.

## Diagnostika a ověřování

USB výpis při 115200 baud uvádí `build=hold-to-run-v2`, stav bezpečnostního časovače, fázi pohonu, čtení pinů, samostatné počty expirací ARM/RUN a důvod posledního vypnutí. Výpis `HTTP ARM/HOLD/STOP/SESSION` rozlišuje úspěch, číslo stisku, čas příjmu/odpovědi a stáří výzvy. Úspěšné HOLD jsou ve výpisu omezené na jeden za sekundu, aby log nezahlcoval spojení. Znak `?` pouze vyžádá diagnostiku, motor nespouští.

Důvody vypnutí: 0 start/lokální stav, 1 STOP, 2 expirace ARM, 3 expirace běhu, 4 ztráta Wi-Fi, 5 nová stránka/relace, 6 chyba PWM/RNG. `ENread` při PWM není měření napětí ani proudu.

- [Regrese a skutečný browser proti hostovému firmwaru](tests/README.md).
- [Přesné hashe, překlad, upload a jeho omezení](overeni-programu.json).
- [Chronologie potíží a oddělení mechaniky od komunikace](../../../../elektronika/auticko/potize-po-montazi.md).
- [Historie Wi-Fi a předchozích uploadů](../../../../elektronika/auticko/diagnostika-webu.md).

Fyzickou zkoušku po návratu uživatel potvrdil: obnovení stránky, souvislé držení, puštění a nový stisk. Přesné podmínky zatížení a délka doběhu nejsou změřené. Fyzická zkouška ztráty spojení není potvrzená. Agent motor ani servo samostatně nespouštěl; navazující návrh zatáčení firmware nemění.
