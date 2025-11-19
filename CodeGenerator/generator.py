from Parser.ast import (
    AssignmentNode,
    BinaryOpNode,
    NumberNode,
    IdentifierNode,
    FunctionCallNode,
)
from Lexer.token import TokenType


from Parser.ast import (
    AssignmentNode,
    BinaryOpNode,
    NumberNode,
    IdentifierNode,
    FunctionCallNode,
)
from Lexer.token import TokenType

# --- Pass 1: Variable Collection ---

class Visitor:
    def visit(self, node):
        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f"No visit_{type(node).__name__} method")

class VariableCollector(Visitor):
    def __init__(self):
        self.variables = set()

    def visit_AssignmentNode(self, node):
        self.variables.add(node.identifier.name)
        self.visit(node.expression)

    def visit_BinaryOpNode(self, node):
        self.visit(node.left)
        self.visit(node.right)

    def visit_NumberNode(self, node):
        pass

    def visit_IdentifierNode(self, node):
        self.variables.add(node.name)

    def visit_FunctionCallNode(self, node):
        for arg in node.arguments:
            self.visit(arg)

# --- Pass 2: Code Generation ---

class AssemblyGenerator:
    def __init__(self, ast):
        self.ast = ast
        self.instructions = []
        self.temp_storage = [] # Stack to manage temp storage locations ('B', 'STACK')
        self.label_count = 0
        self.line_count = 0
        self.mem_access_count = 0

    def generate(self):
        collector = VariableCollector()
        collector.visit(self.ast)
        
        data_block = self._generate_data_block(collector.variables)
        
        self.instructions = []
        self.line_count = 0
        self.mem_access_count = 0

        self._add_instruction("START:")
        self._generate_node(self.ast)
        self._generate_error_routines()
        self._generate_mul_div_subroutines()
        
        return data_block + self.instructions

    def _add_instruction(self, instruction):
        self.instructions.append(instruction)
        if not instruction.endswith(':'):
            self.line_count += 1

    def _generate_data_block(self, variables):
        data = ["DATA:"]
        # Add temp vars for subroutines
        temp_vars = {'_temp_mul_op', '_temp_mul_res', '_temp_div_quot'}
        all_vars = sorted(list(variables | {'error', 'result'} | temp_vars))
        for var in all_vars:
            data.append(f"{var} 0")
        data.append("")
        return data

    def _generate_error_routines(self):
        self._add_instruction("DIV_ZERO_ERROR:")
        self._add_instruction("MOV A, 1")
        self._add_instruction("MOV (error), A"); self.mem_access_count += 1
        self._add_instruction("MOV A, 0")
        self._add_instruction("MOV (result), A"); self.mem_access_count += 1
        self._add_instruction("OVERFLOW_ERROR:")
        self._add_instruction("MOV A, 1")
        self._add_instruction("MOV (error), A"); self.mem_access_count += 1
        self._add_instruction("MOV A, 0")
        self._add_instruction("MOV (result), A"); self.mem_access_count += 1

    def _generate_mul_div_subroutines(self):
        # MUL: A = A * B. Destroys B.
        self._add_instruction("MUL_SUBROUTINE:")
        self._add_instruction("MOV (_temp_mul_op), A")
        self.mem_access_count += 1
        self._add_instruction("MOV A, 0")
        self._add_instruction("MOV (_temp_mul_res), A")
        self.mem_access_count += 1
        self._add_instruction("MUL_LOOP:")
        self._add_instruction("CMP B, 0")
        self._add_instruction("JEQ MUL_EXIT")
        self._add_instruction("SUB B, 1")
        self._add_instruction("MOV A, (_temp_mul_res)")
        self.mem_access_count += 1
        self._add_instruction("ADD A, (_temp_mul_op)")
        self.mem_access_count += 1
        self._add_instruction("MOV (_temp_mul_res), A")
        self.mem_access_count += 1
        self._add_instruction("JMP MUL_LOOP")
        self._add_instruction("MUL_EXIT:")
        self._add_instruction("MOV A, (_temp_mul_res)")
        self.mem_access_count += 1
        self._add_instruction("RET")
        
        # DIV: A = A / B. Remainder in A, Quotient in A on return. Destroys B.
        self._add_instruction("DIV_SUBROUTINE:")
        self._add_instruction("MOV (_temp_div_quot), 0")
        self.mem_access_count += 1
        self._add_instruction("DIV_LOOP:")
        self._add_instruction("CMP A, B")
        self._add_instruction("JL DIV_EXIT")
        self._add_instruction("SUB A, B")
        self._add_instruction("MOV B, (_temp_div_quot)") # Use B as temp
        self.mem_access_count += 1
        self._add_instruction("ADD B, 1")
        self._add_instruction("MOV (_temp_div_quot), B")
        self.mem_access_count += 1
        self._add_instruction("JMP DIV_LOOP")
        self._add_instruction("DIV_EXIT:")
        self._add_instruction("MOV A, (_temp_div_quot)")
        self.mem_access_count += 1
        self._add_instruction("RET")

    def _generate_node(self, node):
        method_name = f"_generate_{type(node).__name__}"
        generator = getattr(self, method_name)
        return generator(node)

    def _generate_AssignmentNode(self, node):
        self._generate_node(node.expression)
        self._add_instruction(f"MOV ({node.identifier.name}), A")
        self.mem_access_count += 1

    def _generate_BinaryOpNode(self, node):
        op_map = {
            TokenType.PLUS: "ADD", TokenType.MINUS: "SUB",
            TokenType.MULTIPLY: "CALL MUL_SUBROUTINE", 
            TokenType.DIVIDE: "CALL DIV_SUBROUTINE",
            TokenType.MODULO: "CALL DIV_SUBROUTINE",
        }
        op_instruction = op_map[node.op.type]

        if op_instruction == "CALL DIV_SUBROUTINE":
            self._generate_node(node.right)
            self._add_instruction("CMP A, 0")
            self._add_instruction("JEQ DIV_ZERO_ERROR")
            self._push_temp()
            self._generate_node(node.left)
            self._pop_temp()
            self._add_instruction(op_instruction)
            if node.op.type == TokenType.MODULO:
                pass
            return

        self._generate_node(node.right)
        self._push_temp()
        self._generate_node(node.left)
        self._pop_temp()
        
        if op_instruction.startswith("CALL"):
             self._add_instruction(op_instruction)
        else:
            self._add_instruction(f"{op_instruction} A, B")

        if op_instruction in ("ADD", "SUB"):
            self._add_instruction("JO OVERFLOW_ERROR")

    def _generate_NumberNode(self, node):
        self._add_instruction(f"MOV A, {node.value}")

    def _generate_IdentifierNode(self, node):
        self._add_instruction(f"MOV A, ({node.name})")
        self.mem_access_count += 1

    def _generate_FunctionCallNode(self, node):
        func_name = node.identifier.name
        if func_name == 'abs':
            self._generate_node(node.arguments[0])
            label = self._new_label()
            self._add_instruction("CMP A, 0")
            self._add_instruction(f"JGE {label}")
            self._add_instruction("NEG A")
            self._add_instruction(f"{label}:")
        elif func_name in ('max', 'min'):
            self._generate_node(node.arguments[1])
            self._push_temp()
            self._generate_node(node.arguments[0])
            self._pop_temp()
            self._add_instruction(f"CMP A, B")
            label = self._new_label()
            jump_instruction = "JGE" if func_name == 'max' else "JLE"
            self._add_instruction(f"{jump_instruction} {label}")
            self._add_instruction(f"MOV A, B")
            self._add_instruction(f"{label}:")

    def _push_temp(self):
        if 'B' not in self.temp_storage:
            self._add_instruction("MOV B, A")
            self.temp_storage.append('B')
        else:
            self._add_instruction("PUSH A")
            self.temp_storage.append('STACK')

    def _pop_temp(self):
        loc = self.temp_storage.pop()
        if loc == 'B':
            pass
        else:
            self._add_instruction("POP B")

    def _new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

