class Node:
    pass


class NumberNode(Node):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"NumberNode({self.value})"


class IdentifierNode(Node):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"IdentifierNode('{self.name}')"


class BinaryOpNode(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op  # Token object for the operator
        self.right = right

    def __repr__(self):
        return f"BinaryOpNode({self.left}, {self.op.type.name}, {self.right})"


class AssignmentNode(Node):
    def __init__(self, identifier, expression):
        self.identifier = identifier  # IdentifierNode
        self.expression = expression

    def __repr__(self):
        return f"AssignmentNode({self.identifier}, {self.expression})"


class FunctionCallNode(Node):
    def __init__(self, identifier, arguments):
        self.identifier = identifier  # IdentifierNode
        self.arguments = arguments  # List of Nodes

    def __repr__(self):
        return f"FunctionCallNode({self.identifier}, {self.arguments})"
