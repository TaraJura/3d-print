# Podložka 01 – nástěnný držák krabičky LaskaKit MAXI RFID

| Podložka | Fyzické díly | Otevřít v Anycubic Slicer Next | Alternativa bez profilu | Náhledy |
|---|---:|---|---|---|
| 01 | 1× jednodílný držák | [Nastavený a místně nařezaný projekt](podlozka-01-nastaveny-projekt.3mf) | [Pouze geometrie](podlozka-01-geometrie.3mf) | [Poloha skutečného STL](podlozka-01.png), [skutečná první vrstva](prvni-vrstva-01.png), [kritické vrstvy](kriticke-vrstvy-01.png) |

**Otevři jen jednu variantu této podložky, právě jednou.** Geometrická a nastavená varianta jsou dvě podoby téhož jednoho dílu, nikoli dva kusy k tisku. Umístění a měřítko 1:1 jsou již připravené; automatické přerovnání nebo další kopii nepřidávej. Nastavený projekt obsahuje tiskárnu, proces, filamentový návrh a místní G-code. Geometrická alternativa obsahuje jen STL geometrii a polohu bez procesu, filamentu, podpor a G-code a nemá tiše měnit uživatelovy presety.

## Skutečné nastavení a řez

- Stroj: **Anycubic Kobra X, tryska 0,4 mm**, tiskový prostor 260 × 260 × 260 mm. Jeden díl má obálku 238 × 189 × 80 mm a stojí na spodní hraně obruče, nízkých spojek a montážních patek; dno držák nemá. Geometrický okraj od podložky je nejméně 11 mm.
- Proces vychází ze systémového profilu **0,20 mm Standard**. V předaném projektu je vrstva 0,20 mm, 4 stěny, 25 % gyroid, vnější 5mm brim, podpory vypnuté, první vrstva 25 mm/s, vnější stěny 50 mm/s a vnitřní stěny 75 mm/s.
- Filament je **návrhový, nekalibrovaný profil Alzament PLA Basic**, odvozený z Anycubic PLA: tryska 215 °C první / 205 °C další vrstvy, texturovaná podložka 50 °C. Název, barva náhledu ani 3MF nepotvrzují nasazení fyzické cívky nebo její slot. Při změně materiálu či procesu je třeba znovu řezat a kontrolovat dráhy.
- Místní řez obsahuje **400 vrstev do výšky 80 mm**. Odhad sliceru je **8 h 55 min 52 s / 160,85 g**. Všechny vrstvy mají extruzi, jeden objekt zůstal zachovaný, skutečný brim má 691 segmentů a extruzní dráhy mají od hrany podložky nejméně **6,56 mm**. Slicer uvedl `outside=false`.
- Podpory jsou skutečně vypnuté a G-code má **0 segmentů podpor**. Zvýšené výztuhy jsou až za zadní hranou obruče; spojky pod nimi dosahují k podložce. Podél boků obruče už nic nevystupuje nad její horní rovinu 30 mm. Na **zadní straně u stěny** jsou dva 40mm výseky od horní hrany, se zatím návrhovou hloubkou **12 mm**; strana a hloubka čekají na potvrzení podle skutečných pantů. Kontrolní náhled ukazuje Z 18,2 / 29,2 / 48 / 73 mm, včetně horních výseků, krátkých mostů přes montážní otvory a vnitřních mostů nad výplní. Audit eviduje 3 508 segmentů mostů či převisových stěn (z toho 3 296 vnitřních mostů nad výplní). Skutečnou kvalitu mostů, průchodnost otvorů a možnost nasazení krabičky lze potvrdit až po fyzickém tisku.
- V metadatech řezu zůstalo varování `not_support_traditional_timelapse`; CLI navíc zaznamenalo `calc_exclude_triangles: Unable to create exclude triangles`. Neoznačujeme řez jako bezvarovný. Použitá podložka nemá ve strojovém profilu vyloučenou oblast a audit skutečných drah zjistil bezpečné hranice extruze; příčina hlášky CLI nebyla samostatně určena.

[Kontrola geometrického rozložení](overeni-rozlozeni.json), [kontrola místního řezu](overeni-rezu.json) a [kontrola skutečných drah](kontrola-drah.json) dokládají počty, použité profily, hashe a rozsah kontroly. Výchozí STL bylo při tomto běhu `7aa12e55f7feb787c1dff9e9a8806b92e455b5d9edc65a8e29a1c48a69b9c6df` (SHA-256). Projekt lze reprodukovat z kořene repozitáře postupně:

```bash
python3 models/drzak-krabicky-laskakit-rfid/rozlozeni/vytvor-podlozku.py
python3 models/drzak-krabicky-laskakit-rfid/rozlozeni/pripravit-projekt.py --supports off
python3 models/drzak-krabicky-laskakit-rfid/rozlozeni/overit-drahy.py
```

Parametr `--supports` je povinné vědomé rozhodnutí po kontrole aktuální geometrie; při její změně nelze automaticky převzít `off`. Skripty přepisují výstupy pouze v této složce a místně spouštějí slicer; tiskárnu neovládají.

**Fyzicky neověřené:** skutečná velikost a přesah víka krabičky, poloha a rozměry pantů vůči zadním výsekům, dosednutí do obruče, pevnost a nosnost vytištěného dílu, typ stěny, šrouby a hmoždinky, kvalita mostů, tisk a zavěšení. Nastavený projekt je počítačově připravený prototyp, nikoli potvrzený funkční držák. Než ponese krabičku, ověř konkrétní uchycení a zatížení na místě.
