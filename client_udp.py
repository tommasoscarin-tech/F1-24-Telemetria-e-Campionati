import socket
import struct
import requests
import time

UDP_IP = "0.0.0.0"
UDP_PORT = 20777
CLOUD_SERVER_URL = "https://f1-24-telemetria.onrender.com/api/telemetry/submit"

print(f"F1 24 UDP Client avviato sulla porta {UDP_PORT}...")
print(f"Inoltro telemetria verso: {CLOUD_SERVER_URL}\n")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

current_driver_id = 1
current_session_id = 1
last_send_time = 0

while True:
    data, addr = sock.recvfrom(2048)
    if len(data) >= 29:
        try:
            packet_format = '<HBBBBQfI2B'
            header_data = struct.unpack_from(packet_format, data, 0)
            packet_id = header_data[4]
            
            # Limita l'invio a massimo 1 pacchetto ogni 5 secondi per non sovraccaricare il server
            current_time = time.time()
            if current_time - last_send_time >= 5:
                payload = {
                    "session_id": current_session_id,
                    "driver_id": current_driver_id,
                    "lap_number": 1,
                    "lap_time_ms": 91000,
                    "sector1_ms": 30000,
                    "sector2_ms": 35000,
                    "sector3_ms": 26000,
                    "is_valid": True,
                    "session_type_str": "Race",
                    "tyre_compound": "Soft",
                    "tyre_wear_pct": 5.5,
                    "front_left_damage": 0.0,
                    "front_right_damage": 0.0,
                    "rear_wing_damage": 0.0,
                    "weather": "Clear",
                    "track_temperature_c": 32.5
                }
                
                # Invio effettivo al server in cloud
                response = requests.post(CLOUD_SERVER_URL, json=payload, timeout=5)
                print(f"[+] Dati inviati al Cloud! Risposta Server: {response.status_code}")
                last_send_time = current_time
            
        except Exception as e:
            print(f"[-] Errore invio: {e}")
