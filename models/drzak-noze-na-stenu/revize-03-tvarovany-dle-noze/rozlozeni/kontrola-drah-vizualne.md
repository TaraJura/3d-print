# Kontrola drah — tvarovaný držák V03, 30. 10. 2026

Kontrola vychází z G-code ve finálním nastaveném projektu 3MF. SHA-256 navazuje na finální STL v `kontrola-rezani.json`; detaily otvorů a přechodu jsou navázané na stejný G-code v `kontrola-mostku.json`. Tiskárna nebyla ovládána.

- Prohlédnut očíslovaný náhled: 1 fyzický kus, délka X 230 mm v rovině podložky. Instalovaná svislá osa Y je tisková Z. Tisková obálka je 230 × 42,314 × 59,996 mm.
- První vrstva má souvislou spodní patku, dvě výztužná žebra a dvě montážní ouška. Kolem skutečné první vrstvy je 3mm brim. Svislé stojiny navazují na patku a nesou obě sedla.
- Prohlédnuty skutečné vrstvy při růstu šikmého sedla čepele a vyššího, širšího sedla rukojeti. Stěny se rozšiřují postupně pod návrhovými 45°, vnitřní zaoblené drážky se otevřou nad jejich dny. Nevzniká plovoucí střecha nad dutinou.
- Detail přechodu ukazuje souvislé propojení patkou do Z 4,0 mm. Od Z 4,2 mm zůstává mezi sedly otevřený 10mm přechod. Automatická kontrola všech vrstev nad patkou nalezla **0 extruzních tahů v jeho vnitřních 9,4 mm**; 0,3mm okraje jsou vynechané kvůli šířce obvodové extruze. Most přes tento přechod se netiskne.
- Oba vodorovné montážní otvory Ø5,5 mm zůstávají otevřené. Samostatné detaily obou otvorů ukazují skutečné vrstvy Z 48,0 až 51,0 mm. Na vrcholu se otvor zužuje, v Z 50,8 mm jsou místní převisové stěny a v Z 51,0 mm jej uzavřou tři mostové tahy. Nejdelší celá mostová extruzní úsečka má 5,944 mm; obsahuje i část na materiálu a není to měření nepodepřené mezery. Předchozí vrstva je šedá, nové dráhy tmavé a mosty/převisy oranžové.
- Další růst zaoblených oušek směřuje dovnitř. Nejvyšší vrstva je Z 60,0 mm.

Automatický graf návaznosti drah prošel všech **300 vrstev** bez nových nepřipojených ostrovů a bez podporových výjimek. Podpory jsou skutečně vypnuté a G-code obsahuje **0 segmentů podpor**. Slicer neopravil žádnou síť a nehlásí přesah podložky. Nejmenší rezerva modelových extruzí a brimu od okraje podložky je **5,386 mm**.

Náhled a graf neprokazují fyzickou přilnavost, kvalitu mostků, pevnost úzkého spojení, montážní kotvy, přesný fit ani stabilitu skutečného nože. Po tisku prohlédnout vršky otvorů a odstranit otřepy. Výsledek je digitálně připravený prototyp.

Slicer hlásí `not_support_traditional_timelapse`; CLI vypisuje `calc_exclude_triangles:Unable to create exclude triangles`. Řez proto není označený jako bezvarovný.
