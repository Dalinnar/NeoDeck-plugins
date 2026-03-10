from flask import Blueprint
import os
from spotify_connect.functions import *

# === METADATOS DEL PLUGIN ===
plugin_name = 'spotify_connect'
plugin_version = "1.0.3"
creators = ["Dalinnar"]
description = "Control Spotify and manage your playlists directly from your deck."

plugin = Blueprint(plugin_name, __name__)
plugin.BASE_DIR = os.path.dirname(os.path.abspath(__file__))

plugin.settings = {
    "#conect_to_spotify": "/spotyconect",
    "#make_your_app": "https://developer.spotify.com/dashboard",
    "_Client_ID": "",
    "_Client_Secret": ""
}

plugin.metadata = {
    "name": plugin_name,
    "version": plugin_version,
    "creators": creators,
    "description": description,
    "icon": "assets/icon.jpg"
}

plugin.command_map = {
    "/spotyfy_add_to_playlist"      : lambda message: add_to_playlist(message),
    "/spotyfy_remove_from_playlist" : lambda message: remove_from_playlist(message),
    "/spotyfy_play_playlist"        : lambda message: play_playlist(message),
    "!spotify_volume"               : lambda message: set_volume(message),
    "/spotify_pp"                   : lambda        : play_pause(),
    "/spotify_next"                 : lambda        : next_track(),
    "/spotify_previous"             : lambda        : previous_track(),
    "/spotify_shuffle"              : lambda        : shuffle_toggle(),
    "/spotify_repeat"               : lambda        : repeat_toggle(),
    "/spotify_follow_artist"        : lambda        : follow_artist(),
    "/spotify_unfollow_artist"      : lambda        : unfollow_artist(),
    "/spotify_like_song"            : lambda        : toggle_like_song(),
}

plugin.add_url_rule("/spotyconect", view_func=spotyconect)
plugin.add_url_rule("/callback", view_func=callback)
plugin.add_url_rule("/status", view_func=status)
plugin.add_url_rule("/spotyfy_connect/get_playlists", view_func=get_user_playlists)


def init():
    pass
plugin.init = init