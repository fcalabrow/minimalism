# Parser minimalista
Este es un parser basado en la implementación hecha por Alex Warstadt del formalismo introducido en "A Formalization of Minimalist Syntax" por Chris Collins y Edward Stabler (2016). Su objetivo es determinar si las oraciones introducidas por el usuario son o no gramaticales, y devolver en caso positivo una estructura sintáctica. 

## Modo de uso
Para utilizar este programa es necesario ejecutar el archivo `main.py`, ubicado en la carpeta principal del repositorio. Ejecutado el archivo, aparecerá un menú de cinco opciones: 

**1. Parser** *(Permite introducir la oración a parsear)*<br>
**2. Manual derivation** *(Permite generar la derivación manualmente, utilizando el mecanismo original de Warstadt)*<br>
**3. Change grammar** *(Permite seleccionar una gramática distinta)*<br>
**4. Enable/disable stage-by-stage view** *(Cuando está activado, muestra el paso a paso de una derivación, incluyendo las reglas que fueron aplicadas)*<br>
**5. Quit** *(Finaliza el programa)*

### La gramática
Por defecto, el Lexicon de la gramática se genera a partir del archivo `lexicon.xml` de la carpeta `data`. Este es un documento en formato XML que organiza el léxico como un árbol de nodos. A cada ítem le corresponde un elemento con la etiqueta `<word>`, dentro del cual se insertan nuevos elementos con una etiqueta distinta para cada rasgo: la etiqueta `<phon>` corresponde a los rasgos fonológicos, `<syn>` a los sintácticos, y `<sem>` a los semánticos (aunque estos últimos no son utilizados en la implementación actual). Por ejemplo, la entrada léxica correspondiente a un verbo como "corrió" sería la siguiente:
```
    <word>
        <phon>corrió</phon>
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
        </syn>
        <sem>none</sem>
    </word>
```
Los rasgos sintácticos se subdividen en rasgos categoriales (`Cat_Feature`) y de selección (`Trigger_Feature`). Los primeros se insertan dentro de la etiqueta `<syn>`; y los segundos, dentro de `<sel>`.
