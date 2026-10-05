import socket
import struct
import requests
import time

UDP_IP = "0.0.0.0"
UDP_PORT = 20777
CLOUD_SERVER_URL = "http://localhost:8000/api/telemetry/submit" # Change this to your Render/Railway URL

print(f"F1 24 UDP Client starting on port {UDP_PORT}...")
print(f"Will forward telemetry to: {CLOUD_SERVER_URL}")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

# Mock state for demonstration (in a real scenario, full packet decoding is required)
current_driver_id = 1 # e.g. Charles Leclerc
current_session_id = 1

while True:
    data, addr = sock.recvfrom(2048)
    if len(data) >= 29:
        try:
            packet_format = '<HBBBBQfI2B'
            header_data = struct.unpack_from(packet_format, data, 0)
            packet_id = header_data[4]
            
            # Simple simulation: trigger a lap send every 60 seconds (or parse real lap packet)
            # For this MVP client, we just listen to prove the pipe works.
            
            # Simulated telemetry payload
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
            
            # requests.post(CLOUD_SERVER_URL, json=payload)
            # time.sleep(10) # Prevent spamming
            
        except Exception as e:
            pass
