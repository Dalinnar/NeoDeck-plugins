import json
import time
import threading
import os
from pynput import keyboard, mouse
import pyautogui
from win10toast import ToastNotifier

# ==============================
#   CONFIG
# ==============================
print("[DEBUG] CURRENT WORKING DIR:", os.getcwd())
MACRO_FOLDER = "macros"
#os.makedirs(MACRO_FOLDER, exist_ok=True)

print(f"[INFO] Macros folder: {os.path.abspath(MACRO_FOLDER)}")

toaster = ToastNotifier()

# PyAutoGUI settings
pyautogui.PAUSE = 0  # Remove default pause between actions
pyautogui.FAILSAFE = True  # Move mouse to corner to abort

recording = False
events = []
start_time = None

keyboard_listener = None
mouse_listener = None
lock = threading.Lock()

current_macro_file = None


# ==============================
#   NOTIFICACIONES
# ==============================
def notify(msg):
    try:
        toaster.show_toast("Auto Macro", msg, duration=3, threaded=True)
    except:
        print("[NOTIF]", msg)


# ==============================
#   INICIAR GRABACIÓN
# ==============================
def start_recording(macro_file):
    global recording, events, start_time, keyboard_listener, mouse_listener, current_macro_file

    with lock:
        if recording:
            return

        recording = True
        events = []
        start_time = time.time()
        current_macro_file = macro_file

    notify(f"Recording macro: {macro_file}")

    keyboard_listener = keyboard.Listener(on_press=on_key_press, on_release=on_key_release)
    mouse_listener = mouse.Listener(on_click=on_click, on_move=on_move, on_scroll=on_scroll)

    keyboard_listener.start()
    mouse_listener.start()


# ==============================
#   DETENER GRABACIÓN
# ==============================
def stop_recording():
    global recording, keyboard_listener, mouse_listener, current_macro_file

    with lock:
        if not recording:
            return None

        recording = False

    if keyboard_listener: 
        keyboard_listener.stop()
    if mouse_listener: 
        mouse_listener.stop()

    full_path = save_macro(current_macro_file)
    notify(f"Macro saved:\n{full_path}")
    
    print(f"[INFO] Macro saved at: {full_path}")
    
    current_macro_file = None
    return full_path


# ==============================
#   GUARDAR MACRO
# ==============================
def save_macro(macro_file):
    print("[DEBUG] save_macro CALLED with:", macro_file)
    path = os.path.join(MACRO_FOLDER, macro_file)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=4)
    print(f"[INFO] Saved macro: {path}")
    print("[DEBUG] events length:", len(events))
    return path


# ==============================
#   EVENTOS DE TECLADO
# ==============================
def on_key_press(key):
    if recording:
        key_data = {
            "type": "key_press",
            "time": time.time() - start_time
        }
        
        # Handle special keys vs regular keys
        if hasattr(key, 'char') and key.char is not None:
            key_data["key"] = key.char
            key_data["key_type"] = "char"
        else:
            key_data["key"] = str(key)
            key_data["key_type"] = "special"
        
        events.append(key_data)


def on_key_release(key):
    if recording:
        key_data = {
            "type": "key_release",
            "time": time.time() - start_time
        }
        
        if hasattr(key, 'char') and key.char is not None:
            key_data["key"] = key.char
            key_data["key_type"] = "char"
        else:
            key_data["key"] = str(key)
            key_data["key_type"] = "special"
        
        events.append(key_data)


# ==============================
#   EVENTOS DE MOUSE
# ==============================
def on_click(x, y, button, pressed):
    if recording:
        events.append({
            "type": "mouse_click",
            "x": x, "y": y,
            "button": str(button),
            "pressed": pressed,
            "time": time.time() - start_time
        })


def on_move(x, y):
    if recording:
        events.append({
            "type": "mouse_move",
            "x": x, "y": y,
            "time": time.time() - start_time
        })


def on_scroll(x, y, dx, dy):
    if recording:
        events.append({
            "type": "mouse_scroll",
            "x": x, "y": y, "dx": dx, "dy": dy,
            "time": time.time() - start_time
        })


# ==============================
#   CONVERTIR TECLAS PARA PYAUTOGUI
# ==============================
def convert_key_to_pyautogui(key_str, key_type=None):
    """
    Convert pynput key format to PyAutoGUI key format
    """
    # Mapping from pynput special keys to PyAutoGUI keys
    key_mapping = {
        "Key.space": "space",
        "Key.enter": "enter",
        "Key.tab": "tab",
        "Key.backspace": "backspace",
        "Key.delete": "delete",
        "Key.esc": "esc",
        "Key.up": "up",
        "Key.down": "down",
        "Key.left": "left",
        "Key.right": "right",
        "Key.home": "home",
        "Key.end": "end",
        "Key.page_up": "pageup",
        "Key.page_down": "pagedown",
        "Key.insert": "insert",
        "Key.shift": "shift",
        "Key.shift_l": "shiftleft",
        "Key.shift_r": "shiftright",
        "Key.ctrl": "ctrl",
        "Key.ctrl_l": "ctrlleft",
        "Key.ctrl_r": "ctrlright",
        "Key.alt": "alt",
        "Key.alt_l": "altleft",
        "Key.alt_r": "altright",
        "Key.cmd": "win",
        "Key.cmd_l": "winleft",
        "Key.cmd_r": "winright",
        "Key.caps_lock": "capslock",
        "Key.num_lock": "numlock",
        "Key.scroll_lock": "scrolllock",
        "Key.f1": "f1", "Key.f2": "f2", "Key.f3": "f3", "Key.f4": "f4",
        "Key.f5": "f5", "Key.f6": "f6", "Key.f7": "f7", "Key.f8": "f8",
        "Key.f9": "f9", "Key.f10": "f10", "Key.f11": "f11", "Key.f12": "f12",
    }
    
    # If it's a regular character, return as-is
    if key_type == "char":
        return key_str
    
    # If it's a special key, convert it
    if key_str in key_mapping:
        return key_mapping[key_str]
    
    # Handle character keys with quotes
    if key_str.startswith("'") and key_str.endswith("'"):
        return key_str.strip("'")
    
    # Default: return as-is and hope for the best
    return key_str


def parse_button(btn_str):
    """Convert pynput button to PyAutoGUI button"""
    button_mapping = {
        "Button.left": "left",
        "Button.right": "right",
        "Button.middle": "middle",
    }
    return button_mapping.get(btn_str, "left")


# ==============================
#   DETECTAR Y EJECUTAR COMBOS
# ==============================
def detect_and_execute_combos(events_slice):
    """
    Detect key combinations (like Ctrl+L) and execute them as hotkeys
    Returns True if a combo was detected and executed, False otherwise
    """
    if len(events_slice) < 4:
        return False, 0
    
    # Pattern: modifier_press -> key_press -> key_release -> modifier_release
    modifiers = ["Key.ctrl", "Key.ctrl_l", "Key.ctrl_r", 
                 "Key.shift", "Key.shift_l", "Key.shift_r",
                 "Key.alt", "Key.alt_l", "Key.alt_r"]
    
    if (events_slice[0]["type"] == "key_press" and 
        events_slice[0]["key"] in modifiers and
        events_slice[1]["type"] == "key_press" and
        events_slice[1]["key"] not in modifiers):
        
        # Found a potential combo
        modifier = convert_key_to_pyautogui(events_slice[0]["key"], events_slice[0].get("key_type"))
        regular_key = convert_key_to_pyautogui(events_slice[1]["key"], events_slice[1].get("key_type"))
        
        # Simplify modifier names for hotkey
        if modifier.startswith("ctrl"):
            modifier = "ctrl"
        elif modifier.startswith("shift"):
            modifier = "shift"
        elif modifier.startswith("alt"):
            modifier = "alt"
        
        try:
            print(f"[INFO] Executing hotkey: {modifier}+{regular_key}")
            pyautogui.hotkey(modifier, regular_key)
            return True, 4  # Skip the next 4 events (modifier press, key press, key release, modifier release)
        except Exception as e:
            print(f"[ERROR] Failed to execute hotkey {modifier}+{regular_key}: {e}")
            return False, 0
    
    return False, 0


# ==============================
#   EJECUTAR MACRO
# ==============================
def execute_macro(message):
    message = message.split(" ", 1)[1]
    global recording

    macro_file = f"{message}.json"
    path = os.path.join(MACRO_FOLDER, macro_file)

    # Si estamos grabando → detener
    if recording:
        saved_path = stop_recording()
        if saved_path:
            return f"Stopped recording and saved macro '{message}' at: {saved_path}"
        return f"Stopped recording macro '{message}'."

    # Si NO existe → iniciar grabación
    if not os.path.exists(path):
        start_recording(macro_file)
        return f"Macro '{message}' does not exist. Started recording it. Call again to stop recording."

    # Si existe → ejecutar
    notify(f"Executing macro: {message}")

    with open(path, "r", encoding="utf-8") as f:
        macro = json.load(f)

    start = time.time()
    i = 0
    
    # Track pressed keys to avoid duplicate presses
    pressed_keys = set()

    while i < len(macro):
        event = macro[i]
        
        # Calculate and apply delay
        delay = event["time"] - (time.time() - start)
        if delay > 0:
            time.sleep(delay)

        # Try to detect key combinations
        combo_detected, skip_count = detect_and_execute_combos(macro[i:])
        if combo_detected:
            i += skip_count
            continue

        # Handle individual events
        if event["type"] == "key_press":
            key_type = event.get("key_type", "special")
            key = convert_key_to_pyautogui(event["key"], key_type)
            
            # Avoid duplicate presses
            if key not in pressed_keys:
                try:
                    pyautogui.keyDown(key)
                    pressed_keys.add(key)
                except Exception as e:
                    print(f"[ERROR] Failed to press key {event['key']}: {e}")

        elif event["type"] == "key_release":
            key_type = event.get("key_type", "special")
            key = convert_key_to_pyautogui(event["key"], key_type)
            
            if key in pressed_keys:
                try:
                    pyautogui.keyUp(key)
                    pressed_keys.remove(key)
                except Exception as e:
                    print(f"[ERROR] Failed to release key {event['key']}: {e}")

        elif event["type"] == "mouse_move":
            try:
                pyautogui.moveTo(event["x"], event["y"], duration=0)
            except Exception as e:
                print(f"[ERROR] Failed to move mouse: {e}")

        elif event["type"] == "mouse_click":
            button = parse_button(event["button"])
            try:
                if event["pressed"]:
                    pyautogui.mouseDown(x=event["x"], y=event["y"], button=button)
                else:
                    pyautogui.mouseUp(x=event["x"], y=event["y"], button=button)
            except Exception as e:
                print(f"[ERROR] Failed to click: {e}")

        elif event["type"] == "mouse_scroll":
            try:
                # PyAutoGUI scroll: positive = up, negative = down
                # dy from pynput: positive = up, negative = down (same)
                pyautogui.scroll(int(event["dy"] * 120))  # Multiply for better scrolling
            except Exception as e:
                print(f"[ERROR] Failed to scroll: {e}")

        i += 1

    # Release any keys that are still pressed
    for key in list(pressed_keys):
        try:
            pyautogui.keyUp(key)
        except:
            pass

    notify(f"Macro finished: {message}")
    return f"Macro '{message}' executed successfully."


# ==============================
#   RECORD MACRO (COMANDO)
# ==============================
def record_macro(message):
    message = message.split(" ", 1)[1]
    global recording

    macro_file = f"{message}.json"

    # Si está grabando → detener
    if recording:
        saved_path = stop_recording()
        if saved_path:
            return f"Stopped recording macro '{message}' at: {saved_path}"
        return f"Stopped recording macro '{message}'."

    # Comenzar grabación
    start_recording(macro_file)
    return f"Recording macro '{message}'... Call again to stop."