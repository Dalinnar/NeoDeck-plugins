# __init__.py

from flask import Blueprint
from obs_studio.routes import *
from obs_studio.functions import _raw_request, get_obs_manager, generate_obs_scene_folder,_set_volume,_get_volume

plugin_name = 'obs_studio'
plugin_version = "1.3.2"
creators = ["Dalinnar"]
description = "A powerful NeoDeck plugin for OBS Studio that lets you control scenes, sources, audio, and more with a single press."

plugin = Blueprint(plugin_name, __name__)

plugin.metadata = {
    "name": plugin_name,
    "version": plugin_version,
    "creators": creators,
    "description": description,
    "icon": "assets/icon.jpg"
}

plugin.settings = {
    "check_connection": {
        "type": "status",
        "endpoint": "/obs/check_connection",
    },
    "obs_guide": {
        "type": "link",
        "href": "https://github.com/obsproject/obs-websocket/blob/master/docs/generated/protocol.md",
    },
    "server_port": {
        "type": "number",
        "default": 4455,
    },
    "server_password": {
        "type": "text",
        "default": "",
        "secret": True,
    },
}

plugin.command_map = {
    "/obs_toggle_recording":        lambda:         get_obs_manager().toggle_recording(),
    "/obs_start_recording":         lambda:         get_obs_manager().start_recording(),
    "/obs_stop_recording":          lambda:         get_obs_manager().stop_recording(),
    "/obs_toggle_streaming":        lambda:         get_obs_manager().toggle_streaming(),
    "/obs_start_streaming":         lambda:         get_obs_manager().start_streaming(),
    "/obs_stop_streaming":          lambda:         get_obs_manager().stop_streaming(),
    "/obs_toggle_virtual_camera":   lambda:         get_obs_manager().toggle_virtual_camera(),
    "/obs_change_scene":            lambda message: get_obs_manager().change_scene(message.split(" ", 1)[1]),
    "/obs_trigger_hotkey":          lambda message: get_obs_manager().trigger_hotkey(message.split(" ", 1)[1]),
    "/obs_toggle_source":           lambda message: get_obs_manager().toggle_source(message.split(" ", 1)[1]),
    "/obs_raw_request":             lambda message: _raw_request(message),
    "!obs_set_volume":              lambda message: _set_volume(message),
}

plugin.monitors = {}

plugin.getters = {
    "!obs_set_volume": lambda message: _get_volume(message),
}

# ── routes ────────────────────────────────────────────────────────────────────
plugin.add_url_rule('/obs/get_scenes',        view_func=get_scene_list_page)
plugin.add_url_rule('/obs/get_sources',       view_func=get_source_list_page)
plugin.add_url_rule('/obs/get_audio_sources', view_func=get_audio_source_list_page)
plugin.add_url_rule('/obs/sources',           view_func=dynamic_sources)
plugin.add_url_rule('/obs/scenes',            view_func=dynamic_scenes)
plugin.add_url_rule('/obs/check_connection',  view_func=check_connection)