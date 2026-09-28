"""
Laboratorio 7 - Teoria de la computacion
Ejercicio 1: Carga de gramaticas, validacion de producciones mediante
expresiones regulares, y eliminacion de producciones-epsilon.

Uso:
    python grammar_simplifier.py [archivo1.txt archivo2.txt ...]

Si no se pasan argumentos, se procesan por defecto:
    grammars/grammar1.txt
    grammars/grammar2.txt

Formato esperado de cada linea del archivo de gramatica:
    <NO_TERMINAL> -> <cuerpo1> | <cuerpo2> | ...

Donde:
    - <NO_TERMINAL> es una unica letra mayuscula (A-Z).
    - "->" separa el no-terminal de sus producciones.
    - Cada <cuerpo> es una concatenacion de simbolos (letras mayusculas
      para no-terminales, letras minusculas/digitos para terminales),
      o bien la palabra "epsilon" (o el simbolo "e") para representar
      la cadena vacia.
    - Los distintos cuerpos de produccion para el mismo no-terminal se
      separan con el operador OR "|".

Ejemplo valido:
    S -> 0A0 | 1B1 | BB

Ejemplo invalido (detiene la ejecucion):
    s -> 0a0 | 1B1      (no-terminal en minuscula)
    S --> 0A0           (flecha mal escrita)
    S -> 0A0 |          (cuerpo vacio tras el OR)
"""

import sys
import re
from itertools import combinations
from collections import defaultdict

EPSILON = "epsilon"

# Un no-terminal: una sola letra mayuscula.
# Un cuerpo de produccion: uno o mas simbolos alfanumericos individuales
# (letras mayusculas, minusculas o digitos), o la palabra "epsilon"/"e"
# representando la cadena vacia.
LINE_REGEX = re.compile(
    r'^[A-Z]\s*->\s*(epsilon|e|[A-Za-z0-9]+)(\s*\|\s*(epsilon|e|[A-Za-z0-9]+))*\s*$'
)


class GrammarFormatError(Exception):
    """Se lanza cuando una linea del archivo de gramatica no es valida."""
    pass


def validate_line(line, line_number, source):
    """Valida una linea contra la expresion regular de producciones.
    Si no es valida, detiene la ejecucion del programa."""
    if not LINE_REGEX.match(line):
        raise GrammarFormatError(
            f"Linea invalida en '{source}' (linea {line_number}): '{line}'\n"
            f"  Se esperaba el formato: <NO_TERMINAL> -> <cuerpo1> | <cuerpo2> | ..."
        )


def parse_line(line):
    """Convierte una linea ya validada en (no_terminal, lista_de_cuerpos).
    Cada cuerpo es una tupla de simbolos; la tupla vacia () representa epsilon."""
    lhs, rhs = line.split("->", 1)
    lhs = lhs.strip()
    bodies = []
    for raw_body in rhs.split("|"):
        raw_body = raw_body.strip()
        if raw_body in (EPSILON, "e"):
            bodies.append(tuple())
        else:
            bodies.append(tuple(raw_body))
    return lhs, bodies


def load_grammar_file(path):
    """Carga y valida un archivo de gramatica linea por linea.
    Retorna un diccionario {no_terminal: [cuerpos...]} y detiene la
    ejecucion si alguna linea esta mal escrita."""
    productions = defaultdict(list)
    order = []

    with open(path, "r", encoding="utf-8") as f:
        raw_lines = [l.rstrip("\n") for l in f]

    print(f"\n>>> Cargando archivo: {path}")
    for i, raw_line in enumerate(raw_lines, start=1):
        line = raw_line.strip()
        if not line:
            continue

        validate_line(line, i, path)
        print(f"  [OK] Linea {i}: '{line}'")

        lhs, bodies = parse_line(line)
        if lhs not in order:
            order.append(lhs)
        productions[lhs].extend(bodies)

    return productions, order


def format_body(body):
    return EPSILON if body == tuple() else "".join(body)


def format_grammar(productions, order):
    lines = []
    for nt in order:
        bodies = productions.get(nt, [])
        if not bodies:
            continue
        bodies_str = " | ".join(format_body(b) for b in bodies)
        lines.append(f"{nt} -> {bodies_str}")
    return lines


def print_grammar(productions, order, title):
    print(f"\n{title}")
    print("-" * len(title))
    for line in format_grammar(productions, order):
        print(f"  {line}")


def find_nullable_symbols(productions):
    """Encuentra el conjunto de simbolos anulables (que pueden derivar
    la cadena vacia), mostrando el proceso iterativo en pantalla."""
    print("\nPaso 1: Encontrar simbolos y producciones anulables")
    print("-" * 52)

    nullable = set()

    # Caso base: no-terminales con produccion directa a epsilon.
    for nt, bodies in productions.items():
        if tuple() in bodies:
            nullable.add(nt)
            print(f"  {nt} es anulable (produccion directa: {nt} -> {EPSILON})")

    # Cierre: no-terminales cuyos cuerpos son enteramente anulables.
    changed = True
    round_num = 1
    while changed:
        changed = False
        round_num += 1
        for nt, bodies in productions.items():
            if nt in nullable:
                continue
            for body in bodies:
                if body and all(sym in nullable for sym in body):
                    nullable.add(nt)
                    changed = True
                    print(
                        f"  {nt} es anulable (produccion {nt} -> {format_body(body)}, "
                        f"todos sus simbolos son anulables: {', '.join(body)})"
                    )
                    break

    print(f"\n  Conjunto final de simbolos anulables: "
          f"{{{', '.join(sorted(nullable)) if nullable else '(ninguno)'}}}")
    return nullable


def remove_epsilon_productions(productions, order, nullable):
    """Elimina las producciones-epsilon generando, para cada produccion
    con m simbolos anulables, los 2^m casos posibles (con y sin cada
    simbolo anulable presente), descartando el caso que produce epsilon."""
    print("\nPaso 2: Generar nuevas producciones (2^m combinaciones) y eliminar epsilon")
    print("-" * 74)

    new_productions = defaultdict(set)

    for nt in order:
        for body in productions.get(nt, []):
            if body == tuple():
                print(f"  Se elimina la produccion {nt} -> {EPSILON}")
                continue

            nullable_positions = [i for i, s in enumerate(body) if s in nullable]
            m = len(nullable_positions)

            if m == 0:
                new_productions[nt].add(body)
                continue

            print(f"\n  Produccion original: {nt} -> {format_body(body)}  "
                  f"(m = {m} simbolo(s) anulable(s): "
                  f"{', '.join(body[i] for i in nullable_positions)})")
            print(f"    Se generan 2^{m} = {2 ** m} combinaciones:")

            for r in range(0, m + 1):
                for combo in combinations(nullable_positions, r):
                    # 'combo' son las posiciones anulables que se OMITEN en este caso.
                    new_body = tuple(
                        s for i, s in enumerate(body) if i not in combo
                    )
                    kept = [body[i] for i in nullable_positions if i not in combo]
                    removed = [body[i] for i in combo]
                    label = (
                        f"quitando {', '.join(removed) if removed else '(nada)'}"
                    )
                    if new_body == tuple():
                        print(f"      - {label} -> resultado vacio: se descarta "
                              f"(no se reintroduce {nt} -> {EPSILON})")
                        continue
                    is_new = new_body not in new_productions[nt] and new_body != body
                    new_productions[nt].add(new_body)
                    tag = "(nueva)" if is_new else ""
                    print(f"      - {label} -> {nt} -> {format_body(new_body)} {tag}")

    # Convertir sets a listas ordenadas para una salida determinista.
    result = {nt: sorted(bodies, key=lambda b: (len(b), b)) for nt, bodies in new_productions.items()}
    return result


def process_grammar_file(path):
    print("\n" + "=" * 70)
    print(f"PROCESANDO GRAMATICA: {path}")
    print("=" * 70)

    try:
        productions, order = load_grammar_file(path)
    except GrammarFormatError as e:
        print(f"\n[ERROR] {e}")
        print("Ejecucion detenida debido a un error de formato en la gramatica.")
        sys.exit(1)

    print_grammar(productions, order, "Gramatica original (interpretada)")

    nullable = find_nullable_symbols(productions)

    new_productions = remove_epsilon_productions(productions, order, nullable)

    print_grammar(new_productions, order, "Gramatica resultante SIN producciones-epsilon")


def main():
    args = sys.argv[1:]
    if not args:
        args = ["grammars/grammar1.txt", "grammars/grammar2.txt"]

    for path in args:
        process_grammar_file(path)


if __name__ == "__main__":
    main()
