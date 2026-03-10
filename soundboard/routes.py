
from flask import Blueprint, current_app, jsonify, request
import os
from .functions import generate_sounds_folder


def soundboard_scenes():
    folder_path = request.headers.get("X-Folder-Path")    
    
    full_path = os.path.abspath(folder_path)
    folder_data = generate_sounds_folder(full_path)
    return jsonify({"data": folder_data})