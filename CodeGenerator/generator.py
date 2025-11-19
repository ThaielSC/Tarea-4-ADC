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
        pass  # Numbers are not variables

    def visit_IdentifierNode(self, node):
        self.variables.add(node.name)

    def visit_FunctionCallNode(self, node):
        # The function name itself is not a variable in the DATA block
        for arg in node.arguments:
            self.visit(arg)

# --- Pass 2: Code Generation ---

class AssemblyGenerator:
    def __init__(self, ast):
        self.ast = ast
        self.instructions = []
        self.temp_register_count = 0
        self.label_count = 0
        self.line_count = 0
        self.mem_access_count = 0

    def generate(self):
        # Pass 1: Collect variables
        collector = VariableCollector()
        collector.visit(self.ast)
        
        # Generate DATA block
        data_block = self._generate_data_block(collector.variables)
        
        # Pass 2: Generate code
        self._add_instruction("START:")
        self._generate_node(self.ast)
        self._add_instruction("HALT")
        self._generate_error_routines()
        
        return data_block + self.instructions

    def _generate_data_block(self, variables):
        data = ["DATA:"]
        all_vars = sorted(list(variables | {'error', 'result'}))
        for var in all_vars:
            data.append(f"{var} 0")
        data.append("")
        return data

    def _generate_error_routines(self):
        # Div by zero
        self._add_instruction("DIV_ZERO_ERROR:")
        self._add_instruction("MOV A, 1")
        self._add_instruction("MOV (error), A")
        self.mem_access_count += 1
        self._add_instruction("MOV A, 0")
        self._add_instruction("MOV (result), A")
        self.mem_access_count += 1
        self._add_instruction("HALT")
        # Overflow
        self._add_instruction("OVERFLOW_ERROR:")
        self._add_instruction("MOV A, 1")
        self._add_instruction("MOV (error), A")
        self.mem_access_count += 1
        self._add_instruction("MOV A, 0")
        self._add_instruction("MOV (result), A")
        self.mem_access_count += 1
        self._add_instruction("HALT")

    def _add_instruction(self, instruction):
        self.instructions.append(instruction)
        if not instruction.endswith(':'):
            self.line_count += 1
        # Memory access counting will be handled inside _generate methods
        
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
            TokenType.MULTIPLY: "MUL", TokenType.DIVIDE: "DIV",
            TokenType.MODULO: "MOD",
        }
        op_instruction = op_map[node.op.type]

        if op_instruction in ("DIV", "MOD"):
            self._generate_node(node.right)
            self._add_instruction("CMP A, 0")
            self._add_instruction("JZ DIV_ZERO_ERROR")
            temp_reg = self._new_temp_register()
            self._add_instruction(f"MOV {temp_reg}, A")
            self._generate_node(node.left)
            self._add_instruction(f"{op_instruction} A, {temp_reg}")
            self._free_temp_register()
        else:
            self._generate_node(node.right)
            temp_reg = self._new_temp_register()
            self._add_instruction(f"MOV {temp_reg}, A")
            self._generate_node(node.left)
            self._add_instruction(f"{op_instruction} A, {temp_reg}")
            self._free_temp_register()
            if op_instruction in ("ADD", "SUB", "MUL"):
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
            temp_reg = self._new_temp_register()
            self._add_instruction(f"MOV {temp_reg}, A")
            self._generate_node(node.arguments[0])
            self._add_instruction(f"CMP A, {temp_reg}")
            label = self._new_label()
            jump_instruction = "JGE" if func_name == 'max' else "JLE"
            self._add_instruction(f"{jump_instruction} {label}")
            self._add_instruction(f"MOV A, {temp_reg}")
            self._add_instruction(f"{label}:")
            self._free_temp_register()

    def _new_temp_register(self):
        self.temp_register_count += 1
        return f"R{self.temp_register_count}"

    def _free_temp_register(self):
        self.temp_register_count -= 1
        
    def _new_label(self):
        self.label_count += 1
        return f"L{self.label_count}"

