from lexer.lexer import *

class ASTNode:
    """Clase para representar un nodo en el Árbol de Sintaxis Abstracta"""
    def __init__(self, type, value=None, children=None):
        self.type = type
        self.value = value
        self.children = children if children is not None else []

    def __repr__(self):
        return f"ASTNode(type={self.type}, value={self.value}, children={self.children})"

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def parse(self):
        return self.parse_statement_list()

    def current_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def advance(self):
        self.pos += 1

    def expect(self, token_type):
        token = self.current_token()
        if token and token.type == token_type:
            self.advance()
            return token
        raise SyntaxError(f"Expected {token_type} but got {token.type if token else 'None'}")

    def parse_statement_list(self):
        nodes = []
        while self.current_token():
            nodes.append(self.parse_statement())
            if self.current_token() and self.current_token().type == 'T_SEMICOLON': # Assuming T_SEMICOLON for ';'
                self.advance()
        return ASTNode('STATEMENT_LIST', children=nodes)

    def parse_statement(self):
        token = self.current_token()
        if token.type == T_ID and self.tokens[self.pos + 1].type == T_ASSIGN:
            return self.parse_assignment()
        return self.parse_expression()

    def parse_assignment(self):
        name = self.expect(T_ID)
        self.expect(T_ASSIGN)
        expr = self.parse_expression()
        return ASTNode('ASSIGN', value=name.value, children=[expr])

    def parse_expression(self):
        node = self.parse_term()

        while self.current_token() and self.current_token().type in (T_OP_ADD, T_OP_SUB):
            op = self.current_token()
            self.advance()
            right = self.parse_term()
            node = ASTNode(op.type, children=[node, right])

        return node

    def parse_term(self):
        node = self.parse_factor()

        while self.current_token() and self.current_token().type in (T_OP_MUL, T_OP_DIV, T_OP_MOD):
            op = self.current_token()
            self.advance()
            right = self.parse_factor()
            node = ASTNode(op.type, children=[node, right])

        return node

    def parse_factor(self):
        token = self.current_token()

        if token.type == T_NUMBER:
            self.advance()
            return ASTNode('NUMBER', value=token.value)
        elif token.type == T_ID:
            self.advance()
            return ASTNode('IDENTIFIER', value=token.value)
        elif token.type == T_LPAREN:
            self.advance()
            node = self.parse_expression()
            self.expect(T_RPAREN)
            return node
        elif token.type in (T_FUNC_MAX, T_FUNC_MIN, T_FUNC_ABS):
            return self.parse_function_call()
        
        raise SyntaxError(f"Invalid factor: {token}")

    def parse_function_call(self):
        func_token = self.current_token()
        self.advance()
        self.expect(T_LPAREN)
        args = self.parse_arguments()
        self.expect(T_RPAREN)
        return ASTNode(func_token.type, children=args)

    def parse_arguments(self):
        args = []
        if self.current_token().type != T_RPAREN:
            args.append(self.parse_expression())
            while self.current_token() and self.current_token().type == T_COMMA:
                self.advance()
                args.append(self.parse_expression())
        return args

def parse(tokens_list):
    """
    Manejo precedencia de operadores
    """
    parser = Parser(tokens_list)
    return parser.parse()

