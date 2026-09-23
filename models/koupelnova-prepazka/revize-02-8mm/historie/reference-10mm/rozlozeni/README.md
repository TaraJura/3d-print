# Pracovní podložka – pouze geometrie

**Stav 22. 9. 2026:** zdejší soubory zachycují referenční variantu vysokou 10 mm. Jiří následně upřesnil, že limit 10 mm platí pro **celou nalepenou instalaci včetně lepicího lože**. Model vysoký 10 mm již neponechává prostor na lepidlo a není finální tiskovou revizí. Zvažovaná varianta 8 mm plast + 2 mm lože ještě není potvrzené zadání. Před výrobou je nutná výšková a montážní korekce podle zvoleného lepení.

`prepazka-B-pracovni-geometrie.3mf` obsahuje tři samostatné díly v měřítku 1:1 a jednotkách mm, plochou spodní stranou na Z = 0. Jde o **rozpracovanou alternativu bez tiskového procesu**, nikoli hotový tiskový projekt. Neobsahuje profil materiálu, proces ani G-code; nebyl řezán a tiskárna nebyla ovládána.

Jiří zadal sestavu dlouhou 570 mm, výšku 10 mm a následně opravil maximální šířku na **20 mm**. Tři díly a způsob napojení jsou návrhovou volbou. Délky samostatných dílů jsou 196, 202 a 196 mm; dvě společné oblasti dlouhé 12 mm dávají sestavenou délku `196 + 202 + 196 − 12 − 12 = 570 mm`.

| Díl | Obálka STL [mm] | Posun na podložce X/Y/Z [mm] |
|---|---|---|
| 1 | 196 × 20 × 10 | 32 / 70 / 0 |
| 2 | 202 × 20 × 10 | 29 / 110 / 0 |
| 3 | 196 × 20 × 10 | 32 / 150 / 0 |

Rozložení vychází z místního profilu **Anycubic Kobra X 0.4 nozzle**: tiskový prostor 260 × 260 × 260 mm, bez vyloučené oblasti. Samotný standardní 3MF konfiguraci tiskárny neobsahuje; správnou tiskárnu je nutné vybrat ve sliceru. Všechny díly mají původní orientaci bez otáčení a škálování. Mezi obálkami sousedních dílů je 20 mm a nejmenší rezerva k okraji desky 29 mm. Brim a podpory nejsou nastaveny ani započteny jako schválený tiskový proces. Při importu zachovat umístění a orientaci; automatické rozmístění nebo orientace by přepsaly toto zkontrolované rozložení.

`vytvor_podlozku.py` čte tři STL ze sousední složky `stl/`, před přepsáním výstupů ověřuje jejich rozměry a topologii, vytvoří standardní 3MF ZIP a znovu přečte uloženou geometrii i transformace. Přepisuje pouze zdejší 3MF a `kontrola-podlozky.json`. JSON obsahuje konkrétní výsledky včetně hashů vstupů a místního profilu. Spuštění: `python3 models/koupelnova-prepazka/rozlozeni/vytvor_podlozku.py` z kořene checkoutu.

Samotná geometry-only podložka neobsahuje filament ani proces. Dodatečně určený materiál a experimentální řezání jsou popsány níže; spojové vůle, uchycení k podkladu a fyzická funkce zůstávají neověřené. Uzavřená síť, suché napojení ani rozložení na podložce nedokazují těsnost, mechanický fit nebo úspěšný výtisk. Kontakt s podkladem, oba spoje i konce vyžadují samostatné vyřešení a fyzickou zkoušku.

## Samostatný experimentální řezaný projekt

[EXPERIMENT-prepazka-B-Alzament-TPU95A.3mf](EXPERIMENT-prepazka-B-Alzament-TPU95A.3mf) je úplný místní projekt s uloženou geometrií, nastavením a skutečným G-code. Má tři díly na jediné podložce; otevírat celý projekt bez automatického uspořádání a otáčení. Referenční výška 10 mm má výše uvedený montážní blok. **Projekt není schválený k výrobě ani ověřený materiálový profil.**

Jiří mezitím potvrdil vyzvednutý **Alzament TPU95A Gray**. Materiál tedy již není neznámý; neověřené zůstávají konkrétní fyzické vlastnosti, přilnavost, parametry tisku a těsnost. Barva uložená ve sliceru nepotvrzuje vložení správné cívky ani cestu podávání.

Pracovní nastavení vychází z přesného systémového profilu Kobra X 0,4 mm a profilu Anycubic TPU 95A pro tutéž tiskárnu:

- vrstvy 0,2 mm, tryska 225 °C včetně první vrstvy, vybraná Textured PEI Plate 60 °C;
- první vrstva 20 mm/s, ostatní extruzní pohyby nejvýše 40 mm/s, limit objemového průtoku 3,2 mm³/s;
- 4 stěny, 5 horních a 5 spodních vrstev, 100% výplň jako návrhová volba, nikoli záruka těsnosti;
- vnější lem 5 mm s mezerou 0,1 mm, bez podpor: bokové přeplátování má souvislou základnu a směrem nahoru se průřez zmenšuje;
- účinné nastavení chlazení 100 % po první vrstvě (převzato z varianty BRASS systémového TPU profilu), retrakce 0,8 mm při 30 mm/s, flow ratio 1,0; fyzicky nekalibrováno.

**Nevyřešený rozpor teploty desky:** předané údaje [Alzament TDS](https://dwn.alza.cz/manual/161249) uvádějí trysku 220–240 °C a desku 60–80 °C; produktová informace Gray uvádí 190–230 °C a desku 30–50 °C. Tryska 225 °C leží v průniku rozsahů, rozsahy desky se nepřekrývají. Zvolených 60 °C je pouze experimentální volba podle TDS a výchozího TPU profilu. Slicer navíc ukládá varování **`bed_temperature_too_high_than_filament`**. Varování nebylo potlačeno úpravou hranice materiálu; bez vyřešení nelze konfiguraci označit za finální.

CLI Anycubic Slicer Next 2.0.0.5 vrátilo úspěch a vytvořilo 50 vrstev. Znovu načtený ZIP obsahuje přesně tři objekty, nulové opravy sítí a G-code shodný s vnějším souborem `experimentalni-slice/plate_1.gcode`. Audit skutečných pohybů ověřil rychlost nejvýše 40 mm/s, první vrstvu 20 mm/s, všechny tři objekty v každé tiskové vrstvě, přítomný lem a žádnou extruzi podpor. Všechny extruzní dráhy včetně poloviny šířky čáry jsou uvnitř desky. Konzolová diagnostika `calc_exclude_triangles` při prázdném seznamu vyloučených oblastí je zachycena v auditu jako omezení; geometrie i skutečné dráhy byly nezávisle zkontrolovány proti celé desce 260 × 260 mm.

[Náhled skutečných vrstev](experimentalni-slice/nahled-skutecnych-vrstev.png) zobrazuje 1., 25. a 50. vrstvu přímo z extruzních souřadnic G-code. Byl vizuálně zkontrolován; nejde o snímek GUI sliceru. [Kontrola G-code](experimentalni-slice/kontrola-gcode.json) zachovává také surové maximum vypočteného průtoku 3,309 mm³/s na segmentu dlouhém pouze 0,006 mm; na úsecích alespoň 0,1 mm je maximum přibližně 3,20 mm³/s. Rozdíl u mikrosegmentu odpovídá citlivosti výpočtu na serializaci souřadnic a extruze; audit jej neskrývá ani nemění G-code.

Odhad sliceru pro běžný režim je **7 h 23 min, 29,84 m filamentu a přibližně 89 g**. Hmotnost používá neověřenou hustotu 1,24 g/cm³ zděděnou ze systémového profilu Anycubic. Čas a spotřeba nejsou měření skutečného tisku.

Reprodukce: `priprav_experimentalni_slice.py` vytvoří kopie systémového nastavení v `experimentalni-profily/` a řeže do `experimentalni-slice/`. Používá izolovaný dočasný datový adresář sliceru; nečte uživatelský cloudový profil, nepřenáší soubory ven a neovládá tiskárnu. `zkontroluj_slice.py` znovu zkontroluje uložené soubory a pomocí matplotlib vykreslí dráhy. Ověřený místní Python s matplotlib je `/home/novakj/.cache/freecad-shelf-1.1.3/runtime/AppRun python`. Po výslovné změně CAD výšky lze podložku validovat přepínačem `vytvor_podlozku.py --height-mm NOVA_HODNOTA`; soubory se tím neškálují a audit vrstvy odvodí z uložené nominální výšky. Soubory neobsahují tokeny, přihlašovací údaje ani soukromé cloudové logy; runtime se neukládá do projektu.
