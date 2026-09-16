"""
Logger GPS -> CSV para el proyecto Unidad de Navegación IMU + GNSS
-------------------------------------------------------------------
Lee la salida serie (printf) de la STM32 Nucleo-F446RE por el puerto COM
virtual del ST-Link (USART2, debug) y guarda un CSV con las posiciones
y velocidades durante un tiempo fijo.

Formato esperado en la salida serie del firmware:
    POS[hh:mm:ss.ss]: lat=xx.xxxxxx lon=xx.xxxxxx alt=xxx.x sat=x hdop=x.x
    MOV: vel=xx.x rumbo=xxx.x

Si tu printf usa otros nombres de campo o separadores, ajusta las
expresiones regulares POS_RE y MOV_RE más abajo.
"""

import serial
import csv
import re
import time
from datetime import datetime

# ---------------- CONFIGURACIÓN (ajusta según tu equipo) ----------------
SERIAL_PORT = "COM9"        # tu puerto COM (Administrador de dispositivos > Puertos COM y LPT)
BAUDRATE = 115200           # baudrate configurado para el printf por USART2 (ST-Link VCP)
DURATION_SECONDS = 120      # duración del logging en segundos
OUTPUT_CSV = "gps_log.csv"  # nombre del archivo de salida
# --------------------------------------------------------------------------

POS_RE = re.compile(
    r"POS\[(?P<hora>[\d.]+)\]:\s*lat=(?P<lat>-?[\d.]+)\s*lon=(?P<lon>-?[\d.]+)\s*"
    r"alt=(?P<alt>-?[\d.]+)m\s*sat=(?P<sat>\d+)\s*hdop=(?P<hdop>[\d.]+)"
)
MOV_RE = re.compile(
    r"MOV:\s*vel=(?P<vel>[\d.]+)\s*km/h\s*rumbo=(?P<rumbo>[\d.]+)\s*grados"
)


def main():
    print(f"Abriendo puerto {SERIAL_PORT} a {BAUDRATE} baudios...")
    try:
        ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
    except serial.SerialException as e:
        print(f"ERROR: no se pudo abrir el puerto serie: {e}")
        print("Revisa que el puerto sea correcto y que ningún otro programa "
              "(STM32CubeIDE, Tera Term, PuTTY...) lo tenga abierto a la vez.")
        return

    # Guardamos la última vel/rumbo conocidos para combinarlos con cada POS,
    # ya que llegan en líneas separadas.
    last_vel = ""
    last_rumbo = ""

    rows_written = 0
    start_time = time.time()

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["timestamp_pc", "hora_gps", "lat", "lon", "alt", "sat", "hdop", "vel_kmh", "rumbo"]
        )

        print(f"Grabando durante {DURATION_SECONDS} segundos. Pulsa Ctrl+C para parar antes de tiempo.")

        try:
            while time.time() - start_time < DURATION_SECONDS:
                raw = ser.readline()
                line = raw.decode(errors="ignore").strip()
                if not line:
                    continue

                mov_match = MOV_RE.search(line)
                if mov_match:
                    last_vel = mov_match.group("vel")
                    last_rumbo = mov_match.group("rumbo")
                    continue

                pos_match = POS_RE.search(line)
                if pos_match:
                    timestamp_pc = datetime.now().isoformat(timespec="seconds")
                    writer.writerow([
                        timestamp_pc,
                        pos_match.group("hora"),
                        pos_match.group("lat"),
                        pos_match.group("lon"),
                        pos_match.group("alt"),
                        pos_match.group("sat"),
                        pos_match.group("hdop"),
                        last_vel,
                        last_rumbo,
                    ])
                    f.flush()  # para no perder datos si el script se interrumpe
                    rows_written += 1
                    print(
                        f"[{rows_written}] {timestamp_pc}  "
                        f"lat={pos_match.group('lat')}  lon={pos_match.group('lon')}  "
                        f"sat={pos_match.group('sat')}"
                    )

        except KeyboardInterrupt:
            print("\nDetenido manualmente por el usuario.")

    ser.close()
    elapsed = time.time() - start_time
    print(f"\nListo. {rows_written} posiciones guardadas en '{OUTPUT_CSV}' "
          f"({elapsed:.0f} s de grabación).")


if __name__ == "__main__":
    main()