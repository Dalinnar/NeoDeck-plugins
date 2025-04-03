
from flask import Blueprint, current_app, jsonify, request


def function_route_1():
    """Example route function that returns a success message."""
    return jsonify({"status": "success", "message": "Route 1 executed"})

def function_route_2():
    """Example route function that processes a request."""
    data = request.get_json()
    return jsonify({"status": "success", "received": data})
def function_route_3(message):
    """Example route function that processes a message."""
    return jsonify({"status": "success", "message": f"Route 3 received: {message}"})