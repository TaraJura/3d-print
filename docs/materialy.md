# Materiály a profily

Stav zapsaný 19. 9. 2026. Důsledně rozlišovat údaje dodavatele, načtený default, doporučení a skutečný soubor či tisk.

## Materiál potvrzený uživatelem

**Alzament PLA Basic, 1,75 mm**, bílá a černá. První polička byla zvolena bílá. Nezaměňovat s PLA+, Silk ani HighSpeed.

| Údaj dodavatele | Rozsah |
|---|---:|
| Tryska | 190–220 °C |
| Podložka | 45–60 °C |
| Doporučená rychlost | 50–100 mm/s |
| Průměr filamentu | 1,75 mm |

Zdroje použité při přípravě: [Alzament na Alza.cz](https://www.alza.cz/alzament/v46531.htm), [filamenty Alza.cz](https://www.alza.cz/filamenty-pro-3d-tiskarny/18854774.htm). Jde o dodavatelské údaje, nikoli vlastní kalibraci cívky.

## Doporučení pro počáteční test

Jako start bylo navrženo použít profil **Anycubic PLA @Anycubic Kobra X 0.4 nozzle**, teploty 215 °C první / 205 °C další vrstvy a podložku 60 °C; extruzní rychlosti snížit nejvýše na **100 mm/s**. Sport pro první nezkalibrovaný test nebyl doporučen.

Toto je návrh výchozího testu, **nikoli změřená kalibrace ani potvrzené nastavení provedeného tisku**. Uživatel snížení rychlostí nepotvrdil a kontrolovaný lokální G-code je neměl snížené na 100 mm/s. Výsledek prvního tisku je zatím neznámý; viz [deník](denik-tisku.md).

## Skutečně načtené defaulty

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
