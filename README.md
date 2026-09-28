# Laboratorio 7 - Teoria de la computacion

## Ejercicio 1 (Problema 1) - Eliminacion de producciones-epsilon

Programa en Python que:

1. Carga gramaticas libres de contexto desde archivos de texto (`grammars/grammar1.txt`, `grammars/grammar2.txt`).
2. Valida que cada linea del archivo tenga el formato correcto usando una expresion regular. Si una linea esta mal escrita, el programa se detiene inmediatamente mostrando el error.
3. Elimina las producciones-epsilon de la gramatica, mostrando en pantalla cada paso del algoritmo:
   - Busqueda de simbolos anulables.
   - Generacion de las nuevas producciones considerando las 2^m combinaciones posibles para cada produccion con `m` simbolos anulables.
4. Muestra en pantalla la gramatica resultante sin producciones-epsilon.

### Formato de archivo de gramatica

Cada linea representa las producciones de un no-terminal:

```
<NO_TERMINAL> -> <cuerpo1> | <cuerpo2> | ...
```

- `<NO_TERMINAL>`: una unica letra mayuscula (A-Z).
- `<cuerpo>`: concatenacion de simbolos individuales (mayusculas para no-terminales, minusculas/digitos para terminales), o la palabra `epsilon` para representar la cadena vacia.
- Los distintos cuerpos de un mismo no-terminal se separan con `|`.

Ejemplo valido:

```
S -> 0A0 | 1B1 | BB
A -> C
B -> S | A
C -> S | epsilon
```

Expresion regular usada para validar cada linea:

```
^[A-Z]\s*->\s*(epsilon|e|[A-Za-z0-9]+)(\s*\|\s*(epsilon|e|[A-Za-z0-9]+))*\s*$
```

### Como ejecutar

```bash
python grammar_simplifier.py
```

Por defecto procesa `grammars/grammar1.txt` y `grammars/grammar2.txt`. Tambien se puede indicar explicitamente uno o mas archivos:

```bash
python grammar_simplifier.py grammars/grammar1.txt
python grammar_simplifier.py ruta/a/otra_gramatica.txt
```

### Gramaticas utilizadas (tomadas del Problema 2 del laboratorio)

**Gramatica 1** (`grammars/grammar1.txt`):

```
S -> 0A0 | 1B1 | BB
A -> C
B -> S | A
C -> S | epsilon
```

**Gramatica 2** (`grammars/grammar2.txt`):

```
S -> aAa | bBb | epsilon
A -> C | a
B -> C | b
C -> CDE | epsilon
D -> A | B | ab
```

### Video de demostracion

[Pendiente: agregar enlace al video de YouTube (no listado)]
