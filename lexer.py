# Definición de tokens
T_ID = 'IDENTIFIER'
T_NUMBER = 'NUMBER'
T_ASSIGN = 'ASSIGN'

T_OP_ADD = 'OP_ADD'
T_OP_SUB = 'OP_SUB'
T_OP_MUL = 'OP_MUL'
T_OP_DIV = 'OP_DIV'
T_OP_MOD = 'OP_MOD'

T_LPAREN = 'LPAREN'
T_RPAREN = 'RPAREN'
T_COMMA = 'COMMA'      # (para separar argumentos de funciones)

T_FUNC_MAX = 'FUNC_MAX'
T_FUNC_MIN = 'FUNC_MIN'
T_FUNC_ABS = 'FUNC_ABS'

SYMBOLS = {
    '+': T_OP_ADD, '-': T_OP_SUB, '*': T_OP_MUL, '/': T_OP_DIV, 
    '%': T_OP_MOD, '(': T_LPAREN, ')': T_RPAREN, ',': T_COMMA, '=': T_ASSIGN
}
KEYWORDS = {
    'max': T_FUNC_MAX, 'min': T_FUNC_MIN, 'abs': T_FUNC_ABS
}


class Token:
    """Clase para representar un token con su tipo y valor."""
    def __init__(self, type, value=None):
        self.type = type
        self.value = value
    
    def __repr__(self):
        # Depuración
        if self.value:
            return f"<{self.type}: {self.value}>"
        return f"<{self.type}>"
    
    

def tokenize(expression):  #Tokenizar (Lista de tokens)
    tokens = []
    i = 0
    n = len(expression)
    
    while i < n:
        char = expression[i]
        
        # Ignorar Espacios
        if char.isspace():
            i += 1
            continue
            
        # Identificar Simbolos
        if char in SYMBOLS:
            tokens.append(Token(SYMBOLS[char], char))
            i += 1
            continue

        # Identificar si es una Variable o una Funcion
        if char.isalpha():
            start = i
            while i < n and (expression[i].isalnum()):
                i += 1
            value = expression[start:i]
            
            # Es una funcion, si no un identificador
            if value in KEYWORDS:
                tokens.append(Token(KEYWORDS[value], value))
            else:
                tokens.append(Token(T_ID, value))
            continue

        # Identificar Numeros
        if char.isdigit():
            start = i
            while i < n and expression[i].isdigit():
                i += 1
            value = expression[start:i]
            tokens.append(Token(T_NUMBER, int(value)))
            continue

        # Si llegamos aqui, hay error
        raise ValueError(f"Error: Carácter desconocido '{char}' en la posición {i}")

    return tokens