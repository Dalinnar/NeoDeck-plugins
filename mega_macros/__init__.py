from flask import Blueprint
from functools import partial

from mega_macros.functions import *
from mega_macros.routes import *


plugin_name = 'mega_macros'  # Plugin name (must be the same as the folder name)
plugin_version = "1.4.1"  # Plugin version
creators = ["Dalinnar"]  # List of creators
description = "record your own macros and start doing automatizing them"  # Plugin description

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
    "/MM_execute_macro": lambda message: execute_macro(message),
    "/MM_record_macro": lambda message: record_macro(message),
}

# PLUGIN MONITORS
plugin.monitors = {}




def init():
    pass
plugin.init = init