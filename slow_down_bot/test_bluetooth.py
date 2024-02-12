# from bluepy import btle  
# import time

# mac_address = "5E:C9:E8:B7:7A:FC"  # Your BLE device MAC address
# SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"
# R_CHARACTERISTIC_UUID = "12345678-1234-5678-1234-56789abcdef1"
# G_CHARACTERISTIC_UUID = "12345678-1234-5678-1234-56789abcdef2"
# B_CHARACTERISTIC_UUID = "12345678-1234-5678-1234-56789abcdef3"

# class MyDelegate(btle.DefaultDelegate):
#     def __init__(self):
#         super().__init__()

#     def handleNotification(self, cHandle, data):
#         # This method will be called for every notification received
#         print(f"Notification: Data from Handle {cHandle}: {data}")

# def setup_characteristic_notifications(peripheral, service_uuid, char_uuids):
#     service = peripheral.getServiceByUUID(service_uuid)
#     for uuid in char_uuids:
#         characteristic = service.getCharacteristics(uuid)[0]
#         if characteristic.supportsRead():
#             # This part subscribes to notifications
#             descriptor = characteristic.getDescriptors(forUUID=0x2902)[0]  # 0x2902 is the Client Characteristic Configuration Descriptor (CCCD)
#             descriptor.write(0x01.to_bytes(2, byteorder="little"), withResponse=True)
#         else:
#             print(f"Characteristic {uuid} does not support notifications.")

# # Main script
# print("Connecting...")
# nano_sense = btle.Peripheral(mac_address)
# nano_sense.setDelegate(MyDelegate())

# print("Discovering Services...")
# _ = nano_sense.services

# print("Setting Up Notifications...")
# setup_characteristic_notifications(nano_sense, SERVICE_UUID, [R_CHARACTERISTIC_UUID, G_CHARACTERISTIC_UUID, B_CHARACTERISTIC_UUID])

# print("Waiting for notifications...")
# while True:
#     if nano_sense.waitForNotifications(1.0):
#         # handleNotification() was called
#         continue
#     print("Waiting...")

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
def button_press():
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
        new_value_a = value_a + 10 if value_a < 100 else 100
        value_a_char.write(new_value_a.to_bytes(4, byteorder='little'), withResponse=True)
        print(f"New Value A written to characteristic: {new_value_a}")
        time.sleep(0.5)  # Delay to ensure the write is processed
        updated_value_a = int.from_bytes(value_a_char.read(), byteorder='little')
        print(f"Read back updated Value A: {updated_value_a}")
    except btle.BTLEException as e:
        print(f"BLE error: {e}")
        connect_to_peripheral()

# Initial connection to the peripheral
print("Connecting to peripheral...")
connect_to_peripheral()

# Main loop
try:
    print("Waiting for button press...")
    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:
            button_press()
            time.sleep(0.2)
        else:
            time.sleep(0.1)
except KeyboardInterrupt:
    GPIO.cleanup()
    if peripheral:
        peripheral.disconnect()
