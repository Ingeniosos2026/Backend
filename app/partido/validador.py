import ast

PRIMITIVAS_PERMITIDAS = {
    "correr",
    "patear",
    "direccionPelota",
    "direccionCompañeros",
    "direccionRivales",
    "pelotaCerca",
    "direccionArcoRival",
    "direccionArcoPropio",
}

ATRIBUTOS_PERMITIDOS = {"x", "y"}

OPERADORES_BINARIOS = (
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.FloorDiv,
    ast.Mod,
)

OPERADORES_COMPARACION = (
    ast.Eq,
    ast.NotEq,
    ast.Lt,
    ast.LtE,
    ast.Gt,
    ast.GtE,
    ast.In,
    ast.NotIn,
)

OPERADORES_UNARIOS = (ast.Not, ast.UAdd, ast.USub)

class CodigoComportamientoInvalido(ValueError):
    """El código no cumple las reglas permitidas para un comportamiento."""


class ValidadorComportamiento(ast.NodeVisitor):
    def __init__(self):
        self.variables = {"primitivas"}

    def error(self, mensaje: str):
        raise CodigoComportamientoInvalido(mensaje)

# probé los visit y por como esta hecha la libreria se ve que tienen que tener esos nombres exactos
    def generic_visit(self, node):
        self.error(f"Construcción de python no permitida: "f"{type(node).__name__}")

    def visit_Module(self, node):
        if len(node.body) != 1:
            self.error("El codigo debe definir unicamente la funcion comportamiento(primitivas)")
        funcion = node.body[0]

        if not isinstance(funcion, ast.FunctionDef):
            self.error("Se requiere una funcion comportamiento")

        self.visit(funcion)

    def visit_FunctionDef(self, node):
        if node.name != "comportamiento":
            self.error("La funcion se tiene que llamar comportamiento")

        if node.decorator_list:
            self.error("No se permiten decoradores")

        if (
            node.args.posonlyargs
            or node.args.kwonlyargs
            or node.args.vararg
            or node.args.kwarg
            or node.args.defaults
            or node.args.kw_defaults
        ):
            self.error("La funcion debe recibir unicamente el parametro primitivas")

        if (len(node.args.args) != 1 or node.args.args[0].arg != "primitivas"):
            self.error("La firma debe ser comportamiento(primitivas)")

        for sentencia in node.body:
            self.visit(sentencia)

    def visit_Assign(self, node):
        if len(node.targets) != 1:
            self.error("No se permiten asignaciones multiples")

        destino = node.targets[0]

        if not isinstance(destino, ast.Name):
            self.error("Solo se permite asignar valores a variables locales")

        if destino.id == "primitivas":
            self.error("No se puede sobrescribir primitivas")

        self.visit(node.value)
        self.variables.add(destino.id)

    def visit_If(self, node):
        self.visit(node.test)

        for sentencia in node.body:
            self.visit(sentencia)

        for sentencia in node.orelse:
            self.visit(sentencia)

    def visit_Expr(self, node):
        if not isinstance(node.value, ast.Call):
            self.error("Expresion independiente no permitida")

        self.visit(node.value)

    def visit_Call(self, node):
        if not isinstance(node.func, ast.Attribute):
            self.error("No se permiten llamadas a funciones arbitrarias")

        if not isinstance(node.func.value, ast.Name):
            self.error("La llamada debe dirigirse a una primitiva")

        if node.func.value.id != "primitivas":
            self.error("Solo se permiten llamadas a primitivas")

        if node.func.attr not in PRIMITIVAS_PERMITIDAS:
            self.error(f"Primitiva no permitida: {node.func.attr}")

        if node.keywords:
            self.error("No se permiten argumentos con nombre")

        for argumento in node.args:
            self.visit(argumento)

    def visit_Name(self, node):
        if node.id not in self.variables:
            self.error(f"Variable no definida: {node.id}")

    def visit_Constant(self, node):
        if not isinstance(node.value, (bool, int, float, str, type(None))):
            self.error("Constante no permitida")

    def visit_List(self, node):
        for elemento in node.elts:
            self.visit(elemento)

    def visit_Tuple(self, node):
        for elemento in node.elts:
            self.visit(elemento)

    def visit_Subscript(self, node):
        self.visit(node.value)
        self.visit(node.slice)

    def visit_Attribute(self, node):
        if node.attr not in ATRIBUTOS_PERMITIDOS:
            self.error(f"Atributo no permitido: {node.attr}")

        self.visit(node.value)

    def visit_BinOp(self, node):
        if not isinstance(node.op, OPERADORES_BINARIOS):
            self.error("Operador aritmetico no permitido")

        self.visit(node.left)
        self.visit(node.right)

    def visit_BoolOp(self, node):
        if not isinstance(node.op, (ast.And, ast.Or)):
            self.error("Operador logico no permitido")

        for valor in node.values:
            self.visit(valor)

    def visit_UnaryOp(self, node):
        if not isinstance(node.op, OPERADORES_UNARIOS):
            self.error("Operador unario no permitido")

        self.visit(node.operand)

    def visit_Compare(self, node):
        if not all(
            isinstance(op, OPERADORES_COMPARACION)
            for op in node.ops
        ):
            self.error("Comparacion no permitida")

        self.visit(node.left)

        for comparador in node.comparators:
            self.visit(comparador)


def validar_codigo_comportamiento(codigo: str) -> str:
    if not isinstance(codigo, str) or not codigo.strip():
        raise CodigoComportamientoInvalido("El codigo no puede estar vacio")
    try:
        arbol = ast.parse(codigo)
    except (SyntaxError, ValueError, RecursionError) as exc:
        raise CodigoComportamientoInvalido("El codigo python no tiene sintaxis válida") from exc
    validador = ValidadorComportamiento()
    validador.visit(arbol)

    return codigo