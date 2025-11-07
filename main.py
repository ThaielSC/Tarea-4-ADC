# Importar todas las fases
from lexer import tokenize
from parser import parse
from generator import generate_assembly, generate_error_handler

def count_metrics(assembly_code_list):
    """
    Cuenta el número total de líneas y el número de accesos a memoria (LOAD, STORE).
    """
    line_count = len(assembly_code_list)
    memory_access_count = 0
    
    for instruction in assembly_code_list:
        # ASUA usa instrucciones extendidas, asume que 'LOAD' y 'STORE' acceden a memoria
        if instruction.startswith("LOAD") or instruction.startswith("STORE"):
            memory_access_count += 1
            
    return line_count, memory_access_count

def compile_expression(expression):
    
    # 1. Tokenizar
    tokens = tokenize(expression)
    
    # 2. Parsear y construir AST
    ast_root = parse(tokens)
    
    # 3. Generar Assembly optimizado y manejador de errores
    assembly_code = generate_assembly(ast_root)
    assembly_code.extend(generate_error_handler())
    
    # 4. Reportería
    lines, accesses = count_metrics(assembly_code)
    
    # Imprimir o guardar el código assembly y el reporte
    print("Código Assembly Generado:\n" + "\n".join(assembly_code))
    print(f"\nNúmero total de líneas generadas: {lines}")
    print(f"Número de accesos a memoria: {accesses}")

if __name__ == "__main__":
    # La expresión de ejemplo
    test_expression = "result = a + b * max(c, d)" 
    compile_expression(test_expression)