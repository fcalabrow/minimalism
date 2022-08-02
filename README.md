# Parser minimalista
Este es un parser basado en la implementación de Alex Warstadt del formalismo descrito en ["A Formalization of Minimalist Syntax"](https://onlinelibrary.wiley.com/doi/abs/10.1111/synt.12117) por Chris Collins y Edward Stabler (2016). Su objetivo es determinar si las oraciones introducidas por el usuario son o no gramaticales, y devolver en caso positivo una estructura sintáctica.

El parser es capaz de reconocer oraciones transitivas (*el perro comió el hueso/the dog ate the bone*), oraciones inergativas (*el perro corrió/the dog run*) y oraciones inacusativas (*el perro llegó*/*the dog arrived*)

## Modo de uso
Para utilizar el programa es necesario ejecutar el archivo `main.py`, ubicado en la carpeta principal del repositorio. Hecho esto, el usuario verá un menú de cinco opciones: 

**1. Parser** *(Permite introducir la oración a parsear)*<br>
**2. Manual derivation** *(Permite generar la derivación manualmente, como en la implementación de Warstadt)*<br>
**3. Change grammar** *(Permite seleccionar una gramática distinta)*<br>
**4. Enable/disable stage-by-stage view** *(Cuando está activado, muestra el paso a paso de una derivación, incluyendo las reglas aplicadas)*<br>
**5. Quit** *(Finaliza el programa)*

### La gramática
Por defecto, el Lexicon de la gramática se genera a partir del archivo `lexicon.xml` de la carpeta `data`. La elección de este archivo puede ser modificada mediante la opción 3 del menú principal.<br>
Las gramáticas están definidas en el formato XML, que organiza el léxico como un árbol de nodos. A cada ítem le corresponde un elemento con la etiqueta `<word>`, dentro del cual se insertan nuevos elementos con una etiqueta distinta para cada rasgo: la etiqueta `<phon>` corresponde a los rasgos fonético, `<syn>` a los sintácticos, y `<sem>` a los semánticos (aunque estos últimos no son utilizados en la implementación actual). Por ejemplo, la entrada léxica correspondiente a un verbo como *corrió* sería la siguiente:
```
    <word>
        <phon>llegó</phon>
        <syn>
            <cat>V</cat>
        </syn>
        <sem>none</sem>
    </word>
    <word>
        <phon>comió</phon>
        <syn>
            <cat>V</cat>
            <sel>D</sel>
            <sel>D/</sel>
        </syn>
        <sem>none</sem>
    </word>
```
Los rasgos sintácticos se subdividen en rasgos categoriales (`Cat_Feature`) y de selección (`Trigger_Feature`). Los primeros se insertan dentro de la etiqueta `<syn>`; y los segundos, dentro de `<sel>`. <br>
#### Merge interno
Los rasgos de selección pueden ir acompañados de una **barra al final** (`D/`). Este operador le indica a la gramática que el ítem léxico en cuestión se somete a merge interno junto a otro ítem de la categoría declarada (en este caso, *llegó* primero se combina mediante merge externo con un determinante, y luego se combina con este determinante mediante merge interno, lo que en la práctica supone que el D se "mueva" o más bien se copie en la posición de especificador del SV). Este operador hace que el merge interno sólo pueda efectuarse con ciertos ítems léxicos, y una vez que los demás rasgos de selección ya fueron cotejados. Fue necesario añadir esta restricción, que no aparece en la implementación original, con el fin de subsanar el hecho de que los rasgos de selección (y todos los rasgos) constituyen un conjunto, y por lo tanto no están ordenados.
#### Categorías funcionales
Para indicar que un item léxico es una categoría funcional se necesitan dos cosas: 1) el contenido del rasgo fonético debe aparecer entre corchetes, y 2) la categoría del primer elemento con el que se combina debe estar precedida por una barra. La **barra al comienzo** (`/V`) permite que el algoritmo sepa en qué momento de la derivación debe seleccionarse la categoría funcional. Por ejemplo, así quedaría la entrada léxica de un *v* que se pudiera combinar con *llegó*:
```
    <word>
        <phon>[]</phon>
        <syn>
            <cat>v</cat>
            <sel>/V</sel>
            <sel>D/</sel>
        </syn>
        <sem>none</sem>
    </word>
```
Dada esta gramática, una oración como *El perro llegó* pasaría por las siguientes etapas: una vez satisfechos los rasgos de selección del *V*, el *v* es seleccionado, luego se combina por merge externo con el *V*, y finalmente se combina por merge interno con el *D*, dando lugar a la siguiente estructura:

![](https://img001.prntscr.com/file/img001/YnnsxD8ASmy8ea0zR2ilIQ.png)

Como se ve, es posible definir una gramática de tal modo que dos o más categorías funcionales se combinen entre sí.
<br>También es posible declarar dos ítems con los mismos rasgos fonéticos y categoriales, pero diferentes rasgos de selección. En este caso, el programa generará dos lexical arrays distintos, e imprimirá todas las derivaciones exitosas. 
### Implementación
#### Reglas
El programa utiliza un algoritmo bottom-up que se basa en las siguientes reglas (utilizamos el nombre de las variables tal como aparecen en la función `autotf()` del módulo `derivations/parser`.

| N°  | If len(x.triggers) | & len(workspace.w) | & len(lexical_array.the_list) | then:
| ------------- |:-------------:| --------  | ---------  |  ------- |
| 0 | | | | select(x) 
| 1 | 0 | 1 | 0 | *success*
| 2| = 1 (con /) | = 1 | | *internal* merge(x,y)
| 3| | = 1 | > 0 | select(y)
| 4| 0 | = 2 | > 0 | select(z)
| 5| = 0 | = 2 & len(y.triggers) > 0 | | merge(y,x)
| 6| = 1 | = 2 | | merge(x,y)
| 7| = 1 | = 3 | | merge(z,y)

La numeración de las reglas indica precedencia en cuanto a su aplicación. *x* es el elemento a analizar en cada etapa de la derivación, mientras que *y* es un segundo elemento que puede pertenecer al lexical array (en la regla 2, *y* es el elemento con el índice inmediatamente superior a *x*, salvo cuando se trata de una categoría funcional) o al workspace, e incluso estar contenido en *x* (en el caso del merge interno). El primer valor que toma *x* es el *lexical item token* correspondiente a la última palabra de la oración (i.e., que coincide con sus rasgos fonéticos), el cual aparece indexado en el *lexical array* con el número 0 (`x.idx = 0`).
La derivación falla cuando su último estado no coincide con ninguna de las posibilidades ilustradas en la tabla, o cuando falla el merge (si el rasgo de selección de *x* no coincide con el de *y*, o si coincide pero *y* tiene rasgos de selección todavía sin satisfacer).

#### Transfer
La operación Transfer, tal como se encuentra definida en el trabajo de Collins-Stabler, interviene en el pasaje entre la estructura sintáctica y las formas fonética (Transfer<sub>PF</sub>) y semántica (Transfer<sub>LF</sub>). Nuestro programa implementa una versión simplificada de Transfer<sub>PF</sub>, que se aplica a toda derivación exitosa mediante la función recursiva `transfer()`. Este algoritmo opera de la siguiente manera:

* Si *x* e *y* son ítems léxicos (i.e., objetos sintácticos simples), se añaden a la lista `transferred_sentence` sus respectivos rasgos `Phon`, en este orden: primero el elemento con rasgos de selección (es decir, el núcleo) y luego el elemento seleccionado por aquél (que será el complemento).
* Si *x* es núcleo pero, al mismo tiempo, un conjunto de objetos sintácticos (i.e., un objeto sintáctico complejo), entonces se añade a la lista en primer lugar el rasgo `Phon` de *y* (especificador), en caso de que éste sea un item léxico, y luego se aplica nuevamente `transfer()` sobre *x*. En cambio, si *y* también es un objeto complejo, entonces se aplica `transfer()` primeramente a *y*, y luego a *x*.

Mediante estas reglas el programa obtiene la forma lineal de la estructura sintáctica generada, y luego evalúa si coincide con la de la oración introducida por el usuario. En caso afirmativo, la derivación es exitosa.

#### Categorías funcionales
Las categorías funcionales se añaden mediante la función `add_functional_categories()`. Sencillamente, aquí el algoritmo revisa la lista de ítems y evalúa si para cada elemento (sea funcional o léxico) existe una categoría funcional que lo seleccione. En caso afirmativo, se añade en último lugar a la lista con la que se elaborará el *lexical array*.
#### Manejo de ítems duplicados
Cuando dos o más entradas léxicas coinciden en sus rasgos fonéticos y categoriales, la función `get_possible_lexicons()` genera todas las combinaciones posibles de ítems, de tal modo que en cada combinación no haya más que un ítem con dichos rasgos. Estas listas son recogidas luego por la función `parse()`, que produce tantas derivaciones como listas haya. Finalmente se imprimen todas las derivaciones exitosas. En `data/lexicon.xml` hay dos `v` con distintos rasgos, uno para la oración inacusativa (con merge interno) y otro para las oraciones transitiva e inergativa.

### Problemas conocidos
La mayoría de los escollos que presenta este parser se deben a que utiliza la forma fonética (de la oración-input) para reconstruir la estructura sintáctica: un camino inverso al que proponen las gramáticas generativas. Y si bien la implementación de *transfer* subsana desde el punto de vista teórico esta limitación, lo cierto es que la estructura sintáctica se mantiene atada a la linealidad de la frase, en la medida en que los dos primeros elementos (empezando desde la derecha) siempre intentarán combinarse entre sí, o a lo sumo se seleccionará un tercero (regla 4). Esto vuelve imposible el reconocimiento de -por ejemplo- oraciones interrogativas o focalizadas donde el elemento sintáctico de la derecha (el primero en combinarse) se realiza luego en el margen izquierdo de la oración. Y asimismo dificulta el análisis de oraciones ditransitivas (como *el perro entregó el hueso al dueño*, en las que el OD ocuparía la posición de especificador y el OI, la de complemento. En nuestra implementación, en cambio, estas posiciones aparecen invertidas, debido al orden en que se da el merge.

![](https://img001.prntscr.com/file/img001/yzdTEc4TQW-G-MTzhEvQsQ.png)

Nótese que `12,V` es un objeto complejo, y que por lo tanto en `13,V`, `10,P` es especificador. Esto supone que la oración generada por `transfer()` será *el perro al dueño entregó el hueso*. A su vez, un merge interno entre `12,V` y `13,V` resulta imposible, ya que el primer objeto tiene rasgos de selección sin satisfacer. El objeto `14,V` sí podría combinarse con `13,V`, pero sólo después del merge externo con `15,D`, por lo que el sintagma verbal quedaría por encima del argumento externo. De todos modos, un Lexicon con rasgos de selección y/o categorías funcionales distintas podría llegar a dar cuenta de esta oración sin necesidad de modificar el código.

### A futuro
Elegimos el parser bottom-up porque es el que mejor se adapta a la implementación y el formalismo originales. Tal vez sería posible mejorarlo mediante la adición de nuevos operadores (como una o varias categorías iniciales), y permitiendo que se combinen elementos independientemente del orden lineal.

Otra alternativa sería recurrir a un parser top-down capaz de generar todas las oraciones posibles de una gramática, y luego evaluar si la oración ingresada por el usuario coincide con alguna de ellas. Para esto, podríamos seguir el mecanismo descrito por [Shieber et al. (2005)](https://arxiv.org/abs/cmp-lg/9404008):
1. Initialize the chart to the empty set of items and the agenda to the axioms of the deduction system.
2. Repeat the following steps until the agenda is exhausted:
 * a) Select an item from the agenda, called the trigger item, and remove it.
 * b) Add the trigger item to the chart, if the item is not already in the chart.
 * c) If the trigger item was added to the chart, generate all items that can be derived from the trigger item and any items in the chart by one application of a rule of inference, and add these generated items to the agenda.
3. If a goal item is in the chart, the goal is proved, i.e., the string is recognized, otherwise it is not.

Queda por ver cuán compatible sería esta solución con la propuesta de Collins-Stabler.
