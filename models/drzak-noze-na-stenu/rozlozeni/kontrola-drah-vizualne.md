# Kontrola skutečných drah — 30. 10. 2026

Kontrola vychází z lokálně vygenerovaného G-code uloženého přímo ve finálních projektech 3MF. Neproběhlo ovládání tiskárny ani fyzický tisk. Vazbu na geometrie, nastavení a G-code zajišťují SHA-256 v `kontrola-rezani.json` a `kontrola-podpor-detail.json`.

Prohlédnuty očíslované půdorysy, přehled vrstev vaniček a detaily podpor:

- Vaničky leží celou zadní plochou na podložce. Oba kusy mají první vrstvu; čtyři montážní průchody zůstávají otevřené. Při vyšších vrstvách pokračují krajní stěny a podpěry čepů.
- Pod záchytným lemem jsou skutečné podpory. Detail levé vaničky ukazuje kontaktní vrstvu na zádech v Z 3,0 mm, spodní mezeru a vznik podpory v Z 3,4 mm. Podpůrné rozhraní v Z 31,6–31,8 mm podepírá vnější kraj lemu; první vrstva lemu v Z 32,2 mm překlene krátký prostor mezi dnem/stěnou a podporou. Další vrstva Z 32,4 mm je souvislá. Jde o navržený krátký přemostěný úsek s podporou, nikoli fyzicky ověřený povrch.
- Pravý stupňový spoj vaničky má podporu z podložky; detail Z 1,2 mm / 1,6 mm / 1,8 mm ukazuje rozhraní, mezeru a první přemostěnou vrstvu přesahu. Otvory pro montážní vruty nejsou zaplněné podporou.
- Pravý kryt má podporu pouze u středového přesahu, s rozhraním do Z 1,4 mm, mezerou a první vrstvou přesahu v Z 1,8 mm. Klíčové otvory zůstávají průchozí. V okolí levého plochého krytu nebyl zjištěn žádný segment podpory.
- Čepy vaniček rostou v ose Z; rozšíření hlavy je kuželové. Přehled vyšších vrstev 39–41,8 mm ukazuje jejich návaznost. Brim není zaměněný za podporu.

Automatický graf skutečných drah prošel všech 209 a 15 vrstev bez nových nepřipojených ostrovů. Každý fyzický kus má extruzi v první vrstvě. Nejmenší rezerva extruzí včetně podpor/brimu vůči okraji 260mm podložky je 3,25 mm. Graf neověřuje pořadí jednotlivých tahů v rámci vrstvy ani fyzickou kvalitu přemostění.

Podpory jsou přístupné z otevřených vaniček a vnějšího spoje krytu; jejich reálná odstranitelnost bez poškození, tolerance spojů, pevnost, funkce čepů a přesný fit nože zatím nejsou fyzicky ověřené. Před sestavením je nutné očistit podporové kontakty, brim a montážní plochy.

U finální podložky 01 zůstává varování `not_support_traditional_timelapse`; u obou řezů CLI hláška `calc_exclude_triangles:Unable to create exclude triangles`. Počet oprav sítě je 0 a slicer nehlásí přesah podložky.
