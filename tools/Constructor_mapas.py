"""
Visualizador GPS -> Mapa HTML interactivo
-------------------------------------------
Lee el CSV generado por gps_logger.py y crea un mapa interactivo (HTML)
con la ruta recorrida, un marcador por cada punto y colores según la
calidad del fix (HDOP).

Requiere: pip install folium
"""

import csv
import folium

# ---------------- CONFIGURACIÓN ----------------
INPUT_CSV = "gps_log.csv"     # el CSV generado por gps_logger.py
OUTPUT_HTML = "gps_mapa.html"  # el mapa que se abrirá en el navegador
# -------------------------------------------------


def color_por_hdop(hdop):
    """Verde = buena precisión, amarillo = media, rojo = mala."""
    if hdop < 2.0:
        return "green"
    elif hdop < 5.0:
        return "orange"
    else:
        return "red"


def main():
    puntos = []

    with open(INPUT_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                lat = float(row["lat"])
                lon = float(row["lon"])
            except (ValueError, KeyError):
                continue  # fila mal formada o vacía, la saltamos
            puntos.append(row | {"lat": lat, "lon": lon})

    if not puntos:
        print(f"ERROR: no se encontraron puntos válidos en '{INPUT_CSV}'.")
        print("Revisa que el archivo exista y tenga columnas lat/lon rellenas.")
        return

    # Centramos el mapa en el primer punto registrado
    centro = [puntos[0]["lat"], puntos[0]["lon"]]
    mapa = folium.Map(location=centro, zoom_start=18, tiles="Esri.WorldStreetMap")

    # Línea que une todos los puntos (la ruta recorrida)
    ruta = [[p["lat"], p["lon"]] for p in puntos]
    folium.PolyLine(ruta, color="blue", weight=3, opacity=0.7).add_to(mapa)

    # Un marcador por cada punto, con popup con los datos y color según HDOP
    for p in puntos:
        hdop = float(p.get("hdop", 99))
        popup_html = (
            f"<b>Hora GPS:</b> {p.get('hora_gps', '?')}<br>"
            f"<b>Lat/Lon:</b> {p['lat']:.6f}, {p['lon']:.6f}<br>"
            f"<b>Alt:</b> {p.get('alt', '?')} m<br>"
            f"<b>Satélites:</b> {p.get('sat', '?')}<br>"
            f"<b>HDOP:</b> {hdop}<br>"
            f"<b>Vel:</b> {p.get('vel_kmh', '?')} km/h<br>"
            f"<b>Rumbo:</b> {p.get('rumbo', '?')}°"
        )
        folium.CircleMarker(
            location=[p["lat"], p["lon"]],
            radius=4,
            color=color_por_hdop(hdop),
            fill=True,
            fill_opacity=0.8,
            popup=folium.Popup(popup_html, max_width=250),
        ).add_to(mapa)

    # Marcadores destacados de inicio y fin
    folium.Marker(
        [puntos[0]["lat"], puntos[0]["lon"]],
        popup="Inicio",
        icon=folium.Icon(color="green", icon="play"),
    ).add_to(mapa)
    folium.Marker(
        [puntos[-1]["lat"], puntos[-1]["lon"]],
        popup="Fin",
        icon=folium.Icon(color="red", icon="stop"),
    ).add_to(mapa)

    mapa.save(OUTPUT_HTML)
    print(f"Mapa generado con {len(puntos)} puntos: '{OUTPUT_HTML}'")
    print("Ábrelo haciendo doble clic, se abrirá en tu navegador por defecto.")


if __name__ == "__main__":
    main()