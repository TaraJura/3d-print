# Zaoblený kryt trubky digestoře – první návrh

**Stav 26. 9. 2026:** předběžný parametrický návrh a místně nařezaná tisková podložka. Počítačově ověřená geometrie neprokazuje nasazení na konkrétní potrubí, vhodnost materiálu ani výsledek tisku. Nic nebylo odesláno tiskárně.

## Zadání a interpretace

Jiří chce zakrýt **viditelný svislý úsek trubky mezi horní plochou kuchyňské skříňky a sádrokartonem**. Trubka dále prochází skříňkami a stropem. Zadní strana krytu má zůstat otevřená ke zdi. Původní [ruční náčrt](podklady/nacrt-od-jiriho.png) byl hranatý; následně požádal o plynule kulatý vzhled.

| Údaj | Hodnota | Původ a význam |
|---|---:|---|
| Šířka krytu napříč trubkou | 150 mm | Jiří zadal 15 cm; výklad osy pro tento návrh |
| Výška krytu | 98 mm | Jiří zadal 9,8 cm pro přibližně 100mm mezeru |
| Průměr trubky | přibližně 130 mm | Jiří uvedl 13 cm, zatím bez měření |
| Zadní dosah boků | přibližně 70 mm | Jiří řekl „třeba 7 cm“ |
| Skutečná hloubka kruhového návrhu | **75 mm** | Návrhový poloměr při šířce 150 mm; o 5 mm více než odhad boků |
| Tloušťka stěny | 3 mm | Návrhová hodnota, nikoli zadaný rozměr |

Jeden díl tvoří **přední půlkruhový plášť**. Je otevřený vzadu, nahoře i dole, takže se může nasunout zepředu kolem stávajícího svislého potrubí; spodní zakřivená hrana má stát na skříňce. Boky zaoblení tvoří zadní ramena. Kryt nemá kotevní prvky ani tvrzenou stabilitu.

Při ideálně soustředné kruhové trubce Ø130 mm vychází vnitřní poloměr krytu **72 mm** a nominální radiální vůle **7 mm**. To je výpočet z přibližného zadání. Poloha trubky vůči zdi a skříňce není známa, proto ani soustřednost nelze předpokládat jako skutečnost. Půlkryt sahá dozadu jen k rovině středu kruhu; nemusí dosáhnout ke zdi ani skrýt pohled ze strany.

## Co je potřeba na místě ověřit

Před fyzickým tiskem nebo nasazením změřit:

1. **Nejmenší skutečnou světlou výšku** od skříňky po sádrokarton na celé šířce a hloubce krytu. Nominálních 98 mm ponechává proti odhadovaným 100 mm jen 2 mm.
2. **Největší vnější průměr** viditelného potrubí včetně spojů, límců, izolace a nerovností; zda je potrubí opravdu kruhové a svislé.
3. **Vzdálenost osy potrubí od zadní stěny a od přední hrany skříňky**, volný prostor před potrubím a zamýšlený pohled z boku. Z toho plyne potřebná hloubka krytu a reálný dosed otevřených ramen.
4. Zda má kryt pouze stát, nebo být bezpečně upevněný, a zda mu nepřekážejí dvířka či jiný díl kuchyně.
5. **Teplotu u potrubí při běžícím odsávání a vaření.** PLA v připraveném 3MF je jen dostupný návrhový tiskový profil; jeho vhodnost a bezpečnost v tomto místě nejsou potvrzené. Pokud místní teplota či požadavky instalace PLA vylučují, je nutné materiál a proces znovu zvolit a nařezat.

## Soubory a kontrola

- [Editovatelný FreeCAD dokument](kryt.FCStd) obsahuje tabulku `Parameters`, běžné objekty `Part` a výrazy; přepočet nevyžaduje vlastní Python třídu.
- [Zdrojové makro](kryt.FCMacro) vytváří FCStd, [STL](stl/kryt.stl) a [kontrolu modelu](kontrola-modelu.json). **Při opětovném spuštění tyto soubory přepíše**; před regenerací nejdřív slaď případné ruční změny ve FCStd s makrem.
- [Makro náhledů](nahled.FCMacro) vytváří [šikmý pohled](nahled-zaobleny-kryt.png) a [pohled shora](nahled-shora.png) ze skutečné CAD geometrie. Také ukládá FCStd pouze se zobrazeným finálním dílem.
- [Jedna připravená podložka](rozlozeni/README.md) obsahuje přesně jeden fyzický kus, očíslovaný náhled, variantu pouze s geometrií i místně nařezaný projekt pro Anycubic Kobra X 0,4 mm.

FreeCAD potvrdil platný **jeden solid** s hranicemi **150 × 75 × 98 mm**. STL je uzavřená manifold síť s 396 trojúhelníky, bez degenerovaných trojúhelníků; odpovídá měřítku 1:1. Uložený FCStd byl znovu otevřen a přepočten při zkušební změně šířky, výšky, hloubky a tloušťky, pak vrácen na výchozí hodnoty. Náhledy odpovídají finální geometrii. Tisk, dosednutí, stabilita ani provozní teplota nejsou fyzicky ověřené.
