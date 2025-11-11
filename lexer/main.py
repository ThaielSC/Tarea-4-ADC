from lexer import tokenize

def main():
    expression = "a = max(10, b) + 5"
    try:
        tokens = tokenize(expression)
        print("Tokens generados:")
        for token in tokens:
            print(token)
    except ValueError as e:
        print(e)

if __name__ == "__main__":
    main()
