from obswebsocket import obsws
from obswebsocket import requests as obsrequests
from flask import Response,current_app
from functools import wraps
import json
from obs_studio.functions import *



def get_scene_list_page():
    return Response(json.dumps(get_scene_list()), mimetype='application/json')

def get_source_list_page():    
    return Response(json.dumps(get_source_list()), mimetype='application/json')
def get_audio_source_list_page():
    return Response(json.dumps(get_audio_source_list()), mimetype='application/json')



def dynamic_scenes():
    print("heelo from here")
    #return generate_obs_scene_folder(scenes)
    print(generate_obs_scene_folder(get_scene_list()))
    #return Response(json.dumps(generate_obs_scene_folder(get_scene_list())), mimetype='application/json')
    return jsonify({"success": True, "data": generate_obs_scene_folder(get_scene_list())})

def check_connection():
    return "obs connected succesfully" if obs_is_connected() else "connection error"