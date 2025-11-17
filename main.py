from lexer.lexer import tokenize
from parser.parser import parse
from generator import generate_assembly, generate_error_handler

def count_metrics(assembly_code_list):
    """Contador líneas y accesos a memoria."""
    line_count = 0
    memory_access_count = 0
    
    for instruction in assembly_code_list:
        if instruction.strip().endswith(':'): 
            continue 
        if instruction.strip().startswith(';'): 
            continue
            
        line_count += 1
            
        if "(result)" in instruction or "(error)" in instruction or "MOV" in instruction and '(' in instruction:
            memory_access_count += 1
            
    return line_count, memory_access_count

def main():
    data_vars = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'error', 'result']
    
    print("\n--- ESCRIBA UNA EXPRESIÓN ---")
    # Ejemplo de expresión compleja (con multiplicación y división)
    expression = input(">>")
    
    try:
        # 1. Tokenizar
        tokens = tokenize(expression)
        
        # 2. Parsear
        ast_root = parse(tokens)
        
        # 3. Generar Assembly
        assembly_code = generate_assembly(ast_root, data_vars)
        
        # 4. Reports
        lines, accesses = count_metrics(assembly_code)
        
        print("--- CÓDIGO ASSEMBLY GENERADO ---")
        print("\n".join(assembly_code))
        
        print("\n--- REPORTE DE MÉTRICAS ---")
        print(f"Número total de líneas generadas: {lines}")
        print(f"Número de accesos a memoria (estimado): {accesses}")
        
    except (ValueError, SyntaxError, NotImplementedError) as e:
        print(f"ERROR DURANTE LA COMPILACIÓN: {e}")

if __name__ == "__main__":
    main()