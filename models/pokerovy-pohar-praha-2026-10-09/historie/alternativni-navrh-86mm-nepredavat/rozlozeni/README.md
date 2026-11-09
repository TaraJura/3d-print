# Pokerový pohár — jedna připravená podložka

**Otevřít [podlozka-01-kobra-x-zlaty-silk-projekt.3mf](podlozka-01-kobra-x-zlaty-silk-projekt.3mf) jako celý projekt v Anycubic Slicer Next.** Je vložený právě **1× celý pohár**, nastojato na podstavci. Neimportovat navíc STL, nenásobit, nepřerovnávat a neotáčet. Podložka je pro **Anycubic Kobra X, trysku 0,4 mm**, ve skutečném měřítku 1:1; model má 58 × 58 × 86 mm.

| Podložka | Skutečné kusy | Odhad sliceru | Materiál |
|---|---:|---:|---|
| [01 — očíslovaný náhled](podlozka-01.png) | 1 pohár | **1 h 38 min 03 s / 25,46 g / 8,53 m** | Alzament PLA Silk Gold 1,75 mm, `ALZMNTS07` |

Odhad má proti dvouhodinovému zadání rezervu asi 22 minut; skutečný čas a spotřeba nejsou změřené. Jedna logická zlatá barva, bez výměn filamentu a bez purge tower. Skutečně vloženou zlatou cívku a fyzický vstup tiskárny je potřeba při případném spuštění správně přiřadit. Historické hlášení z 22. 9. o zavádění do vstupu 4 nepotvrzuje dnešní stav. Nebyla odeslána ani spuštěna tisková úloha.

## Skutečně uložené nastavení

- Vrstva 0,20 mm, 430 vrstev; 2 stěny, Arachne, 8 % gyroid; 4 horní a 4 spodní vrstvy.
- Tryska **225 °C první / 220 °C další vrstvy**, texturovaná podložka **50 °C**.
- Vnější stěny a horní povrch 45 mm/s; vnitřní stěny a řídká výplň 80 mm/s; plná vnitřní výplň 70 mm/s; první vrstva 25 mm/s. Malé obvody se zpomalují. Maximum objemového průtoku **6 mm³/s**.
- Podpory **vypnuté**, vnější brim **3 mm**, mezera 0,1 mm. Brim pomáhá přilnavosti; není podporou převisů.
- Zachovaný kompatibilní základ `Anycubic PLA @Anycubic Kobra X 0.4 nozzle`, upravený a pojmenovaný pro Alzament PLA Silk Gold. Profil je **návrhový, bez fyzické kalibrace**. Hustota 1,24 g/cm³ pro odhad hmotnosti je zděděná z tohoto základu, nikoli vlastní měření Silk cívky.

[Produktová stránka Alza pro přesný Gold `ALZMNTS07`](https://www.alza.cz/alzament-pla-silk-1-kg-gold-d12869930.htm), ověřená 9. 10. 2026, uvádí trysku 210–230 °C, podložku 45–60 °C a rychlost 40–250 mm/s; pro detaily popis doporučuje přibližně 50 mm/s. Profil zůstává uvnitř těchto teplotních rozsahů a omezuje vnější stěny i průtok. Rychlosti první vrstvy, malých obvodů a mostů jsou záměrně nižší návrhové hodnoty. Cívka je doložena v [kanonické evidenci materiálů](/home/novakj/3d-print/docs/materialy.md), současný zůstatek není známý. Barva v projektu nepotvrzuje fyzickou cívku.

## Provedená kontrola

Projekt byl skutečně lokálně nařezaný Anycubic Slicer Next 2.0.0.5 a obsahuje skutečný G-code. Ověřena byla jedna fyzická kopie, správná tiskárna/tryska, mm, 1:1, nezměněné vrcholy/rozměry/umístění, nulové opravy sítě, extruze ve všech 430 vrstvách a do Z = 86 mm, první vrstva s brimem, dráhy uvnitř podložky, nepřítomnost podpor i purge tower a startovací teploty G-code. Slicer nezaznamenal varování.

- [Vybrané skutečné vrstvy](podlozka-01-vrstvy.png) ukazují první vrstvu, podstavec, karty/dřík a růst otevřené misky.
- [Čelní projekce skutečných drah reliéfu](nahled-reliefu-drahy.png) zachycuje `POKER`, `VÍTĚZ`, `PRAHA`, datum `9. 10. 2026`, zadní `JIŘÍ NOVÁK`, dvě `A` a velké symboly ♠ a ♥. Akcenty a drobný datum jsou v drahách zachované; fyzická čitelnost čeká na výtisk. Projekce není simulace povrchu.
- Vzorkování 553 324 bodů stěn zaznamenalo 4 body vzdálené přes 0,5 mm od předchozích drah, **žádný přes 1 mm**. Jde o lokální kontrolu růstu stěn, ne o záruku fyzické tisknutelnosti. Kužel misky se rozšiřuje zhruba 32,5° od svislice; karty mají 13° a reliéf vyčnívá 0,55 mm.
- Podrobná evidence včetně hashů: [kontrola-rezani.json](kontrola-rezani.json).

CLI během úspěšného řezu (exit 0) zapsalo známou zprávu `calc_exclude_triangles:Unable to create exclude triangles`. Geometrie, počet kusů, nastavení a celistvé extruzní dráhy byly následně nezávisle ověřeny. Funkce vynechání jednotlivého objektu za fyzického tisku nebyla zkoušená.

Fyzický tisk, první vrstva, lesk, čitelnost, stabilita a odstraňování brimu nejsou potvrzené.

## Reprodukce a alternativa

`python3 pripravit-projekt.py` čte `../stl/pohar.stl` a přepíše zdejší profily, geometrii, nastavený 3MF, kontrolu a náhled podložky/vrstev. Používá izolované datadir a logy v ignorované `.cache/`; nemění globální presety. Následně `python3 overit-drahy.py` doplní kontrolu návaznosti stěn a čelní náhled reliéfu. Při regeneraci zachovat oba kroky.

[podlozka-01-geometrie.3mf](podlozka-01-geometrie.3mf) je pouze alternativní geometry-only podložka bez procesu, filamentu a G-code. **Netisknout navíc**; pro přímé otevření použít nastavený projekt výše.
