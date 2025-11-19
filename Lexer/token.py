from enum import Enum


class TokenType(Enum):
    # data types
    NUMBER = "NUMBER"
    IDENTIFIER = "IDENTIFIER"

    # operators
    PLUS = "PLUS"
    MINUS = "MINUS"
    MULTIPLY = "MULTIPLY"
    DIVIDE = "DIVIDE"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    ASSIGN = "ASSIGN"
    MODULO = "MODULO"
    COMMA = "COMMA"

    # others
    EOF = "EOF"  # End of File


class Token:
    def __init__(self, type: TokenType, value = None):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"Token({self.type.name}, {repr(self.value)})"
