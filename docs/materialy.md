# Sklad tiskových materiálů a profily

Toto je kanonická evidence materiálů pro 3D tisk v tomto projektu. Sklad aktualizován 22. 9. 2026; původní záznam profilu PLA níže pochází z 19. 9. 2026. Důsledně rozlišovat nákup, vyzvednutí, fyzický zůstatek, údaje dodavatele, načtený default, doporučení a skutečný soubor či tisk. Další tiskové potřeby evidovat až po potvrzení konkrétní položky.

## Sklad filamentů

Nákupy a vyzvednutí byly ověřeny 22. 9. 2026 z přihlášené historie a detailů objednávek Alza při kontrole pouze pro čtení. Košík při této kontrole filamenty neobsahoval. Obsah balení, průměry a kódy pocházejí z produktových stránek odkazovaných v tabulce. Každý řádek představuje **jedno zakoupené balení**; dvojbalení obsahuje dvě cívky.

| Filament a kódy | Zakoupená balení / cívky | Obsah a barva | Katalogový průměr | Objednávka | Fyzický zůstatek k 22. 9. 2026 |
|---|---:|---|---|---|---|
| [Alzament Dualpack – Basic PLA Combo](https://www.alza.cz/alzament-pla-basic-dualpack-2x1kg-black-white-d12717993.htm), `ALZMNTDL01` | 1 / 2 | 1× bílá 1 kg + 1× černá 1 kg | 1,75 mm ±0,02 mm | `1058475679` | Bílá **0 g, spotřebovaná**; černá **cca 200 g**, odhad uživatele, neváženo. |
| [Alzament TPU 95A 1 kg Gray](https://www.alza.cz/alzament-tpu-95a-1-kg-gray-d13015353.htm), `ALZMNTTPU03` | 1 / 1 | 1× šedá 1 kg | 1,75 mm ±0,02 mm | `1059428805` | Zbývající hmotnost neznámá. |
| [Alzament Dualpack – Basic PLA White](https://www.alza.cz/alzament-pla-basic-dualpack-2x1kg-white-d12717997.htm), `ALZMNTDL03` | 1 / 2 | 2× bílá 1 kg | 1,75 mm ±0,02 mm | `1059428805` | Zbývající hmotnost obou nových bílých cívek neznámá. |
| [Elegoo PLA 1kg Red](https://www.alza.cz/elegoo-pla-1kg-cervena-d7585016.htm), `ELEPD2208`; výrobní kód `14.0007.203` | 1 / 1 | 1× červená 1 kg | 1,75 mm ±0,02 mm | `1059428805` | Zbývající hmotnost neznámá. |
| [Alzament PLA Silk 1 kg Gold](https://www.alza.cz/alzament-pla-silk-1-kg-gold-d12869930.htm), `ALZMNTS07` | 1 / 1 | 1× zlatá 1 kg | 1,75 mm ±0,02 mm | `1059428805` | Zbývající hmotnost neznámá. |

| Objednávka | Vytvořena | Vyzvednuta | Ověření položek |
|---|---|---|---|
| `1058475679` | 15. 9. 2026 23:30 | 16. 9. 2026 08:58 | Combo: 1 ks balení, stav Vyzvednuto. |
| `1059428805` | 21. 9. 2026 17:56 | 22. 9. 2026 18:05 | TPU Gray, PLA White Dualpack, Elegoo PLA Red a PLA Silk Gold: každé 1 ks balení, stav Vyzvednuto. |

Celkem bylo v těchto dvou nákupech **7 cívek po nominálním 1 kg**. Jde o původní obsah zakoupených balení, **nikoli současný zůstatek 7 kg**. Starší Combo je tatáž bílá a černá Alzament PLA Basic z původní evidence níže; není započítané podruhé. Spotřebování staré bílé a odhad cca 200 g na jediné černé cívce výslovně nahlásil Jiří 22. 9. 2026. Tento údaj se nevztahuje na dvě nově vyzvednuté bílé cívky.

Současnou celkovou hmotnost zásob nelze určit. Zbývající hmotnosti nových cívek nejsou potvrzené. Samotný stav Vyzvednuto dokládá převzetí objednávky, nikoli následné použití filamentu; pozdější hlášení o nasazení je oddělené níže.

**Nasazení podle přímého hlášení Jiřího večer 22. 9. 2026:** šedé **Alzament TPU95A dal do fyzického vstupu 3** Kobra X; do vstupu **4 právě dává zlaté Alzament PLA Silk**. U zlata jde o probíhající zavádění, dokončení nepotvrzené. Agent tiskárnu neprohlížel ani neovládal. Pro přepážku je určen vstup 3; logický filament 1 v projektu je nutné při případném odesílání správně mapovat, samotný soubor fyzický vstup neprokazuje. [Kontext hlášení a neúspěšného tisku](../models/koupelnova-prepazka/diagnostika/2026-09-22-nepovedeny-tisk/README.md). Žádný nový úspěšný tisk ani spotřeba tím nejsou potvrzené.

## Alzament TPU 95A Gray

Jiří 22. 9. 2026 určil **TPU pro koupelnovou přepážku**. Převzatá cívka v evidenci je Alzament TPU 95A 1 kg Gray. **Tvrdost 95A je katalogový údaj**, nikoli vlastní měření. Večer potvrdil nasazení šedého TPU do vstupu 3 a neúspěšný tisk přepážky; vazba výsledku na konkrétní soubor není potvrzená. Úspěšná fyzická zkouška této konfigurace chybí.

| Katalogový údaj Alza | Rozsah |
|---|---:|
| Tryska | 190–230 °C |
| Podložka | 30–50 °C |
| Rychlost | 40–80 mm/s |

Zdroj: [produktová stránka Alzament TPU 95A Gray](https://www.alza.cz/alzament-tpu-95a-1-kg-gray-d13015353.htm), ověřena při kontrole 22. 9. 2026. Tyto rozsahy **nejsou ověřený ani kalibrovaný profil pro Anycubic Kobra X 0,4 mm**. Konkrétní nastavení a jeho zkoušky je nutné zaznamenat samostatně.

**Rozpor v podkladech výrobku:** [technický list Alzament TPU 95A](https://dwn.alza.cz/manual/161249), ověřený 22. 9. 2026, uvádí trysku 220–240 °C, podložku 60–80 °C, rychlost 40–80 mm/s a toleranci průměru ±0,03 mm. Konkrétní produktová stránka Gray výše uvádí jiné teplotní rozsahy a ±0,02 mm. Obě evidence zůstávají oddělené; nejde o naše měření. Přesný režim sušení této cívky nebyl doložen.

Místně existuje profil **Anycubic TPU 95A @Anycubic Kobra X 0.4 nozzle**, odlišný od „TPU for ACE“. Jeho defaultní maximální objemový průtok je 3,2 mm³/s a průtokový násobitel 1,0. V [projektu přepážky](../models/koupelnova-prepazka/README.md) vznikl experimentální místní proces: tryska 225 °C, texturovaná tisková podložka 60 °C podle TDS a místního profilu, extruzní rychlosti nejvýše 40 mm/s, první vrstva 20 mm/s. **60 °C odporuje produktové stránce Gray; volba je návrhová, fyzicky neověřená.** Stav konkrétního řezu a kontrola skutečně exportovaných hodnot patří do modelu, nikoli do záznamu zásoby. Koupelnová kachlička není tisková podložka.

## Alzament PLA Basic: evidence a profil z 19. 9. 2026

Uživatel tehdy potvrdil **Alzament PLA Basic, 1,75 mm**, bílou a černou ze staršího Combo. První polička byla zvolena bílá. Aktuální zůstatky jsou ve skladu výše. Nezaměňovat s PLA+, Silk ani HighSpeed.

| Údaj dodavatele | Rozsah |
|---|---:|
| Tryska | 190–220 °C |
| Podložka | 45–60 °C |
| Doporučená rychlost | 50–100 mm/s |
| Průměr filamentu | 1,75 mm |

Zdroje použité při přípravě: [Alzament na Alza.cz](https://www.alza.cz/alzament/v46531.htm), [filamenty Alza.cz](https://www.alza.cz/filamenty-pro-3d-tiskarny/18854774.htm). Jde o dodavatelské údaje, nikoli vlastní kalibraci cívky.

### Doporučení pro počáteční test PLA

Jako start bylo navrženo použít profil **Anycubic PLA @Anycubic Kobra X 0.4 nozzle**, teploty 215 °C první / 205 °C další vrstvy a podložku 60 °C; extruzní rychlosti snížit nejvýše na **100 mm/s**. Sport pro první nezkalibrovaný test nebyl doporučen.

Toto je návrh výchozího testu, **nikoli změřená kalibrace ani potvrzené nastavení provedeného tisku**. Uživatel snížení rychlostí nepotvrdil a kontrolovaný lokální G-code je neměl snížené na 100 mm/s. Výsledek prvního tisku je zatím neznámý; viz [deník](denik-tisku.md).

### Skutečně načtené defaulty PLA

Základ: **Anycubic PLA @Anycubic Kobra X 0.4 nozzle**, proces **0.20 mm Standard**. Tabulka je dokumentace defaultu této instalace, nikoli doporučený profil pro Alzament PLA Basic.

| Parametr | Default |
|---|---:|
| Tryska, první / další vrstvy | 215 / 205 °C |
| Podložka | 60 °C |
| Maximální objemový průtok (MVS) | 13 mm³/s |
| Výška vrstvy | 0,20 mm |
| Vnější stěny | 200 mm/s |
| Vnitřní stěny | 300 mm/s |
| Řídká výplň | 300 mm/s |
| Plná výplň | 250 mm/s |
| Horní povrch | 200 mm/s |
| První vrstva | 50 mm/s |
| Počet stěn | 2 |
| Výplň | 15 % |
| Podpory | Vypnuté |

Profil **Generic PLA** v této instalaci uváděl kompatibilitu pouze se starší Kobra 1, nikoli Kobra X; měl 230 °C pro první vrstvu a 65 °C pro podložku. Proto nebyl doporučen k nasazení na Kobra X bez ověření.

Výběr všech materiálů v instalačním průvodci jen rozšiřuje katalog profilů. Barva v náhledu nenahrazuje přiřazení skutečné cívky. Název profilu, nastavené rychlosti a rychlosti příkazů v G-code nejsou fyzicky změřené podmínky tisku.

## Co doplnit po zkoušce

Zaznamenat skutečně použitou cívku a profil, změny oproti defaultu, první vrstvu, vady a výsledek. Kalibraci a použitelnost pro daný účel potvrdit až z pozorování a měření; žádný vlastní kalibrovaný profil zde zatím není.
