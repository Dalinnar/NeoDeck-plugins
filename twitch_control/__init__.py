from flask import Blueprint
from twitch_control.functions import *
from twitch_control.routes import *

plugin_name = 'twitch_control'
plugin_version = "1.0.3"
creators = ["Dalinnar"]
description = "Easily interact with your Twitch audience using powerful chat commands. Manage polls, trigger ads, send messages, and switch between chat modes. and more!"  

plugin = Blueprint(plugin_name, __name__)


# Twitch
plugin.settings = {
    "get_your_api_key_here": {
        "type": "link",
        "href": "https://twitchtokengenerator.com/",
    },
    "twitch_username": {
        "type": "text",
        "default": "",
    },
    "access_token": {
        "type": "text",
        "default": "",
        "secret": True,
    },
    "client_id": {
        "type": "text",
        "default": "",
        "secret": True,
    },
    "refresh_token": {
        "type": "text",
        "default": "",
        "secret": True,
    },
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
    "/twitch_control_end_poll"              :   lambda          : end_active_poll(),
    "/twitch_control_emote_mode"            :   lambda          : toggle_emote_mode(),
    "/twitch_control_execute_add"           :   lambda          : execute_ad(),
    "/twitch_control_toggle_sub_mode"       :   lambda          : toggle_sub_mode(),
    "/twitch_control_toggle_follow_mode"    :   lambda          : toggle_follow_mode(),

    "/twitch_control_make_poll"     :   lambda message  : setup_poll(message),
    "/twitch_control_toggle_slow"   :   lambda message  : toggle_slow_mode(message),
    "/twitch_control_send_message"  :   lambda message  : send_message(message.split(" ",1)[1]),

}
# PLUGIN MONITORS
plugin.monitors = {
    "twitch_live_viewers": lambda : get_viewer_count(),
    "latest_supporters" : lambda : get_latest_supporters()
}

plugin.getters ={
    "/twitch_control_emote_mode" : lambda : get_emote_mode_status()
}

def init():
    pass

plugin.init = init