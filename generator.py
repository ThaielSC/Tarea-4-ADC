from parser.parser import ASTNode

ASSEMBLY_CODE = []
LABEL_COUNTER = 0
TEMP_VAR_COUNTER = 0
ERROR_LABEL = "ERROR_HANDLER"
END_LABEL = "PROGRAM_END"

def get_new_label(prefix="L"):
    global LABEL_COUNTER
    label = f"{prefix}{LABEL_COUNTER}"
    LABEL_COUNTER += 1
    return label

def get_temp_var():
    global TEMP_VAR_COUNTER
    var = f"temp{TEMP_VAR_COUNTER}"
    TEMP_VAR_COUNTER += 1
    return var

def generate_assembly(node: ASTNode, data_vars: list):
    global ASSEMBLY_CODE, TEMP_VAR_COUNTER, LABEL_COUNTER
    ASSEMBLY_CODE = []
    TEMP_VAR_COUNTER = 0
    LABEL_COUNTER = 0
    
    _generate_assembly(node)
    
    ASSEMBLY_CODE.append(f"JMP {END_LABEL}")

    # Generar el manejador de errores y el final del programa
    ASSEMBLY_CODE.extend(generate_error_handler())
    
    return ASSEMBLY_CODE

def _generate_assembly(node: ASTNode, target_reg="A"):
    node_type = node.type
    
    if node_type == 'STATEMENT_LIST':
        for child in node.children:
            _generate_assembly(child)
        return

    #  Asignación 
    elif node_type == 'ASSIGN':
        var_name = node.value
        _generate_assembly(node.children[0], "A")
        ASSEMBLY_CODE.append(f"MOV ({var_name}), A")
        return

    #  Operaciones Simples (+ / -) 
    elif node_type in ('OP_ADD', 'OP_SUB'):
       
        
        op_code = "ADD" if node_type == 'OP_ADD' else "SUB"
        lhs = node.children[0]
        rhs = node.children[1]

        _generate_assembly(lhs, "A") # Evaluar LHS, resultado en A

        # Si el RHS es simple (ID o NUMBER), lo operamos directamente
        if rhs.type in ('IDENTIFIER', 'NUMBER'):
            if rhs.type == 'IDENTIFIER':
                ASSEMBLY_CODE.append(f"{op_code} A, ({rhs.value})")
            else:
                ASSEMBLY_CODE.append(f"{op_code} A, {rhs.value}")
        else:
            ASSEMBLY_CODE.append("PUSH A") # Guardar LHS
            _generate_assembly(rhs, "A") # Evaluar RHS, resultado en A
            ASSEMBLY_CODE.append("MOV B, A") # Mover RHS a B
            ASSEMBLY_CODE.append("POP A") # Restaurar LHS a A
            ASSEMBLY_CODE.append(f"{op_code} A, B") # Operar A = A op B

        # Comprobación de Overflow para ADD/SUB
        ASSEMBLY_CODE.append(f"JMP_OVF {ERROR_LABEL}")

        if target_reg == "B":
            ASSEMBLY_CODE.append("MOV B, A")
        return
    
    #  Operaciones Complejas (* / %)
    elif node_type in ('OP_MUL', 'OP_DIV', 'OP_MOD'):
        
        op_code = node_type.split('_')[1]
        division_check = (node_type != 'OP_MUL')
        
        _generate_complex_op(node, target_reg, op_code, division_check=division_check)
        return

    #  Valores
    elif node_type == 'NUMBER':
        ASSEMBLY_CODE.append(f"MOV {target_reg}, {node.value}")
        return

    elif node_type == 'IDENTIFIER':
        ASSEMBLY_CODE.append(f"MOV {target_reg}, ({node.value})")
        return

    #  Funciones
    elif node_type in ('FUNC_MAX', 'FUNC_MIN', 'FUNC_ABS'):
        # Aquí iría la lógica de las funciones
        # Por ahora, levantamos un error para la entrega parcial
        raise NotImplementedError(f"Function calls ({node_type}) not supported in this phase.")

    else:
        raise Exception(f"Unknown node type: {node_type}")

# Función Auxiliar para Operaciones Complejas
def _generate_complex_op(node, target_reg, op_code, division_check):
    
    lhs = node.children[0]
    rhs = node.children[1]
    
    # 1. Evaluar LHS (resultado en A)
    _generate_assembly(lhs, "A")

    # 2. Manejo de RHS (lo queremos en B)
    if rhs.type not in ('IDENTIFIER', 'NUMBER'):
        # RHS complejo: Guardar LHS, calcular RHS, mover RHS a B, restaurar LHS a A
        ASSEMBLY_CODE.append("PUSH A")
        _generate_assembly(rhs, "A")
        ASSEMBLY_CODE.append("MOV B, A") # RHS en B
        ASSEMBLY_CODE.append("POP A")    # LHS en A
    elif rhs.type == 'IDENTIFIER':
        ASSEMBLY_CODE.append(f"MOV B, ({rhs.value})") # Cargar Var a B
    else: # NUMBER
        ASSEMBLY_CODE.append(f"MOV B, {rhs.value}") # Cargar Immediato a B

    # 3. CRÍTICO: Chequeo de División por Cero (para DIV y MOD)
    if division_check:
        # Se asume JMP_EQ_ZERO Reg, Label
        ASSEMBLY_CODE.append(f"JMP_EQ_ZERO B, {ERROR_LABEL}") 
    
    # 4. Operación Extendida (A = A op B)
    ASSEMBLY_CODE.append(f"{op_code} A, B") # Ejemplo: MUL A, B

    # 5. CRÍTICO: Chequeo de Overflow (Solo para MUL, que es la más propensa)
    if op_code == 'MUL':
        # Se asume JMP_OVF Label
        ASSEMBLY_CODE.append(f"JMP_OVF {ERROR_LABEL}")
    
    # 6. Mover resultado al registro destino
    if target_reg == "B":
        ASSEMBLY_CODE.append("MOV B, A")


# --- Manejador de Errores Requerido ---
def generate_error_handler():
    
    handler_code = []
    # Etiqueta de inicio del manejador de errores
    handler_code.append(f"{ERROR_LABEL}:") 
    
    # Escribir un 1 en error
    handler_code.append("MOV A, 1")
    handler_code.append("MOV (error), A") 
    
    # El valor de result debe permanecer en cero
    handler_code.append("MOV A, 0")
    handler_code.append("MOV (result), A")
    
    # Salta al final del programa para terminar la ejecución
    handler_code.append(f"{END_LABEL}:") 
    handler_code.append("HALT") # Asumiendo una instrucción HALT para terminar el programa
    
    return handler_code