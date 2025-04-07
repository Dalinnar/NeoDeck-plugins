import math
from functools import wraps
from flask import current_app
from obswebsocket import obsws,requests as obsrequests


def with_obs_connection(func):
    """Decorador que maneja la conexión y desconexión de OBS WebSocket."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        settings = current_app.get_settings("OBS")  # Obtener configuración de OBS
        ws = obsws(
            current_app.local_ip,
            settings.get("port", 4455),
            settings.get("server_password", "")
        )
        try:
            ws.connect()  # Establece la conexión con OBS
            # Llamamos a la función original y pasamos ws como primer argumento
            return func(ws, *args, **kwargs)
        finally:
            ws.disconnect()  # Aseguramos la desconexión cuando termine

    return wrapper

@with_obs_connection
def change_scene(ws, message=""):
    scene_name = message.split(" ", 1)[1]
    ws.call(obsrequests.SetCurrentProgramScene(sceneName=scene_name))

#get current scene name
@with_obs_connection
def get_current_scene(ws):
    response = ws.call(obsrequests.GetCurrentProgramScene())
    return response.datain.get('currentProgramSceneName')

@with_obs_connection
def toggle_recording(ws):
    ws.call(obsrequests.ToggleRecord())

#start recording
@with_obs_connection
def start_recording(ws):
    ws.call(obsrequests.StartRecord())

#stop recording
@with_obs_connection
def stop_recording(ws):
    ws.call(obsrequests.StopRecord())

#toggle streaming
@with_obs_connection
def toggle_streaming(ws):
    ws.call(obsrequests.ToggleStream())

#start streaming
@with_obs_connection
def start_streaming(ws):
    ws.call(obsrequests.StartStream())

#stop streaming
@with_obs_connection
def stop_streaming(ws):
    ws.call(obsrequests.StopStream())


#toggle virtual camera
@with_obs_connection
def toggle_virtual_camera(ws):
    ws.call(obsrequests.ToggleVirtualcam())

#return a list of all the scenes
@with_obs_connection
def get_scene_list(ws):
    response = ws.call(obsrequests.GetSceneList())
    scene_names = [scene["sceneName"] for scene in response.getScenes()]    
    return scene_names

#return a list of all the sources in all scenes
@with_obs_connection
def get_source_list(ws):
    scenes = get_scene_list()
    sources = set()
    for scene in scenes:
        scene_items = ws.call(obsrequests.GetSceneItemList(sceneName=scene))
        for item in scene_items.datain.get("sceneItems", []):
            sources.add(item["sourceName"])
    return list(sources)



@with_obs_connection
def get_audio_source_list(ws):
    possible_audio_sources = ["audio_capture","wasapi_input_capture","wasapi_output_capture","wasapi_process_output_capture","image_source","vlc_source","ffmpeg_source"]
    scenes = get_scene_list()  
    audio_inputs = set()
    for scene in scenes:
        scene_items = ws.call(obsrequests.GetSceneItemList(sceneName=scene))  # Obtener los items de la escena
        
        for item in scene_items.datain.get("sceneItems", []):
            if item["inputKind"] in possible_audio_sources:
                audio_inputs.add(item["sourceName"])
    return list(audio_inputs)

@with_obs_connection
def toggle_source(ws, message):
    source_name = message.split(" ", 1)[1].strip()
    current_scene = get_current_scene()
    scene_items = ws.call(obsrequests.GetSceneItemList(sceneName=current_scene)).datain.get("sceneItems", [])
    for item in scene_items:
        if item["sourceName"] == source_name:
            ws.call(obsrequests.SetSceneItemEnabled(
                sceneName=current_scene,
                sceneItemId=item["sceneItemId"],
                sceneItemEnabled=not item["sceneItemEnabled"]
            ))
            return
    raise ValueError(f"Source '{source_name}' not found in the current scene '{current_scene}'.")


@with_obs_connection
def get_source_id(ws, source_name):
    current_scene = get_current_scene()
    scene_items = ws.call(obsrequests.GetSceneItemList(sceneName=current_scene))
    for item in scene_items.datain.get("sceneItems", []):
        if item.get("sourceName") == source_name:
            return item.get("sceneItemId")
    return None

@with_obs_connection
def get_source_data(ws, source_name):
    try:
        response = ws.call(obsrequests.GetInputSettings(inputName=source_name))
        return response.datain  # Devuelve toda la configuración de la fuente
    except Exception as e:
        raise ValueError(f"Error retrieving data for source '{source_name}': {e}")
    


def set_volumedb(x):
    """transform the volume level from 0 to 100 to a value between -100 and 0 on a logarithmic scale"""
    return 21.67 * math.log(x + 1) - 100

@with_obs_connection
def set_source_volume(ws, message):
    message = message.split(" ", 1)[1]
    volume_level = set_volumedb(max(0, min(100, int(message.split()[-1]))))
    source_name = message.rsplit(" ", 1)[0]
    
    try:
        # Establece el volumen de la fuente de audio usando inputVolumeDb
        ws.call(obsrequests.SetInputVolume(
            inputName=source_name,
            inputVolumeDb=volume_level
        ))
    except Exception as e:
        raise ValueError(f"Error setting volume for source '{source_name}': {e}")
    

@with_obs_connection
def trigger_hotkey(ws, message):
    message = message.lower()
    keyModifiers = {}
    if "ctrl" or "control" in message.lower():
        keyModifiers["control"] = True
        message = message.replace("ctrl", "")
    if "shift" in message.lower(): 
        keyModifiers["shift"] = True
        message = message.replace("shift", "")
    if "alt" in message.lower():
        keyModifiers["alt"] = True
        message = message.replace("alt", "")
    message = message.replace("+", "")

    keySequence = message.split(" ", 1)[1].replace(" ", "")

    keyId = f"OBS_KEY_{keySequence}".upper()
    ws.call(obsrequests.TriggerHotkeyByKeySequence(keyId=keyId, keyModifiers=keyModifiers))