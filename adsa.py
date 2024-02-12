import RPi.GPIO as GPIO
from bluepy import btle
import time

# Setup for button on Raspberry Pi
BUTTON_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# BLE device information
mac_address = "5E:C9:E8:B7:7A:FC"  # Replace with your Arduino BLE address
service_uuid = "12345678-1234-5678-1234-56789abcdef0"
value_a_uuid = "12345678-1234-5678-1234-56789abcdef1"

# Connect to BLE peripheral
def connect_to_peripheral():
    global peripheral
    peripheral = btle.Peripheral(mac_address)

# Decrease Value A when the button is pressed
def button_callback(channel):
    global peripheral
    print("Button pressed, decreasing Value A")
    if peripheral is None:
        print("Peripheral device not connected")
        return
    try:
        # Read, decrement, and write Value A
        service = peripheral.getServiceByUUID(service_uuid)
        value_a_char = service.getCharacteristics(value_a_uuid)[0]
        value_a = int.from_bytes(value_a_char.read(), byteorder='little')
        print(f"Current Value A: {value_a}")
        new_value_a = max(0, value_a - 100)
        value_a_char.write(new_value_a.to_bytes(4, byteorder='little'), withResponse=True)
        print(f"New Value A written to characteristic: {new_value_a}")
        time.sleep(0.5)  # Delay to ensure the write is processed
        updated_value_a = int.from_bytes(value_a_char.read(), byteorder='little')
        print(f"Read back updated Value A: {updated_value_a}")
    except btle.BTLEException as e:
        print(f"BLE error: {e}")
        connect_to_peripheral()

# Add event detection for button press
GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=button_callback, bouncetime=300)

# Initial connection to the peripheral
print("Connecting to peripheral...")
connect_to_peripheral()

# Main loop
try:
    print("Waiting for button press...")
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()
    if peripheral:
        peripheral.disconnect()
