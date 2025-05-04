from flask import request, redirect, session, url_for, current_app
import spotipy
from spotipy.oauth2 import SpotifyOAuth


def get_plugin_settings():
    from spotify_connect import plugin_name
    return current_app.get_settings(plugin_name)

def get_oauth():
    settings = get_plugin_settings()
    port = current_app.get_settings().get("webdeck", {}).get("port", 5000)
    redirect_uri = f"http://127.0.0.1:{port}/callback"

    client_id = settings.get("Client_ID") or settings.get("_Client_ID")
    client_secret = settings.get("Client_Secret") or settings.get("_Client_Secret")

    if not client_id or not client_secret:
        raise RuntimeError("Missing Spotify Client ID or Secret.")

    return SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=(
            "user-library-modify user-library-read "
            "user-read-currently-playing user-read-playback-state user-modify-playback-state "
            "playlist-read-private playlist-read-collaborative "
            "playlist-modify-private playlist-modify-public "
            "user-follow-modify user-follow-read "
            "user-read-recently-played"
        ),
)

def get_spotify_client(refresh=True):
    from spotify_connect import plugin_name
    settings = current_app.get_settings()

    creds = settings.get(plugin_name, {})
    access_token = creds.get("access_token")
    refresh_token = creds.get("refresh_token")

    if not access_token and not refresh_token:
        raise RuntimeError(
            "Spotify no está inicializado. Ve a /spotyconect para autenticarte."
        )

    try:
        # Si piden refrescar y hay refresh_token, renovar el access_token
        if refresh and refresh_token:
            oauth = get_oauth()
            token_info = oauth.refresh_access_token(refresh_token)

            # Actualizar credenciales en settings
            creds["access_token"] = token_info["access_token"]
            creds["refresh_token"] = token_info.get("refresh_token", refresh_token)
            settings[plugin_name] = creds
            current_app.load_settings(settings)

            access_token = creds["access_token"]

        # Si no refrescamos, usamos el access_token guardado
        sp = spotipy.Spotify(auth=access_token)

        # Validar token; si es inválido y no refrescamos, lanzará SpotifyException
        sp.current_user()
        return sp

    except spotipy.SpotifyException:
        raise RuntimeError(
            "El token de Spotify es inválido o ha expirado. Por favor, autentícate de nuevo."
        )
    except Exception as e:
        raise RuntimeError(f"Error al obtener el cliente de Spotify: {e}")



def spotyconect():
    oauth = get_oauth()
    return redirect(oauth.get_authorize_url())


def callback():
    from spotify_connect import plugin_name
    oauth = get_oauth()
    code = request.args.get('code')
    if not code:
        return "No authorization code provided."

    try:
        token_info = oauth.get_access_token(code)
    except Exception as e:
        return f"Failed to get access token: {str(e)}"

    access_token = token_info.get('access_token')
    if not access_token:
        return "No access token received from Spotify."

    session['token_info'] = token_info

    settings = current_app.get_settings()
    settings[plugin_name]["access_token"] = access_token
    settings[plugin_name]["refresh_token"] = token_info.get('refresh_token', '')
    current_app.load_settings(settings)

    try:
        get_spotify_client()
    except Exception as e:
        return f"Error connecting to Spotify: {str(e)}"

    return redirect(url_for(f'{plugin_name}.status'))


def status():
    try:
        sp = get_spotify_client()
        user = sp.current_user()
        html = f"""
            <h1>Connected to Spotify as {user['display_name']}</h1>
            <a href="/">Go back</a>
        """
        return html
    except Exception as e:
        return f"<h1>Spotify not connected:</h1><p>{str(e)}</p>"



def get_device_id():
    sp = get_spotify_client(refresh=False)
    devices = sp.devices()["devices"]
    if not devices:
        raise RuntimeError("No Spotify devices found.")
    return devices[0]["id"]

def get_user_playlists():
    sp = get_spotify_client()
    playlists_dict = {}
    for playlist in sp.current_user_playlists()["items"]:        
        playlists_dict[playlist["id"]] = playlist["name"]

    return playlists_dict

def add_to_playlist(message: str):    
    playlist_id = message.split(" ",1)[1]

    sp = get_spotify_client()
    track = sp.current_user_playing_track()["item"]["id"]
    sp.playlist_add_items(playlist_id, [track])



def remove_from_playlist(message):
    playlist_id = message.split(" ",1)[1]
    sp = get_spotify_client()
    track = sp.current_user_playing_track()["item"]["id"]

    sp.playlist_remove_all_occurrences_of_items(playlist_id, [track])

def play_playlist(message):
    playlist_id = message.split(" ",1)[1]
    sp = get_spotify_client()
    sp.start_playback(context_uri=f"spotify:playlist:{playlist_id}")


last_state = {"is_playing": None}
def play_pause():
    sp = get_spotify_client(refresh=False)
    devices = sp.devices()["devices"]
    if not devices:
        raise RuntimeError("No Spotify devices found.")
    device = devices[0]["id"]

    # Obtener el estado actual
    playback = sp.current_playback()
    is_playing = playback and playback["is_playing"]

    # Guardar estado
    last_state["is_playing"] = is_playing

    # Cambiar estado
    if is_playing:
        sp.pause_playback(device_id=get_device_id())
    else:
        sp.start_playback(device_id=get_device_id())

def next_track():
    sp = get_spotify_client()
    sp.next_track()

def previous_track():
    sp = get_spotify_client()
    sp.previous_track()

def shuffle():
    sp = get_spotify_client()
    sp.shuffle(True)
#repeat track or playlist

def is_shuffle_enabled():
    sp = get_spotify_client(refresh=False)
    playback = sp.current_playback()
    if not playback:
        raise RuntimeError("No playback info available.")
    return playback.get("shuffle_state", False)


def shuffle_toggle():
    sp = get_spotify_client()
    sp.shuffle(not is_shuffle_enabled(), device_id=get_device_id())



def get_repeat_mode():
    sp = get_spotify_client(refresh=False)
    playback = sp.current_playback()
    if not playback:
        raise RuntimeError("No playback info available.")
    return playback.get("repeat_state", "off")


def repeat_toggle():
    sp = get_spotify_client()
    current_mode = get_repeat_mode()
    
    next_mode = {
        "off": "context",
        "context": "track",
        "track": "off"
    }.get(current_mode, "off")

    sp.repeat(next_mode, device_id=get_device_id())



def set_volume(message):
    volume = message.split(" ",1)[1]
    sp = get_spotify_client(refresh=False)
    sp.volume(int(volume), device_id=get_device_id())


#follow the artis on the current track
def follow_artist():
    sp = get_spotify_client()
    sp.user_follow_artists([sp.current_user_playing_track()["item"]["artists"][0]["id"]])
    
    
def unfollow_artist():
    sp = get_spotify_client()
    sp.user_unfollow_artists([sp.current_user_playing_track()["item"]["artists"][0]["id"]])
    print("Unfollowed artist")


#favorite the current track
def toggle_like_song():
    sp = get_spotify_client()
    current_track = sp.current_user_playing_track()
    track_id = current_track["item"]["id"]

    is_liked = sp.current_user_saved_tracks_contains([track_id])[0]

    if is_liked:
        sp.current_user_saved_tracks_delete([track_id])
        print("Track removed from liked songs.")
    else:
        sp.current_user_saved_tracks_add([track_id])
        print("Track added to liked songs.")