# Historická diagnostika revize vůlí — 20. 9. 2026

**Tento adresář zachycuje ukončený experiment před následným uživatelským rozhodnutím vytisknout celý nominální prototyp.** Aktuální stav hlavních výstupů je v [README modelu](../README.md) a [hlavním kontrolním záznamu](../kontrola-modelu.json). Níže uvedené nepřegenerování platí pouze pro tehdejší diagnostickou etapu: hlavní FCStd, STL, PNG, ZIP a 3MF v ní nebyly přegenerované. Jejich stará revize je zachována také v [archivu](../historie/pred-kalibraci-8_6-12_6-2026-09-20/puvodni-revize.zip). Tehdejší `kontrola-modelu.json` měl `validation_pass=false` a výslovné upozornění na nesoulad exportů s rozpracovaným zdrojem. Následná autorizace nominálního tiskového prototypu tento historický stav nahrazuje; selhání14° kandidáta zůstává platným zjištěním.

Uživatel potvrdil otáčení nominálního Ø8 čepu v nominálním otvoru8,6. Skutečná boční vůle, rozměry čepu a otvoru ani orientace tohoto výtisku nejsou změřené. Hodnoty CAD proto nepředstavují změřenou skutečnou vůli.

## Zdrojová revize

Volná vedení převodu8,6; pevná sedla8,1; zadní ložiska12,6; nově samostatný výstupní náboj12,1; D otvor zadních kol12,1 s plochou4,05 od středu; statické Ø4 zámky mají otvory4,1; lůžka plošiny8,1 mm. Průměry nosných čepů, přední8,6 otvory, Ø6 táhlové klouby, pojistky a dvě5mm vodicí plochy se nezměnily. Minima pro pevné spoje jsou uživatelsky zvolený návrh, nikoli ověřený lisovaný spoj; nezasouvat násilím.

Všech10 Ø4 čepů slouží jako statické zámky nebo příčný přenašeč momentu:1 výstup,2 motor,4 plošina,2 servo,1 objímka páčky. Nejde o10 volně otočných kloubů.

Odvozený nejhorší nominální CAD součet radiálních vůlí je0,35 mm pro každé mezikolo a0,35 mm pro výstup; relativní přiblížení stupňů0,50/0,70/0,70 mm. Výstupní axiální rozsah je±0,30 mm =±0,20 mm osy a±0,10 mm součtu obou otvorů příčného klínku. Tyto hodnoty nezahrnují deformaci, naklopení nebo skutečnou tiskovou kompenzaci.

## Samostatný experiment ozubení

Použit skutečný obrys z lokálního `fcgear` ve FreeCAD1.1.3 a jeho1mm extruze. Poměr zůstal18:54,18:60,22:55 =25:1. Kandidát: modul1,1; tlakový úhel14°; hlava malých kol1,31m a velkých1,59m; pata1,7m; profilové posunutí0. Šlo o změnu výšek hlavy/paty, nikoli profilové posunutí. Hlavní makro ponechává původní20° profil; kandidát se do hlavních výstupů nedostal.

| Důkaz | Rozsah | Výsledek |
|---|---|---|
| [probe.json](probe.json), [makro](probe.FCMacro), [log](probe.log) | CentreExtra0,80;32 fází každého páru při MIN roztečce, střed vůle |18:54 bez průniku;18:60 max0,00556022 mm³;22:55 max0,000263291 mm³ |
| [probe-085.json](probe-085.json), [makro](probe-085.FCMacro), [log](probe-085.log) | CentreExtra0,85;32 fází/pár při MIN/NOM/MAX, střed vůle |18:60 max0,000915346 mm³; ostatní páry bez průniku |
| [probe-090.json](probe-090.json), [makro](probe-090.FCMacro), [log](probe-090.log) | CentreExtra0,90; první pár kompletně32 fází×MIN/NOM/MAX×oba nosné boky a střed |První pár vykazuje střet u kořene. Následující dlouhý běh byl záměrně ukončen; log obsahuje i část druhého páru, JSON pouze dokončený první pár. **Není úplný průchod celé převodovky.** |
| [focused-090.json](focused-090.json), [makro](focused-090.FCMacro), [log](focused-090.log) | Cílená kontrola prvního páru při úhlu velkého kola1,666667° | Potvrzený FAIL níže |

Objemy jsou pro1mm extruzi, číselně tedy odpovídají ploše průniku v mm². Kritérium1e−6 mm³ je pouze práh pro detekci průniku; není výrobní tolerance ani automatické rozlišení skutečné kolize od numerické aproximace.

Nosné boky byly nastaveny korekcí `±(inv(αw)−inv(α))·(zs+zl)/zs`, kde `inv(a)=tan(a)−a`. Spline kořeny se měří ze skutečných hran; analytický kontaktní interval se ořezává na vytvořenou evolventu. Měření špiček vybírá maximální poloměr kruhových hran a ověřuje jejich počet. Nejmenší skutečná tětiva18z kandidáta je0,569135 mm; samo o sobě to nepotvrzuje tisknutelnost zubu ani správný záběr.

## Rozhodující skutečný střet

U18:54 při minimální roztečce40,0 mm, fázi velkého kola1,666667° a záporném nosném boku je průnik0,002991016 mm³. Body průniku leží vůči středu18z kola na poloměrech9,200820 až10,030899 mm; základní kružnice má poloměr9,605928 mm a skutečný začátek spline9,625464 mm. Část průniku tedy leží pod bází, v neaktivní oblasti kořene.

Po ústupu fáze o0,007/rb radiánu směrem do vůle, tedy7µm po základní kružnici, zůstává průnik0,000838750 mm³. Kandidát proto nebyl přijat.7µm je zde diagnostická obálka aproximace, nikoli přidaná vůle výtisku.

Kontrolní původní20° profil měl ve stejném rozšířeném testu32×3×3 maximální mikroskopický průnik0,00000788334 mm³; dřívější8fázový test středu vůle měl nulu. Kontrola ukazuje, proč nelze každý nenulový objem automaticky považovat za funkční selhání, ale nezachraňuje zde doložený střet pod bází.

Další neověřené profily se nezkoušely. Nová hlavní sestava nebyla generovaná; původně navrženým dalším krokem byl funkční vytištěný vzorek se stejnou orientací a vedením. Uživatel jej následně odmítl a výslovně autorizoval celý nominální prototyp s původním20° profilem a přiznaným nepokrytým krajním radiálním scénářem. Tato diagnostika nedokazuje, že nominální vůle0,6 mm odpovídá skutečnému radiálnímu pohybu vytištěných částí.

Zdrojové checkery byly parametrizované a mají ochranu proti nesouladu zdrojů a exportů. Byla ověřena jejich Python syntaxe, nikoli přepočet celého nového modelu. Úplné hashe a kontrola zachování výstupů jsou v [manifestu](manifest.json).
