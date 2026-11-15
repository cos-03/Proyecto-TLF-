# Especificación formal de AgroScript

## 1. Lenguaje y alcance

AgroScript describe declaraciones de variables, asignaciones, decisiones,
ciclos y acciones de riego. El analizador comprueba la forma del programa y
produce un árbol de derivación; no evalúa expresiones ni controla dispositivos.

```text
programa finca {
    var humedad = 42;
    var meta = 60.5;
    si (humedad < meta) {
        regar((meta - humedad) * 2);
    } sino {
        alerta("humedad óptima");
    }
}
```

## 2. Formalismo léxico

### 2.1 Alfabeto

El alfabeto finito se particiona en conjuntos disjuntos:

`Σ = L ∪ D ∪ S ∪ W ∪ O ∪ E`

| Conjunto | Símbolos | Uso |
|---|---|---|
| `L` | `a-z`, `A-Z` | Identificadores y palabras reservadas |
| `D` | `0-9` | Números e identificadores |
| `S` | `_ . " + - * / = ! < > ( ) { } ; #` | Operadores y delimitadores |
| `W` | Espacio, tabulador, CR, LF | Separadores |
| `O` | Resto de ASCII imprimible | Solo dentro de cadenas y comentarios |
| `E` | `áéíóúÁÉÍÓÚñÑüÜ¡¿` | Solo dentro de cadenas y comentarios |

Un carácter fuera de `Σ` produce un error léxico. El lexer clasifica cada
carácter en una columna; las transiciones no listadas en la tabla `TABLA`
conducen al sumidero `qE`.

### 2.2 Tokens

| Token | Forma |
|---|---|
| `ID` | Letra ASCII seguida por letras, dígitos o `_` |
| `NUM` | Dígitos, opcionalmente seguidos por `.` y uno o más dígitos |
| `CADENA` | Comilla, símbolos de `Σ` excepto comilla y LF, comilla |
| Palabras reservadas | `programa`, `var`, `si`, `sino`, `mientras`, `regar`, `mostrar`, `alerta` |
| Operadores | `+ - * / = == != < <= > >=` |
| Delimitadores | `( ) { } ;` |
| Comentario | `#` hasta antes del fin de línea; se descarta |
| Espacio | Uno o más blancos; se descartan |

El lexer aplica coincidencia más larga. `<=`, `>=`, `==` y `!=` son tokens
únicos. Un lexema `ID` se convierte en palabra reservada si coincide
exactamente con la tabla de reservadas.

### 2.3 AFD

`M = (Q, Σ, δ, q0, F)` se define por:

- `Q = {q0, q1, ..., q25, qE}`; `q0` es inicial y `qE` es sumidero.
- `F = Q \\ {q0, q3, q5, q13, qE}`.
- `δ(qE, a) = qE` para todo `a ∈ Σ`.
- Las transiciones omitidas en `TABLA` también tienen destino `qE`.

Las transiciones útiles se agrupan así:

| Estado | Entrada | Destino / aceptación |
|---|---|---|
| `q0` | letra, dígito, comilla, operadores, delimitadores, `#`, blanco | `q1`, `q2`, `q5`, `q7-q23`, `q24`, `q25` |
| `q1` | letra, dígito, `_` | `q1` (acepta `ID` o reservada) |
| `q2` | dígito / `.` | `q2` (acepta entero) / `q3` (incompleto) |
| `q3` | dígito | `q4` |
| `q4` | dígito | `q4` (acepta decimal) |
| `q5` | cualquier categoría salvo comilla y LF / comilla | `q5` / `q6` (acepta cadena) |
| `q11`, `q13`, `q15`, `q17` | `=` | `q12`, `q14`, `q16`, `q18` |
| `q24` | cualquier categoría salvo LF | `q24` (comentario descartado) |
| `q25` | espacio o LF | `q25` (blanco descartado) |

`q7-q10` aceptan `+ - * /`; `q19-q23` aceptan `( ) { } ;`. `q11`, `q12`,
`q14-q18` distinguen asignación, igualdad, diferencia, menor y mayor con o
sin igualdad. `q3`, `q5` y `q13` son estados de rechazo no finales que permiten
diagnosticar `12.`, cadenas sin cerrar y `!` aislado.

## 3. Estructura sintáctica

### 3.1 Gramática original `G0`

La definición directa contiene recursividad izquierda en `sentencias` y
`expr`, además de un prefijo común en `condicional`:

```bnf
<programa>    ::= PROGRAMA ID LLAVE_A <sentencias> LLAVE_C
<sentencias>  ::= <sentencias> <sentencia> | ε
<sentencia>   ::= <declaracion> | <asignacion> | <condicional> | <ciclo> | <accion>
<declaracion> ::= VAR ID ASIG <expr> PYC
<asignacion>  ::= ID ASIG <expr> PYC
<condicional> ::= SI PAR_A <condicion> PAR_C <bloque>
                | SI PAR_A <condicion> PAR_C <bloque> SINO <bloque>
<ciclo>       ::= MIENTRAS PAR_A <condicion> PAR_C <bloque>
<accion>      ::= REGAR PAR_A <expr> PAR_C PYC
                | MOSTRAR PAR_A <expr> PAR_C PYC
                | ALERTA PAR_A CADENA PAR_C PYC
<bloque>      ::= LLAVE_A <sentencias> LLAVE_C
<condicion>   ::= <expr> <oprel> <expr>
<oprel>       ::= IGUAL | DIF | MENOR | MENORIG | MAYOR | MAYORIG
<expr>        ::= <expr> MAS <expr> | <expr> MENOS <expr>
                | <expr> POR <expr> | <expr> DIV <expr>
                | MENOS <expr> | PAR_A <expr> PAR_C | ID | NUM
```

`ID - ID * ID` es ambigua: una derivación puede elegir la resta como raíz y
otra la multiplicación. También `ID - ID - ID` admite asociatividad derecha o
izquierda. La gramática no especifica precedencia.

### 3.2 Eliminación de ambigüedad: `G1`

Se separan los niveles de precedencia:

```bnf
<expr>    ::= <expr> MAS <termino> | <expr> MENOS <termino> | <termino>
<termino> ::= <termino> POR <factor> | <termino> DIV <factor> | <factor>
<factor>  ::= MENOS <factor> | PAR_A <expr> PAR_C | ID | NUM
```

La estructura fija precedencia y asociatividad, pero `expr` y `termino`
continúan siendo recursivos por la izquierda.

### 3.3 Eliminación de recursividad izquierda y factorización: `G2`

Se sustituyen las recursiones binarias por colas recursivas por la derecha y
se factoriza el `sino` opcional:

```bnf
<programa>    ::= PROGRAMA ID LLAVE_A <sentencias> LLAVE_C
<sentencias>  ::= <sentencia> <sentencias> | ε
<sentencia>   ::= <declaracion> | <asignacion> | <condicional> | <ciclo> | <accion>
<declaracion> ::= VAR ID ASIG <expr> PYC
<asignacion>  ::= ID ASIG <expr> PYC
<condicional> ::= SI PAR_A <condicion> PAR_C <bloque> <sino_opt>
<sino_opt>    ::= SINO <bloque> | ε
<ciclo>       ::= MIENTRAS PAR_A <condicion> PAR_C <bloque>
<accion>      ::= REGAR PAR_A <expr> PAR_C PYC
                | MOSTRAR PAR_A <expr> PAR_C PYC
                | ALERTA PAR_A CADENA PAR_C PYC
<bloque>      ::= LLAVE_A <sentencias> LLAVE_C
<condicion>   ::= <expr> <oprel> <expr>
<oprel>       ::= IGUAL | DIF | MENOR | MENORIG | MAYOR | MAYORIG
<expr>        ::= <termino> <expr'>
<expr'>       ::= MAS <termino> <expr'> | MENOS <termino> <expr'> | ε
<termino>     ::= <factor> <termino'>
<termino'>    ::= POR <factor> <termino'> | DIV <factor> <termino'> | ε
<factor>      ::= MENOS <factor> | PAR_A <expr> PAR_C | ID | NUM
```

La transformación de `A ::= A α | β` a `A ::= β A'` y
`A' ::= α A' | ε` conserva el lenguaje porque `A'` genera `α*`.
La factorización de `condicional` conserva el prefijo común y deja la decisión
entre `SINO <bloque>` y `ε` para el siguiente token.

### 3.4 FIRST, FOLLOW y LL(1)

`I` abrevia `{VAR, ID, SI, MIENTRAS, REGAR, MOSTRAR, ALERTA}` y
`R` abrevia `{IGUAL, DIF, MENOR, MENORIG, MAYOR, MAYORIG}`.

| No terminal | FIRST | FOLLOW |
|---|---|---|
| `programa` | `PROGRAMA` | `$` |
| `sentencias` | `I, ε` | `LLAVE_C` |
| `sentencia` | `I` | `I, LLAVE_C` |
| `declaracion` | `VAR` | `I, LLAVE_C` |
| `asignacion` | `ID` | `I, LLAVE_C` |
| `condicional` | `SI` | `I, LLAVE_C` |
| `sino_opt` | `SINO, ε` | `I, LLAVE_C` |
| `ciclo` | `MIENTRAS` | `I, LLAVE_C` |
| `accion` | `REGAR, MOSTRAR, ALERTA` | `I, LLAVE_C` |
| `bloque` | `LLAVE_A` | `I, LLAVE_C, SINO` |
| `condicion` | `MENOS, PAR_A, ID, NUM` | `PAR_C` |
| `oprel` | `R` | `MENOS, PAR_A, ID, NUM` |
| `expr` | `MENOS, PAR_A, ID, NUM` | `PYC, PAR_C, R` |
| `expr'` | `MAS, MENOS, ε` | `PYC, PAR_C, R` |
| `termino` | `MENOS, PAR_A, ID, NUM` | `MAS, MENOS, PYC, PAR_C, R` |
| `termino'` | `POR, DIV, ε` | `MAS, MENOS, PYC, PAR_C, R` |
| `factor` | `MENOS, PAR_A, ID, NUM` | `POR, DIV, MAS, MENOS, PYC, PAR_C, R` |

Para cada no terminal con varias alternativas, los conjuntos de predicción son
disjuntos. En particular, `SINO` no pertenece a `FOLLOW(sino_opt)`, los
operadores `MAS/MENOS` no pertenecen a `FOLLOW(expr')`, `POR/DIV` no pertenecen
a `FOLLOW(termino')`, y `LLAVE_C` no inicia una sentencia. Por tanto, G2 es
LL(1) y no ambigua. El lexer resuelve los prefijos `= / ==`, `< / <=`, `> / >=`
y `! / !=` antes del parser.

## 4. Implementación

- `agroscript/lexer.py`: tabla de transiciones, coincidencia más larga,
  palabras reservadas, trazas y errores léxicos.
- `agroscript/parser.py`: un método por no terminal de G2, árbol sintáctico y
  recuperación en modo pánico en límites de sentencia y bloques.
- `agroscript/tree.py`: representación del árbol.
- `agroscript/cli.py`: lectura del archivo, salida de tokens/árbol, errores y
  códigos de salida.

La implementación solo usa la biblioteca estándar y no importa `re`.
