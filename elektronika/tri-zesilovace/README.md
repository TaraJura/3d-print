# Tři zesilovače v nástěnném krytu

Zadání Jiřího 21. 10. 2026 a čtyři fotografie: společný nástěnný kryt pro tři moduly s pohodlným přístupem k ovladačům hlasitosti. Mechanický návrh a všechny exporty jsou v [modelu krytu](../../models/kryt-tri-zesilovace/README.md).

## Pozorování a hranice evidence

Na fotografiích jsou tři podobně osazené desky, každá s chladičem/ventilátorem, jedním ovladačem a dvěma RCA na přední hraně. Protilehlé svorky jsou na fotografii spodní strany označené L+/L−, VCC/GND a R−/R+. Je viditelné značení SANWU, ale přesný typ modulu, výkon a napájecí parametry nejsou ověřené. Tyto moduly nelze ztotožnit se starším pravděpodobným PAM8403 v [inventáři](../vybaveni.md).

Uživatel chce zezadu „vstup na zdroj 2 kabely a 2×2 kabely na přívod zvuku“. Zatím není potvrzené, zda jde pro každý modul o dvojici napájecích vodičů a dva páry reproduktorových výstupů, ani zda mají RCA signálové vstupy vést také dozadu. Není určeno, zda se zdroj umisťuje mimo kryt; koncept vyhrazuje prostor jen třem modulům, nikoli zdroji.

## Další potřebné údaje

Přesné mechanické rozměry a montážní otvory jsou vypsané u modelu. Pro kabelový prostor jsou potřeba skutečné konektory, průměry kabelů a počet svazků. Následně doplnit provozní zahřívání a vhodný tiskový materiál. Žádné zapojení, napájení ani funkční zkouška nebyly v této úloze provedené nebo potvrzené.

## Doplnění 22. 10. 2026

Jiří zadal pevný rozměr PCB **78 × 108 mm**, ovladač široký 12 mm a vzdálený 15 mm od strany, přibližnou mezeru 20 mm a RCA dvojici širokou 25 mm, vzdálenou 10 mm od protější strany. Upřesnil, že měření konektorů může být nepřesné a požaduje tolerance, rozměr PCB však musí zůstat 78 × 108 mm. Osa versus okraj 15mm údaje nebyla jednoznačně potvrzena. V02 používá široké servisní výřezy a PCB kvůli rozměrovému řetězci nemění.

Výška desky/osazení a tloušťka PCB zůstávají nezměřené. Nový [mechanický návrh V02](../../models/kryt-tri-zesilovace/revize-02-posuvne-celo/README.md) se sestavuje bez lepení: čelo shora před osazením, PCB zezadu do lišt a zadní víko sešroubovat. Požaduje odstranění překážejících bílých nožiček a volný 1,2mm pás podél dlouhých hran PCB. Jde o podmínky návrhu, nikoli potvrzenou vlastnost modulů. Zapojení, funkční test a provozní teplota nebyly ověřeny.

## Následná oprava uložení PCB — 22. 10. 2026

Jiří upozornil, že nahoře přímo u hran PCB jsou kondenzátory a desky do původních drážek nezajedou. Požaduje prosté položení. [V03](../../models/kryt-tri-zesilovace/revize-03-volne-polozeni/README.md) proto odstranila horní lemy: PCB se otevřenými zády přivede nad spodní podpěry a položí na ně. Horní strana může být osazená až k hraně; pouze spodní opěrný pás 1,2 mm musí být bez pájených vývodů. Nízké dorazy mají 0,6 mm, PCB není svisle sevřená. Pevný rozměr 78 × 108 mm i mechanismus čela se nemění. Výška osazení 38 mm a tloušťka PCB 1,6 mm jsou nadále návrhové, žádná fyzická montáž nebo provozní zkouška není potvrzená.
