from flask import Blueprint
from functools import partial

from plugin_template.functions import *
from plugin_template.routes import *

# CHANGE THESE VALUES FOR THE PLUGIN
plugin_name = 'PLUGIN_NAME'  # Plugin name
plugin_version = "1.0.0"  # Plugin version
creators = ["CREATOR_NAME"]  # List of creators

plugin = Blueprint(plugin_name, __name__)
plugin.settings = {
    
}
# PLUGIN METADATA
plugin.metadata= {
    "name": plugin_name,
    "version": plugin_version,
    "creators": creators,
    "description": "Plugin description",
    "icon": "assets/icon.jpg"
}
# COMMAND MAPPING
plugin.command_map = {
    "/plugin_command_1": lambda: function_1(),
    "/plugin_command_2": lambda: function_2(),
    "/plugin_command_3": lambda message: function_3(message),
}

# PLUGIN MONITORS
plugin.monitors = {}

# PLUGIN ROUTES
plugin.add_url_rule('/plugin/route_1', view_func=function_route_1)
plugin.add_url_rule('/plugin/route_2', view_func=function_route_2)
plugin.add_url_rule('/plugin/route_3', view_func=function_route_3)


def init():
    pass
plugin.init = init