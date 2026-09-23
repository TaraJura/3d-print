# Přepážka B – podložky a experimentální řezání

22. 9. 2026 · aktuální revize má **TPU tělo vysoké 8 mm a nominální lepicí lože 2 mm**. Cílová instalace je 570 × nejvýše 20 × přibližně 10 mm; konečná výška 10 mm již není tvrdý výškový doraz. Původní 10mm model je pouze [historická reference](../historie/reference-10mm/rozlozeni/README.md).

Jsou připravené **dvě oddělené podložky**. Zkušební pár není součástí hlavní sestavy a nesmí být připočten k jejím třem dílům.

**Po hlášeném selhání 22. 9.:** [diagnostika](../../diagnostika/2026-09-22-nepovedeny-tisk/README.md) našla místní exporty s jiným procesem, včetně PLA. Pro obnovení zdejšího nastavení otevřít [TEST-EXPERIMENT-spoj-Alzament-TPU95A.3mf](TEST-EXPERIMENT-spoj-Alzament-TPU95A.3mf) **jako celý projekt do prázdného projektu**, nikoli importovat jen geometrii nebo kopírovat STL. Před případným tiskem má náhled ukázat **2 díly, výšku 8 mm, 40 vrstev po 0,2 mm, TPU, trysku 225 °C, desku 60 °C, 4 stěny, 100% výplň a normální odhad 33 min 9 s**. Teplotní rozpor popsaný níže zůstává otevřený. Kopie STL do jiného projektu tato nastavení nepřenese. Samotná kontrola souboru nepotvrzuje správné podávání ani úspěch fyzického tisku.

| Úloha | Počet a nominální rozměry jednotlivých STL | Geometry-only 3MF | Úplný experimentální projekt s G-code |
|---|---|---|---|
| Celá přepážka | 3 kusy: 193 / 200 / 193 × 20 × 8 mm | [Pracovní geometrie](prepazka-B-pracovni-geometrie.3mf) | [EXPERIMENT – hlavní sestava](EXPERIMENT-prepazka-B-Alzament-TPU95A.3mf) |
| Samostatná zkouška spoje | 2 kusy po 30 × 20 × 8 mm | [TEST – pracovní geometrie](TEST-spoj-pracovni-geometrie.3mf) | [TEST – EXPERIMENT spoje](TEST-EXPERIMENT-spoj-Alzament-TPU95A.3mf) |

TPU těla hlavní sestavy leží v sestavovacích souřadnicích X = 2…195, 185…385 a 375…568 mm. Konce rezervují 2 mm pro tmel uvnitř cílové délky 570 mm. Nominální mezery ve všech třech plochách každého stupňovitého spoje jsou 2 mm. Jde o navržené lepicí prostory, nikoli suchý vodotěsný zámek; úplnou sestavu a lepicí objemy popisuje [model](../README.md).

## Geometry-only alternativy

Standardní 3MF obsahují pouze uzavřené sítě v mm a jejich umístění 1:1, bez materiálu, procesu a G-code. Neobsahují konfiguraci tiskárny; ve sliceru je nutné zvolit správnou Kobra X 0,4 mm. Zkontrolovaný místní profil má tiskový prostor 260 × 260 × 260 mm bez vyloučené oblasti.

| Díl | Posun X / Y / Z na desce [mm] |
|---|---|
| Hlavní 1 | 33,5 / 70 / 0 |
| Hlavní 2 | 30 / 110 / 0 |
| Hlavní 3 | 33,5 / 150 / 0 |
| Test 1 | 90 / 120 / 0 |
| Test 2 | 140 / 120 / 0 |

Všechny díly mají plochou základnu na Z = 0, bez otáčení nebo škálování. Mezera mezi obálkami sousedních dílů je na obou podložkách 20 mm; minimální rezerva k okraji desky je 30 mm u hlavní a 90 mm u testovací podložky. Geometry-only soubory samy nemají lem ani podpory.

[Audit hlavní podložky](kontrola-podlozky.json) a [audit testu](kontrola-podlozky-TEST.json) ověřují počty, přesné obálky, uzavřené orientované sítě, jedinou komponentu každého STL, nulové degenerace, dosedací plochu, jednotky a polohu na desce. Po exportu se znovu načítají ZIP, XML, vrcholy, trojúhelníky a transformace. STL vrchol oblouku může být nepatrně nižší než nominální CAD výška; audit zachovává skutečná čísla a připouští rozměrovou odchylku nejvýše 0,001 mm bez změny sítě.

## Experimentální proces

Jiří potvrdil vyzvednutý **Alzament TPU95A Gray**. Profily jsou pracovní kopie systémového nastavení Anycubic Kobra X 0,4 mm a Anycubic TPU 95A pro tuto tiskárnu. Nejsou fyzicky kalibrovaným profilem Alzamentu. Otevírat celý vybraný projekt bez automatického uspořádání a otáčení; barva náhledu nepotvrzuje skutečnou cívku nebo cestu podávání.

- Vrstva 0,2 mm, tryska 225 °C včetně první vrstvy, Textured PEI Plate 60 °C.
- První vrstva 20 mm/s, ostatní extruzní pohyby nejvýše 40 mm/s, objemový limit 3,2 mm³/s.
- 4 stěny, 5 horních a spodních vrstev, 100% výplň: návrhová volba, nikoli záruka těsnosti.
- Vnější lem 5 mm s mezerou 0,1 mm; bez podpor, protože bokové napojení zachovává plochou základnu a průřez se směrem vzhůru zmenšuje.
- Účinné chlazení 100 % po první vrstvě, převzaté z varianty BRASS systémového TPU profilu. Retrakce 0,8 mm při 30 mm/s, flow ratio 1,0; nekalibrováno.

**Rozpor teploty desky zůstává otevřený.** Předané ověření [Alzament TDS](https://dwn.alza.cz/manual/161249) uvádí trysku 220–240 °C a desku 60–80 °C; produktová informace Gray uvádí 190–230 °C a desku 30–50 °C. Tryska 225 °C leží v průniku rozsahů, rozsahy desky se nepřekrývají. Zvolených 60 °C je pouze experimentální volba podle TDS a systémového TPU profilu. Oba projekty ukládají varování **`bed_temperature_too_high_than_filament`**. Nebylo potlačeno změnou materiálového prahu. Bez vyřešení tohoto rozporu a fyzické zkoušky nelze konfiguraci označit za finální.

## Co bylo ověřeno

Opětovné ověření teploty včetně vizuální kontroly TDS a vysvětlení, proč 50 °C není průnikem podkladů: [teplotní rozpor](teplotni-rozpor.md).

Anycubic Slicer Next 2.0.0.5 vrátil úspěch pro obě podložky, každá má 40 vrstev. Znovu načtené projekty obsahují přesně 3 a 2 objekty, nulové opravy sítí a G-code shodný s vnějšími soubory. Každý trojúhelník uložených objektů i umístění byly porovnány s příslušným STL při přesnosti zaokrouhlení 0,00001 mm. Materiál a proces uložený v projektu odpovídají účinnému nastavení sliceru.

Audit skutečných pohybů ověřil první vrstvu do 20 mm/s a ostatní extruzi do 40 mm/s, všechny příslušné objekty v každé vrstvě, přítomný lem, žádnou extruzi podpor a všechny dráhy včetně poloviny šířky čáry uvnitř desky. Konzolovou diagnostiku `calc_exclude_triangles` při prázdném seznamu vyloučených oblastí audit uvádí jako omezení; skutečné dráhy byly nezávisle ověřeny proti celé desce 260 × 260 mm.

- [Hlavní podložka – skutečné vrstvy](experimentalni-slice/nahled-skutecnych-vrstev.png), [audit G-code](experimentalni-slice/kontrola-gcode.json).
- [Test spoje – skutečné vrstvy](experimentalni-TEST-slice/nahled-skutecnych-vrstev.png), [audit G-code](experimentalni-TEST-slice/kontrola-gcode.json).

Náhledy přímo vykreslují extruzní souřadnice 1., 20. a 40. vrstvy G-code, nikoli snímek GUI sliceru. Byly vizuálně zkontrolovány. Surové maximum vypočteného průtoku je přibližně 3,272 mm³/s na velmi krátkém segmentu; na úsecích alespoň 0,1 mm nejvýše 3,206 mm³/s. Odchylka odpovídá citlivosti na zaokrouhlení souřadnic na 0,001 mm a extruze na 0,00001 mm. Audit zachovává surové hodnoty i mez po zohlednění tohoto zaokrouhlení; G-code nebyl upraven.

Odhad hlavní podložky je **5 h 54 min, 23,68 m filamentu a přibližně 70,6 g**. Zkušební pár vychází přibližně na **33 minut, 2,02 m a 6,0 g**. Hmotnost používá neověřenou hustotu 1,24 g/cm³ zděděnou z profilu Anycubic. Odhady nejsou měření skutečného tisku.

## Reprodukce a omezení

`vytvor_podlozku.py` přegeneruje hlavní geometry-only soubor a audit; `--sample` zvolí oddělený test. Očekávaná CAD výška je 8 mm, případný `--height-mm` mění pouze validaci a nikdy neškáluje STL. `priprav_experimentalni_slice.py` přepíše místní kopie profilů a vytvoří řezaný projekt; `--sample` opět zvolí test. `zkontroluj_slice.py` provede kontrolu uložených souborů a vykreslí dráhy, rovněž s volbou `--sample`.

Audit s matplotlib lze místně spustit přes `/home/novakj/.cache/freecad-shelf-1.1.3/runtime/AppRun python`. Slicer používá izolovaný dočasný datový adresář a pouze systémové zdrojové profily. Uložené projekty byly zkontrolovány na absenci přihlašovacích hodnot a soukromých cest; neobsahují cloudové logy. Runtime a konzolový log se neukládají do projektu. Nebyl proveden žádný přenos ani ovládání tiskárny.

Fyzicky nebyla ověřena první vrstva, pružnost, fit, rozměry po vychladnutí, přilnavost TPU k lepidlu, těsnost spoje, spodní lože ani konce. Úspěšné řezání není úspěšný výtisk. Nejprve je určena samostatná zkouška spoje a lepení; před tiskem je potřeba vyřešit uvedenou teplotu desky a zvolit skutečnou cívku i podávání.
