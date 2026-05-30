# routes.py

from flask import Response, current_app, jsonify
import json
from obs_studio.functions import get_obs_manager, generate_obs_scene_folder,generate_obs_sources_folder


# ─────────────────────────────────────────────
#  List getters
# ─────────────────────────────────────────────

def get_scene_list_page():
    obs = get_obs_manager()
    return Response(json.dumps(obs.get_scene_list()), mimetype='application/json')

def get_source_list_page():
    obs = get_obs_manager()
    return Response(json.dumps(obs.get_source_list()), mimetype='application/json')

def get_audio_source_list_page():
    obs = get_obs_manager()
    return Response(json.dumps(obs.get_audio_source_list()), mimetype='application/json')


# ─────────────────────────────────────────────
#  Dynamic folder pages
# ─────────────────────────────────────────────

def dynamic_scenes():
    obs = get_obs_manager()
    return jsonify({"success": True, "data": generate_obs_scene_folder(obs.get_scene_list())})


def dynamic_sources():
    obs = get_obs_manager()
    scene_items = obs.get_scene_item_list()  # usa la escena actual
    return jsonify({"success": True, "data": generate_obs_sources_folder(scene_items)})

# ─────────────────────────────────────────────
#  Status endpoints
# ─────────────────────────────────────────────

def check_connection():
    obs = get_obs_manager()
    if obs.connected:
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