from flask import Blueprint,current_app
from obs.routes import *
from obs.functions import *
from functools import partial


#CHANGE plugin_template TO YOUR PLUGIN NAME
#LEARN HOW TO USE OBS WEBSOCKET ON 
#https://github.com/obsproject/obs-websocket/blob/master/docs/generated/protocol.md
plugin_name = 'OBS'
plugin_version = "1.0.0"

creators = ["Dalinnar"]

plugin = Blueprint(plugin_name, __name__)
plugin.settings = {
    "server_port" : 4455,
    "server_password" : "",
    }

plugin.command_map = {
    
    "/obs_toggle_recording":        lambda: toggle_recording(),
    "/obs_start_recording":         lambda: start_recording(),
    "/obs_stop_recording":          lambda: stop_recording(),
    "/obs_toggle_streaming":        lambda: toggle_streaming(),
    "/obs_start_streaming":         lambda: start_streaming(),
    "/obs_stop_streaming":          lambda: stop_streaming(),
    "/obs_toggle_virtual_camera":    lambda: toggle_virtual_camera(), #

    "/obs_change_scene":            lambda message: change_scene(message),
    "/obs_trigger_hotkey":          lambda message: trigger_hotkey(message),
    "/obs_toggle_source" :          lambda message: toggle_source(message),
    "!obs_set_volume":              lambda message: set_source_volume(message),
}   
plugin.monitors= {}

#ROUTES
plugin.add_url_rule('/obs/get_scenes', view_func=get_scene_list_page)
plugin.add_url_rule('/obs/get_sources', view_func=get_source_list_page)
plugin.add_url_rule('/obs/get_audio_sources', view_func=get_audio_source_list_page)
