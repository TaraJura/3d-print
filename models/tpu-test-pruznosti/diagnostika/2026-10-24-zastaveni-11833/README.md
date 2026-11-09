# Zastavení prvního TPU testu — 24. 10. 2026

## Potvrzeno uživatelem

Jiří hlásí: „nefunguje to .... tisk se zastavil hned na zacatku!“
[Dodaná obrazovka](chyba-11833.png) uvádí Anycubic Kobra X, **Error Code: 11833**, text **Abnormal filament entanglement/jam detected** a úlohu `TPU-test-Alzament95A-plate1.gcode`. Náhled odpovídá třem páskům a dvěma kroužkům. Ze screenshotu nelze ověřit hash souboru skutečně spuštěného na tiskárně ani jeho mapování na fyzický vstup.

Předchozí potvrzený materiál je Alzament TPU 95A. Fyzický tisk byl uživatelem vyzkoušen a zastavil se na začátku; první vrstva ani úspěšný výtisk nejsou potvrzené. Přesná fáze selhání (zavádění / čištění / vlastní model), aktuální vstup, skutečně nastavený materiál na tiskárně a průchodnost nejsou zatím známy. Starší stav vstupu 3 nelze převzít jako dnešní fakt.

## Kontrola předaného souboru, nikoli zařízení

Kontrola beze změn 3MF potvrdila původní hash projektu `57802d559b4c5b03d0049fa4aed8fad02bbf53a10da04a3ba52c5afd1cf413bb` a vnitřního G-code `41dabb8cd453d75afc76b817f2210c763a688748dde2c38981ca8450a565d5ca`. Start používá nativní příkaz Kobra X `G9111 bedTemp=60 extruderTemp=225`, řádek 63 vnitřního G-code. Před tímto příkazem není explicitní extruzní pohyb. Startovací ohřev, čekání a zavádění jsou ve firmwaru; jejich skutečný průběh a rychlosti z tohoto souboru neznáme. Chybějící samostatné M109/M190 proto není důkaz studené extruze.

První explicitní pohyby filamentu jsou retrakce −0,8 mm a návrat +0,8 mm při F1800 (30 mm/s filamentu), převzaté z místního profilu tiskárny; první tisková dráha je 15 mm/s. Dřívější limit 25 mm/s platí pro pohyb při tisku modelu, nikoli pro celý zaváděcí cyklus nebo rychlost posuvu samotné struny při retrakci. Podávání, teploty a jejich fyzická realita nebyly změřeny. Závada nebyla touto kontrolou opravena ani její příčina určena.

## Oficiální postup konzultovaný 24. 10. 2026

[TPU Printing Guide pro Kobra X](https://wiki.anycubic.com/en/fdm-3d-printer/anycubic-kobra-x/tpu-printing-guide) podporuje TPU95A pro jednobarevný tisk a uvádí zvláštní postup počátečního zavedení: strunu provést hadičkou, hadičku u hlavy odpojit, ručně zavést do extruderu do potvrzovacího pípnutí a hadičku vrátit. Na tiskárně nastavit TPU. To je obecný návod výrobce, nikoli pokyn již fyzicky provedený či ověřená oprava tohoto případu.

Článek chyby11833 pro Kobra X se na zkoušené adrese `/en/error-codes/11833-code/kx` nepodařilo najít (404); postup jiného modelu se nepovažuje za ověřený servisní postup Kobra X. Samotný text chyby na uživatelově obrázku potvrzuje hlášení o zamotání/zaseknutí, ne jeho přesné místo.

Další diagnostika začíná zjištěním, zda z trysky před chybou vytékal filament, a aktuální cestou podávání. Uživatel byl dotázán. Zatím neprovádět další opakované pokusy přes odpor, netahat strunu silou a nevypínat detekci zaseknutí. Agent tiskárnu neovládal, neměnil její firmware ani nastavení a neupravil model, profil nebo G-code.

## Zjištěné riziko retrakcí v původním profilu

Původní proces ponechal zapnuté stírání při zatahování filamentu (`wipe`). Na první vrstvě, řádek 2360 vnitřního G-code, je `G1 X70.541 Y132.008 E-.8` při modálním F900 přes úsek XY přibližně 0,086 mm. Poměr E/XY dává nominální rychlost struny asi 139,5 mm/s; nejde o změřenou rychlost motoru a firmware ji může omezit. V celém souboru bylo nalezeno 96 záporných E segmentů s takto odvozenou rychlostí nad 30 mm/s. Původní audit limitu rychlosti tyto záporné pohyby nezahrnoval. To je skutečná mezera kontroly a důvod připravit samostatný proces bez wipe; není to důkaz příčiny chyby 11833. Pokud nastala před první tiskovou čárou, uvedené řádky ještě nebyly vykonány.

Oficiální Kobra X TPU Printing Guide doporučuje wipe vypnutý. Další samostatná revize proto zachová geometrii i původní start a teploty, ale vypne wipe a výslovně omezí retrakci i návrat na návrhových 20 mm/s se zachovanou délkou 0,8 mm. Ověření tohoto kandidáta a fyzický výsledek se musí zaznamenat odděleně; původní 3MF se nepřepisuje.


Samostatná [V02 bez wipe](../../rozlozeni/revize-02-bez-wipe/README.md) byla následně připravena, nařezána a znovu ověřena. [3MF V02](../../rozlozeni/revize-02-bez-wipe/podlozka-01-v02-bez-wipe-kobra-x-alzament-tpu95a.3mf) má SHA256 `cf52630d61a79766a2db4b2466c3b582ed70c6f0d9d14f49acc744a8519a1248`. Oproti V01 mění pouze TPU override retrakcí/wipe, text poznámky a identifikaci exportu; původní vstupní soubory zůstaly hashově shodné. Nezávislá následná kontrola potvrdila chybějící wipe bloky, 493 explicitních retrakcí a 492 návratů nejvýše20 mm/s; žádné záporné E při XY pohybu. Jediný zaokrouhlený XY mikropohyb s E0,00001 a F1500 zůstal jako vyčíslený artefakt sliceru (nejde o retrakci). Start G9111 zůstává stejný a jeho vnitřní pohyby jsou mimo kontrolu. **V02 je kandidát pro další test, nikoli potvrzená oprava11833; nejprve je potřeba zjistit fázi selhání a průchodnost podávání.**


## Navazující uživatelská hlášení 24. 10. 2026

Jiří potvrdil použití horních vstupů1–4, bez upřesnění konkrétního kanálu. Následně ohlásil nový pokus („davam to tisknout ted uvidime“) a poté **„z trycky TPU netece“**. Verze právě spuštěného souboru (V01/V02), skutečná teplota trysky, dokončení zavedení a nový případný chybový kód nejsou potvrzené. Nejde o potvrzení průchodné či ucpané trysky: příčinou může být i nezavedená struna nebo stav ohřevu, který je potřeba zjistit. Uživatel dostal pokyn tisk zastavit; provedení tohoto zastavení zatím nepotvrdil. Žádný příkaz tiskárně agent neodeslal.

Jiří na dotaz na skutečnou teplotu odpověděl **„250 tam bylo“**. Jde o uživatelské hlášení zobrazené hodnoty při pokusu, nikoli nezávislé měření; současná teplota není potvrzená. Obě místně předané varianty mají start225 °C, takže původ rozdílu250 °C není určený (aktuální soubor, ruční volba ani firmware nebyly ověřeny). Hlášená absence extruze při této zobrazené teplotě je důvod zkontrolovat zavedení a cestu struny, nikoli dále zvyšovat teplotu. Další krok je po zastavení tisku a nastavení225 °C uvolnit pouze horní PTFE hadičku použitého vstupu, ponechat filament v místě a zkontrolovat jeho jemné ruční zavedení podle oficiálního TPU návodu. Provedení, pípnutí ani obnovená extruze zatím nejsou potvrzené.

**Následná oprava uživatele:** „jo sorry ted tam bylo 225 ale predtim i 250 mam pocit“. Pro nynější pokus tedy hlásí225 °C, což odpovídá předanému nastavení. Dřívější250 °C je jen nejistá vzpomínka; nelze ji uvádět jako potvrzenou teplotní odchylku nebo příčinu selhání. Hlášení, že TPU nevytéká, zůstává beze změny.


## Ověřený postup čištění trysky — zatím pouze návod

Na uživatelův dotaz na čištění byl24.10.2026 načten [oficiální Kobra X Cleans Clogged Nozzles](https://wiki.anycubic.com/en/fdm-3d-printer/anycubic-kobra-x/cleans-clogged-nozzles). Pro první pokus bez demontáže výrobce popisuje čištění tenkou jehlou při230 nebo250 °C a následnou kontrolu podáváním. Doporučený první čisticí krok pro tento případ je230 °C, jemná práce správnou čisticí jehlou zespodu, bez síly a mimo pohyb stroje; před podáváním jehlu úplně vyjmout. Návod také výslovně uvádí, že příkazE+ nahřívá na250 °C: to může vysvětlit dřívější nejistě hlášenou hodnotu, ale použitíE+ tehdy uživatel nepotvrdil. Čištění ani obnovená extruze nejsou potvrzené; místo blokace zůstává neprokázané.


## Čištění nepomohlo; nová chyba 11853

Jiří následně hlásí „vycisteni trysky nepomohlo!“. [Nový screenshot](chyba-11853.png) uvádí **Code:11853 — Channel 3 filament retracting error**. Aktuální hlášení tedy výslovně identifikuje chybu vysouvání filamentu v kanálu 3. Nelze z něj zpětně určit kanál původní chyby 11833 ani verzi G-code při novém pokusu. Uživatel potvrzuje neúspěšný pokus o čištění, nikoli přesný průběh nebo prokázanou průchodnost trysky.

[Oficiální postup Anycubic pro 11853](https://wiki.anycubic.com/en/error-codes/11853-code/kx), ověřený 24. 10. 2026, rozlišuje blokaci trysky, vyšší části dráhy a mechanické příčiny. Místo závady zde zůstává neznámé. Dalším navrženým krokem je zrušit úlohu, vypnout ohřev, nechat hlavu vychladnout při zapnutém napájení a teprve poté tiskárnu vypnout a odpojit. Pokud je přední kryt nasazený, jemně jej sejmout stiskem spodní části a tahem dopředu; při odporu nepáčit. Požadována fotografie odkryté hlavy zepředu a mírně shora před další demontáží. Zatím nemanipulovat s klipy, tryskou ani kabely a netahat filament silou. Tato prohlídka ani její výsledek nejsou zatím potvrzené. Agent tiskárnu neovládal.


Jiří potvrdil sejmutý přední kryt a odmítl další fotografování. Odpojení napájení ani úplné vychladnutí samostatně nepotvrdil; pro další manipulaci zůstávají podmínkou. Další poskytnutý krok vychází z oddílu 3 / Step 2 oficiálního postupu 11853: sejmout silikonový návlek, uvolnit klip trysky a potom klip chladiče a zkusit trysku vyjmout. Při odporu zastavit, bez páčení a násilného tahu. Směr vytažení nebyl z dostupného textu ověřen a nebyl stanoven. Provedení demontáže ani příčina závady zatím nejsou potvrzené; další odpověď uživatele má rozlišit vyjmutou versus držící trysku.

Jiří následně potvrdil **„tryska venku“**. Vyjmutí trysky je tedy potvrzené uživatelem; průchodnost, přítomnost zbytku TPU a místo blokace zůstávají nepotvrzené.

Při navazující prohlídce zespodu do hlavy po vyjmutí trysky Jiří hlásí **„vidím ho, ale drží“**. Potvrzuje tím viditelný filament, který nelze volně vyjmout; není potvrzeno, že jde o ulomený samostatný kus, ani kde přesně je filament zadržen.

Po sejmutí horního vstupního bloku se čtyřmi PTFE rychlospojkami Jiří potvrzuje **„vidím kolečka“**. Horní blok je tedy sejmutý a ozubená kolečka odkrytá; tryska zůstává vyjmutá. Filament byl dosud hlášen jako viditelný pouze zespodu a držící. Jeho vyjmutí, průchodnost ani přesné místo zadržení nejsou potvrzené.

Na lehký ruční test průchodu krátkým PLA shora kanálem 3 při vypnuté tiskárně Jiří odpověděl **„nejde protlačit“**. Tento pokus tedy průchod nepotvrdil; výsledek sám nerozlišuje sevření podávacími kolečky od blokace dále v dráze.

Jiří následně hlásí **„uz vidim ten zaseknlu kousek ale nejde vytahnout asi ho drzi ty ozubene kolecka nahore“**. Potvrzuje viditelný a stále nevyjmutý filament; sevření horními ozubenými kolečky je jeho domněnka, nikoli prokázaná příčina. Dokončení předchozího navrženého odšroubování chladiče výslovně nepotvrdil a aktuální uchycení chladiče zůstává neznámé.


## Uživatelsky potvrzená oprava a nové zavádění

Jiří následně oznámil **„hotovo uz loaduju filamentu opraveno“**. Závadu tedy podle svého hlášení odstranil a zahájil zavádění filamentu. Přesný závěrečný zásah nepopsal; nelze z toho potvrdit konkrétní příčinu ani přisoudit opravu změně profilu V02. Dokončené zavedení, plynulý výtok z trysky a úspěšný tisk testovacího modelu zatím samostatně nepotvrdil. Agent tiskárnu neovládal.
