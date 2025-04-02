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