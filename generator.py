from parser.parser import ASTNode

ASSEMBLY_CODE = []
LABEL_COUNTER = 0
TEMP_VAR_COUNTER = 0

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

def generate_assembly(node: ASTNode):
    global ASSEMBLY_CODE, TEMP_VAR_COUNTER, LABEL_COUNTER
    ASSEMBLY_CODE = []
    TEMP_VAR_COUNTER = 0
    LABEL_COUNTER = 0
    _generate_assembly(node)
    return ASSEMBLY_CODE

def _generate_assembly(node: ASTNode, target_reg="A"):
    node_type = node.type
    if node_type == 'STATEMENT_LIST':
        for child in node.children:
            _generate_assembly(child)
        return

    elif node_type == 'ASSIGN':
        var_name = node.value
        _generate_assembly(node.children[0], "A")
        ASSEMBLY_CODE.append(f"MOV ({var_name}), A")
        return

    elif node_type == 'OP_ADD':
        lhs = node.children[0]
        rhs = node.children[1]

        # First, we evaluate the left side of the expression
        _generate_assembly(lhs, "A")

        # If the right side is a simple value (number or variable), we can add it directly
        if rhs.type in ('IDENTIFIER', 'NUMBER'):
            if rhs.type == 'IDENTIFIER':
                ASSEMBLY_CODE.append(f"ADD A, ({rhs.value})")
            else:  # NUMBER
                ASSEMBLY_CODE.append(f"ADD A, {rhs.value}")
        else:
            # If the right side is a complex expression, we need to use the stack
            # to temporarily store the result of the left side
            ASSEMBLY_CODE.append("PUSH A")
            # Now, we evaluate the right side. The result will be in register A
            _generate_assembly(rhs, "A")
            # We move the result of the right side to register B to make way for the left side
            ASSEMBLY_CODE.append("MOV B, A")
            # We retrieve the result of the left side from the stack into register A
            ASSEMBLY_CODE.append("POP A")
            # Finally, we perform the addition. The result is stored in A
            ASSEMBLY_CODE.append("ADD A, B")

        # If the final result of this operation needs to be in register B (because it is the right side of another operation), we move it
        if target_reg == "B":
            ASSEMBLY_CODE.append("MOV B, A")
        return

    elif node_type == 'OP_SUB':
        lhs = node.children[0]
        rhs = node.children[1]

        # First, we evaluate the left side of the expression
        _generate_assembly(lhs, "A")

        # If the right side is a simple value, we subtract it directly
        if rhs.type in ('IDENTIFIER', 'NUMBER'):
            if rhs.type == 'IDENTIFIER':
                ASSEMBLY_CODE.append(f"SUB A, ({rhs.value})")
            else:  # NUMBER
                ASSEMBLY_CODE.append(f"SUB A, {rhs.value}")
        else:
            # If the right side is a complex expression, we use the stack
            # We store the result of the left side on the stack
            ASSEMBLY_CODE.append("PUSH A")
            # We evaluate the right side. The result will be in register A
            _generate_assembly(rhs, "A")
            # We move the result of the right side to register B
            ASSEMBLY_CODE.append("MOV B, A")
            # We retrieve the result of the left side from the stack into register A
            ASSEMBLY_CODE.append("POP A")
            # We perform the subtraction. The result is stored in A
            ASSEMBLY_CODE.append("SUB A, B")

        # If the final result needs to be in B, we move it
        if target_reg == "B":
            ASSEMBLY_CODE.append("MOV B, A")
        return

    elif node_type in ('OP_MUL', 'OP_DIV', 'OP_MOD'):
        # These operations are more complex and might require a subroutine
        # For now, let's assume they are not supported in this simple model
        # Or we can implement them with loops and additions/subtractions
        # Let's stick to a simple error for now
        raise NotImplementedError(f"Operation {node.type} not supported with this instruction set.")

    elif node_type == 'NUMBER':
        ASSEMBLY_CODE.append(f"MOV {target_reg}, {node.value}")
        return

    elif node_type == 'IDENTIFIER':
        ASSEMBLY_CODE.append(f"MOV {target_reg}, ({node.value})")
        return

    elif node_type in ('FUNC_MAX', 'FUNC_MIN', 'FUNC_ABS'):
        # Function calls are also complex without PUSH/POP and a proper stack
        # We would need to manage the stack pointer in memory
        raise NotImplementedError(f"Function calls not supported with this instruction set.")

    else:
        raise Exception(f"Unknown node type: {node_type}")


def generate_error_handler():
    error_label = get_new_label("ERROR")
    end_label = get_new_label("END")
    
    handler_code = []
    handler_code.append(f"{error_label}:")
    handler_code.append("MOV A, 1")
    handler_code.append("MOV (error), A")
    handler_code.append("MOV A, 0")
    handler_code.append("MOV (result), A")
    handler_code.append(f"JMP {end_label}")
    
    return handler_code