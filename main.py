from Lexer.lexer import Lexer
from Parser.parser import Parser
from CodeGenerator.generator import AssemblyGenerator


def main():
    source_code = "result = a * b / c"
    lexer = Lexer(source_code)
    tokens = list(lexer.tokens())

    print(f"Tokens for: '{source_code}'")
    for token in tokens:
        print(token)

    parser = Parser(tokens)
    ast = parser.parse()

    print("\nAbstract Syntax Tree:")
    print(ast)

    generator = AssemblyGenerator(ast)
    instructions = generator.generate()

    print("\nGenerated Assembly:")
    for instruction in instructions:
        print(instruction)

    print(f"\nTotal lines of code: {generator.line_count}")
    print(f"Total memory accesses: {generator.mem_access_count}")


if __name__ == "__main__":
    main()