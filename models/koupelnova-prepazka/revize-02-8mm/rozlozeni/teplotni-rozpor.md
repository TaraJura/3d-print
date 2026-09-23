# Teplota podložky — opětovně ověřeno 22. 9. 2026

Pro Alzament TPU 95A Gray **neexistuje teplota podložky v průniku obou dostupných primárních podkladů**:

| Podklad | Tryska | Podložka |
|---|---:|---:|
| [Konkrétní produkt Gray, ALZMNTTPU03](https://www.alza.cz/alzament-tpu-95a-1-kg-gray-d13015353.htm) | 190–230 °C | 30–50 °C |
| [Alzament TPU 95A Technical Data Sheet V1.0, strana 1](https://dwn.alza.cz/manual/161249) | 220–240 °C | 60–80 °C |

PDF bylo ověřeno textově i skutečným vykreslením první strany. Označení je **V1.0**; extraktor může připojit číslo následující stránky 2 a vytvořit zavádějící `V1.02`. TDS výslovně zahrnuje Textured PEI Plate a uvádí také ošetření povrchu lepidlem; přesný prostředek a jeho použití na tiskové desce zde nejsou fyzicky ověřené. Tisková deska není koupelnová kachlička a toto není pokyn nanášet montážní Fix ALL na tiskárnu.

Tryska 225 °C leží v průniku 220–230 °C. Podložka 60 °C byla vědomě zvolena jako spodní mez TDS a současně default pro Textured PEI ve skutečném místním profilu **Anycubic TPU 95A @Anycubic Kobra X 0.4 nozzle**. Tento profil i uložené účinné nastavení obsahují `temperature_vitrification = 60` a teplotu texturované desky60 °C. Hodnota `temperature_vitrification` je zděděná hodnota profilu Anycubic, nikoli doložené měření Alzamentu.

Oba experimentální projekty mají skutečně exportovanou desku 60 °C v první i dalších vrstvách a varování `bed_temperature_too_high_than_filament`. Nejde o zapomenutý 60°C příkaz po deklarované změně na 50 °C. Výstraha nebyla umlčena změnou prahu ani editací G-code.

**Podmínka výstrahy:** veřejný [zdroj AnycubicSlicerNext, commit 987a3c2, GCodeProcessor.cpp](https://github.com/ANYCUBIC-3D/AnycubicSlicerNext/blob/987a3c2bf9ed13934137326bfd522896c70e5101/src/libslic3r/GCode/GCodeProcessor.cpp#L5036-L5051) přidává `BED_TEMP_TOO_HIGH_THAN_FILAMENT` / `1000C001`, pokud je nenulová maximální teplota desky alespoň rovná nenulové `temperature_vitrification` použitého filamentu. Zde tedy 60 ≥ 60. Teplota 50 °C v obou fázích by podle této podmínky výstrahu nevyvolala, ale neřeší rozpor s TDS a nebyla nově řezána. Shoda uvedeného veřejného commitu s místní binárkou 2.0.0.5 není doložená; pozorovaná výstraha a její kód odpovídají.

**Proč nyní nepřepínat na 50 °C jen kvůli výstraze:**50 °C splňuje prodejní stránku, ale je pod minimem 60 °C v TDS. Změna by znamenala výběr jiného rozporného podkladu, nikoli nalezení společného doporučení. Bez určení, který údaj platí pro konkrétní výrobek/šarži, nelze slíbit profil vyhovující oběma zdrojům a současně bez varování. Rozpor má vyjasnit výrobce/dodavatel nebo údaj na konkrétní cívce; následně lze upravit proces a přegenerovat oba řezy. To je odlišné od následné fyzické kalibrace průtoku, první vrstvy, rozměru a přilnavosti.

Geometrie se tímto auditem nemění. Současné 3MF zůstávají místně úspěšně řezanými **experimentálními** projekty s přiznanými předpoklady. Agent nic neodeslal tiskárně a nepotvrdil konkrétní zahájený tisk.
