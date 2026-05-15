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

def get_source_filters_page():
    """GET /obs/get_filters?source=SourceName"""
    source_name = request.args.get("source", "")
    if not source_name:
        return Response(json.dumps([]), mimetype='application/json')
    return Response(json.dumps(get_source_filters(source_name)), mimetype='application/json')


# ─────────────────────────────────────────────
#  Dynamic folder pages
# ─────────────────────────────────────────────

def dynamic_scenes():
    return jsonify({"success": True, "data": generate_obs_scene_folder(get_scene_list())})

def dynamic_sources():
    """
    GET /obs/sources_folder?scene=SceneName
    Optional: omit ?scene to use the current scene.
    """
    scene_name = request.args.get("scene", None)
    items = get_scene_items_with_state(scene_name)
    display_scene = scene_name or get_current_scene()
    return jsonify({"success": True, "data": generate_obs_sources_folder(display_scene, items)})

def dynamic_filters():
    """
    GET /obs/filters_folder?source=SourceName
    """
    source_name = request.args.get("source", "")
    if not source_name:
        return jsonify({"success": False, "error": "Missing ?source= parameter"}), 400
    filters = get_source_filters_with_state(source_name)
    return jsonify({"success": True, "data": generate_obs_filter_folder(source_name, filters)})

def dynamic_audio():
    return jsonify({"success": True, "data": generate_obs_audio_folder(get_audio_source_list())})


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

def stream_status_page():
    status = get_stream_status()
    return jsonify({"success": True, "data": status})

def record_status_page():
    status = get_record_status()
    return jsonify({"success": True, "data": status})