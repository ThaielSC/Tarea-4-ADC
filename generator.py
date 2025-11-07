# Diccionario para almacenar el código assembly generado
ASSEMBLY_CODE = []
# Contador para las etiquetas de control de flujo (ej. saltos de error)
LABEL_COUNTER = 0

def generate_assembly(node):
    """
    Función principal que recorre el ARBOL.
    Debe priorizar el uso de registros para evitar LOAD/STORE innecesarios.
    """
    # Lógica de generación para diferentes tipos de nodos
    if node.type == 'OP_ADD':
        # Generar código para el hijo izquierdo
        # Generar código para el hijo derecho
        # Insertar ADD e inmediatamente la comprobación de Overflow
        pass
    
    # Lógica para funciones (max, min, abs)
    # Lógica para divisiones (con comprobación de división por cero)
    
def generate_error_handler():
    """
    Función que genera la sección de código al final que maneja los errores:
    - Escribir un '1' en la variable 'error'.
    - Asegurar que 'result' permanezca en cero.
    - Terminar la ejecución.
    """
    pass

# Importar de parser.py:
# from parser import ASTNode, parse