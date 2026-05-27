# smart-home-tuya-iot
Smart home IoT system with NodeMCU ESP8266, DHT11, PIR and RCWL motion sensors, connected to Tuya IoT cloud platform.
# Smart Home IoT Automation System

A smart home monitoring and control system built with **NodeMCU ESP8266**, multiple sensors, and the **Tuya IoT cloud platform**. The system streams real-time sensor data to a mobile app and allows remote control of devices from anywhere.

Built as a Bachelor's thesis project at the University of Sarajevo, Faculty of Electrical Engineering.

---

## Features

- **Temperature & humidity monitoring** via DHT11 sensor
- **Dual motion detection** using two different sensor technologies (PIR infrared + microwave Doppler radar)
- **Remote LED control** via mobile app (representing a light switch)
- **Real-time updates** through Tuya cloud — works from any network, anywhere
- **Push notifications** on motion detection

---

## Hardware

| Component | Purpose |
|-----------|---------|
| NodeMCU ESP8266 | Main microcontroller with built-in WiFi |
| DHT11 | Temperature and humidity sensor |
| HC-SR501 PIR | Passive infrared motion sensor (detects humans/animals by heat) |
| RCWL-0516 | Microwave Doppler radar motion sensor (works through walls, unaffected by heat) |
| LED | Simulates a controllable light |

The two motion sensors complement each other: the PIR sensor is energy-efficient but affected by heat, while the RCWL-0516 uses radar and works in high-temperature environments where PIR can give false positives.

---

## System Architecture

```
[Sensors + NodeMCU]
       |
   Serial (UART)
       |
  [Python script] ── TuyaOS Link SDK ──► [Tuya Cloud]
                                               |
                                        [Tuya Smart App]
                                         (iOS / Android)
```

The Arduino firmware reads sensor data and sends it over serial to a Python script running on a host PC. The Python script connects to Tuya Cloud via the Link SDK and pushes data to the mobile app. LED control works in reverse — app → cloud → Python → serial → Arduino.

---

## Software

### Arduino (C/C++)
- Reads DHT11 temperature and humidity every 60 seconds
- Reads both motion sensors continuously and sends updates only on state change
- Receives LED on/off commands (`'H'` / `'L'`) over serial from Python

### Python
- Connects to Tuya IoT cloud using TuyaOS Link SDK
- Forwards sensor data to cloud (temperature, humidity, motion states)
- Receives LED commands from the mobile app and relays them to Arduino via serial

---

## Setup

### 1. Hardware wiring

| Sensor/Device | NodeMCU Pin |
|---------------|-------------|
| DHT11 data    | D4 (GPIO2)  |
| HC-SR501 OUT  | D0 (GPIO16) |
| RCWL-0516 OUT | D1 (GPIO5)  |
| LED (+)       | D7 (GPIO13) |

### 2. Arduino firmware

1. Open `arduino/main.ino` in Arduino IDE
2. Install ESP8266 board support: Tools → Board → Boards Manager → search `esp8266`
3. Select **NodeMCU 1.0** as the board
4. Upload to the board

### 3. Tuya IoT platform setup

1. Create a free account at [iot.tuya.com](https://iot.tuya.com)
2. Create a new product and define these data points (DPs):

| DP ID | Name        | Type   | Direction      |
|-------|-------------|--------|----------------|
| 101   | LED control | Bool   | Send & Report  |
| 102   | Temperature | Value  | Report only    |
| 103   | Humidity    | Value  | Report only    |
| 104   | PIR motion  | String | Report only    |
| 105   | RCWL motion | String | Report only    |

3. Choose **LinkSDK** as the connection method and download your credentials (productid, uuid, authkey)

### 4. Python script

```bash
pip install tuyalinksdk pyserial coloredlogs
```

Edit `python/tuya_client.py` and replace the placeholders:
```python
client = TuyaClient(
    productid = 'YOUR_PRODUCT_ID',
    uuid      = 'YOUR_UUID',
    authkey   = 'YOUR_AUTH_KEY'
)
```

Also set your serial port:
```python
ser = serial.Serial('COM4', 115200)  # Windows
# ser = serial.Serial('/dev/ttyUSB0', 115200)  # Linux
```

Run:
```bash
python python/tuya_client.py
```

5. Scan the QR code printed in the terminal using the **Tuya Smart** mobile app (available on iOS and Android)

---

## Mobile App

After scanning the QR code, the device appears in the Tuya Smart app. From the app you can:
- See live temperature and humidity
- See motion detection status from both sensors
- Turn the LED on/off remotely

The mobile app can be used from any network and any location. The NodeMCU and the host PC running the Python script must remain powered on and connected to their local WiFi network.

---

## Tech Stack

- **C/C++** (Arduino IDE) — embedded firmware
- **Python** — cloud bridge script
- **Tuya IoT Platform** — cloud connectivity and mobile app
- **ESP8266 / NodeMCU** — WiFi microcontroller

---

## Notes

- Free Tuya account includes 6 license slots (2 per device)
- The DHT11 measures temperature (0–50 °C) and humidity (20–90% RH)
- PIR detection range: 3–7 m (adjustable via potentiometer)
- RCWL-0516 detection range: up to 7 m
