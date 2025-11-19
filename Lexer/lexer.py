import re
from .token import Token, TokenType


class Lexer:
    def __init__(self, source_code: str):
        self.source_code = source_code
        self.position = 0
        self.tokens_rules = [
            (r"^\s+", None),  
            (r"^\d+(\.\d+)?", TokenType.NUMBER),
            (r"^[a-zA-Z_][a-zA-Z0-9_]*", TokenType.IDENTIFIER),
            (r"^\+", TokenType.PLUS),
            (r"^\-", TokenType.MINUS),
            (r"^\*", TokenType.MULTIPLY),
            (r"^\/", TokenType.DIVIDE),
            (r"^\(", TokenType.LPAREN),
            (r"^\)", TokenType.RPAREN),
            (r"^\=", TokenType.ASSIGN),
            (r"^\%", TokenType.MODULO),
            (r"^\,", TokenType.COMMA),
        ]

    def _get_next_token(self) -> Token | None:
        if self.position >= len(self.source_code):
            return Token(TokenType.EOF)

        for pattern, token_type in self.tokens_rules:
            match = re.match(pattern, self.source_code[self.position :])
            if match:
                value = match.group(0)
                self.position += len(value)

                if token_type is None:  # Skip whitespace
                    return self._get_next_token()

                if token_type == TokenType.NUMBER:
                    return Token(token_type, float(value))

                return Token(token_type, value)

        raise Exception(f"Invalid character: {self.source_code[self.position]}")

    def tokens(self):
        while (token := self._get_next_token()) and token.type != TokenType.EOF:
            yield token
        yield token  # Yield EOF token at the end
