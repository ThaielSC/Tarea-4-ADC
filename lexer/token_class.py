class Token:
    """Clase para representar un token con su tipo y valor."""
    def __init__(self, type, lexema=None, group=None):
        self.type = type
        self.group = group
        self.value = lexema
    
    def __repr__(self):
        # Depuración
        if self.value:
            return f"<{self.type}: {self.value}>"
        return f"<{self.type}>"
