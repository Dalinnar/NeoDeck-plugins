from flask import Blueprint
from functools import partial

from plugin_template.functions import *
from plugin_template.routes import *


plugin_name = 'PLUGIN_NAME'  # Plugin name (must be the same as the folder name)
plugin_version = "1.0.0"  # Plugin version
creators = ["CREATOR_NAME"]  # List of creators
description = "Plugin description"  # Plugin description

plugin = Blueprint(plugin_name, __name__)


"""
"#" : link reference, to go and see maybe some docts about how to ...
"_" : private variable, not visible in the settings
"""
plugin.settings = {
    "_setting_hide" : "value",
    "#button" : "https://example.com",
    "setting_bool" : True,
    "setting_int" : 1,
    "settings_list" : ["item1", "item2", "item3"],
    "setting_dict" : {
        "key1": "value1",
        "key2": "value2",
        "key3": "value3"
    }
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