from flask import Blueprint

from death_counter.functions import *
from death_counter.routes import *

# CHANGE THESE VALUES FOR THE PLUGIN
plugin_name = 'death_counter'  # Plugin name
plugin_version = "1.0.1"  # Plugin version
creators = ["Dalinnar"]  # List of creators
description = "A simple counter to track deaths,runs, or any other actions with ease."

plugin = Blueprint(plugin_name, __name__)

# PLUGIN METADATA
plugin.metadata= {
    "name": plugin_name,
    "version": plugin_version,
    "creators": creators,
    "description":description,
    "icon": "assets/icon.jpg"
}
plugin.settings = {
    
}
# COMMAND MAPPING
plugin.command_map = {
    "/counter_add": lambda message:counter_substract(message),
    "/counter_substract": lambda message:counter_substract(message),
    "/counter_set": lambda message: counter_set(message),
}

# PLUGIN MONITORS
plugin.monitors = {}

# PLUGIN ROUTES
#plugin.add_url_rule('/plugin/route_1', view_func=function_route_1)




def init():
    # Add your initialization logic here
    #print(f"Plugin {plugin_name} initialized.")
    pass
    
plugin.init = init