import math
import ast
import re
import json
from obswebsocket import obsws, requests as obsrequests
from obswebsocket.exceptions import ConnectionFailure
from flask import current_app


class OBSManager:
    def __init__(self, host: str, port: int = 4455, password: str = ""):
        self.host = host
        self.port = port
        self.password = password
        self._ws: obsws | None = None

    # ── connection ────────────────────────────────────────────────────────────

    @property
    def connected(self) -> bool:
        return self._ws is not None

    def connect(self) -> bool:
        self._ws = obsws(self.host, self.port, self.password)
        try:
            self._ws.connect()
            return True
        except ConnectionFailure:
            self._ws = None
            return False

    def disconnect(self):
        if self._ws:
            self._ws.disconnect()
            self._ws = None

    def _ws_call(self, request):
        """Make a single call, raising if not connected."""
        if not self._ws:
            raise RuntimeError("Not connected to OBS. Call connect() first.")
        return self._ws.call(request)

    # ── scenes ────────────────────────────────────────────────────────────────

    def get_scene_list(self) -> list[str]:
        response = self._ws_call(obsrequests.GetSceneList())
        return [scene["sceneName"] for scene in response.getScenes()]

    def get_current_scene(self) -> str:
        response = self._ws_call(obsrequests.GetCurrentProgramScene())
        return response.datain.get("currentProgramSceneName")

    def change_scene(self, scene_name: str):
        self._ws_call(obsrequests.SetCurrentProgramScene(sceneName=scene_name))

    # ── sources ───────────────────────────────────────────────────────────────

    def get_source_list(self) -> list[str]:
        sources = set()
        for scene in self.get_scene_list():
            items = self._ws_call(obsrequests.GetSceneItemList(sceneName=scene))
            for item in items.datain.get("sceneItems", []):
                sources.add(item["sourceName"])
        return list(sources)

    def get_audio_source_list(self) -> list[str]:
        audio_kinds = {
            "wasapi_input_capture",
            "wasapi_output_capture",
            "wasapi_process_output_capture",
            "coreaudio_input_capture",
            "coreaudio_output_capture",
        }
        response = self._ws_call(obsrequests.GetInputList())
        return [
            i["inputName"]
            for i in response.getInputs()
            if i["inputKind"] in audio_kinds
        ]
    
    def get_scene_item_list(self, scene_name: str = None) -> list[dict]:
        """Returns all scene items for a given scene (or current scene if none given)."""
        if scene_name is None:
            scene_name = self.get_current_scene()
        response = self._ws_call(obsrequests.GetSceneItemList(sceneName=scene_name))
        return response.datain.get("sceneItems", [])

    def toggle_source(self, source_name: str):
        scene = self.get_current_scene()
        items = self._ws_call(
            obsrequests.GetSceneItemList(sceneName=scene)
        ).datain.get("sceneItems", [])
        for item in items:
            if item["sourceName"] == source_name:
                self._ws_call(obsrequests.SetSceneItemEnabled(
                    sceneName=scene,
                    sceneItemId=item["sceneItemId"],
                    sceneItemEnabled=not item["sceneItemEnabled"],
                ))
                return
        raise ValueError(f"Source '{source_name}' not found in scene '{scene}'.")

    def get_source_id(self, source_name: str) -> int | None:
        scene = self.get_current_scene()
        items = self._ws_call(obsrequests.GetSceneItemList(sceneName=scene))
        for item in items.datain.get("sceneItems", []):
            if item.get("sourceName") == source_name:
                return item.get("sceneItemId")
        return None

    def get_source_data(self, source_name: str) -> dict:
        response = self._ws_call(obsrequests.GetInputSettings(inputName=source_name))
        return response.datain

    # ── volume ────────────────────────────────────────────────────────────────

    @staticmethod
    def _db_to_level(db: float) -> float:
        """Convert dB (-100..0) to a 0-100 user-facing level."""
        return math.exp((db + 100) / 21.67) - 1

    @staticmethod
    def _level_to_db(level: float) -> float:
        """Convert a 0-100 user-facing level to dB (-100..0)."""
        return 21.67 * math.log(max(level, 1e-9) + 1) - 100

    def get_source_volume(self, source_name: str) -> float:
        response = self._ws_call(obsrequests.GetInputVolume(inputName=source_name))
        return self._db_to_level(response.datain.get("inputVolumeDb"))

    def set_source_volume(self, source_name: str, level: int):
        db = self._level_to_db(max(0, min(100, level)))
        self._ws_call(obsrequests.SetInputVolume(inputName=source_name, inputVolumeDb=db))

    # ── recording ─────────────────────────────────────────────────────────────

    def toggle_recording(self):
        self._ws_call(obsrequests.ToggleRecord())

    def start_recording(self):
        self._ws_call(obsrequests.StartRecord())

    def stop_recording(self):
        self._ws_call(obsrequests.StopRecord())

    # ── streaming ─────────────────────────────────────────────────────────────

    def toggle_streaming(self):
        self._ws_call(obsrequests.ToggleStream())

    def start_streaming(self):
        self._ws_call(obsrequests.StartStream())

    def stop_streaming(self):
        self._ws_call(obsrequests.StopStream())

    # ── virtual camera ────────────────────────────────────────────────────────

    def toggle_virtual_camera(self):
        self._ws_call(obsrequests.ToggleVirtualcam())

    # ── hotkeys ───────────────────────────────────────────────────────────────

    def trigger_hotkey(self, message: str):
        message = message.lower()
        modifiers = {"control": False, "shift": False, "alt": False}

        for token, key in (("ctrl", "control"), ("control", "control"),
                           ("shift", "shift"), ("alt", "alt")):
            if token in message:
                modifiers[key] = True
                message = message.replace(token, "")

        key = message.replace("+", " ").strip().split()[-1]
        key_id = f"OBS_KEY_F{key[1:]}" if key.startswith("f") and key[1:].isdigit() \
                 else f"OBS_KEY_{key.upper()}"

        self._ws_call(obsrequests.TriggerHotkeyByKeySequence(
            keyId=key_id,
            keyModifiers=modifiers,
        ))

    # ── raw ───────────────────────────────────────────────────────────────────

    def raw_call(self, request_type: str, data: dict):
        request_class = getattr(obsrequests, request_type, None)
        if not request_class:
            raise ValueError(f"Unknown request type: '{request_type}'")
        self._ws_call(request_class(**data))


# ── standalone utility (no WebSocket) ────────────────────────────────────────

def _parse_args(message: str, expected: int):
    """Extrae los argumentos después del nombre del comando."""
    parts = message.split(" ", expected)
    args = parts[1:]  # descarta el nombre del comando
    if len(args) < expected:
        # faltan argumentos, rellenamos con None para detectarlo después
        args += [None] * (expected - len(args))
    return args


def _set_volume(message):
    source_name, level = _parse_args(message, 2)
    if level is None:
        raise ValueError("Uso: !obs_set_volume <source> <level>")
    return get_obs_manager().set_source_volume(source_name, int(level))


def _get_volume(message):
    source_name, = _parse_args(message, 1)
    if source_name is None:
        raise ValueError("Uso: !obs_set_volume <source>")
    return get_obs_manager().get_source_volume(source_name)

def _raw_request(message):
    match = re.search(r"\|(.*?)\|\s*\|(.*?)\|", message)
    if not match:
        raise ValueError("Uso: /obs_raw_request |RequestType| |RequestDataJSON|")
    
    request_type = match.group(1).strip()
    raw_data = match.group(2).strip()
    data = _parse_request_data(raw_data)
    
    return get_obs_manager().raw_call(request_type, data)


def _parse_request_data(raw_data: str) -> dict:
    """Parsea el JSON del raw request, tolerando comillas simples y sintaxis mixta JSON/Python."""
    if not raw_data:
        return {}

    # 1. Intento directo: JSON estricto válido
    try:
        return json.loads(raw_data)
    except json.JSONDecodeError:
        pass

    # 2. Fallback: normalizar keywords JSON → Python, luego literal_eval
    normalized = re.sub(r'\btrue\b', 'True', raw_data)
    normalized = re.sub(r'\bfalse\b', 'False', normalized)
    normalized = re.sub(r'\bnull\b', 'None', normalized)

    try:
        parsed = ast.literal_eval(normalized)
        if not isinstance(parsed, dict):
            raise ValueError("El requestData debe ser un objeto/diccionario.")
        return parsed
    except (ValueError, SyntaxError) as e:
        raise ValueError(
            f"requestData inválido. Debe ser JSON válido (con comillas dobles) "
            f"o sintaxis tipo Python. Error: {e}"
        )


def generate_obs_scene_folder(scenes: list[str]) -> dict:
    cols = 4
    rows = (len(scenes) + cols - 1) // cols
    base_color = (0x00, 0x23, 0x96)
    buttons = []

    for index, scene_name in enumerate(scenes):
        col = (index % cols) + 1
        row = (index // cols) + 1
        offset = min(index * 10, 100)
        r, g, b = (min(c + offset, 255) for c in base_color)
        buttons.append({
            "background_color": f"#{r:02x}{g:02x}{b:02x}",
            "column": col, "row": row,
            "endcolumn": col, "endrow": row,
            "command": f"/obs_change_scene {scene_name}",
            "image": "", "image_size": "0",
            "text_color": "#000000",
            "btn_text": scene_name,
        })

    buttons.append({
        "background_color": f"#{base_color[0]:02x}{base_color[1]:02x}{base_color[2]:02x}",
        "command": "$folder()",
        "column": cols, "row": rows,
        "endcolumn": cols, "endrow": rows,
        "image": "/static/img/back11.svg",
        "image_size": "95",
        "text_color": "#000000",
    })

    return {"background": "#383838", "buttons": buttons, "columns": cols, "rows": rows}


# functions.py  — add this helper at the bottom

def get_obs_manager() -> OBSManager:
    settings = current_app.get_settings("obs_studio")
    manager = OBSManager(
        host=current_app.local_ip,
        port=settings.get("server_port", 4455),
        password=settings.get("server_password", ""),
    )
    if not manager.connect():
        raise RuntimeError(
            "No se pudo conectar a OBS. Verificá que esté abierto, "
            "que el WebSocket server esté habilitado y que el puerto/contraseña sean correctos."
        )
    return manager


def generate_obs_sources_folder(scene_items: list[dict]) -> dict:
    cols = 4
    rows = max(1, (len(scene_items) + cols - 1) // cols)
    buttons = []

    for index, item in enumerate(scene_items):
        source_name = item.get("sourceName", "")
        is_enabled = item.get("sceneItemEnabled", True)

        col = (index % cols) + 1
        row = (index // cols) + 1

        # Verde si visible, gris si oculto
        bg_color = "#1a6b2e" if is_enabled else "#3a3a3a"
        text_color = "#ffffff"

        buttons.append({
            "background_color": bg_color,
            "column": col,
            "row": row,
            "endcolumn": col,
            "endrow": row,
            "command": f"/obs_toggle_source {source_name}",
            "image": "",
            "image_size": "0",
            "text_color": text_color,
            "btn_text": source_name,
        })

    # Botón volver
    buttons.append({
        "background_color": "#002396",
        "command": "$folder()",
        "column": cols,
        "row": rows + 1,
        "endcolumn": cols,
        "endrow": rows + 1,
        "image": "/static/img/back11.svg",
        "image_size": "95",
        "text_color": "#000000",
    })

    return {
        "background": "#383838",
        "buttons": buttons,
        "columns": cols,
        "rows": rows + 1,
    }