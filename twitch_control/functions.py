from twitch_control.__init__ import plugin_name
import re
import requests
from flask import current_app


def get_loaded_settings():
    if not hasattr(get_loaded_settings, "cache"):
        get_loaded_settings.cache = current_app.get_settings(plugin_name)
    return get_loaded_settings.cache

def end_active_poll():
    # Obtener la encuesta activa
    active_poll = get_active_poll()
    if not active_poll:
        print("No hay encuesta activa para terminar.")
        return False

    poll_id = active_poll["id"]

    # Obtener configuración de la app
    app_settings = get_loaded_settings()
    access_token = app_settings.get('access_token', '')
    client_id = app_settings.get('client_id', '')
    username = app_settings.get('twitch_username', '')
    broadcaster_id = get_channel_id(username, app_settings)

    if not broadcaster_id:
        print("No se pudo obtener el broadcaster ID")
        return False

    url = "https://api.twitch.tv/helix/polls"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Client-ID": client_id,
        "Content-Type": "application/json"
    }

    payload = {
        "broadcaster_id": broadcaster_id,
        "id": poll_id,
        "status": "TERMINATED"
    }

    response = requests.patch(url, headers=headers, json=payload)

    if response.status_code == 200:
        print(f"Encuesta '{active_poll['title']}' terminada correctamente.")
        return True
    else:
        print(f"Error al terminar la encuesta: {response.status_code} - {response.text}")
        return False

def get_active_poll():
    app_settings = get_loaded_settings()
    access_token = app_settings.get('access_token', '')
    client_id = app_settings.get('client_id', '')
    username = app_settings.get('twitch_username', '')
    broadcaster_id = get_channel_id(username, app_settings)

    if not broadcaster_id:
        print("No se pudo obtener el broadcaster ID")
        return None

    url = f"https://api.twitch.tv/helix/polls?broadcaster_id={broadcaster_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Client-ID": client_id
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json().get("data", [])
        for poll in data:
            if poll["status"] == "ACTIVE":
                print(f"Poll activa detectada: {poll['title']}")
                return poll  # Retorna todo el dict de la encuesta activa
        print("No hay encuesta activa.")
        return None
    else:
        print(f"Error al obtener las encuestas: {response.status_code} - {response.text}")
        return None

def get_viewer_count():
    app_settings = get_loaded_settings()
    url = f"https://api.twitch.tv/helix/streams?user_login={app_settings.get('twitch_username', 'twitch_username')}"
    headers = {
        "Authorization": f"Bearer {app_settings.get('access_token', '')}",
        "Client-ID": app_settings.get('client_id', '')
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        streams = data.get("data", [])
        if streams:
            return streams[0]["viewer_count"]
        else:
            return 0  # No está en vivo
    else:
        print("Error:", response.status_code, response.text)
        return None

def send_message(message):
    app_settings = get_loaded_settings()
    username = app_settings.get('twitch_username', '')
    access_token = app_settings.get('access_token', '')
    client_id = app_settings.get('client_id', '')
    
    # Primero, obtenemos el ID del canal y el sender_id (ID del usuario autenticado)
    user_url = f"https://api.twitch.tv/helix/users?login={username}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Client-ID": client_id
    }
    
    # Realizamos la solicitud para obtener el ID del canal y el ID del usuario
    user_response = requests.get(user_url, headers=headers)
    if user_response.status_code == 200:
        user_data = user_response.json()
        broadcaster_id = user_data['data'][0]['id']
        sender_id = user_data['data'][0]['id']  # Usamos el mismo ID para el sender_id
    else:
        print("Error obteniendo el ID del canal:", user_response.status_code, user_response.text)
        return False
    
    # Ahora enviamos el mensaje al chat
    message_url = "https://api.twitch.tv/helix/chat/messages"
    message_data = {
        "broadcaster_id": broadcaster_id,
        "sender_id": sender_id,  # Añadimos el sender_id
        "message": message
    }
    
    message_response = requests.post(message_url, headers=headers, json=message_data)
    
    if message_response.status_code == 200:
        print(f"Mensaje enviado con éxito: {message}")
        return True
    else:
        print(f"Error enviando el mensaje: {message_response.status_code} - {message_response.text}")
        return False  


emote_mode_active = False
def toggle_emote_mode():
    global emote_mode_active
    app_settings = get_loaded_settings()
    username = app_settings.get('twitch_username', '')
    channel_id = get_channel_id(username, app_settings)
    
    if not channel_id:
        print("Could not find channel ID")
        return False
    
    moderator_id = channel_id
    url = f"https://api.twitch.tv/helix/chat/settings?broadcaster_id={channel_id}&moderator_id={moderator_id}"
    headers = {
        "Authorization": f"Bearer {app_settings.get('access_token', '')}",
        "Client-ID": app_settings.get('client_id', ''),
        "Content-Type": "application/json"
    }
    
    emote_mode_active = not emote_mode_active
    data = {"emote_mode": emote_mode_active}
    response = requests.patch(url, headers=headers, json=data)
    
    if response.status_code == 200:
        action = "enabled" if emote_mode_active else "disabled"
        print(f"Emote-only mode {action} for channel")
        return True
    else:
        emote_mode_active = not emote_mode_active
        print(f"Error toggling emote-only mode: {response.status_code} - {response.text}")
        return False
    
slow_mode_active = False

def toggle_slow_mode(message):
    seconds = int(message.split(" ")[1])
    
    global slow_mode_active
    app_settings = get_loaded_settings()
    username = app_settings.get('twitch_username', '')
    channel_id = get_channel_id(username, app_settings)
    if not channel_id:
        print("Could not find channel ID")
        return False
    moderator_id = channel_id
    url = f"https://api.twitch.tv/helix/chat/settings?broadcaster_id={channel_id}&moderator_id={moderator_id}"
    headers = {
        "Authorization": f"Bearer {app_settings.get('access_token', '')}",
        "Client-ID": app_settings.get('client_id', ''),
        "Content-Type": "application/json"
    }
    # Alternar estado
    slow_mode_active = not slow_mode_active
    data = {
        "slow_mode": slow_mode_active,
        "slow_mode_wait_time": seconds if slow_mode_active else 0
    }

    response = requests.patch(url, headers=headers, json=data)

    if response.status_code == 200:
        action = "enabled" if slow_mode_active else "disabled"
        print(f"Slow mode {action} (delay: {seconds}s)" if slow_mode_active else "Slow mode disabled")
        return True
    else:
        slow_mode_active = not slow_mode_active  # revertir cambio local si falla
        print(f"Error toggling slow mode: {response.status_code} - {response.text}")
        return False
    
def setup_poll(message):
    try:
        # Remover comando inicial
        message = message.split(" ", 1)[1].strip()

        # Extraer opciones entre corchetes
        parts = re.findall(r'\[(.*?)\]', message)
        if len(parts) < 2:
            print("Debes tener al menos un título y una opción.")
            return

        title = parts[0]
        choices = parts[1:]
        #remove the empty choices
        choices = [choice for choice in choices if choice]

        # Extraer configuraciones entre paréntesis (on) (1000)
        extras = re.findall(r'\((.*?)\)', message)
        enable_channel_points = False
        points_per_vote = 200  # valor por defecto

        if len(extras) >= 1 and extras[0].lower() == "on":
            enable_channel_points = True
            if len(extras) >= 2 and extras[1].isdigit():
                points_per_vote = int(extras[1])

        print(f"Creando poll con título: {title}, opciones: {choices}, puntos: {points_per_vote}, puntos activados: {enable_channel_points}")
        create_poll(
            title=title,
            choices=choices,
            duration_sec=180,
            enable_channel_points=enable_channel_points,
            points_per_vote=points_per_vote
        )
    except Exception as e:
        print(f"Error al procesar el mensaje de la encuesta: {e}")
    

def create_poll(title, choices, duration_sec=180, enable_channel_points=False, points_per_vote=200):
    app_settings = get_loaded_settings()
    access_token = app_settings.get('access_token', '')
    client_id = app_settings.get('client_id', '')
    username = app_settings.get('twitch_username', '')
    broadcaster_id = get_channel_id(username, app_settings)
    
    if not broadcaster_id:
        print("Could not find broadcaster ID")
        return False

    url = "https://api.twitch.tv/helix/polls"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Client-ID": client_id,
        "Content-Type": "application/json"
    }

    options = [{"title": choice} for choice in choices]

    data = {
        "broadcaster_id": broadcaster_id,
        "title": title,
        "choices": options,
        "duration": duration_sec,
        "channel_points_voting_enabled": enable_channel_points,
        "channel_points_per_vote": points_per_vote
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 201 or response.status_code == 200:
        print(f"Poll '{title}' created successfully!")
        return True
    else:
        print(f"Error creating poll: {response.status_code} - {response.text}")
        return False
    
def get_viewer_count():
    app_settings = get_loaded_settings()
    username = app_settings.get('twitch_username', 'twitch_username')
    url = f"https://api.twitch.tv/helix/streams?user_login={username}"
    
    headers = {
        "Authorization": f"Bearer {app_settings.get('access_token', '')}",
        "Client-ID": app_settings.get('client_id', '')
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        streams = data.get("data", [])
        
        if streams:  # Si el canal está en vivo
            return streams[0]["viewer_count"]
        else:
            return 0 
    else:
        print("Error:", response.status_code, response.text)
        return None

def execute_ad():
    app_settings = get_loaded_settings()
    username = app_settings.get('twitch_username', '')
    access_token = app_settings.get('access_token', '')
    client_id = app_settings.get('client_id', '')
    
    # Primero, obtenemos el ID del canal usando el nombre de usuario
    user_url = f"https://api.twitch.tv/helix/users?login={username}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Client-ID": client_id
    }
    user_response = requests.get(user_url, headers=headers)
    if user_response.status_code == 200:
        user_data = user_response.json()
        broadcaster_id = user_data['data'][0]['id']
    else:
        print("Error obteniendo el ID del canal:", user_response.status_code, user_response.text)
        return False
    
    # Ahora ejecutamos el anuncio
    ad_url = "https://api.twitch.tv/helix/streams/commercial"
    ad_data = {
        "broadcaster_id": broadcaster_id,
        "length": 30  # Duración del anuncio en segundos (30 segundos es un valor típico)
    }
    
    ad_response = requests.post(ad_url, headers=headers, params=ad_data)
    
    if ad_response.status_code == 200:
        print("Anuncio ejecutado con éxito.")
        return True
    else:
        print("Error ejecutando el anuncio:", ad_response.status_code, ad_response.text)
        return False

def get_channel_id(username, app_settings=None):
    if not app_settings:
        app_settings = get_loaded_settings()
        
    url = f"https://api.twitch.tv/helix/users?login={username}"
    headers = {
        "Authorization": f"Bearer {app_settings.get('access_token', '')}",
        "Client-ID": app_settings.get('client_id', '')
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data.get("data"):
            return data["data"][0]["id"]
    
    return None


def get_latest_supporters(chat_log=None):
    app_settings = get_loaded_settings()
    username = app_settings.get('twitch_username', '')
    channel_id = get_channel_id(username, app_settings)

    headers = {
        "Authorization": f"Bearer {app_settings.get('access_token', '')}",
        "Client-ID": app_settings.get('client_id', '')
    }

    # Último seguidor
    follower_name = None
    followers_url = f"https://api.twitch.tv/helix/channels/followers?broadcaster_id={channel_id}&first=1"
    followers_resp = requests.get(followers_url, headers=headers)
    if followers_resp.status_code == 200 and followers_resp.json()["data"]:
        follower_name = followers_resp.json()["data"][0]["user_name"]
    

    # Último subscriptor
    subscriber_name = None
    subs_url = f"https://api.twitch.tv/helix/subscriptions?broadcaster_id={channel_id}&first=1"
    subs_resp = requests.get(subs_url, headers=headers)
    if subs_resp.status_code == 200 and subs_resp.json()["data"]:
        subscriber_name = subs_resp.json()["data"][0]["user_name"]


    return {
        "last_follower": follower_name or "None",
        "last_subscriber": subscriber_name or "None",
    }
follow_mode_active = False

def toggle_follow_mode():
    global follow_mode_active
    app_settings = get_loaded_settings()
    username = app_settings.get('twitch_username', '')
    channel_id = get_channel_id(username, app_settings)

    if not channel_id:
        print("Could not find channel ID")
        return False

    moderator_id = channel_id  # si sos broadcaster, podés usarte como mod
    url = f"https://api.twitch.tv/helix/chat/settings?broadcaster_id={channel_id}&moderator_id={moderator_id}"
    headers = {
        "Authorization": f"Bearer {app_settings.get('access_token', '')}",
        "Client-ID": app_settings.get('client_id', ''),
        "Content-Type": "application/json"
    }

    follow_mode_active = not follow_mode_active
    data = {
        "follower_mode": follow_mode_active,
        "follower_mode_duration": 0  # tiempo mínimo en minutos que deben haber seguido, podés cambiarlo
    }

    response = requests.patch(url, headers=headers, json=data)

    if response.status_code == 200:
        state = "enabled" if follow_mode_active else "disabled"
        print(f"Follow-only mode {state}")
        return True
    else:
        follow_mode_active = not follow_mode_active
        print(f"Error toggling follow-only mode: {response.status_code} - {response.text}")
        return False
    
sub_mode_active = False
def toggle_sub_mode():
    global sub_mode_active
    app_settings = get_loaded_settings()
    username = app_settings.get('twitch_username', '')
    channel_id = get_channel_id(username, app_settings)

    if not channel_id:
        print("Could not find channel ID")
        return False

    moderator_id = channel_id
    url = f"https://api.twitch.tv/helix/chat/settings?broadcaster_id={channel_id}&moderator_id={moderator_id}"
    headers = {
        "Authorization": f"Bearer {app_settings.get('access_token', '')}",
        "Client-ID": app_settings.get('client_id', ''),
        "Content-Type": "application/json"
    }

    sub_mode_active = not sub_mode_active
    data = {
        "subscriber_mode": sub_mode_active
    }

    response = requests.patch(url, headers=headers, json=data)

    if response.status_code == 200:
        state = "enabled" if sub_mode_active else "disabled"
        print(f"Sub-only mode {state}")
        return True
    else:
        sub_mode_active = not sub_mode_active
        print(f"Error toggling sub-only mode: {response.status_code} - {response.text}")
        return False
    
def create_clip():
    app_settings = get_loaded_settings()
    access_token = app_settings.get('access_token', '')
    client_id = app_settings.get('client_id', '')
    username = app_settings.get('twitch_username', '')
    broadcaster_id = get_channel_id(username, app_settings)

    if not broadcaster_id:
        print("Could not find broadcaster ID")
        return None

    url = f"https://api.twitch.tv/helix/clips?broadcaster_id={broadcaster_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Client-ID": client_id
    }

    response = requests.post(url, headers=headers)

    if response.status_code == 202:
        clip_data = response.json()
        clip_id = clip_data.get("data", [{}])[0].get("id", "")
        send_message(f"Clip created: https://clips.twitch.tv/{clip_id}")
        return clip_id
    else:
        send_message(f"Error creating clip: {response.status_code} - {response.text}")
        return None