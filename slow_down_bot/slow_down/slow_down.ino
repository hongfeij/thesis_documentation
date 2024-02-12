// #include <ArduinoBLE.h>

// const int fsrPin = A0; // Analog pin connected to the FSR
// int valueA = 0; // Starting value of A

// BLEService valueService("12345678-1234-5678-1234-56789abcdef0"); // Custom service UUID
// BLEUnsignedIntCharacteristic valueACharacteristic("12345678-1234-5678-1234-56789abcdef1", BLERead | BLEWrite | BLENotify); // Value A characteristic

// void setup() {
//   Serial.begin(9600);
//   pinMode(fsrPin, INPUT);
//   if (!BLE.begin()) {
//     Serial.println("starting BLE failed!");
//     while (1);
//   }

//   BLE.setLocalName("Value Controller");
//   BLE.setAdvertisedService(valueService);
//   valueService.addCharacteristic(valueACharacteristic);
//   BLE.addService(valueService);

//   valueACharacteristic.writeValue(valueA);
//   BLE.advertise();
//   Serial.println("BLE Peripheral Ready");
// }

// void loop() {
//   BLEDevice central = BLE.central();
//   if (central) {
//     Serial.print("Connected to central: ");
//     Serial.println(central.address());
    
//     while (central.connected()) {
//       int fsrValue = analogRead(fsrPin);
//       if (fsrValue > 10) { // Threshold for FSR pressure
//         valueA += fsrValue; // Add FSR value to Value A
//         valueACharacteristic.writeValue(valueA);
//         Serial.print("Value A: ");
//         Serial.println(valueA);
//       }
//       if (valueACharacteristic.written()) {
//         valueA = valueACharacteristic.value();
//         Serial.print("Value A written by central: ");
//         Serial.println(valueA);
//       }
//       delay(200); // Delay to prevent too frequent updates
//     }
//     Serial.print("Disconnected from central: ");
//     Serial.println(central.address());
//   }
// }

#include <ArduinoBLE.h>

const int fsrPin = A0; // FSR connected to analog pin A0
const int redPin = D2;  // Red pin of the RGB LED
const int greenPin = D3; // Green pin of the RGB LED
const int bluePin = D4;  // Blue pin of the RGB LED

BLEService valueService("12345678-1234-5678-1234-56789abcdef0");
BLEUnsignedIntCharacteristic valueACharacteristic("12345678-1234-5678-1234-56789abcdef1", BLERead | BLEWrite | BLENotify);

int valueA = 0; // Starting value of A

void setup() {
  Serial.begin(9600);
  pinMode(fsrPin, INPUT);
  pinMode(redPin, OUTPUT);
  pinMode(greenPin, OUTPUT);
  pinMode(bluePin, OUTPUT);

  if (!BLE.begin()) {
    Serial.println("starting BLE failed!");
    while (1);
  }

  BLE.setLocalName("RGB LED Controller");
  BLE.setAdvertisedService(valueService);
  valueService.addCharacteristic(valueACharacteristic);
  BLE.addService(valueService);

  valueACharacteristic.writeValue(valueA);
  BLE.advertise();
  Serial.println("BLE Peripheral Ready");
}

void loop() {
  BLEDevice central = BLE.central();
  if (central) {
    Serial.print("Connected to central: ");
    Serial.println(central.address());
    
    while (central.connected()) {
      // Serial.print("fsr: ");
      // Serial.print(analogRead(fsrPin));
      if (analogRead(fsrPin) > 100) {
        if (valueA - 10 > 0) {
          valueA = valueA - 10;
        }
        valueACharacteristic.writeValue(valueA);
        Serial.print("Current value: ");
        Serial.println(valueA);
      }
      if (valueACharacteristic.written()) {
        valueA = valueACharacteristic.value();
        Serial.print("From Rp: ");
        Serial.println(valueA);
      }
      updateLEDColor(valueA);
      delay(1000); // Delay to prevent too frequent updates
    }
    Serial.print("Disconnected from central: ");
    Serial.println(central.address());
  }
}

void updateLEDColor(int value) {
  // When value is 0, LED is fully blue. When value is 100, LED is fully red.
  int redValue = map(value, 0, 100, 255, 0);
  int blueValue = map(value, 0, 100, 0, 255);

  analogWrite(redPin, redValue);
  analogWrite(greenPin, 255); // No green component
  analogWrite(bluePin, blueValue);
}
