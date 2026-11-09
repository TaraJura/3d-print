# Pokerový pohár — Praha, 9. 10. 2026

Jednobarevná trofej pro Jiřího Nováka, vítěze pokerového turnaje. Jeden tisknutelný kus: otevřená pohárová miska s lemem, dřík, dvě reliéfní esa (piky a srdce) a stabilní zaoblený podstavec. Na čele **POKER / VÍTĚZ / PRAHA / 9. 10. 2026**, zezadu **JIŘÍ / NOVÁK**. Žádné lepení ani množení dílů.

## Hotový tiskový projekt

Otevřít **[rozlozeni/podlozka-01-kobra-x-zlaty-silk-projekt.3mf](rozlozeni/podlozka-01-kobra-x-zlaty-silk-projekt.3mf)** v Anycubic Slicer Next jako **celý projekt**, jednou. Obsahuje jednu fyzickou kopii na jedné podložce, správnou polohu a proces; nic ručně nepřerovnávat, nemnožit ani automaticky neotáčet. [Přehled podložky a kontrol](rozlozeni/README.md).

Skutečný místní odhad sliceru: **1 h 38 min 03 s, 25,46 g, 430 vrstev**. Rezerva vůči požadavku max. 2 h je 21 min 57 s. Jde o odhad stroje, nikoli záruku doby včetně obsluhy, nahřívání a konkrétních změn rychlosti tiskárny.

| Nastavení | Předaný projekt |
|---|---|
| Tiskárna / tryska | Anycubic Kobra X / 0,4 mm |
| Materiál | Alzament PLA Silk Gold, 1,75 mm, `ALZMNTS07` |
| Barvy / logické filamenty | 1 zlatý; bez změn filamentu a bez čisticí věže |
| Vrstva | 0,20 mm |
| Stěny / výplň | 2 / 8 % gyroid, Arachne pro malé detaily |
| Tryska / podložka | 225 °C první, 220 °C další / 50 °C |
| Vnější / vnitřní stěny | 45 / 80 mm/s, maximální objemový průtok 6 mm³/s |
| Podpory / přilnavost | Bez podpor / 3mm brim |

Zlaté **Alzament PLA Silk** je doložené v [kanonickém skladu](/home/novakj/3d-print/docs/materialy.md). Teploty a rychlosti jsou návrhový profil této trofeje podle dodavatelského rozsahu; fyzická kalibrace této cívky chybí. Aktuální hmotnost cívky a skutečný vstup/slot jsou neověřené. Historické hlášení 22. 9. 2026 pouze říká, že Jiří zaváděl zlato do vstupu 4; dokončení ani dnešní stav nepotvrzuje. Před spuštěním vybrat skutečnou zlatou cívku, nikoli odvozovat vstup z barvy náhledu.

## Návrhové rozměry a zdroje

Rozměry zvolil autor podle časového limitu, uživatel je nezadával ani fyzicky neměřil. Výška **86 mm**, maximální obrys **58 × 58 mm** (miska Ø58); kontaktní pata **58 × 40 mm**, výška paty 2 mm. Podstavec 50 × 32 × 20 mm nad patou, stěna misky přibližně 2 mm. Reliéf nápisů 0,55 mm. Miska je dekorativní trofej.

- [pohar.FCStd](pohar.FCStd): editovatelný FreeCAD 1.1.3, standardní Part objekty, tabulka `Parameters`, výrazy, uložené obrysy textu; přepočet nevyžaduje vlastní Python třídu ani font.
- [pohar.FCMacro](pohar.FCMacro): zdroj, obsahuje návrhové hodnoty a upozornění na přepisování. Spustit skutečným FreeCADem, ne systémovým Pythonem. Obnoví FCStd, STL a kontrolní JSON v této složce; ruční změny tabulky nepřenáší zpět do zdroje. Při změně sladit makro, export, náhled a znovu nařezat 3MF.
- [stl/pohar.stl](stl/pohar.stl): jedna uzavřená síť, bez tiskového procesu.
- [nahled-cad.png](nahled-cad.png), [čelní](nahled-celni.png), [zadní](nahled-zadni.png): skutečná CAD geometrie, zlatá barva je pouze vizualizace.
- [nahled.FCMacro](nahled.FCMacro): reprodukovatelné skutečné CAD náhledy a kontrola uložené viditelnosti.
- [kontrola-modelu.json](kontrola-modelu.json): výsledky CAD, STL, znovuotevření a změn parametrů.

## Provedené kontroly a omezení

CAD je platný, jeden solid, rozměry 58 × 58 × 86 mm, Z=0 na podložce. Exportovaná STL byla znovu načtena: jedna uzavřená komponenta. Uložený FCStd zobrazuje pouze finální `Pohar`; pomocné tvary jsou skryté. Změna výšky misky 33 → 35 → 33 mm i šířky podstavce 50 → 52 → 50 mm prošla standardním přepočtem, po kontrole byly návrhové hodnoty obnoveny.

Geometrie používá mírně rozevřený kužel a karty nakloněné v rovině o 13°; vyhýbá se visícím uchům a velkým vodorovným převisům. Podpory jsou skutečně vypnuté v projektu. Přehled skutečných drah, čitelných nápisů a případných diagnostik je v dokumentaci podložky. Brim slouží pouze přilnavosti.

**Stav: digitálně připraveno a nařezáno.** Agent nic neodeslal do tiskárny, neprovedl tisk ani neověřil fyzickou první vrstvu, lesk, čitelnost nebo stabilitu výtisku. Commit ani push nebyly provedené.
