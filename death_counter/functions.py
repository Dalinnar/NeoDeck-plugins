from flask import request, jsonify
import re
import os
# FUNCTION 1
def modify_counter(message, operation):
    """Modifica el contador en el archivo según la operación: 'add', 'substract' o 'set'."""
    match = re.match(r"/\w+ \[(.+?)\] (-?\d+)", message)
    if not match:
        print("Formato inválido")
        return

    route, value = match.group(1), int(match.group(2))
    if not os.path.exists(route):
        with open(route, "w") as f:
            f.write("0")

    with open(route, "r") as f:
        try:
            current_value = int(f.readline().strip())
        except ValueError:
            current_value = 0

    new_value = value if operation == "set" else (current_value + value if operation == "add" else current_value - value)

    with open(route, "w") as f:
        f.write(str(new_value))

    print(f"Nuevo valor en {route}: {new_value}")

def counter_add(message):    
    modify_counter(message, "add")

def counter_substract(message):
    modify_counter(message, "substract")

def counter_set(message):
    modify_counter(message, "set")