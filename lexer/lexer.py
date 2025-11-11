from .tokens import *
from .token_class import Token

def tokenize(expression) -> list[Token]:  #Tokenizar (Lista de tokens)
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
