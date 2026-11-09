# V03 — PCB položené na otevřené podpěry

Úprava podle Jiřího 22. 10. 2026: kondenzátory jsou nahoře přímo u hrany PCB, proto desky nemají zajíždět do sevřených drážek. **PCB zůstává přesně 78 × 108 mm.** Předchozí V02 zůstává zachovaná jako historie.

## Změna uložení PCB

- Odstraněno všech šest horních lemů PCB drážek. **Nad okrajem desky není žádná přídržná lišta.** Osazení může sahat až k bočním hranám PCB.
- Každá PCB leží na dvou spodních podpěrách: přesah pod desku 1,2 mm, tloušťka podpěry 1,6 mm. Na spodní straně je proto stále potřeba volný opěrný pás bez pájených vývodů. Volný pás na horní straně už není požadovaný.
- Nízké boční, přední a zadní dorazy mají výšku **0,6 mm od spodku PCB**, tedy pod předpokládaným horním povrchem 1,6mm PCB. Boční vůle zůstává 0,4 mm na každé straně.
- Čelo si zachovává vlastní svislé vedení, spodní doraz a horní pojistku s jedním M3 šroubem. Tyto drážky patří čelu, nikoli PCB.
- Záda, nástěnné zavěšení, tři kabelové průchody 34 × 18 mm, otvory pro pásky a ventilace zůstávají.

Tělo má **88,4 × 134 × 157,2 mm (šířka × hloubka × výška)**. Celá tištěná sestava včetně distancí, ouška a pojistky má **88,4 × 144,8 × 173,5 mm**, bez konektorů, kabelů a šroubů. Pro tuto změnu se kryt nezvětšoval.

**Nezměřená výška osazení stále činí v modelu 38 mm nad horní plochou PCB.** Není to potvrzený rozměr zesilovačů. Tloušťka PCB 1,6 mm, svislá poloha a přesah konektorů jsou rovněž návrhové. Před tiskem celé sady doplnit výšku od spodní plochy PCB k nejvyšší součástce a ověřit spodní opěrné pásy. Rozměrové rezervy v otvorech nemohou nahradit chybějící výšku.

## Jak desky položit

1. Mimo zeď do prázdného těla vložit pět matic M3. Čtyři zadní matice vstupují ze stran zevnitř těla; horní matice zezadu do kapsy.
2. Čelo nasunout shora do jeho drážek a zajistit horní pojistkou, šroub M3×10. Nad krytem je pro tento krok potřeba prostor alespoň 154,8 mm.
3. Zesilovače zbavit případných bílých nožiček, pokud brání spodním opěrným pásům. Zkontrolovat, že podpěry nesedí na pájených vývodech.
4. Otevřenými zády přivést PCB nad příslušný pár podpěr a **spustit ji dolů na podpěry**. Nevkládá se do horní drážky. Digitálně zkoušená trajektorie vede 0,8 mm nad dosedem a potom svisle dolů; konektory procházejí stávajícími čelními výřezy. Nejde o vložení shora skrz pevnou střechu celého krytu. Patra osazovat odspodu.
5. Zapojit kabely, odlehčit jejich tah pásky v zadním víku a připevnit víko pomocí 4× M3×12. Nízké zadní dorazy omezí posun desek dozadu.
6. Na dva horní vruty ve zdi nejprve nasadit 8mm distanční kroužky a pak zavěsit celou sestavu do klíčových otvorů; dole zajistit třetím vrutem a distancí. Kroužky se nelepí ke skříňce, zůstávají na vrutech u zdi.

PCB drží svisle vlastní tíha, nikoli horní přítlak. Při montáži držet skříňku ve vzpřímené poloze; převrácení nebo tah kabelů mohou desky nadzvednout. Vruty a kotvy je potřeba zvolit podle skutečné stěny a hmotnosti. Návrh vyžaduje 5 běžných matic M3; skutečný spojovací materiál a jeho fit nebyly potvrzené.

Pro demontáž čela nejprve sundat skříňku, otevřít záda a odebrat zesilovače, aby konektory opustily rovinu čela. Teprve poté odstranit horní pojistku a vysunout čelo nahoru. Lepidlo není potřeba.

## Náhledy a soubory

- [Detail podpěry s PCB a kondenzátorem u hrany](detail-polozeni-pcb.png) — skutečný výřez CAD; rozměry kondenzátoru jsou pouze ilustrační, nikoli měření.
- [Prázdný kryt a otevřené podpěry](nahled-podpory.png), [celá sestava](nahled-zpredu.png), [zasouvání čela](nahled-nasouvani-cela.png), [vnitřek](nahled-vnitrek.png), [záda](nahled-zezadu.png).
- [Parametrický FreeCAD](kryt.FCStd), [zdrojové makro](kryt.FCMacro), [STL těla](stl/telo.stl), [STL zad](stl/zada.stl).
- [Připravené tiskové podložky](rozlozeni/README.md): všech 7 fyzických dílů ve dvou samostatných projektech, Kobra X 0,4 mm. Otevřít každou jednou, nic nenásobit. **PLA rozměrový prototyp**, nikoli schválený materiál pro provoz zahřívajících se zesilovačů.
- [Geometrická kontrola](kontrola-modelu.json), [montážní audit](audit-montaze.json), [parametrická kontrola](kontrola-parametru.json), [kontrola řezu](rozlozeni/kontrola-rezani.json).

V03 mění tělo a nízké zadní dorazy. Čelo, horní pojistka a tři distanční kroužky zůstávají geometricky stejné jako ve V02. Všechny díly jsou v nové sadě znovu zahrnuté; obě sady se nesčítají. Žádný předchozí fyzický tisk nebyl potvrzený.

## Ověření a jeho hranice

Export ověřuje sedm validních jednotlivých solidů, uzavřené STL sítě po jedné komponentě, rozměry a nulové statické kolize tištěných dílů s PCB. Uložený FCStd má standardní FreeCAD objekty, tabulku a výrazy; žádná vlastní Python třída není nutná k přepočtu. Náhledy vznikly z této geometrie, pomocné tvary jsou v uloženém dokumentu skryté.

Nezávislý montážní audit prošel všemi 78 kontrolami za níže uvedených předpokladů. Zkouší celou dráhu přiblížení zezadu i následného položení, s obálkou horního osazení **přes celou šířku 78 mm**, nikoli s volným pásem na horní hraně. Nejtěsnější navržený průchod při zástupné výšce 38 mm je pod zadními horními úchyty: po zvednutí PCB o 0,8 mm zbývá 0,6 mm. Větší skutečná výška může vyžadovat další úpravu. Hypotetické 2mm vývody pod PCB se zkouší mimo spodní opěrné pásy; skutečné vývody nebyly změřené.

Tělo se tiskne zadním otevřeným lemem na podložce, se skutečnými lokálními podporami v nastaveném projektu. Po tisku je nutné podpory odstranit a očistit kapsy matic a vedení čela. Ostatní díly mají samostatně určenou orientaci. Digitální kontrola není ověřením fyzického tisku, položení PCB, materiálu, chlazení ani kotvení. Tiskárna nebyla ovládána.
