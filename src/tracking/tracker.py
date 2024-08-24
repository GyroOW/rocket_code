import serial
import time
import webbrowser
from typing import Optional, Dict

class GPSTracker:
    def __init__(self, port: str = '/dev/ttyS0', baudrate: int = 9600) -> None:
        self.port = port
        self.baudrate = baudrate
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
        except Exception as e:
            print(f"Error opening serial port {self.port}: {e}")
            raise e
        self.last_known_position: Dict[str, Optional[float]] = {"latitude": None, "longitude": None}

    def parse_gps_data(self, data: str) -> None:
        if data.startswith('$GPRMC'):
            parts = data.split(',')
            if len(parts) > 5:
                latitude = float(parts[3][:2]) + float(parts[3][2:])/60
                if parts[4] == 'S':
                    latitude = -latitude
                longitude = float(parts[5][:3]) + float(parts[5][3:])/60
                if parts[6] == 'W':
                    longitude = -longitude
                self.last_known_position = {"latitude": latitude, "longitude": longitude}

    def get_location(self) -> Dict[str, Optional[float]]:
        return self.last_known_position

    def generate_google_maps_url(self) -> Optional[str]:
        lat = self.last_known_position["latitude"]
        lon = self.last_known_position["longitude"]
        if lat is not None and lon is not None:
            return f"https://www.google.com/maps?q={lat},{lon}"
        return None

    def open_google_maps(self) -> None:
        url = self.generate_google_maps_url()
        if url:
            webbrowser.open(url)
        else:
            print("No location data available to open in Google Maps.")

    def read_gps(self) -> None:
        while True:
            line = self.ser.readline().decode('ascii', errors='replace')
            self.parse_gps_data(line)
            time.sleep(1)

    def stop(self) -> None:
        self.ser.close()

if __name__ == "__main__":
    gps_tracker = GPSTracker()
    try:
        print("GPS Tracker started. Press Ctrl+C to stop.")
        while True:
            location = gps_tracker.get_location()
            print(f"Current Location: Latitude: {location['latitude']}, Longitude: {location['longitude']}")
            gps_tracker.open_google_maps()
            time.sleep(30)
    except KeyboardInterrupt:
        print("GPS Tracker stopped.")
    finally:
        gps_tracker.stop()
