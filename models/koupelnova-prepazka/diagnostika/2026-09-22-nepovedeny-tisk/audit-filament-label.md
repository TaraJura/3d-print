# Audit názvu filamentu a načtení celého projektu

22. 9. 2026. **Oba předané úplné projekty revize 02 obsahují aktivní profil Alzament. Izolované načtení celého testovacího projektu nativním CLI tento profil zachovalo.** Pozdější místní export z 20:36 naproti tomu obsahuje standardní Anycubic TPU a odlišné nastavení. Rozdíl tedy není pouze kosmetický název výrobce.

## Porovnání uložených hodnot

První sloupec byl přečten přímo z `Metadata/project_settings.config` obou zmrazených 3MF v `evidence/model/revize-02-8mm/rozlozeni/`. Druhý z konfiguračních komentářů souboru `0922-2036-dil-1_plate(01)_TPU_0.2_2h28m26s.gcode`, identifikovaného v [manifestu dočasných souborů](manifest-docasnych-souboru.json). Jeho SHA-256 `09baac1bab0d99ace009a8b9292e3d60ba54825af78d54283415322b2bc227e4` odpovídá manifestu; `mtime` je 20:36:33 +02:00.

| Pole | Naše hlavní i testovací 3MF | Místní export 20:36 |
|---|---|---|
| `filament_settings_id` | `EXPERIMENT Alzament TPU95A Gray Kobra X 0.4 225C bed60C` | `Anycubic TPU 95A @Anycubic Kobra X 0.4 nozzle` |
| `filament_vendor` | `Alzament` | `Anycubic` |
| `filament_type` | `TPU` | `TPU` |
| `filament_ids` | `EXPERIMENT-Alzament-TPU95A-Gray` | `GFTPU 95A` |
| Tryska první / další | 225 / 225 °C | 215 / 210 °C |
| Textured PEI první / další | 60 / 60 °C | 60 / 60 °C |
| `print_settings_id` | `EXPERIMENT prepazka B TPU95A 0.20mm Kobra X 0.4` | `0.20mm Standard @Anycubic Kobra X 0.4 nozzle` |
| Výplň | 100 % | 15 % |
| Limit objemového průtoku | 3,2 mm³/s | 3,2 mm³/s |
| `default_filament_profile` | `Anycubic PLA @Anycubic Kobra X 0.4 nozzle` | Stejná hodnota |

`default_filament_profile` je zároveň hodnota v přibaleném zdrojovém profilu tiskárny `experimentalni-profily/machine.json`. **Sama nedokazuje aktivní PLA**: u úplného projektu jsou současně aktivní ID, typ, výrobce a teploty Alzament TPU, které přežily níže popsaný import. Nelze tuto výchozí hodnotu zaměnit za použitý materiálový profil.

Zdrojový `experimentalni-profily/filament.json` má `from = user`, `is_custom_defined = 1`, prázdné `inherits`, vlastní `filament_id` a uvedený experimentální název v `name` i `filament_settings_id`. Uvnitř 3MF je sloučená konfigurace `name = project_settings`, `from = project`, `inherits_group = ["", "", ""]`; jednotlivá pole `is_custom_defined`, `inherits` a `filament_id` tam nejsou. Místo posledního je přítomné pole `filament_ids`. Chybějící zdrojové klíče tedy nelze vykládat jako chybějící aktivní profil: uložené účinné hodnoty jsou explicitní.

## Přímá zkouška importu bez řezání

Ve 20:39:51 +02:00 bylo spuštěno `/usr/bin/AnycubicSlicerNext` s novým dočasným `--datadir`, `--outputdir` v tomto diagnostickém adresáři a `--export-settings`. Jediným vstupem byl zmrazený `TEST-EXPERIMENT-spoj-Alzament-TPU95A.3mf`. **Nebyly použity `--slice`, `--load-settings` ani `--load-filaments`** a nebyla otevřena ani změněna uživatelská konfigurace sliceru.

- Návratový kód **0**; vznikl [export nastavení po importu](audit-import-cli/whole-project-settings.json).
- Zachovány `filament_settings_id` s názvem **EXPERIMENT Alzament TPU95A Gray…**, výrobce Alzament, typ TPU, vlastní ID a teploty **225/225 °C a 60/60 °C**. Také experimentální proces zůstal zachován.
- SHA-256 vstupního 3MF před i po: `1c04a2b9552a54f4700226fa9cf96b08383968b373eedde3a96c2785f18a7ca7`. 3MF nebyl přepsán.
- Konzole dvakrát vypsala `calc_exclude_triangles:Unable to create exclude triangles`; export přesto úspěšně dokončila. Zkouška nic netvrdí o novém řezání nebo fyzickém tisku.
- [Záznam příkazu a výsledku](audit-import-cli/result.json) obsahuje přesné argumenty a hashe. Dočasný datový adresář byl po dokončení odstraněn.

Tento výsledek ověřuje místní **CLI import celého projektu**, nikoli libovolnou volbu v GUI importním dialogu, současný otevřený projekt ani průběh neúspěšného tisku. Nepotvrzuje, že se aktuální fyzická cívka shoduje s nastaveným typem.

## Co z toho plyne pro požadovaný název v GUI

Požadavek zobrazovat **ALZAMENT TPU 95A Gray** odpovídá skutečnému výrobku v evidenci. Náš původní balík již používá vlastní Alzament profil, avšak s delším experimentálním názvem. Místní export z 20:36 prokazuje jiné aktivní ID i teploty; samotné přejmenování jeho standardního Anycubic profilu by tento rozdíl nastavení neodstranilo.

Není doloženo, jak se GUI k tomuto stavu dostalo; možnost importu geometrie či ruční změny profilu zůstává hypotézou. Tento audit nic nepřejmenoval, nevybral a nesynchronizoval. Neprovádí přiřazení fyzického slotu ani cesty podávání; při tomto dílčím auditu nebyl vstup ověřen. Následné přímé hlášení Jiřího potvrzuje šedé TPU ve fyzickém vstupu 3, viz aktuální [záznam diagnostiky](README.md); nejde o přímou inspekci agentem. Čas 20:36 je čas souboru, nikoli doklad odeslání na tiskárnu.
