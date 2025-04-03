from flask import request, jsonify

# FUNCTION 1
def function_1():
    """Example function that returns a success message."""
    return jsonify({"status": "success", "message": "Function 1 executed"})

# FUNCTION 2
def function_2():
    """Example function that processes a request."""
    data = request.get_json()
    return jsonify({"status": "success", "received": data})

# FUNCTION 3
def function_3(message):
    """Example function that processes a message."""
    return jsonify({"status": "success", "message": f"Function 3 received: {message}"})