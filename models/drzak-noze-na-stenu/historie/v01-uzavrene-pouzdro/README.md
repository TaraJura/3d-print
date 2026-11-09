# Nástěnné pouzdro na jeden nůž

První návrh z 30. 10. 2026: vodorovná vanička s plnými konci a dvěma snímatelnými předními kryty. Uzavřený držák prostorově zakrývá celý nůž včetně ostří a špičky. Po sejmutí krytů zůstává dno a přední záchytný lem; rukojeť lze uchopit zepředu bez výřezu závislého na neznámé délce čepele.

**Jde o digitálně kontrolovaný návrh. Nůž, montáž, tisk a pevnost nebyly fyzicky ověřeny.** Úloha nebyla odeslána tiskárně. Hlavní výstup k posouzení je [vizualizace návrhu](prehled-navrhu.png), doplněná [pohledem na montáž](nahled-montaz.png).

## Zadání a návrhové hodnoty

| Údaj | mm | Původ |
|---|---:|---|
| Celková délka nože | 340 | Zadání Jiřího |
| Výška nože | 45 | Zadání Jiřího |
| Maximální šířka rukojeti | 25 | Zadání Jiřího |
| Konzervativní volná obálka | 346 × 49 × 29 | Návrh; vůle 6 / 4 / 4 celkem |
| Celá sestava včetně hlav čepů | 360 × 90 × 41,7 | CAD: délka × výška × hloubka od stěny |
| Zadní stěna / přední kryt | 3 / 3 | Návrh |
| Dno / záchytný lem | 4 / 8 | Návrh: tloušťka dna / výška lemu |
| Stupňové překrytí / montážní vůle | 4 / 0,3 | Návrh, fyzický tiskový fit neověřen |
| Zdvih krytu před sejmutím | 7 | CAD ověřená trajektorie |
| Zdvih obálky nože před vytažením | 9 | CAD ověřená trajektorie nad 8mm lemem |
| Montážní průchozí otvory | 4× Ø5,5 | Návrh; skutečné vruty a stěna nejsou zadány |

Rozdělení celkové délky na čepel a rukojeť, tloušťka a obrys čepele, hmotnost nože, materiál stěny ani vruty nejsou známy. Hodnota 25 mm je známa pro rukojeť; její použití jako tloušťky obálky celého nože je konzervativní **návrhový předpoklad**, nikoli měření čepele. Model nepotřebuje konkrétní délku čepele.

Nůž, nýty, vruty a stěna v náhledu jsou **ilustrační referenční geometrie**. Ilustrační rozdělení čepele a rukojeti není rozměrovou podmínkou držáku. Zelená barva náhledu je vizuální volba a nepotvrzuje vlastnictví ani založení zelené cívky.

## Konstrukce a použití

Sestava má čtyři tištěné díly: levou a pravou vaničku a levý a pravý kryt. Každá vanička je samostatně připevněna ke stěně dvěma vruty. Středový stupňový spoj propojuje a překrývá zadní stěnu, dno, střechu a přední lem. Spoj nenahrazuje kotvení obou polovin. Spára předních krytů je rovněž překrytá. Montážní vůle zůstává přítomná, ale kontrolované přímé paprsky přes spoje nemají otevřenou cestu skrz stěnu držáku.

1. Obě vaničky bez nože sesadit posunem podél délky. Srovnat jejich záda na rovné stěně, zkontrolovat spoj a upevnit **obě** poloviny. Středy otvorů od levého dolního rohu sestavy jsou X = 22 / 158 / 202 / 338 mm, Y = 79 mm. Vruty a hmoždinky vybrat až podle skutečné stěny a zatížení.
2. Nůž držet za rukojeť, přiblížit zepředu nad záchytný lem a položit do vaničky. Před zatížením zkontrolovat skutečné dosednutí a stabilitu. Kontakt ostří se dnem nelze bez přesného obrysu vyloučit.
3. Nasadit nejprve pravý kryt a potom levý: velké části klíčových otvorů přes hlavy čepů, přitisknout a spustit o 7 mm. Levý kryt překrývá středový spoj zepředu.
4. Při vyjímání sejmout nejprve levý kryt, potom pravý. Každý zvednout o 7 mm, vysunout dopředu přes hlavy čepů a odložit. Uchopit rukojeť, nůž zvednout přibližně 9 mm nad lem a vytáhnout dopředu. Zvolený postup je digitálně ověřen pro obálku, skutečná ergonomie není ověřena.

Kryty jsou vedené čepy a držené vlastní vahou, bez pružných západek. Držák nemá zámek ani dětskou pojistku. Ponechat prostor pro ruce a sejmutí krytů; 7 mm je geometrický zdvih, nikoli dostatečný prostor pro lidskou ruku. Povrch po odstranění podpor a styčné hrany je nutné fyzicky prohlédnout, zejména u ostří a spojů.

## Soubory

- [drzak.FCStd](drzak.FCStd) — editovatelný parametrický FreeCAD; tabulka `Parameters`, standardní objekty a výrazy, bez vlastního Python proxy.
- [drzak.FCMacro](drzak.FCMacro) — zdroj modelu, geometrické a parametrické kontroly a exporty.
- [nahled.FCMacro](nahled.FCMacro) — skutečné CAD náhledy a uložení finální viditelnosti.
- [sestavit-nahled.py](sestavit-nahled.py) — pouze sazba skutečných CAD snímků a popisek; geometrii nepřekresluje.
- [stl/](stl/) — čtyři díly v tiskové orientaci, každý 1×.
- [rozlozeni/README.md](rozlozeni/README.md) — dvě samostatné nastavené podložky pro Kobra X 0,4 mm a skutečné řezy.
- [kontrola-modelu.json](kontrola-modelu.json), [audit-montaze.json](audit-montaze.json) — geometrie, obálky, trajektorie a nezávislá montážní kontrola.
- [print-manifest.json](print-manifest.json) — kusovník, orientace a SHA-256 exportů.

## Tisk a rozsah kontrol

Kobra X má podle projektové dokumentace a ověřeného místního profilu plochu 260 × 260 mm. Délka 360 mm je proto rozdělena; největší jednotlivý díl má 182 × 90 × 41,7 mm. Podložka 01 obsahuje obě vaničky, podložka 02 oba kryty. **Každou nastavenou 3MF otevřít jednou jako celý projekt; nic nemnožit ani nepřerovnávat.** Geometry-only 3MF jsou jen alternativou stejné geometrie bez procesu, nikoli dalšími díly.

Vaničky se tisknou zadní plochou na podložce. Záchytný lem má převis, takže připravený proces obsahuje skutečné podpory i na modelu. Kryty se tisknou pohledovým čelem dolů; u pravého je podpíraný středový přesah, levý plochý kryt podporu nepotřebuje. Přesné procesní hodnoty, odhady, podporové dráhy a kontrolní obrázky uvádí dokumentace podložek. Profil pro PLA je návrhový pro Alzament PLA Basic; skutečná cívka, její stav a kalibrace nejsou potvrzené.

Geometrická kontrola zahrnuje platnost a jeden solid každého dílu, uzavřenou jednokomponentovou STL síť, nulové objemové kolize sestavy, volnou obálku, dráhy vyjmutí krytů a nože, montovatelnost půlek a přístup k vrutům. Test změnil rozměry nože na 350 × 47 × 27 mm, přepočítal nativní vazby a následně obnovil zadání. Náhledy zachycují stejnou konečnou geometrii jako exporty; v uloženém FCStd jsou zobrazeny jen čtyři finální díly.

Počítačová kontrola neověřuje pevnost výtisku a čepů, chování PLA v čase, bezpečné kotvení, ostré hrany po tisku, kontakt ostří s plastem, čistitelnost ani fyzické usazení konkrétního nože. Není to ověřený výrobek pro libovolný nůž rozměru 340 mm.

## Regenerace

Makro zapisuje vedle sebe; před spuštěním uložit a zavřít rozpracovaný stejnojmenný dokument. Změny tabulky FCStd sladit s `VALUES` v makru, jinak je regenerace obnoví na hodnoty zdroje. STL a PNG se samotnou změnou tabulky neobnoví.

Použít FreeCAD 1.1.3, nikoli systémový Python:

```bash
/home/novakj/.cache/freecad-shelf-1.1.3/runtime/AppRun freecadcmd \
  -u /home/novakj/.cache/freecad-shelf-1.1.3/task-user.cfg \
  -s /home/novakj/.cache/freecad-shelf-1.1.3/task-system.cfg \
  /home/novakj/3d-print/models/drzak-noze-na-stenu/drzak.FCMacro
```

Poté spustit `audit-montaze.FCMacro`, GUI makro `nahled.FCMacro`, skript `sestavit-nahled.py` a `build_print_projects.py` ve stejné složce. GUI render lze provést izolovaně přes `LIBGL_ALWAYS_SOFTWARE=1 LP_NUM_THREADS=2 xvfb-run -a …/runtime/AppRun …/nahled.FCMacro`. Runtime ani konfigurace nejsou součástí modelu. Při změně geometrie zopakovat příslušné kontroly a obnovit SHA-256 předání.
