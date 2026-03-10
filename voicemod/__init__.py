from flask import Blueprint

from voicemod.functions import *
import uuid



plugin_name = 'voicemod'  # Plugin name (must be the same as the folder name)
plugin_version = "1.0.4"  # Plugin version
creators = ["Dalinnar"]  # List of creators
description = "Switch voices, play sounds, and control your Voicemod directly from your deck."  # Plugin description

plugin = Blueprint(plugin_name, __name__)


"""
"#" : link reference, to go and see maybe some docts about how to ...
"_" : private variable, not visible in the settings
"""
plugin.settings = {
    "_voicemod_key" :"",    
    "port": 59129,
    "uuid" : str(uuid.uuid4()),
    "#get_your_key_here": "https://control-api.voicemod.net/"
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
    "/voicemod_playmeme": lambda message: play_meme(message),
    "/voicemod_loadvoice": lambda message: play_voice(message),
    
    "/voicemod_toggleBackground": lambda: toggleBackground(),
    "/voicemod_toggleVoiceChanger": lambda : toggleVoiceChanger(),
    "/voicemod_toggleHearMyVoice": lambda : toggleHearMyVoice(),
}

# PLUGIN MONITORS
plugin.monitors = {}

# PLUGIN ROUTES
plugin.add_url_rule('/voicemod/soundboards_list', view_func=soundboards_list)
plugin.add_url_rule('/voicemod/generate_soundboard/<soundboard_id>', view_func=generate_soundboard)
plugin.add_url_rule('/voicemod/generate_voices/' ,view_func=generate_voices)


def init():
    pass

plugin.init = init