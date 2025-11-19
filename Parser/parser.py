from Lexer.token import TokenType
from .ast import (
    NumberNode,
    IdentifierNode,
    BinaryOpNode,
    AssignmentNode,
    FunctionCallNode,
)


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0
        self.current_token = self.tokens[self.current_token_index]

    def advance(self):
        self.current_token_index += 1
        if self.current_token_index < len(self.tokens):
            self.current_token = self.tokens[self.current_token_index]
        else:
            self.current_token = None  # EOF

    def eat(self, token_type):
        if self.current_token and self.current_token.type == token_type:
            self.advance()
        else:
            raise Exception(
                f"Expected {token_type}, got {self.current_token.type if self.current_token else 'EOF'}"
            )

    def parse(self):
        # Entry point for parsing
        return self.expression()

    def expression(self):
        # Handles assignments and operations
        # Check for assignment first
        if (
            self.current_token
            and self.current_token.type == TokenType.IDENTIFIER
            and self.current_token_index + 1 < len(self.tokens)
            and self.tokens[self.current_token_index + 1].type == TokenType.ASSIGN
        ):
            return self.assignment()
        else:
            return self.binary_operation()

    def assignment(self):
        # identifier = expression
        identifier_token = self.current_token
        self.eat(TokenType.IDENTIFIER)
        self.eat(TokenType.ASSIGN)
        expression_node = self.expression()  # Recursive call for the right-hand side
        return AssignmentNode(IdentifierNode(identifier_token.value), expression_node)

    def binary_operation(self):
        # Handles operations with precedence
        node = self.term()

        while self.current_token and self.current_token.type in (
            TokenType.PLUS,
            TokenType.MINUS,
        ):
            op_token = self.current_token
            self.advance()
            node = BinaryOpNode(node, op_token, self.term())
        return node

    def term(self):
        # Handles multiplication, division, modulo
        node = self.factor()

        while self.current_token and self.current_token.type in (
            TokenType.MULTIPLY,
            TokenType.DIVIDE,
            TokenType.MODULO,
        ):
            op_token = self.current_token
            self.advance()
            node = BinaryOpNode(node, op_token, self.factor())
        return node

    def factor(self):
        # Handles numbers, identifiers, parenthesized expressions, function calls
        token = self.current_token

        if token.type == TokenType.NUMBER:
            self.eat(TokenType.NUMBER)
            return NumberNode(token.value)
        elif token.type == TokenType.IDENTIFIER:
            # Check for function call
            if (
                self.current_token_index + 1 < len(self.tokens)
                and self.tokens[self.current_token_index + 1].type == TokenType.LPAREN
            ):
                return self.function_call()
            else:
                self.eat(TokenType.IDENTIFIER)
                return IdentifierNode(token.value)
        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.expression()
            self.eat(TokenType.RPAREN)
            return node
        else:
            raise Exception(f"Unexpected token: {token.type}")

    def function_call(self):
        allowed_functions = {'max': 2, 'min': 2, 'abs': 1}
        identifier_token = self.current_token
        func_name = identifier_token.value

        if func_name not in allowed_functions:
            raise Exception(f"Unknown function: {func_name}")

        self.eat(TokenType.IDENTIFIER)
        self.eat(TokenType.LPAREN)

        arguments = []
        if self.current_token.type != TokenType.RPAREN:
            arguments.append(self.expression())

        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            arguments.append(self.expression())

        if len(arguments) != allowed_functions[func_name]:
            raise Exception(
                f"Wrong number of arguments for {func_name}: expected {allowed_functions[func_name]}, got {len(arguments)}"
            )

        self.eat(TokenType.RPAREN)

        return FunctionCallNode(IdentifierNode(func_name), arguments)
