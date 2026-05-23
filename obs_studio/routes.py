from flask import Response, current_app, jsonify, request
import json
from obs_studio.functions import *


# ─────────────────────────────────────────────
#  List getters
# ─────────────────────────────────────────────

def get_scene_list_page():
    return Response(json.dumps(get_scene_list()), mimetype='application/json')

def get_source_list_page():
    return Response(json.dumps(get_source_list()), mimetype='application/json')

def get_audio_source_list_page():
    return Response(json.dumps(get_audio_source_list()), mimetype='application/json')



# ─────────────────────────────────────────────
#  Dynamic folder pages
# ─────────────────────────────────────────────

def dynamic_scenes():
    return jsonify({"success": True, "data": generate_obs_scene_folder(get_scene_list())})


# ─────────────────────────────────────────────
#  Status endpoints
# ─────────────────────────────────────────────

def check_connection():
    if obs_is_connected():
        return Response(
            json.dumps({"message": "OBS connected successfully"}),
            status=200,
            mimetype="application/json"
        )
    return Response(
        json.dumps({"message": "Connection error"}),
        status=503,
        mimetype="application/json"
    )