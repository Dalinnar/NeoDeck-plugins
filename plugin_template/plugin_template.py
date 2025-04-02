from functions import *
from flask import Blueprint,current_app
#CHANGE plugin_template TO YOUR PLUGIN NAME

#ALWAYS NEEDS TO END UP WITH TWO UNDERSCORES
plugin_name = 'plugin_template'
creators = [""]
#CREATOR / creators

loaded_settings = {}




plugin = Blueprint(plugin_name, __name__,template_folder="templates")

plugin.settings = {
    "name" : "plugin_template",
    "description" : "A template for creating plugins",
} 

plugin.command_map = {
    "/plugin_template__hello_world" : lambda message :print(current_app.get_settings()),
    "/plugin_template__other function" : lambda:print("porongon"),
    "/template wizlight template"   :lambda message: wizlight_template(message.replace("/template wizlight tepmlate", "").strip()),
}

plugin.monitors= {
    
}




#first init call of the plugin, loads all 
has_run = False
@plugin.before_request
def init():
    global has_run, loaded_settings    
    if has_run:
        return
    has_run = True
    loaded_settings = current_app.get_settings(plugin_name)
    print(loaded_settings)
    
    
