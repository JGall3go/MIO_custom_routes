import folium

# Coordenadas del punto (Latitud, Longitud)
coordenadas = [3.3442322,-76.5174211]  # Madrid, España

# Crear el mapa centrado en las coordenadas
mapa = folium.Map(location=coordenadas, zoom_start=13)

# Añadir un marcador en las coordenadas
folium.Marker(
    location=coordenadas,
    popup="Aquí está Madrid",  # Texto que aparece al hacer clic en el marcador
    icon=folium.Icon(color="blue", icon="info-sign"),  # Personaliza el marcador
).add_to(mapa)

# Guardar el mapa en un archivo HTML (opcional)
mapa.save("mapa_con_marcador.html")