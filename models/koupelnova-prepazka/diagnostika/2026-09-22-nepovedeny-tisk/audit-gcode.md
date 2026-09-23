# Nezávislý audit zmrazených G-code a 3MF

Audit čte pouze původní soubory ze `evidence/`, nepřebírá dřívější kontrolní JSON. SHA-256 všech auditovaných souborů před a po čtení je shodné. Nic nebylo přegenerováno, odesláno ani spuštěno na tiskárně.

**Ve všech nalezených G-code jsou skutečné kladné extruzní pohyby ve 40 nebo 50 výškách, až do 8 nebo 10 mm. Žádný není programem pro jedinou vrstvu.** Zvednutí pro přejezdy (Z-hop) jsou z tohoto počtu vyloučena. Přítomné G90 a M83 určují absolutní souřadnice a relativní extruzi; audit zpracoval i případné G92/M82/G91 samostatně. Nebyl nalezen vložený pause/cancel, předčasné vypnutí ohřevu nebo motorů před posledním extruzním pohybem. Z toho nelze vyvodit, že firmware skutečně vykonal celý program nebo že materiál skutečně vytékal.

| Varianta | Tryska první / další vrstvy | Deska | Skutečná nejvyšší příkazová rychlost první / další extruze | Výška / vrstev | Čas normálně / tiše / sport |
|---|---|---|---|---|---|
| GUI 19:22, PLA | 220 / 205 °C | 60 °C | 100 / 250 mm/s | 10 mm / 50 | 57:23 / 1:34:31 / 50:25 |
| GUI 20:35, PLA | 220 / 205 °C | 60 °C | 100 / 250 mm/s | 8 mm / 40 | 49:39 / 1:22:01 / 43:34 |
| GUI 20:36, systémový TPU | 215 / 210 °C | 60 °C | 50 / 61,315 mm/s | 8 mm / 40 | 2:28:26 / 4:51:45 / 1:56:06 |
| Dodaný TEST, experiment TPU | 225 / 225 °C | 60 °C | 20 / 40 mm/s | 8 mm / 40 | 33:09 / 1:00:19 / 27:40 |
| Dodaná sestava 8 mm, experiment TPU | 225 / 225 °C | 60 °C | 20 / 40 mm/s | 8 mm / 40 | 5:54:08 / 11:11:18 / 4:45:55 |
| Historická sestava 10 mm, experiment TPU | 225 / 225 °C | 60 °C | 20 / 40 mm/s | 10 mm / 50 | 7:23:04 / 13:59:39 / 5:57:49 |

Rychlosti jsou přímo z pohybů s kladnou extruzí, nikoli pouze hodnoty v profilu. Překročení 50 mm/s na první vrstvě PLA pochází mimo jiné z první vrstvy výplně; maximum je 100 mm/s. Název materiálu v souboru není důkazem fyzicky vložené cívky.

| Zdroj | Objektů s extruzí | Skutečných extruzních Z | Nejvyšší extruzní Z [mm] | Nejvyšší příkazová extruzní rychlost [mm/s] | Materiál v G-code |
|---|---:|---:|---:|---:|---|
| `ACGcode3mf/9527/0922-1922-dil-1_plate(01)_PLA_0.2_57m23s.gcode.3mf!Metadata/plate_1.gcode` | 3 | 50 | 10 | 250.000 | PLA |
| `anycubicslicer_model/09_22_2/20_34_44#58503#50/Metadata/.58503.0.gcode` | 3 | 40 | 8 | 61.315 | TPU |
| `anycubicslicer_model/09_22_2/20_34_44#58503#50/Metadata/0922-2035-dil-1_plate(01)_PLA_0.2_49m39s.gcode` | 3 | 40 | 8 | 250.000 | PLA |
| `anycubicslicer_model/09_22_2/20_34_44#58503#50/Metadata/0922-2036-dil-1_plate(01)_TPU_0.2_2h28m26s.gcode` | 3 | 40 | 8 | 61.315 | TPU |
| `historie/reference-10mm/rozlozeni/EXPERIMENT-prepazka-B-Alzament-TPU95A.3mf!Metadata/plate_1.gcode` | 3 | 50 | 10 | 40.000 | TPU |
| `historie/reference-10mm/rozlozeni/experimentalni-slice/plate_1.gcode` | 3 | 50 | 10 | 40.000 | TPU |
| `rozlozeni/EXPERIMENT-prepazka-B-Alzament-TPU95A.3mf!Metadata/plate_1.gcode` | 3 | 40 | 8 | 40.000 | TPU |
| `rozlozeni/TEST-EXPERIMENT-spoj-Alzament-TPU95A.3mf!Metadata/plate_1.gcode` | 2 | 40 | 8 | 40.000 | TPU |
| `rozlozeni/experimentalni-TEST-slice/plate_1.gcode` | 2 | 40 | 8 | 40.000 | TPU |
| `rozlozeni/experimentalni-slice/plate_1.gcode` | 3 | 40 | 8 | 40.000 | TPU |

## Rozhodující rozdíly

- Dodaný TEST projekt obsahuje dvě uzavřené samostatné sítě, bez škálování, přibližně 30 × 20 × 8 mm; 40 skutečných extruzních vrstev, jediný profil TPU, 225/60 °C. Odhad je 33 m 9 s normálně, 60 m 19 s tiše, 27 m 40 s sport. Vestavěný G-code je byte-identický s uloženým vnějším souborem.
- GUI archiv 19:22 obsahuje skutečně profil **PLA**, počáteční trysku 220 °C a následně 205 °C, desku 60 °C, 2 stěny a 15% výplň. Má 50 extruzních vrstev do 10 mm. Proces se liší od našeho experimentálního TPU projektu.
- GUI G-code 20:35 je opět **PLA 220→205 °C**, 40 vrstev do 8 mm. GUI 20:36 je systémový **TPU 95A 215→210 °C**, rovněž 40 vrstev do 8 mm, 2 stěny a 15% výplň; také se liší od dodaného experimentu 225 °C / 4 stěny / 100% výplň.
- Žádný časový odhad nalezeného souboru přesně neodpovídá hlášenému dokončení za 88 min. Přibližné časy nejsou spolehlivým identifikátorem úlohy a skutečně použitý soubor zatím není potvrzen.
- Příkaz G9111 je firmwarem definované zahájení tisku; jeho interní chování a případná nastavení/rychlostní režimy uložené v tiskárně nejsou součástí těchto souborů a tento audit je nepotvrzuje.

Podrobný `audit-gcode.json` uvádí hashe, shodu embedded/external, geometrické komponenty, příkazové i skutečně parsované výšky extruze, počty pohybů po vrstvách, rychlosti podle typu dráhy, režimy E/G92, teplotní příkazy a řádky začátku/konce. Záznamy se stejným hashem G-code jsou auditovány jednou a propojeny se všemi kopiemi. Výsledek neprokazuje fyzickou příčinu selhání ani vinu uživatele.
