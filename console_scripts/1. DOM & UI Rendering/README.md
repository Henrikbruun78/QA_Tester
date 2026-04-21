## DOM & UI Rendering
Denne sektion omhandler analyse af webapplikationens DOM (Document Object Model) og den efterfølgende UI rendering, dvs. hvordan HTML-strukturen omsættes til et interaktivt og visuelt brugerinterface i browseren. DOM’en repræsenterer applikationens runtime-struktur som et hierarkisk træ af noder, der kan tilgås og manipuleres via JavaScript. UI rendering er browserens proces, hvor DOM, CSSOM og JavaScript eksekvering kombineres til det endelige layout gennem rendering pipeline (reflow, repaint, compositing). I stedet for en udelukkende visuel og manuel tilgang (klik-baseret inspektion), anvendes en script-baseret metode via DevTools Console. Denne tilgang muliggør direkte interaktion med DOM’en på runtime-niveau og giver adgang til systemets faktiske tilstand frem for det, der umiddelbart vises i UI’et.

## Formål med metoden ##
Den script-baserede tilgang er valgt af følgende årsager:

''Reproducerbarhed''<br>
Scripts kan genbruges på tværs af sider og projekter, hvilket gør analyser konsistente og mindre afhængige af manuelle steps.<br>
Hastighed og effektivitet<br>
Store mængder DOM-data kan analyseres øjeblikkeligt uden manuel navigation i DevTools.<br>
-- Dybere systemindsigt<br>
Giver adgang til skjulte eller dynamiske elementer, som ikke nødvendigvis er synlige i UI’et (fx display: none, lazy-loaded komponenter eller runtime genererede elementer).<br>
-- Verifikation af runtime-state<br>
Muliggør validering af den faktiske tilstand efter JavaScript eksekvering, frem for statisk HTML.<br>
-- Fejlfinding af rendering issues<br>
Gør det muligt at identificere problemer relateret til layout (fx zero-height elements, overflow, manglende assets) og dynamiske ændringer i DOM’en.<br>
-- Automatiseringspotentiale<br>
Scripts kan senere integreres i testværktøjer (fx Playwright eller Puppeteer), hvilket skaber bro mellem manuel QA og automatiseret test.<br>
-- Linux/CLI-inspireret workflow<br>
Metoden følger en værktøjsbaseret tilgang, hvor systemet analyseres gennem kommandoer frem for GUI-interaktion. Dette giver bedre kontrol, transparens og mulighed for at skalere analysearbejdet.<br>

## Anvendelse
Denne sektion fungerer som et løbende opbygget cheatsheet bestående af konkrete scripts til:

- DOM traversal og struktur-analyse
- Synlighed og layout validering
- Overvågning af dynamiske ændringer
- Identifikation af UI inkonsistens

Formålet er at etablere en praktisk og teknisk funderet tilgang til hurtigt at kunne analysere og forstå nye webapplikationer på et lavt niveau.
