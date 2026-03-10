from flask import Blueprint
from functools import partial

from soundboard.functions import *
from soundboard.routes import *


plugin_name = 'soundboard'  # Plugin name (must be the same as the folder name)
plugin_version = "1.0.0"  # Plugin version
creators = ["Dalinnar"]  # List of creators
description = "simple soundboard"  # Plugin description

plugin = Blueprint(plugin_name, __name__)


"""
"#" : link reference, to go and see maybe some docts about how to ...
"_" : private variable, not visible in the settings
"""
plugin.settings = {
}
# PLUGIN METADATA
plugin.metadata= {
    "name": plugin_name,
    "version": plugin_version,
    "creators": creators,
    "description": description,
    "icon": "assets/icon.jpg"
}
# COMMAND MAPPING
plugin.command_map = {
    #"/plugin_command_1": lambda: function_1(),
    #"/plugin_command_2": lambda: function_2(),
    #"/plugin_command_3": lambda message: function_3(message),
    "/soundboard_playsound" : lambda message: playsound(message),
    "/soundboard/openfolder" : lambda message: generate_sounds_folder(message) 
    #"/plugin_command_4": 

    
}

# PLUGIN MONITORS
plugin.monitors = {}

# PLUGIN ROUTES
plugin.add_url_rule('/soundboard/scenes/', view_func=soundboard_scenes)
#plugin.add_url_rule('/plugin/route_2', view_func=function_route_2)
#plugin.add_url_rule('/plugin/route_3', view_func=function_route_3)


def init():
    pass
plugin.init = init