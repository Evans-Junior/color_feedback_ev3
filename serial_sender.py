# serial_sender.py

import serial
import time

# Customize based on your OS and device
SERIAL_PORT ='COM3' # for a mac or linux '/dev/ttyUSB0'  # Example for Linux. Use 'COM3' for Windows.
BAUD_RATE = 115200

class SerialSender:
    def __init__(self, port=SERIAL_PORT, baudrate=BAUD_RATE):
        try:
            self.serial_conn = serial.Serial(port, baudrate, timeout=2)
            time.sleep(2)  # Wait for connection to initialize
            print(f"Serial connection opened on {port} at {baudrate} baud.")
        except serial.SerialException as e:
            print(f"Serial connection failed: {e}")
            self.serial_conn = None

    def send_color(self, color_code: str):
        if self.serial_conn and self.serial_conn.is_open:
            message = color_code + '\n'
            try:
                self.serial_conn.write(message.encode())
                print(f"Sent color '{color_code}' over serial.")
            except Exception as e:
                print(f"Failed to write to serial: {e}")
        else:
            print("Serial connection not open. Cannot send color.")
