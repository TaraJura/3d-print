# Koupelnová přepážka – vizuální návrhy

22. 9. 2026 · [Srovnávací obrázek A/B/C](srovnani-abc-koncept.png)

Jde o orientační vizualizace bez měřítka, nikoli ověřený CAD model. Dlaždice a instalace jsou pouze ilustrační; fotografie skutečné koupelny nebyla k dispozici. Obrázek vznikl podle zadání porovnat tvary pružné rovné přepážky proti vytékání vody jako zamýšlené náhrady dosavadního silikonu. Jiří následně výslovně potvrdil, že přepážka musí **zabránit průtoku a vytékání vody**; předchozí zmínka o protékání byla opravená nejasnost v řeči, nikoli požadavek na odvádění vody.

- **A:** nízký oblý práh se širokou rovnou spodní plochou.
- **B — vybráno Jiřím:** širší asymetrický náběhový profil s pozvolnou šikmou stranou a zaoblenými hranami.
- **C:** vyšší tenká lamela na široké ploché patce s plynulými přechody.

**Potvrzeno Jiřím v hlasovém rozhovoru 22. 9. 2026:** naměřená celková délka je **570 mm**. Výslovně požaduje napojení z více dílů, protože celek se nevejde na tiskovou desku.

**Navazující skutečný CAD:** [aktuální návrh B](../README.md) má zadanou délku 570 mm, výšku 10 mm a šířku nejvýše 20 mm. Dřívějších 40 mm bylo výslovně opraveno na limit 20 mm. Tři díly délky 196 / 202 / 196 mm, s bočními stupňovitými přesahy 12 mm, jsou návrhovou volbou. Nominální CAD spoj má nulovou vůli, jeho těsnost ani fyzický fit nejsou ověřené.

Jiří potvrdil TPU; dostupný výrobek je Alzament TPU 95A Gray. Podkladem je podle jeho hlášení jedna dlouhá kachlička bez spár pod lištou. Aktuální zdroje, kontroly, skutečné CAD náhledy a tiskový stav jsou v nadřazeném README. Zdejší původní srovnání A/B/C zůstává orientační bez měřítka a není aktuální konstrukční dokumentací.

Obrázek vznikl vestavěným ImageGenem. Vizuální kontrola: tři odlišné profily, čitelná přední čela a dosed na podlahu, pouze označení A/B/C, bez kót. Daleké konce lišt pokračují mimo záběr; délku z obrázku nelze odvozovat.

## Použitý prompt

```text
Use case: product-mockup.
Asset type: single polished comparison board of three conceptual flexible bathroom water-barrier strips, intended only for visual design discussion, not an engineering drawing.
Primary request: a clean professional 3D product render showing three clearly different long, perfectly straight extruded rubber-like strips in three equal side-by-side panels labelled A, B, C.
Scene/backdrop: each panel shows simple pale bathroom floor tiles with subtle grout and soft contact shadows, an illustrative generic setting, no reference to an actual bathroom. Dry surfaces, no water or demonstration of watertightness.
Composition/framing: wide landscape comparison image, three equal vertical panels, consistent three-quarter camera angle looking toward the front cut end of each strip. The long axis runs from foreground lower left toward background upper right in every panel. Keep the near end clearly visible and large enough to read its profile, with enough length behind it to unmistakably read as a long straight strip. Entire objects visible, ample clean margins, no cropped ends. Clear silhouettes against slightly darker neutral tiles. View slightly low enough to show height and front cross-section while also seeing the top surfaces and wide feet.
A: low, gently rounded dome-shaped threshold with a broad, completely flat underside sitting flush on the tile, a shallow smooth half-oval end profile. This is the simplest low rounded bump, without a separate fin.
B: visibly wider ramp profile, one long gentle sloped face rising from a thin rounded toe to a rounded higher shoulder, then a steeper short back face, flat broad underside flush on tile. A clearly asymmetric rounded wedge end profile, distinct from A; no vertical thin fin.
C: noticeably taller slender upright flexible lamella with rounded top edge centered on a wide low flat foot extending visibly to both sides. Smooth generous concave fillets blend the upright fin into the flat foot. Show a continuous straight fin, not a bulky triangular wedge. End view reveals the thin upright blade and wide flat base, all flush on the tile.
Materials/textures: uniform matte white to very light grey soft elastomer-like material for all three concepts, subtle realistic surface response, no specified polymer or hardness. No hollow cavities or internal structure visible.
Lighting/mood: soft professional studio product lighting, sharp readable geometry and subtle shadows, restrained and realistic.
Text (verbatim): "A", "B", "C", one large dark simple sans-serif letter at the top of each respective panel. No other text.
Constraints: no dimensions, measurements, scale bars, numbers, diagrams, arrows, logos, watermarks, titles, people, fixtures, fasteners, adhesive strips, decorative objects or additional sample pieces. Do not imply measured geometry, tested performance or printability. Only the three requested alternatives, visually differentiated by profile. High-quality coherent 3D visualization.
```
