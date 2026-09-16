# stm32-imu-gnss-nav

Proyecto personal de aprendizaje de sistemas embebidos: integración de periféricos **GPS (GNSS)** e **IMU** sobre una **STM32 Nucleo-F446RE**, con el objetivo final de fusionar ambos sensores para una unidad de navegación básica.

> 🎯 **Objetivo del proyecto:** aprender a fondo comunicación serie (UART/I²C), manejo de interrupciones, parsing de protocolos (NMEA), y sentar las bases para fusión de sensores IMU+GNSS.

---

## 📌 Estado actual

- [x] IMU (ISM330DHCX) leyendo acelerómetro por I²C a 10 Hz
- [x] GPS (NEO-M8N) con fix estable, hasta 7 satélites
- [x] Recepción UART por interrupción con doble buffer (sin pérdida de tramas)
- [x] Parser NMEA propio (GGA + RMC) en C
- [x] Logging a CSV desde PC (Python + pyserial)
- [x] Visualización de la ruta en mapa interactivo (Python + folium)
- [ ] Fusión de sensores IMU + GPS
- [ ] Almacenamiento autónomo en SD
- [ ] Alimentación autónoma por batería
- [ ] Visualización 3D de la trayectoria
- [ ] Migración a PCB propia

---

## 🔧 Hardware

| Componente | Modelo | Interfaz |
|---|---|---|
| Microcontrolador | STM32 Nucleo-F446RE | — |
| IMU | ISM330DHCX (SparkFun breakout, Qwiic) | I²C, dirección `0x6B` |
| GPS/GNSS | u-blox NEO-M8N (breakout, antena activa 28dB) | UART, 9600 baudios, 8N1 |
| Antena | Activa, conector U.FL/IPEX | — |

### Conexionado GPS

| GPS | STM32 |
|---|---|
| TXD | PA10 (USART1_RX) |
| RXD | PA9 (USART1_TX) |
| VCC | 3V3 |
| GND | GND |

> ⚠️ Se usa **USART1**, no USART2, porque USART2 está reservado para el puerto COM virtual del ST-LINK (debug por `printf`).

---

## 🏗️ Arquitectura del firmware

### Recepción GPS

- Recepción por interrupción (`HAL_UART_Receive_IT`), 1 byte a la vez, para no bloquear el bucle principal.
- **Doble buffer (ping-pong)**: mientras se imprime/procesa una trama en un buffer, la interrupción escribe la siguiente en el otro. Se intercambian al completar cada línea (`\n`).
- Bandera `volatile uint8_t gps_line_ready` para sincronizar la interrupción con el bucle principal.

### Parser NMEA

- `trocear_gga()`: trocea cualquier trama NMEA por comas, respetando campos vacíos.
- `nmea_a_decimal()`: convierte formato NMEA (`ddmm.mmmmm`) a grados decimales.
- `parsear_gngga()`: extrae hora, lat, lon, altitud, nº satélites, HDOP y validez de fix.
- `parsear_gnrmc()`: extrae velocidad (convertida de nudos a km/h) y rumbo.
- Estructura `GPS_Fix_t gps_fix` centraliza los datos parseados.

Salida por consola de depuración (USART2 / ST-Link VCP):
```
POS[100336.00]: lat=37.385641 lon=-5.941889 alt=39.5m sat=6 hdop=4.36
MOV: vel=1.10 km/h rumbo=0.0 grados
```

---

## 🐛 Problemas encontrados y solucionados

### 1. Tramas NMEA mezclándose al imprimir por pantalla

**Problema:** con un único buffer compartido entre la interrupción de recepción y el bucle principal, no daba tiempo a terminar de imprimir una trama completa antes de que la interrupción empezara a sobrescribir el buffer con la siguiente. Resultado: ruido visual y tramas inutilizables para procesar (el final de una trama se mezclaba con el principio de la siguiente).

**Solución:** ✅ implementado un **doble buffer (ping-pong)** (`gps_buf_A` / `gps_buf_B`) con punteros `gps_fill` (donde escribe la interrupción) y `gps_display` (desde donde se lee/imprime), que se intercambian al completar cada línea. Así la interrupción nunca escribe sobre el buffer que se está leyendo.

### 2. Impresión duplicada de datos

**Problema:** el GPS envía ~9-10 tramas NMEA por segundo (GGA, RMC, VTG, GSA, GSV×3, GLL), pero solo interesan GGA y RMC. El bucle imprimía en cada trama recibida, no solo cuando había un dato nuevo real, generando líneas repetidas.

**Solución:** ✅ el `printf` ahora depende del valor de retorno de `parsear_gngga()` / `parsear_gnrmc()` (que devuelven `1` solo si la línea era del tipo esperado y se procesó), no de la bandera `gps_line_ready` a secas.

---

## 🛠️ Herramientas de análisis (Python)

### `tools/gps_logger.py`
Lee la salida serie del firmware (puerto COM virtual del ST-Link) durante un tiempo configurable y genera un CSV con `timestamp, lat, lon, alt, sat, hdop, vel_kmh, rumbo`.

```bash
pip install pyserial
python gps_logger.py
```

### `tools/gps_mapa.py`
Genera un mapa interactivo (HTML) a partir del CSV, con la ruta recorrida, marcadores coloreados según la calidad del fix (HDOP) y popups con los datos de cada punto.

```bash
pip install folium
python gps_mapa.py
```

---

## 🗺️ Roadmap

1. ~~Recepción GPS robusta (doble buffer, deduplicado)~~ ✅
2. ~~Logging a CSV desde el PC~~ ✅
3. ~~Visualización en mapa~~ ✅
4. **Integración del IMU — fusión de sensores** ← siguiente objetivo central
5. Autonomía: tarjeta SD para logging sin PC, alimentación por batería externa
6. Visualización 3D de la trayectoria (altitud, y más adelante orientación IMU)
7. Migración a PCB propia para resolver tamaño/espacio

---

## 📁 Estructura del repositorio

```
stm32-imu-gnss-nav/
├── firmware/           # Proyecto STM32CubeIDE
│   ├── Core/
│   │   ├── Src/
│   │   └── Inc/
│   └── ...
├── tools/               # Scripts Python de logging y visualización
│   ├── gps_logger.py
│   └── gps_mapa.py
├── docs/                # Capturas, mapas de ejemplo, notas
└── README.md
```

---

## 📄 Licencia

Proyecto personal de aprendizaje — libre uso educativo.
