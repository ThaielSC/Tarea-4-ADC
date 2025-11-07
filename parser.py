class ASTNode:
    """Clase para representar un nodo en el Árbol de Sintaxis Abstracta"""
    def __init__(self, type, value=None, children=None):
        self.type = type  # Ej: 'ASSIGN', 'OP_ADD', 'FUNC_MAX'
        self.value = value
        self.children = children if children is not None else []

def parse(tokens_list):
    """
    Manejo precedencia de operadores
    """
    # Lógica del parser
    pass

# Importar de lexer.py:
# from lexer import tokenize, T_ID, T_OP_ADD