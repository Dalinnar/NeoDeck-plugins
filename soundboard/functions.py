from flask import request, jsonify
import pygame
import os
import base64

pygame.mixer.init()
active_sounds = {}




# FUNCTION 1
def playsound(message: str):
    parts = message.replace("/soundboard_playsound", "").strip()
    path = parts.split(']')[0].replace('[', '').strip()
    
    repeat_str = parts.split(']')[1].strip() if ']' in parts else ""
    repeat = repeat_str.lower() == "true"

    # Cargar y reproducir sin detener sonidos existentes
    sound = pygame.mixer.Sound(path)
    loops = -1 if repeat else 0
    channel = sound.play(loops=loops)
    
    # Guardar el canal activo solo si quieres hacer algo con él luego
    active_sounds[path] = channel

def generate_sounds_folder(path):
    """
    Genera un diccionario con la estructura de botones para un grid de sonidos,
    asignando imagenes si existen archivos con el mismo nombre que el mp3.
    """
    # Listar archivos de sonido
    sound_files = [f for f in os.listdir(path) if f.lower().endswith(('.mp3', '.wav', '.ogg'))]
    sound_files.sort()  # opcional: ordenar alfabéticamente

    # Dimensiones del grid
    def grid_dim(n):
        cols = 4  # número de columnas del grid
        rows = (n + cols - 1) // cols
        return cols, rows

    cols, rows = grid_dim(len(sound_files) + 1)

    buttons = []
    base_color = "#1e1e1e"  # color base de los botones

    # Extensiones válidas de imágenes
    image_exts = ('.png', '.jpg', '.jpeg', '.gif', '.webp')

    for index, filename in enumerate(sound_files):
        col = (index % cols) + 1
        row = (index // cols) + 1

        name_without_ext = os.path.splitext(filename)[0]

        # Buscar imagen con el mismo nombre
        image_file = ""
        for ext in image_exts:
            potential_image = os.path.join(path, name_without_ext + ext)
            if os.path.isfile(potential_image):
                # Abrir el archivo y convertirlo a base64
                with open(potential_image, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode()
                # Asignar la imagen como data URI
                image_file = f"data:image/{ext[1:]};base64,{encoded}"
                break

        buttons.append({
            "command": f"/soundboard_playsound [{os.path.join(path, filename)}] false",
            "column": col,
            "row": row,
            "endcolumn": col,
            "endrow": row,
            "background_color": base_color,
            "text_color": "#000000",
            "btn_text": name_without_ext,
            "toggleable": False,
            "image": image_file,       # imagen opcional
            "image_size": "80"
        })

    # Botón "volver"
    buttons.append({
        "background_color": base_color,
        "command": "$folder()",
        "column": cols,
        "row": rows,
        "endcolumn": cols,
        "endrow": rows,
        "image": "/static/img/back11.svg",
        "image_size": "95",
        "text_color": "#000000",
        "toggleable": False
    })

    return {
        "background": "#383838",
        "buttons": buttons,
        "columns": cols,
        "rows": rows
    }