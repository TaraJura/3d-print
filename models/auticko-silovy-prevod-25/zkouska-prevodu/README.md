# Ruční funkční zkouška původního soukolí 18 → 60

**Samostatný sedmidílný vzorek pro fyzickou zkoušku; chod zatím není potvrzený.** Obsahuje skutečná dvojkola A/B, jejich dlouhé čepy, pojistky a výřez původního rámu. Ověří montáž do pevných sedel, lehký chod ve dvou vodicích pásmech, souosost, vůli a skutečný záběr. Není to celá sada 66 dílů ani řešení 12mm výstupu.

Vzorek zachovává **původní 20° zuby a rozteč 39,4 mm**. V dvojkolech se změnil pouze kluzný otvor **8,2 → 8,6 mm**; dvě vodicí pásma zůstala dlouhá po 5 mm a mezi nimi je 20 mm odlehčení Ø9. Čepy zůstaly plné Ø8 a pevná sedla rámu Ø8,1. Uživatelské hlášení o dobrém otáčení krátkého vzorku 8,6 mm neprokazuje lehký chod tohoto dlouhého uložení ani rezervu záběru při viklání. Původní profil má omezenou rezervu pro větší radiální vůli; tento výtisk slouží k ověření právě těchto potíží.

## Co otevřít

- **[Jedna připravená podložka — 7 kusů](zkouska-prevodu-podlozka-01.3mf)**. Každý objekt tisknout jednou; počty už nenásobit. Geometry-only 3MF obsahuje samostatné objekty v mm, 100 %, se zachovaným Z a tiskovou orientací.
- Alternativa: [ZIP se sedmi fyzickými STL kopiemi](zkouska-prevodu.zip). Neimportovat zároveň se 3MF.
- [Editovatelný FreeCAD](zkouska-prevodu.FCStd), [zdrojové makro](zkouska-prevodu.FCMacro).
- Skutečné CAD pohledy: [sestava](nahled.png), [opačná strana](opacna-strana.png); [očíslená tisková podložka](podlozka-01.png).

| Díl | Počet | Úloha |
|---|---:|---|
| `vyrez-ramu` | 1 | Původní uložení A/B, dorazy a kapsy hlav |
| `dvojkolo-a` | 1 | 54 + 18 zubů; testuje se jeho 18zubý pastorek |
| `dvojkolo-b` | 1 | 60 + 22 zubů; testuje se jeho 60zubý věnec |
| `pevny-cep-8x53_9` | 2 | Ø8, délka 53,9, čtvercová hlava a drážka |
| `pojistka-6_9` | 2 | Původní pojistka čepu |

## Tisk a montáž

V Next vybrat **Anycubic Kobra X 0,4 mm**, skutečný PLA a zachovat orientace. Soubor nepřenáší výšku vrstvy, horní vzor ani podpory. Uživatel uvedl běžnou vrstvu **0,08 mm** a standardní **Monotonic line**; jde o jeho hlášení, ne o ověření tohoto G-code. Pokud nastavení ponechá, použít stejný proces jako u fyzické kalibrace. První vrstva se tím automaticky nemění; lokální Standard má samostatný default 0,20 mm. [Dříve zachycené read-only hodnoty systémového profilu](../rozlozeni/profil-podlozky.json) nejsou živé nastavení tohoto tisku.

- Rám leží dnem; prověřit vodorovná sedla a místní převisy.
- Dvojkola leží velkým ozubeným čelem. Spodní převisy vyvýšeného malého ozubení mohou vyžadovat **lokální podpory na těle modelu**; jen podpory z podložky nemusejí stačit.
- Čepy leží naležato. Jejich větší hlava zvedá spodní oblouk dříku nad podložku, takže je nutné zkontrolovat podporu po délce. Po odstranění podpor musí pracovní plocha zůstat kruhová a rovná.
- Pojistky leží naplocho. Zkontrolovat spojení tenkých stěn a oddělení od brim/podpor.

Rozložení rezervuje mezi obrysy nejméně 11 mm a od hran nejméně 6 mm pro předpokládaný brim 5 mm s mezerou 0,1 mm, bez skirtu. **To není kontrola skutečných podpěr a drah.** Před tiskem zkontrolovat vrstvy a případně zvětšit rozestupy; žádný G-code, odhad času ani nastavení podpěr zde nebyly vytvářeny.

**Pro montáž a otáčení držet rám nad stolem nebo podepřít jen jeho boční plochy mimo obrys kol.** Věnec B zasahuje při otáčení až 3,2 mm pod dno rámu; pod zuby ponechat alespoň 5 mm volného prostoru. Zkouška s rámem přitlačeným na rovnou desku by kolo blokovala. A má velké kolo s 54 zuby, B s 60. Obě velká čela směřují k téže straně, jak ukazuje CAD; 18zubý pastorek A je proti 60zubému věnci B. Čepy se zasouvají stranou s čtvercovými kapsami, hlavy zapadnou do kapes. Na opačné straně se do drážek nasadí dvě pojistky. Pojistkami nestahovat čela dvojkol k rámu.

## Přesná ruční zkouška

1. **Bez motoru a bez napájení; zuby mají volný prostor pod rámem.** Očistit brim a podpory; pro první porovnání neměnit průměr čepů ani otvory vrtáním či násilím.
2. Nejprve zkusit každý čep v samostatném dvojkole a potom každé dvojkolo samostatně v rámu. Nasazení do pevných sedel Ø8,1 a hlavových kapes má jít bez nepřiměřené síly. Když nejde, zastavit a uvést přesně, kde se montáž zastavila.
3. Sestavit obě dvojkola a pojistky. **Otočit dvojkolo B třikrát jedním směrem a třikrát opačným**, nejprve volně a pak s lehkým odporem prstů na A. Tři otáčky B odpovídají deseti otáčkám A; netlačit přes tvrdé místo.
4. Hlásit, zda byl chod plynulý, kde se objeví tvrdé místo, zda se opakuje v určité poloze, zda dvojkolo viditelně viklá, zuby přeskakují nebo čelo drhne o doraz. Rozlišit samotné uložení od potíží až po zapojení obou kol. Hodí se krátké video a fotografie uložení a očištěných čepů.

Výsledek je podklad k revizi. Bez této fyzické zkoušky nelze tvrdit, že hlavní převod je spolehlivý, že se snížilo tření nebo že rám či čepy snesou motorové zatížení.

## Původ a kontroly

Makro načte pouze [zmrazený předkalibrační archiv](../historie/pred-kalibraci-8_6-12_6-2026-09-20/puvodni-revize.zip), ověří původní FCStd SHA-256 `33e6369daa80e11193a0c473c726f60a1f78c2f4cba7d32f66e4d51d3360754e` a vytvoří nový dokument. Současný rozpracovaný generátor hlavního auta se nespouští. Uložený FCStd používá standardní objekty a výrazy, nepotřebuje vlastní Python proxy.

Výřez je skutečný `Part::Common` původního `SteeringFrame` a boxu X63,9…123,3 / Y−36…34 / Z0…45 mm. Samotný rám má 59,4 × 70 × 38 mm. Obě podpěry, čelní dorazy a kapsy hlav každé osy jsou v něm zachované; kontrola porovnává materiál s původní geometrií v jejich úplných obálkách.

[CAD kontrola](kontrola-modelu.json) ověřuje jedno platné těleso každého typu, rozteč, nezměněné zuby/čepy/pojistky/pevná sedla, odebrání materiálu pouze ve dvou kluzných pásmech a skutečné poloměry otvorů. Zkouška parametru 8,7 → 8,6 ověřuje přepočet; nominálně smontované díly se objemově neprotínají. Tato poslední kontrola pokrývá zaznamenanou polohu, ne celý pohyb a krajní vychýlení os.

[Kontrola exportů](overeni-exportu.json), [rozložení](overeni-rozlozeni.json), [3MF proti STL](overeni-3mf.json), [počty CAD → kusovník → ZIP → 3MF](overeni-kusovniku.json) a [import/export v Next CLI](overeni-importu.json) jsou samostatné důkazy. CLI používá izolovanou cache, bez automatického přeuspořádání/otočení, bez řezání a komunikace s tiskárnou. Tiskové podpory ani fyzický výsledek tím ověřené nejsou.

## Regenerace

Spustit `zkouska-prevodu.FCMacro` ve FreeCADu (přepíše pouze zdejší FCStd, STL, ZIP a CAD report), potom `nahled.FCMacro` pro skutečné PNG a uložení viditelnosti sestavy. Pro zachování vazeb ponechat uvedený archiv na relativní cestě. Změna zubního profilu vyžaduje nový návrh a nové ověření, není parametrem tohoto vzorku.

Z této složky pak použít Python prostředí `/home/novakj/.cache/auticko-packing/venv/bin/python`:

```sh
python rozmistit.py zkouska-prevodu.zip . --target-plates 1 --attempts 12
python overit-rozlozeni.py zkouska-prevodu.zip rozlozeni.json overeni-rozlozeni.json
python vytvorit-3mf.py zkouska-prevodu.zip rozlozeni.json .
python overit-3mf.py zkouska-prevodu.zip rozlozeni.json . --expected-wheels 0
python nahled-rozlozeni.py rozlozeni.json . --input-zip zkouska-prevodu.zip
python overit-kusovnik.py kontrola-modelu.json zkouska-prevodu.zip overeni-3mf.json overeni-kusovniku.json
python overit-import.py . --cache /home/novakj/.cache/auticko-functional-test/next
python overit-exporty.py
```
