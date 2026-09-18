# Deník tisků

Záznamy oddělují hlášení uživatele, kontrolu lokálních souborů, odhady sliceru a fyzická měření. Časy jsou místní pro Europe/Prague, pokud není uvedeno jinak.

## 2026-09-19 — polička na zárubeň, první pokus

**Stav: uživatel zahájil, výsledek nepotvrzen.** Model: [polička 90 × 50 mm](../models/policka-na-zaruben/README.md). Uživatel po půlnoci oznámil zahájení prvního tisku a pro poličku zvolil bílý Alzament PLA Basic.

Fyzická první vrstva ani hotový výtisk nebyly viděny a uživatel zatím neoznámil dokončení. **Lokální logy jednoznačně nepotvrdily, že právě níže popsaný G-code běží na tiskárně.**

### Kontrola lokálních souborů

Podle dokončené read-only kontroly při úvodní práci byl přibližně v **00:07** vytvořen místní G-code pro `policka-90x50.stl`. Nejnovější G-code a autosave se shodovaly v rozměrech a přípravě dílu. Surový G-code ani soukromé cloudové logy sem nebyly kopírovány; následuje přenesený výsledek kontroly.

| Parametr kontrolované přípravy | Hodnota |
|---|---:|
| Rozměry modelu | 90 × 50 × 34 mm |
| Vrstva / počet vrstev | 0,20 mm / 170 |
| Stěny / výplň / podpory | 2 / 15 % / vypnuté |
| Materiál a barva uvedené v přípravě | Bílé PLA |
| Poloha středu | X 130 / Y 130 mm |
| Rotace / spodek | Bez rotace / Z 0 |
| Rozsah tiskových drah X | 85,21–174,79 mm |
| Rozsah tiskových drah Y | 105,21–154,79 mm |
| Přesah mimo podložku | V kontrolované přípravě nezjištěn |
| Odhad času | 41 min 34 s |
| Odhad spotřeby | 14,21 g |
| Start v G-code | Tryska 220 °C / podložka 60 °C |
| Další teplota trysky | 205 °C |
| MVS | 13 mm³/s |

Čas a spotřeba jsou **odhady sliceru**, nikoli naměřená doba či hmotnost. Startovních 220 °C v tomto výstupu se liší od defaultu první vrstvy 215 °C; pro popis tohoto souboru platí zjištěných 220 °C.

### Rychlosti a varování

**Doporučené snížení extruzních rychlostí na nejvýše 100 mm/s v tomto souboru provedeno nebylo.** Profil ponechal vnější stěny 200, vnitřní 300, řídkou výplň 300, plnou výplň 250, horní povrch 200 a první vrstvu 50 mm/s. Průtokový limit rychlosti v G-code omezil; zjištěné přibližné příkazy extruze byly:

| Druh dráhy | Rychlost příkazu v G-code |
|---|---:|
| Vnější stěna | 179,56 mm/s |
| Vnitřní stěna | 166,33 mm/s |
| Řídká výplň | 166,33 mm/s |
| Plná výplň | 199,14 mm/s |
| Horní povrch | 178,88 mm/s |

Tyto hodnoty jsou **G-code feedrate, nikoli měření fyzické tiskárny**. Sport pro tento první nezkalibrovaný test nebyl doporučen; jeho skutečný stav není potvrzený.

Slicer obsahoval varování `bed_temperature_too_high_than_filament` a `not_support_traditional_timelapse`. Podložka 60 °C je současně uvnitř dodavatelského rozsahu Alzament PLA Basic 45–60 °C; samotný text varování nedokládá nebezpečí ani příčinu vady. Fyzický výsledek není znám.

### Co ještě doplnit

- Potvrzení, která úloha skutečně běžela a s jakou cívkou a nastavením.
- Pozorování první vrstvy, dokončení nebo přerušení a případné vady.
- Skutečná doba a spotřeba pouze pokud jsou známé, s uvedením zdroje.
- Naměřené rozměry, uchycení ke konkrétní zárubni, použité šrouby a výsledek funkční zkoušky. Nosnost zatím netvrdit.

## Osnova příštího záznamu

Datum a model/verze; stav a zdroj informace; tiskárna a tryska; skutečný materiál/cívka; profil a změny; vazba na konkrétní soubor; odhady; první vrstva a průběh; fyzický výsledek a měření; další změna a její důvod. Neznámé položky nevyplňovat odhadem.
