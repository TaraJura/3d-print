# Robotická ruka na autíčku — elektronika

Projekt založen 23. 9. 2026 pro první lehký tisknutelný prototyp paže na jednoduchém kolovém autíčku. Mechanický model a tiskové soubory jsou v [modelu robotické ruky](../../models/roboticka-ruka/README.md); stav zásob je pouze v [kanonickém inventáři](../vybaveni.md).

## Aktuální stav

- Jiří potvrdil dostupný krokový motor se štítkem hlasem čteným jako „StepMotor 28BY…-48, 5 V DC“. Přesné znaky označení, počet kusů, rozměry a funkce jeho motoru zatím nejsou fyzicky ověřené.
- První návrh využije krokový motor jen pro pomalé otáčení základny kolem svislé osy. Rameno a loket zůstanou ručně polohovatelné a otevřená dvouprstá koncovka nebude zatím aktivně svírat.
- Servo SG90 je v dosavadní evidenci určené pro řízení autíčka; s volným kusem pro paži se nepočítá.
- Pro tuto paži zatím není potvrzené elektrické zapojení, zdroj napájení, přiřazení pinů, firmware, nahrání programu ani fyzická zkouška pohybu.

## Podklady pro navazující zapojení

[LaskaKit uvádí pro běžný 28BYJ-48](https://www.laskakit.cz/krokovy-motor-28byj-48/) napájení 5 V DC, pět vodičů a kompatibilitu s řadičem ULN2003. [Katalog sady MAXI RFID](https://www.laskakit.cz/laskkit-arduino-maxi-starter-kit--rfid/) obsahuje jeden 28BYJ-48 a jeden ULN2003. Katalog není ověřením, že konkrétní řadič Jiří fyzicky převzal nebo že jeho motor je přesně tato varianta. Výrobce také upozorňuje na vůli plastové převodovky; přesnou polohu ani nosnost paže z katalogu neodvozujeme.

Před první elektrickou zkouškou určit štítek a konektor skutečného motoru, ověřit dostupnost odpovídajícího řadiče a regulovaného 5V zdroje, proměřit polaritu a napětí zdroje bez motoru a vybrat volné piny řídicí desky podle [aktuálního zapojení autíčka](../auticko/README.md). Motor se nemá připojovat přímo na výstupy Arduina. Napájení a společnou zem řadiče a řídicí desky zakreslit až pro konkrétní fyzické zapojení.

Zkoušky a jejich výsledky sem zapisovat odděleně od mechanického fitu a od pouhého překladu programu.
