import re
import math
import websocket
from flask import current_app , jsonify
import json
from flask import Response
from functools import wraps
import uuid
from types import SimpleNamespace

def get_settings():
    if not getattr(get_settings, "cache", None):
        from .__init__ import plugin_name
        get_settings.cache = current_app.get_settings(plugin_name)
    return get_settings.cache


def objectify(data):
    if not isinstance(data, str):        
        data = json.dumps(data)
    return json.loads(data, object_hook=lambda d: SimpleNamespace(**d))



def voicemodconnect(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        ws = None
        try:
            settings = get_settings()
            if isinstance(settings["port"], dict):
                settings["port"] = list(settings["port"].values())[0]
            port = settings["port"]

            ws = websocket.create_connection(f"ws://localhost:{port}/v1")
            ws.recv()  # handshake

            # Registro de cliente
            data = json.dumps({
                "id": settings["uuid"],
                "action": "registerClient",
                "payload": {
                    "clientKey": settings["voicemod_key"]
                }
            })
            ws.send(data)
            ws.recv()  # respuesta a registro

            # Se pasa el ws como keyword argument a la función decorada
            return func(*args, ws=ws, **kwargs)
        finally:
            if ws:
                ws.close()
    return wrapper
    
@voicemodconnect
def get_sound_list(ws):
    

    data = json.dumps({
        "action": "getAllSoundboard",
        "id" : str(uuid.uuid4()),
        "payload": {}
    })
    ws.send(data)    
    response = ws.recv()
    response_data = json.loads(response)
    return Response(json.dumps(response_data,indent=4), mimetype='application/json')
    
@voicemodconnect
def get_voices_list(ws):
    
    
    data = json.dumps({
        "action": "getVoices",
        "id" : str(uuid.uuid4()),
        "payload": {}
    })
    ws.send(data)    
    response = ws.recv()

    response_data = json.loads(response)

    voices = []

    for i in objectify(response_data["actionObject"]["voices"]):
        if i.enabled and (i.favorited or i.isCustom):
            voices.append(i)
    print(voices)
    return Response(json.dumps(response_data["actionObject"]["voices"],indent=4), mimetype='application/json')


@voicemodconnect
def soundboards_list(ws):
    data = json.dumps({
        "action": "getAllSoundboard",
        "id" : str(uuid.uuid4()),})
    
    soundboards_dict = {}
    ws.send(data)
    response = json.loads(ws.recv())
    for soundboard in objectify(response["actionObject"]["soundboards"]):
        if soundboard.enabled and soundboard.isCustom:
            soundboards_dict[str(soundboard.id)] = str(soundboard.name)
    return soundboards_dict



@voicemodconnect
def generate_soundboard(ws,soundboard_id):
    
    data = json.dumps({
        "action": "getAllSoundboard",
        "id" : str(uuid.uuid4()),})
    
    ws.send(data)
    response = json.loads(ws.recv())
    for soundboard in objectify(response["actionObject"]["soundboards"]):
        if soundboard.id == soundboard_id:
            folder_data = generate_folder(soundboard.sounds, "/voicemod_playmeme")
            return jsonify({"success": True, "data": folder_data})

def grid_dim(n):
    n += 1
    best = (n, 1)
    for rows in range(1, n + 1):
        cols = math.ceil(n / rows)
        if rows * cols >= n:
            ratio = cols / rows
            best_ratio = best[0] / best[1]
            # Queremos que el ratio esté lo más cerca posible de 2
            if abs(ratio - 2) < abs(best_ratio - 2):
                best = (cols, rows)
    return best



@voicemodconnect
def play_meme(message,ws):
    meme_id = re.search(r'\((.*?)\)', message)
    if meme_id:
        meme_id = meme_id.group(1)
    else:
        meme_id = None

    
    data = json.dumps({
        "action": "playMeme",
        "id" : str(uuid.uuid4()),
        "payload": {
            "FileName": meme_id,
            "IsKeyDown":True
        }
    })
    ws.send(data)
    ws.recv()

@voicemodconnect
def play_voice(message,ws):
    print("new voice")

    # Extraer voiceID del mensaje
    match = re.search(r'\((.*?)\)', message)
    new_voice_id = match.group(1) if match else None
    if not new_voice_id:
        print("No se encontró voiceID en el mensaje.")
        return

    # Paso 1: obtener el voiceID actual
    get_current = json.dumps({
        "action": "getCurrentVoice",
        "id": str(uuid.uuid4()),
        "payload": {}
    })
    ws.send(get_current)
    response = json.loads(ws.recv())

    current_voice_id = response.get("actionObject", {}).get("voiceID", None)

    if current_voice_id == new_voice_id:
        # Paso 2: si ya está activo, hacer toggle (para apagar)
        toggle = json.dumps({
            "action": "toggleVoiceChanger",
            "id": str(uuid.uuid4()),
            "payload": {}
        })
        ws.send(toggle)
        print(f"Voice '{new_voice_id}' ya estaba activo, toggleVoiceChanger enviado.")
    else:
        # Paso 3: cargar nueva voz
        load = json.dumps({
            "action": "loadVoice",
            "id": str(uuid.uuid4()),
            "payload": {
                "voiceID": new_voice_id,
                "IsKeyDown": True
            }
        })
        ws.send(load)
        print(f"Cargando nueva voz: {new_voice_id}")
    
    ws.recv()  # recibir respuesta final (opcional)

@voicemodconnect
def generate_voices(ws):
    data = json.dumps({
        "action": "getVoices",
        "id" : str(uuid.uuid4()),
        "payload": {
            "favorited" : True
        }
    })
    ws.send(data)
    response =objectify(json.loads(ws.recv())["actionObject"]["voices"])
    voices = []
    for voice in response:
        if voice.enabled and (voice.favorited or voice.isCustom):
            voices.append(voice)
    folder_data = generate_folder(voices, "/voicemod_loadvoice")
    return jsonify({"success": True, "data": folder_data})

@voicemodconnect
def toggleBackground(ws):
    data = json.dumps({
        "action": "toggleBackground",
        "id" : str(uuid.uuid4()),
        "payload": {}
    })
    ws.send(data)
    ws.recv()

@voicemodconnect
def toggleVoiceChanger(ws):
    data = json.dumps({
        "action": "toggleVoiceChanger",
        "id" : str(uuid.uuid4()),
        "payload": {}
    })
    ws.send(data)
    ws.recv()

@voicemodconnect
def toggleHearMyVoice(ws):
    data = json.dumps({
        "action": "toggleHearMyVoice",
        "id" : str(uuid.uuid4()),
        "payload": {}
    })
    ws.send(data)
    ws.recv()


def generate_folder(items, command_prefix):
    cols, rows = grid_dim(len(items))

    buttons = []
    for index, item in enumerate(items):
        col = (index % cols) + 1
        row = (index // cols) + 1
        button_data = {
            "background_color" : "#00fff6",
            "column": col,
            "row": row,
            "endcolumn": col,
            "endrow": row,
            "command": f"{command_prefix} ({item.id})",
            "image": item.imageURL if getattr(item, 'imageURL', "") else "",
            "image_size": "95" if getattr(item, 'imageURL', "") else "0",
            "text_color": "#000000"
        }
        buttons.append(button_data)

    # Botón de "volver"
    back_button = {
        "background_color": "#00fff6",
        "command": "$folder()",
        "column": cols,
        "row": rows,
        "endcolumn": cols,
        "endrow": rows,
        "image": "/static/img/back11.svg",
        "image_size": "95",
        "text_color": "#000000"
    }
    buttons.append(back_button)

    return {
        "background": "#383838",
        "buttons": buttons,
        "columns": cols,
        "rows": rows
    }