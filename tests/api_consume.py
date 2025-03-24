import requests

url = "https://servicios.siur.com.co/mapas/marks2.php?ruta=A17D"
response = requests.get(url)

# Comprobar el código de estado
if response.status_code == 200:
    # Convertir la respuesta JSON en un diccionario de Python
    data = response.json()

    for bus in data:

        if bus["TASKID"] != '16': # Si el Bus ( No esta en el taller ) 
            print(bus)

    # print(data)
else:
    print(f"Error: {response.status_code}")