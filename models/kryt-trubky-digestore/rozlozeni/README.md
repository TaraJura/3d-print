# Podložka 01 – zaoblený kryt

| Podložka | Fyzické kusy | Soubor k prohlédnutí | Alternativa bez profilu | Náhled |
|---|---:|---|---|---|
| 01 | 1× zaoblený kryt | [Nastavený a nařezaný projekt](kryt-podlozka-01-nastaveny-projekt.3mf) | [Pouze geometrie](kryt-podlozka-01-geometrie.3mf) | [Rozložení](podlozka-01.png), [skutečná první vrstva](prvni-vrstva-01.png) |

Každou variantu importovat **samostatně jednou**; jsou to dvě podoby téže jedné podložky, ne dvě podložky k tisku. Model je 1:1, stojí na spodní zakřivené hraně, zadní otvor i dutina jsou volné. V tiskovém prostoru Kobra X **260 × 260 × 260 mm** leží v X 55–205 mm, v Y 92,5–167,5 mm a v Z 0–98 mm. Bez lemu je nejmenší odstup od okraje 55 mm. Není třeba nic ručně rozmnožovat nebo posouvat.

Nastavený projekt používá **Anycubic Kobra X, trysku 0,4 mm**, návrhový proces **0,20 mm / 4 stěny / 25 % gyroid**, vnější lem **5 mm**, **bez podpor**. Plášť má konstantní svislý průřez, takže v hotovém řezu nejsou mosty ani podpory. Profil filamentu je návrh pro **Alzament PLA Basic**: 215 °C první vrstva, 205 °C další, podložka 50 °C. Nejde o kalibrované nastavení pro konkrétní cívku ani potvrzení vhodnosti PLA u digestoře. Před případným tiskem ověř skutečně založený materiál/slot a změř provozní teplotu u potrubí; podle výsledku může být potřeba jiný materiál a nový řez.

Místní řez proběhl pro **490 vrstev do výšky 98 mm**. Odhad sliceru je přibližně **3 h 53 min a 80,18 g**, nikoli změřená spotřeba. Kontrola [drah](kontrola-drah.json) četla přímo G-code vložený v předaném 3MF: každá vrstva má extruzi, první vrstva obsahuje 5mm lem, extruze zůstává uvnitř podložky a role podpor i mostů chybí. Metadata sliceru uvádějí `outside=false`, `support_used=false`. Detail je v [ověření řezu](overeni-rezu.json).

Řez obsahuje varování sliceru k tradičnímu časosběru. CLI navíc zapsalo `calc_exclude_triangles: Unable to create exclude triangles`; pole vyloučených oblastí podložky je prázdné a stejné hlášení se objevilo v dřívějších projektech. Příčina hlášky nebyla nezávisle určena. Slicer přesto skončil úspěšně, vzniklo 490 vrstev a hranice všech extruzních drah byly ověřeny. Neoznačujeme proto řez jako bezvarovný.

Podložku reprodukují [generátor geometrického 3MF](vytvor-podlozku.py), [příprava procesu a řezu](pripravit-projekt.py) a [kontrola drah](overit-drahy.py). Geometrická varianta neobsahuje tiskový proces, filament ani G-code a nemá tiše měnit uložené presety. Po změně FCStd nejprve obnov STL a pak postupně tyto tři výstupy; předané 3MF není na FCStd živě navázané. Bez uživatelského zadání se tiskárna neovládala a úloha nebyla spuštěna.
