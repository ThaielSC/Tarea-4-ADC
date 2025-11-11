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
