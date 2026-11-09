# Kontrola skutečných drah — otevřené V, 30. 10. 2026

Kontrola vychází z G-code ve finálním nastaveném projektu 3MF. SHA-256 navazuje na finální STL v `kontrola-rezani.json`; detail mostků je navázaný na stejné G-code v `kontrola-mostku.json`. Tiskárna nebyla ovládána.

- Prohlédnut očíslovaný náhled: 1 fyzický kus, délka X 230 mm v rovině podložky. Instalovaná svislá osa je v tiskové ose Z. Tisková obálka je 230 × 45,243 × 54,996 mm.
- První vrstva obsahuje souvislou spodní patku, dvě výztužná žebra a dvě montážní ouška. Všechny jsou digitálně propojené. Kolem jejich skutečné první vrstvy je 3mm brim.
- Prohlédnuty skutečné vrstvy při růstu V: patka navazuje na postupně rozšiřovaný profil, zaoblená vnitřní drážka se otevře nad dnem. Stěny pokračují pod návrhovými 45° a nepotřebují v této orientaci doplněné podpory.
- Oba vodorovné montážní otvory Ø5,5 mm zůstávají otevřené. Samostatné detaily obou otvorů ukazují skutečné vrstvy Z 43,0 až 46,0 mm. Na vrcholu se otvor postupně zužuje, v Z 45,8 mm jsou místní převisové stěny a v Z 46,0 mm ho uzavřou tři mostové tahy. Nejdelší celá mostová extruzní úsečka v této kontrolované vrstvě má 5,944 mm; obsahuje i část na materiálu a není to měření nepodepřené mezery. Předchozí vrstva je v náhledu šedá, nové dráhy tmavé a mosty/převisy oranžové.
- Další růst zaoblených oušek směřuje dovnitř. V nejvyšší vrstvě Z 55,0 mm nenastává nový volný ostrov.

Automatický graf návaznosti skutečných drah prošel všech **275 vrstev** bez nových nepřipojených ostrovů a bez podporových výjimek. Podpory jsou skutečně vypnuté a G-code obsahuje **0 segmentů podpor**. Slicer neopravil žádnou síť a nehlásí přesah podložky. Nejmenší rezerva modelových extruzí a brimu od okraje podložky je **5,386 mm**.

Náhled vrstev a graf neprokazují fyzickou přilnavost, kvalitu mostků, pevnost, montážní kotvy ani stabilitu konkrétního nože. Vršky otvorů a případné otřepy po tisku prohlédnout. Výsledek je digitálně připravený prototyp.

Slicer hlásí `not_support_traditional_timelapse`; CLI vypisuje `calc_exclude_triangles:Unable to create exclude triangles`. Řez proto není označený jako bezvarovný.
