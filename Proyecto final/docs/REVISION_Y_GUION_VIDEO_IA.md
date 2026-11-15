# Revisión del proyecto y guion para video

## Revisión frente al enunciado

### Resultado general

AgroScript tiene una implementación funcional y una base formal sólida para
las fases 2 y 3. La fase 1 está implementada, pero la evidencia escrita puede
fortalecerse: el enunciado pide expresiones regulares explícitas y una matriz
de transición completa, mientras que la especificación actual presenta las
formas de tokens en una tabla descriptiva y resume las transiciones por grupos.

| Requisito | Evidencia actual | Estado |
|---|---|---|
| Lenguaje propio de dominio | AgroScript describe declaraciones, decisiones, ciclos y acciones de riego cafetero. | Cumple; la unicidad frente a otros grupos debe confirmarse con el docente. |
| Alfabeto y tokens | `docs/ESPECIFICACION_FORMAL.md` define `Σ`, los tokens y sus formas. | Parcial: agregar las expresiones regulares en notación explícita. |
| AFD, aceptación y rechazo | `agroscript/lexer.py` implementa una tabla de 27 estados, `q0`–`q25` y `qE`; documenta aceptación y los estados de rechazo `q3`, `q5` y `q13`. La página solo ilustra un recorrido, no el grafo completo. | Cumple en código; falta presentar el grafo y la matriz completa como evidencia legible. |
| Ambigüedad, BNF y G2 | La especificación muestra G0, G1 y G2, dos agrupaciones para `ID - ID * ID`, eliminación de recursividad izquierda, `sino_opt` y conjuntos FIRST/FOLLOW. | Cumple; conviene sustentar cada transformación con un ejemplo en vivo. |
| Parser y árbol | El CLI recibe la ruta de un `.agro`; el lexer y el parser construyen el árbol o reportan errores. Hay recuperación sintáctica. | Cumple. |
| Pruebas | Hay pruebas de lexer, parser y recuperación; las 10 pruebas pasan en la validación actual. | Cumple para los casos cubiertos. |
| Interacción humano-computador | `index.html` ofrece un configurador de valores NUM, explica entradas inválidas y actualiza el árbol. | Cumple como interfaz; es una plantilla de AgroScript, no un editor o parser general. |
| Aprendizaje automático (R.A.3) | No se encontró un modelo ni un algoritmo de aprendizaje automático. | No evidenciado. No afirmar que el proyecto usa ML; confirmar con el docente si requiere un componente adicional. |
| Trabajo cooperativo y sustentación individual | No se pueden demostrar únicamente con los archivos del programa. | Aportar evidencia del equipo y preparar una explicación individual. |

### Evidencias que recomiendo completar

1. Añadir a la especificación una tabla de expresiones regulares. Por ejemplo,
   para los tokens actuales: `ID = [A-Za-z][A-Za-z0-9_]*` y
   `NUM = [0-9]+(\.[0-9]+)?`. Precisar que estas expresiones describen el
   lenguaje; el lexer implementado usa una tabla AFD y no el módulo `re`.
2. Incluir el grafo completo del AFD y la matriz completa (estados por filas y
   categorías de entrada por columnas), o una impresión vectorizada de
   `TABLA`. Indicar que las transiciones no listadas van a `qE` y marcar
   cuáles estados aceptan.
3. Confirmar que AgroScript es distinto de los lenguajes asignados a los demás
   grupos. Ese requisito no se puede comprobar desde este repositorio.
4. Preparar una demostración individual: cambiar una transición del AFD,
   rastrear un lexema estado por estado, modificar una producción y explicar
   por qué G2 sigue siendo LL(1). El video apoya la presentación, pero no
   reemplaza esta sustentación.
5. Si el R.A.3 se evalúa como requisito literal de ML, consultarlo antes de
   afirmar cumplimiento. La interfaz actual favorece la interacción y explica
   errores de gramática, pero no aprende de datos ni hace predicciones.

### Preguntas útiles para la sustentación

- ¿Por qué `60.5` se acepta y `60.` se rechaza? ¿Qué papel cumplen `q3` y `q4`?
- ¿Qué diferencia hay entre el estado no final `q13` y el sumidero `qE`?
- ¿Cómo se reconoce `<=` como un token único?
- ¿Qué dos árboles puede producir G0 para `ID - ID * ID`?
- ¿Qué problema de G1 resuelve G2 y cómo se factoriza la opción `sino`?
- ¿En qué puntos se recupera el parser después de un error?
- ¿Qué hace la interfaz HTML y qué análisis ejecuta realmente Python?

## Guion listo para copiar en una IA de video

```text
Genera un video educativo en español latinoamericano sobre el proyecto
académico AgroScript. Duración aproximada: 3 minutos y 45 segundos. Formato
16:9, 1080p, ritmo claro y profesional, con narración natural, subtítulos
breves y diagramas legibles. Audiencia: estudiantes de Teoría de Lenguajes
Formales.

Usa como referencia el proyecto AgroScript: un mini-lenguaje de dominio para
describir programas de riego cafetero, implementado con Python. No inventes
funciones, resultados, transiciones ni evidencia. El programa reconoce y
analiza sintaxis; no evalúa variables, no controla equipos de riego y no
ejecuta operaciones agrícolas.

Importante para representar correctamente la implementación:
- El lexer usa un AFD tabulado de 27 estados: q0–q25 y qE. F = Q menos
  {q0, q3, q5, q13, qE}; qE es el sumidero. q3, q5 y q13 ayudan a diagnosticar
  números incompletos, cadenas sin cerrar y el signo ! aislado.
- El lexer aplica coincidencia más larga y clasifica las palabras reservadas
  después de reconocer identificadores. No se implementa con expresiones
  regulares de Python.
- G0 es ambigua para expresiones como ID - ID * ID. G1 organiza precedencia
  pero conserva recursividad izquierda en expr y termino. G2 elimina esa
  recursividad, factoriza sino como sino_opt y está diseñada para LL(1).
- El parser de Python es descendente recursivo, recibe una ruta .agro, produce
  un árbol o errores léxicos/sintácticos y recupera en límites de sentencias
  y bloques.
- La página HTML tiene un configurador limitado a una plantilla: el usuario
  ingresa cinco valores NUM y la página actualiza la muestra del árbol. La
  página no ejecuta el parser Python ni acepta programas AgroScript
  arbitrarios. Para analizar un archivo real se usa el CLI.
- La interfaz mejora la interacción humano-computador, pero el proyecto no
  implementa un modelo de aprendizaje automático. No afirmes que usa ML.

ESTRUCTURA Y NARRACIÓN

Escena 1 — 0:00 a 0:22 — El problema y el lenguaje
Visual: título “AgroScript: un DSL para riego cafetero”; muestra brevemente
el programa ejemplo de la presentación.
Narración: “AgroScript es un mini-lenguaje creado para describir decisiones
de riego en una finca cafetera. Su objetivo es reconocer si un programa tiene
la forma correcta. No evalúa los datos ni controla equipos: aplica los
conceptos de lenguajes formales a un problema de dominio.”

Escena 2 — 0:22 a 0:55 — Alfabeto y análisis léxico
Visual: caracteres que se convierten en tokens; diagrama sencillo con q0,
q1, q2, q3, q4 y qE. Muestra las formas ID = [A-Za-z][A-Za-z0-9_]* y
NUM = [0-9]+(\.[0-9]+)?, e indica que son notación formal: el código no usa
el módulo re. Rotula que el AFD completo tiene 27 estados.
Narración: “El primer componente es el lexer. Parte del alfabeto Sigma, que
incluye letras, dígitos, operadores, delimitadores y separadores. Un
identificador inicia con una letra y puede continuar con letras, dígitos o
guion bajo; un número puede tener una parte decimal. El AFD recorre los
caracteres y aplica coincidencia más larga. Las palabras como var, si y
regar se clasifican como reservadas después de reconocer un identificador.”

Escena 3 — 0:55 a 1:18 — Recorrido y errores léxicos
Visual: anima 60.5 por q0, q2, q2, q3 y q4; después contrasta con 12., una
cadena sin cerrar y ! aislado. Etiqueta q3, q5 y q13 como estados no finales;
qE como sumidero.
Narración: “En el número 60.5, los dígitos llevan a q2, el punto a q3 y el
dígito decimal a q4. En cambio, 12. termina en q3, que no es de aceptación.
El lexer también informa cadenas sin cerrar desde q5 y un signo de
exclamación aislado desde q13. Así, cada error tiene una causa relacionada
con el recorrido del autómata.”

Escena 4 — 1:18 a 1:48 — Ambigüedad de G0
Visual: muestra ID - ID * ID con dos árboles: uno con MENOS como raíz y otro
con POR como raíz.
Narración: “En la fase sintáctica, la gramática inicial G0 no fija la
precedencia. Para ID menos ID por ID pueden construirse dos agrupaciones:
ID menos (ID por ID), o (ID menos ID) por ID. Los operadores quedan en raíces
distintas y la estructura de la expresión no está determinada.”

Escena 5 — 1:48 a 2:23 — De G1 a G2 LL(1)
Visual: G1 separa expr, termino y factor; luego resalta las colas expr prima
y termino prima de G2. Muestra sino_opt para la opción sino.
Narración: “G1 organiza los niveles: factor, multiplicación y división,
luego suma y resta. Sin embargo, expr y termino aún son recursivos por la
izquierda. G2 transforma esas reglas en colas recursivas por la derecha y
representa sino opcional mediante sino_opt. Con FIRST y FOLLOW se justifican
las decisiones de un token y se obtiene una gramática LL(1).”

Escena 6 — 2:23 a 2:58 — Lexer y parser en Python
Visual: flujo archivo .agro → AFD → tokens → parser descendente recursivo →
árbol o errores. Mostrar el comando `python main.py ejemplos/riego_valido.agro`.
Narración: “La implementación separa las responsabilidades. El lexer usa una
tabla de transiciones y conserva los recorridos de estados. El parser tiene
un método por no terminal de G2 y construye el árbol de derivación. Si ocurre
un error, informa su ubicación y trata de continuar en límites seguros. El
CLI procesa archivos indicados por el usuario; no depende de una ruta fija.”

Escena 7 — 2:58 a 3:28 — Interfaz para ingresar valores
Visual: muestra el formulario HTML: humedad, meta, temperatura, multiplicador
de riego y límite; ingresa 60.5 y luego 60. para mostrar el mensaje. Avanza
al diagrama del árbol y al control de pasos.
Narración: “La presentación agrega una forma de acercar el lenguaje al
usuario: en vez de escribir código, ingresa valores NUM. El formulario
explica, por ejemplo, que un decimal necesita dígitos antes y después del
punto. También muestra una plantilla generada y permite recorrer su árbol.
Esta interfaz es una muestra guiada; el análisis general de archivos lo
realiza el parser de Python.”

Escena 8 — 3:28 a 3:45 — Alcance y cierre
Visual: resumen con “AFD · G2 LL(1) · parser · árbol · errores”; cierre con
“Analizar no es ejecutar”.
Narración: “AgroScript conecta alfabeto, autómatas, gramáticas y construcción
de software. La interfaz favorece la interacción, aunque esta versión no
implementa aprendizaje automático. El resultado central es un analizador
formal que puede explicarse, probarse y sustentarse.”

Indicaciones finales:
- Mantén en pantalla los símbolos y estados el tiempo suficiente para leerlos.
- Usa diagramas limpios; no inventes una matriz de transiciones distinta de la
  implementación.
- No presentes la interfaz HTML como si ejecutara Python.
- No añadas claims de machine learning, ejecución de riego o evaluación
  semántica.
- Pronuncia “G dos”, “LL uno”, “Sigma” y “epsilon” con claridad.
```
