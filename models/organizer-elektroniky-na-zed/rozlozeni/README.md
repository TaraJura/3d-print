# Organizér elektroniky · návrh k posouzení, podložka 01

**Neschválený návrh k prohlédnutí. 1 podložka / 1 fyzický kus.** Digitální příprava není pokyn ke spuštění tisku. Otevřít [nastavený a nařezaný projekt](podlozka-01-kobra-x-pla-projekt.3mf) jednou jako celý projekt v Anycubic Slicer Next. Žádné množení ani přerovnávání. Projekt obsahuje geometrii, profily i skutečný G-code.

**Odhad sliceru: 44 h 1 min 46 s / 1066.92 g.** Čas a spotřeba jsou výpočty sliceru, fyzický výsledek není ověřený. **Odhad přesahuje 1 kg: jedna nová nominální 1kg cívka nestačí.** Případné pokračování materiálu/výměna není nastaveno ani fyzicky ověřeno.

Tiskárna **Anycubic Kobra X 0,4 mm**, potvrzená plocha profilu 260 × 260 × 260 mm. Půdorys modelu **246 × 246 mm**, výška 150 mm. Na podložce X/Y 7–253 mm, dnem dolů. Prázdné `bed_exclude_area` a `head_wrap_detect_zone`; uživatelská systémová kopie profilu shodná s instalovanou. Profil volá inicializaci firmwaru `G9111`; její vnitřní pohyby nejsou v exportovaném G-code rozvinuté, a proto je audit nekontroluje. Pro 5mm brim, 0,1mm mezeru a okraj byl zvolen tento praktický maximální půdorys. Konzervativní zbývající okraj skutečné extruze včetně poloviny největší deklarované šířky je **2.277 mm**.

| Parametr | Nastavení |
|---|---|
| Vrstva / první vrstva | 0,24 / 0,20 mm |
| Stěny / výplň | 5 stěn / 25 % gyroid |
| Horní / dolní vrstvy | 5 / 5, minimálně 1,20 / 1,16 mm |
| Brim | Vnější, 5 mm; mezera 0,1 mm |
| Podpory / čisticí věž | Vypnuté / vypnutá |
| Tryska první / další vrstvy | 215 / 205 °C |
| Texturovaná podložka | 50 °C |
| Vnější / vnitřní stěny | 50 / 75 mm/s |
| Výplň / první vrstva | 80 / 25 mm/s |
| Maximální objemový průtok | 8 mm³/s |

Materiálový předpoklad: **Alzament PLA Basic 1,75 mm**, počáteční návrhový profil odvozený ze systémového Anycubic PLA pro Kobra X. Není fyzicky kalibrovaný. Barva náhledu je pouze vizualizace; aktuální cívka, slot, zůstatek a připravenost tiskárny nejsou potvrzené. Před spuštěním je nutné u tiskárny ověřit odpovídající PLA Basic, dostatečný zůstatek pro uvedenou spotřebu, správné přiřazení a volnou připravenou podložku. [Materiálová evidence](../../../docs/materialy.md).

[Očíslovaný náhled podložky](podlozka-01.png), [skutečné vrstvy](podlozka-01-vrstvy.png) a [detail skutečných drah čtyř otvorů](podlozka-01-uchyceni-vrstvy.png). [Kontrola řezání](kontrola-rezani.json) obsahuje hashe, nastavení, rozměry, počty, opravy sítě, skutečné dráhy a test spojitosti. Jediný objekt stojí na první vrstvě, všechny 625 vrstvy obsahují extruzi a žádná extruze nepřesahuje plochu. Po importu a řezu zůstaly geometrie, měřítko, orientace a počet zachované; opravy sítě 0. Test nových nepřipojených ostrůvků: **nedokončen v časovém limitu; úplná spojitost neprokázána**. Je to graf skutečných drah s tolerancí 0,71 mm vůči předchozí vrstvě; nezaručuje plnou podporu každého místa převisu. Svislé stěny, žebra a 45° stříšky otvorů byly zvoleny pro tisk bez podpor. Ve výškách 120,20 a 140,12 mm slicer uzavírá stříšky krátkými mosty; nejdelší celá dráha má 5,512 mm včetně ukotvení na materiálu, nikoli volného rozpětí. Detail je v náhledu uchycení. Brim pomáhá přilnavosti a podpory nenahrazuje.

Varování sliceru: **not_support_traditional_timelapse**. CLI dále uvedlo `calc_exclude_triangles:Unable to create exclude triangles`; obě operace skončily exit 0. Příčina hlášky nebyla nezávisle určena, prázdné vyloučené zóny a skutečná obálka drah byly ověřeny. Nejde o bezvarovný řez.

[Geometry-only 3MF](podlozka-01-geometrie.3mf) je alternativa stejného kusu bez procesu, filamentu a G-code. **Netisknout navíc.** Pro přímé použití slouží nastavený projekt.

Regenerace po aktualizaci STL: `python3 pripravit-podlozku.py`. Přepíše pouze soubory v této složce; diagnostika a izolované datadiry jsou v ignorované `.cache/`. Změny globálních presetů ani komunikaci s tiskárnou neprovádí. `--audit-only` zopakuje pouze kontrolu drah existujícího projektu.

**Žádná tisková úloha nebyla odeslána ani spuštěna. Fyzický tisk, montáž, kotvení a nosnost zůstávají neověřené.**
