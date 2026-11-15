# AgroScript

AgroScript es un lenguaje de dominio específico para describir programas de
riego en lotes cafeteros. Este proyecto implementa el formalismo léxico
mediante un AFD, analiza una GIC LL(1) con un parser descendente recursivo,
construye árboles de derivación y reporta errores con ubicación.

El programa **no ejecuta** el riego ni evalúa expresiones. Solo reconoce y
analiza la sintaxis.

## Requisitos

- Python 3.8 o posterior.
- Solo se utiliza la biblioteca estándar.
- No se usan expresiones regulares.

## Uso

Desde esta carpeta:

```text
python main.py
python main.py --web
python main.py ejemplos/riego_valido.agro
python main.py ejemplos/riego_valido.agro --tokens
python -m unittest discover -s tests -v
```

Sin argumentos, `python main.py` inicia el servidor local de la demostración y
abre la página en el navegador. También puedes iniciar la demo con
`python main.py --web`; cierra el servidor con `Ctrl+C`. Con una ruta de
archivo se conserva el análisis por consola.

En la página puedes recorrer las transiciones de cada estado del AFD, cargar
ejemplos o escribir un programa propio y analizarlo con el lexer y parser de
Python. La demo muestra tokens y recorridos de estados, errores por fase y el
árbol sintáctico generado visualmente con los lexemas ingresados (con una vista
textual alternativa). El configurador numérico y el recorrido paso a paso del
árbol también están disponibles. El programa describe el riego: no ejecuta
acciones en dispositivos físicos.

## Explicación visual

Consulta la explicación visual del proyecto en [esta carpeta de Google Drive](https://drive.google.com/drive/folders/13bDJr9cQpSnvhSOU886DY5Oqy3_CNx_F?usp=drive_link).

El código de salida es `0` si el programa es válido, `1` si hay errores
léxicos o sintácticos y `2` si no se pudo leer el archivo.

`--tokens` muestra cada token reconocido y el recorrido de estados del AFD.
Los comentarios y espacios se descartan.

## Ejemplo

```text
programa finca_la_esperanza {
    var humedad = 42;
    var meta = 60.5;
    si (humedad < meta) {
        regar((meta - humedad) * 2);
    } sino {
        alerta("humedad óptima, no se riega");
    }
}
```

También se incluyen programas con errores para comprobar la recuperación:

```text
python main.py ejemplos/error_lexico.agro --tokens
python main.py ejemplos/error_sintactico.agro
```

## Fase 1: análisis léxico

El lexer está dirigido por la tabla `TABLA` de `agroscript/lexer.py`. El AFD
tiene estados `q0`–`q25` y el sumidero `qE`; reconoce identificadores,
números enteros y decimales, cadenas, operadores, delimitadores, comentarios
y espacios. Implementa coincidencia más larga y prioridad de palabras
reservadas. La tabla conserva los estados de rechazo intermedios `q3`, `q5`
y `q13`, que permiten explicar números incompletos, cadenas sin cerrar y
operadores `!` aislados.

Formalmente, `M = (Q, Σ, δ, q0, F)`:

- `Q = {q0, q1, ..., q25, qE}` y `|Q| = 27`.
- `Σ = L ∪ D ∪ S ∪ W ∪ O ∪ E`, con letras, dígitos, símbolos del lenguaje,
  blancos, otros caracteres ASCII imprimibles y caracteres españoles
  especificados para cadenas y comentarios.
- `F = Q \\ {q0, q3, q5, q13, qE}`.
- `δ` es total sobre `Q × Σ`; toda transición no explícita conduce a `qE`,
  que es sumidero.

## Fase 2: gramática y parser

La gramática de implementación es G2: sin recursividad por la izquierda,
factorizada y LL(1). El parser tiene un método por no terminal y construye un
árbol sintáctico con hojas para los tokens y `ε` para producciones vacías.
En la lista de sentencias, los errores se sincronizan en `;`, inicios de
sentencia o `}` para reducir errores en cascada.

```bnf
<programa> ::= PROGRAMA ID LLAVE_A <sentencias> LLAVE_C
<sentencias> ::= <sentencia> <sentencias> | ε
<sentencia> ::= <declaracion> | <asignacion> | <condicional> | <ciclo> | <accion>
<declaracion> ::= VAR ID ASIG <expr> PYC
<asignacion> ::= ID ASIG <expr> PYC
<condicional> ::= SI PAR_A <condicion> PAR_C <bloque> <sino_opt>
<sino_opt> ::= SINO <bloque> | ε
<ciclo> ::= MIENTRAS PAR_A <condicion> PAR_C <bloque>
<accion> ::= REGAR PAR_A <expr> PAR_C PYC
           | MOSTRAR PAR_A <expr> PAR_C PYC
           | ALERTA PAR_A CADENA PAR_C PYC
<bloque> ::= LLAVE_A <sentencias> LLAVE_C
<condicion> ::= <expr> <oprel> <expr>
<oprel> ::= IGUAL | DIF | MENOR | MENORIG | MAYOR | MAYORIG
<expr> ::= <termino> <expr'>
<expr'> ::= MAS <termino> <expr'> | MENOS <termino> <expr'> | ε
<termino> ::= <factor> <termino'>
<termino'> ::= POR <factor> <termino'> | DIV <factor> <termino'> | ε
<factor> ::= MENOS <factor> | PAR_A <expr> PAR_C | ID | NUM
```

La precedencia es: menos unario, multiplicación/división y suma/resta.
Los operadores binarios se asocian a la izquierda. Los bloques delimitados
por llaves evitan el problema del `sino` colgante.

La justificación de ambigüedad, eliminación de recursividad izquierda,
factorización, conjuntos FIRST/FOLLOW y la especificación del AFD se desarrolla
en [docs/ESPECIFICACION_FORMAL.md](./docs/ESPECIFICACION_FORMAL.md).

## Rangos del configurador

El configurador limita el umbral didáctico de temperatura a **18–21 °C**, el
rango óptimo de referencia reportado para *Coffea arabica*. La temperatura
actual puede quedar fuera de ese rango: se muestra una advertencia, pero se
acepta como lectura. El rango no sustituye recomendaciones locales ni debe
usarse como umbral de control físico sin calibración del sistema.

La humedad del configurador se refiere a **humedad del suelo en una escala
porcentual calibrada**, por eso sus valores deben estar entre 0 y 100 %. Ese
límite es técnico, no un rango agronómico recomendado: no existe un porcentaje
universal de humedad del suelo para todos los cafetales y sensores. Cenicafé
describe el balance hídrico del café mediante humedad del suelo,
evapotranspiración y precipitación; la calibración de sensores también depende
de las propiedades locales del suelo. Por tanto, la meta debe definirse para el
suelo y sensor usados.

Fuentes:

- [NOAA Climate.gov, “Climate & Coffee”](https://www.climate.gov/news-features/climate-and/climate-coffee): referencia térmica para café arábigo.
- [Cenicafé, “Aplicativo de balance hídrico para el cultivo de café en Colombia” (2022)](https://publicaciones.cenicafe.org/index.php/avances_tecnicos/article/view/188): balance entre humedad del suelo, evapotranspiración y precipitación.
- [University of Arizona Cooperative Extension, guía de calibración de sensores de humedad](https://extension.arizona.edu/publication/guide-maintaining-and-calibrating-field-installed-soil-and-plant-moisture-sensors): las lecturas varían con el suelo y requieren calibración.
