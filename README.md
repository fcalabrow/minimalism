# Parser minimalista
Este es un parser basado en la implementación de Alex Warstadt del formalismo descrito en "A Formalization of Minimalist Syntax" por Chris Collins y Edward Stabler (2016). Su objetivo es determinar si las oraciones introducidas por el usuario son o no gramaticales, y devolver en caso positivo una estructura sintáctica. 

## Modo de uso
Para utilizar el programa es necesario ejecutar el archivo `main.py`, ubicado en la carpeta principal del repositorio. Ejecutado el archivo, el usuario verá un menú de cinco opciones: 

**1. Parser** *(Permite introducir la oración a parsear)*<br>
**2. Manual derivation** *(Permite generar la derivación manualmente, utilizando el mecanismo original de Warstadt)*<br>
**3. Change grammar** *(Permite seleccionar una gramática distinta)*<br>
**4. Enable/disable stage-by-stage view** *(Cuando está activado, muestra el paso a paso de una derivación, incluyendo las reglas que fueron aplicadas)*<br>
**5. Quit** *(Finaliza el programa)*

### La gramática
Por defecto, el Lexicon de la gramática se genera a partir del archivo `lexicon.xml` de la carpeta `data`. La elección de este archivo puede ser modificada mediante la opción 3 del menú principal.<br>
Las gramáticas están definidas en formato XML, que organiza el léxico como un árbol de nodos. A cada ítem le corresponde un elemento con la etiqueta `<word>`, dentro del cual se insertan nuevos elementos con una etiqueta distinta para cada rasgo: la etiqueta `<phon>` corresponde a los rasgos fonológicos, `<syn>` a los sintácticos, y `<sem>` a los semánticos (aunque estos últimos no son utilizados en la implementación actual). Por ejemplo, la entrada léxica correspondiente a un verbo como *corrió* sería la siguiente:
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
Los rasgos de selección pueden ir acompañados de una **barra al final** (`D/`). Este operador le indica a la gramática que el ítem léxico en cuestión se somete a merge interno junto a otro ítem con la categoría declarada (en este caso, *llegó* primero se combina mediante merge externo con un determinante, y luego se combina con este -u otro- determinante mediante merge interno, lo que en la práctica supone que el D se "mueva" o se copie a la posición de especificador del SV). Este operador hace que el merge interno sólo pueda efectuarse con ciertos ítems léxicos, y una vez que los demás rasgos de selección ya fueron cotejados. Fue necesario añadir esta restricción, que no aparece en la implementación de Warstadt, con el fin de subsanar el hecho de que los rasgos de selección (y todos los rasgos en general) carecen de orden.
#### Categorías funcionales
Para indicar que un item léxico es una categoría funcional se necesitan dos cosas: 1) el contenido del rasgo fonológico debe aparecer entre corchetes, y 2) la categoría del primer elemento con el que se combina debe estar precedida por una barra. La **barra al comienzo** (`/V`) permite que el algoritmo sepa en qué momento de la derivación debe seleccionarse la categoría funcional. Por ejemplo, así quedaría la entrada léxica de un *v* que se pudiera combinar con *llegó*:
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
Dada esta gramática, una oración como *El perro llegó* atravesaría las siguientes etapas: una vez satisfechos los rasgos de selección del *V*, el *v* es seleccionado, luego se combina por merge externo con el *V*, y finalmente se combinar por merge interno con el *D*, dando lugar a la siguiente estructura:

![](https://img001.prntscr.com/file/img001/YnnsxD8ASmy8ea0zR2ilIQ.png)

Como se ve, es posible definir una gramática de tal modo que dos o más categorías funcionales se combinen entre sí.
<br>También es posible declarar dos ítems con los mismos rasgos fonológicos y categoriales, pero diferentes rasgos de selección. En este caso, el programa generará dos lexical arrays distintos, e imprimirá todas las derivaciones exitosas. 
### Implementación
El programa utiliza un algoritmo bottom-up que, a grandes rasgos, se basa en las siguientes reglas:
### Ventajas
### Problemas
