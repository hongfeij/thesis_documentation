from bluepy import btle

class MyDelegate(btle.DefaultDelegate):
    def __init__(self):
        btle.DefaultDelegate.__init__(self)

    # Handler for when a notification is received
    def handleNotification(self, cHandle, data):
        print("FSR Value:", int.from_bytes(data, byteorder='little'))

# Replace "FSR_SENSOR_MAC_ADDRESS" with your Arduino's BLE address
arduino_address = "0B:CC:05:54:13:11" 
service_uuid = btle.UUID("180C")
fsr_uuid = btle.UUID("2A58")

p = btle.Peripheral(arduino_address)
p.setDelegate(MyDelegate())

# Setup to enable notifications
fsr_service = p.getServiceByUUID(service_uuid)
fsr_characteristic = fsr_service.getCharacteristics(fsr_uuid)[0]
fsr_characteristic_handle = fsr_characteristic.getHandle() + 1
p.writeCharacteristic(fsr_characteristic_handle, b'\x01\x00')

print("Receiving FSR data...")

try:
    while True:
        if p.waitForNotifications(1.0):
            # handleNotification() was called
            continue
        print("Waiting...")
except Exception as e:
    print(e)
finally:
    p.disconnect()
