import math
import random
from functools import wraps
from flask import current_app, jsonify
from obswebsocket import obsws, requests as obsrequests
from obswebsocket.exceptions import ConnectionFailure

def with_obs_connection(func):
    """Decorador que maneja la conexión y desconexión de OBS WebSocket."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        settings = current_app.get_settings("OBS_studio")  # Get OBS settings
        ws = obsws(
            current_app.local_ip,
            settings.get("port", 4455),
            settings.get("server_password", "")
        )
        try:
            ws.connect()
        except ConnectionFailure:
            # OBS no está corriendo o no acepta conexiones
            current_app.logger.warning("OBS is not running or connection failed.")
            return  # Or return jsonify({"error": "OBS not available"}), 503

        try:
            return func(ws, *args, **kwargs)
        finally:
            ws.disconnect()

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
        scene_items = ws.call(obsrequests.GetSceneItemList(sceneName=scene))  #get scene items
        
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
        return response.datain
    except Exception as e:
        raise ValueError(f"Error retrieving data for source '{source_name}': {e}")
    


def set_volumedb(x):
    """transform the volume level from 0 to 100 to a value between -100 and 0 on a logarithmic scale"""
    return 21.67 * math.log(x + 1) - 100

def get_volume_level(db):
    """transform the volume level from -100 to 0 to a value between 0 and 100 on an exponential scale"""
    return math.exp((db + 100) / 21.67) - 1
@with_obs_connection
def set_source_volume(ws, message):
    message = message.split(" ", 1)[1]
    source_name = message.rsplit(" ", 1)[0]

    if message.endswith("get"):
        try:
            response = ws.call(obsrequests.GetInputVolume(inputName=source_name))
            volume = get_volume_level(int(response.datain.get("inputVolumeDb")))
            return jsonify({"data": volume})
        except Exception as e:
            raise ValueError(f"Error retrieving volume for source '{source_name}': {e}")
    
    try:
        volume_level = set_volumedb(max(0, min(100, int(message.split()[-1]))))
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


def generate_obs_scene_folder(scenes):
    def grid_dim(n):
        cols = 4  # You can customize the number of columns
        rows = (n + cols - 1) // cols
        return cols, rows

    cols, rows = grid_dim(len(scenes))

    buttons = []
    base_color = "#002396"
    for index, scene_name in enumerate(scenes):
        col = (index % cols) + 1
        row = (index // cols) + 1
        # Simple gradient: lighten the base color by adding index*10 to each RGB component
        color_offset = min(index * 10, 100)  # Cap the offset to avoid going too bright
        buttons.append({
            "background_color": f"#{int(base_color[1:3], 16) + color_offset:02x}{int(base_color[3:5], 16) + color_offset:02x}{int(base_color[5:7], 16) + color_offset:02x}",
            "column": col,
            "row": row,
            "endcolumn": col,
            "endrow": row,
            "command": f"/obs_change_scene {scene_name}",
            "image": "",
            "image_size": "0",
            "text_color": "#000000",
            "btn_text": scene_name,
        })

    # Botón "volver"
    buttons.append({    
        "background_color": base_color,
        "command": "$folder()",
        "column": cols,
        "row": rows,
        "background":"",
        "endcolumn": cols,
        "endrow": rows,
        "image": "/static/img/back11.svg",
        "image_size": "95",
        "text_color": "#000000"
    })

    return {
        "background": "#383838",
        "buttons": buttons,
        "columns": cols,
        "rows": rows
    }