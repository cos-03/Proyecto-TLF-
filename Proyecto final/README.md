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
python main.py ejemplos/riego_valido.agro
python main.py ejemplos/riego_valido.agro --tokens
python -m unittest discover -s tests -v
```

Para recorrer la presentación visual, abre `index.html` en un navegador. La
página incluye un configurador que recibe valores NUM y construye el programa
sin que el usuario escriba código. Si un dato no cumple el formato de la
gramática, muestra el motivo. El árbol de derivación se actualiza con esos
valores y permite avanzar por las expansiones, reproducirlas y consultar la
forma sentencial. Para analizar otro archivo o regenerar el árbol, usa Python
mediante los comandos anteriores.

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
