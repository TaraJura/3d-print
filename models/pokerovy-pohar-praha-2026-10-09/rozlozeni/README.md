# Pokerový pohár · jedna podložka

**1 podložka / 1 fyzický kus / jedna barva: zlatá.**

Otevřít [nastavený projekt](podlozka-01-kobra-x-zlaty-silk-projekt.3mf) jednou jako celý projekt v Anycubic Slicer Next. Pohár je nastojato a na středu podložky; nic nekopírovat ani nepřerovnávat. Projekt obsahuje skutečný místně vytvořený G-code.

**Odhad sliceru: 1 h 44 min 18 s / 31.15 g.** Skutečný čas, spotřeba a výsledek dosud nejsou ověřené.

Tiskárna **Anycubic Kobra X, tryska 0,4 mm**, plocha 260 × 260 mm. Návrhový profil **Alzament PLA Silk Gold**:

| Parametr | Nastavení |
|---|---|
| Vrstva / první vrstva | 0,24 / 0,20 mm |
| Stěny, výplň | 2 stěny, 10 % gyroid |
| Horní / dolní vrstvy | 4 / 4 |
| Brim | Vnější, 3 mm |
| Podpory / čisticí věž | Vypnuté / vypnutá |
| Tryska / texturovaná podložka | 220 / 50 °C |
| Vnější / vnitřní stěny | 50 / 80 mm/s |
| Výplň / první vrstva | 80 / 25 mm/s |
| Maximální objemový průtok | 5,5 mm³/s |

Profil je počáteční návrh bez fyzické kalibrace. [Dodavatelská stránka Gold](https://www.alza.cz/alzament-pla-silk-1-kg-gold-d12869930.htm), ověřena 9. 10. 2026, uvádí 210–230 °C / podložku 45–60 °C / 40–250 mm/s a pro jemné detaily kolem 50 mm/s. Zvolený návrh leží uvnitř teplotních rozsahů; snížení první vrstvy a převisů je vědomé.

Před tiskem zkontrolovat skutečnou zlatou cívku a její mapování. [Materiálová evidence](../../../docs/materialy.md) potvrzuje převzetí zlata; večer 22. 9. bylo hlášeno probíhající zavádění do vstupu 4 bez potvrzení dokončení. **Nynější slot není ověřený.** Barva modelu není důkaz fyzického slotu.

[Očíslovaný náhled podložky](podlozka-01.png) a [náhled skutečných vrstev](podlozka-01-vrstvy.png). [Kontrola řezání](kontrola-rezani.json) obsahuje hashe, kontroly sítě a objektu, parametry a skutečné dráhy. Všechny vrstvy obsahují extruzi, jediný objekt stojí na první vrstvě, dráhy jsou uvnitř podložky. Kontrola nových ostrůvků: **prošla**, podrobnosti viz JSON. Test spojitosti cest neposuzuje plnou podporu každého místa převisu; samonosnost kužele a drobné reliéfy jsou posouzeny samostatně. Brim pomáhá přilnavosti a nepodpírá převisy.

Slicer uvedl pouze informační varování k nepodporovanému tradičnímu časosběru. Opravy sítí: 0; přesah podložky: ne. CLI navíc vypisuje `calc_exclude_triangles:Unable to create exclude triangles`; obě operace skončily s exit 0 a zachování geometrie, počtu i umístění bylo ověřeno samostatně. Funkce vynechávání objektů nebyla fyzicky zkoušena.

[Geometry-only 3MF](podlozka-01-geometrie.3mf) je alternativa stejného jednoho kusu bez procesu/filamentu/G-code; **netisknout navíc**. Pro přímé použití slouží nastavený projekt.

Regenerace: `python3 pripravit-podlozku.py`. Generátor přepíše zdejší podložky, náhledy, kontrolní JSON a profily; logy/datadir zůstávají v ignorované `.cache/`. Nezmění globální uživatelské presety a neprovádí tiskárnové I/O. G-code zůstává uvnitř projektu a v ignorované cache.

**Žádná úloha nebyla odeslána nebo spuštěna. Fyzický tisk, lesk, čitelnost drobného reliéfu a odstranění brimu neověřeny.**
