from flask import Flask, jsonify, request, render_template
import requests

import schedule
import time
import threading
import json
from datetime import datetime
import pytz
import math
import os

app = Flask(__name__)


def calculate_bearing(lat1, lon1, lat2, lon2):
    """
    Calcula el rumbo (bearing) entre dos puntos geográficos.

    Parámetros:
    lat1, lon1 -- Latitud y longitud del primer punto (en grados)
    lat2, lon2 -- Latitud y longitud del segundo punto (en grados)

    Retorna:
    Bearing en grados (0° = Norte, 90° = Este, 180° = Sur, 270° = Oeste)
    """
    # Convertir grados a radianes
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Calcular la diferencia de longitudes
    delta_lon = lon2 - lon1

    # Calcular ángulo de rumbo
    x = math.sin(delta_lon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(delta_lon)
    
    bearing = math.atan2(x, y)

    # Convertir de radianes a grados y normalizar a 0-360°
    return (math.degrees(bearing) + 360) % 360


def consume_mio_api():

    zona = pytz.timezone("America/Bogota")  # Cambia según tu zona horaria
    ahora_bogota = datetime.now(zona)

    print("Obteniendo información... - " + ahora_bogota.strftime("%Y-%m-%d %H:%M:%S %Z"))

    # Archivos requeridos
    # Construye la ruta absoluta basada en la ubicación de este script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "database", "current_buses.json")
    current_buses_file = file_path

    url = f"https://servicios.siur.com.co/mapas/marks2.php?ruta=A17D"
    response = requests.get(url)

    if response.status_code == 200:

        response_data = response.json()

        # Obtener los buses activos en la API
        buses_activos = [bus["BUSNUMBER"] for bus in response_data]

        with open(current_buses_file, "r", encoding="utf-8") as content:
            current_data = json.load(content)  # Cargar lista existente

        # Identificar y eliminar buses que no están en la API
        buses_a_eliminar = [bus for bus in current_data if bus not in buses_activos]
        print("Buses activos: ", buses_activos)
        print("Buses a eliminar: ", buses_a_eliminar)

        for bus in buses_a_eliminar:
            del current_data[bus]

        # Escribir la lista actualizada en el archivo
        with open(current_buses_file, "w", encoding="utf-8") as archivo:
            json.dump(current_data, archivo, indent=4, ensure_ascii=False)

        for current_bus in response_data:

            # Obtenemos la información organizada
            bus_number = current_bus["BUSNUMBER"]
            bus_delay = current_bus["DELAY"]
            bus_x = int(current_bus["GPSX"]) / 10000000
            bus_y = int(current_bus["GPSY"]) / 10000000
            bus_stop = current_bus["PARADA"]
            bus_name = current_bus["RUTA"]
            bus_route = current_bus["RUTERO"]
            bus_stop_id = current_bus["STOPID"]
            bus_task_id = current_bus["TASKID"]
            bus_telegram_date = current_bus["TELEGRAMDATE"]
            bus_trip_id = current_bus["TRIPID"]

            # Leer el archivo JSON y cargar los datos existentes
            try:
                with open(current_buses_file, "r", encoding="utf-8") as content:
                    current_data = json.load(content)  # Cargar lista existente
            except (FileNotFoundError, json.JSONDecodeError):
                current_data = {} # Si el archivo no existe o está vacío, crear una nueva lista

            if bus_number in current_data:
                
                # Verifica si la lista tiene elementos antes de acceder al último
                if not current_data[bus_number]["POSICIONES"] or current_data[bus_number]["POSICIONES"][-1] != [bus_y, bus_x]:
                    current_data[bus_number]["POSICIONES"].append([bus_y, bus_x])

                try:
                    penultimo = current_data[bus_number]["POSICIONES"][-2]
                    ultimo = current_data[bus_number]["POSICIONES"][-1]

                    current_data[bus_number]["DIRECTION"] = calculate_bearing(penultimo[0], penultimo[1], ultimo[0], ultimo[1])
                except:
                    current_data[bus_number]["DIRECTION"] = None

            else:

                # Definición de estructura del nuevo elemento
                current_data[bus_number] = {
                    "DELAY": bus_delay,
                    "GPSX": bus_x,
                    "GPSY": bus_y,
                    "PARADA": bus_stop,
                    "RUTA": bus_name,
                    "RUTERO": bus_route,
                    "STOPID": bus_stop_id,
                    "TASKID": bus_task_id,
                    "TELEGRAMDATE": bus_telegram_date,
                    "TRIPID": bus_trip_id,
                    "DIRECTION": None,
                    "POSICIONES": [[bus_y, bus_x]]
                }

            # Escribir la lista actualizada en el archivo
            with open(current_buses_file, "w", encoding="utf-8") as archivo:
                json.dump(current_data, archivo, indent=4, ensure_ascii=False)
    
    else:
        return jsonify({"error": "No se encontró el post"}), response.status_code

# Programar la función solo una vez
def schedule_task():
    schedule.every(40).seconds.do(consume_mio_api)

def run_scheduler():
    """Función para ejecutar el scheduler en un hilo separado."""
    while True:
        schedule.run_pending()
        time.sleep(1)

# Landing Route
@app.route('/')
def mapa_version_1():
    return render_template('mapa_con_marcador.html')

# API Routesa
@app.route('/api/get_data', methods=['GET'])
def api_get_data():

    # Construye la ruta absoluta basada en la ubicación de este script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "database", "current_buses.json")
    
    with open(file_path, "r", encoding="utf-8") as content:
        current_data = json.load(content)  # Cargar lista existente

    return jsonify(current_data)

if __name__ == '__main__':

    schedule_task()
    threading.Thread(target=run_scheduler, daemon=True).start()

    app.run(debug=True)