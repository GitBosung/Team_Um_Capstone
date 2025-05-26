#include <ArduinoBLE.h>
#include <Arduino_BMI270_BMM150.h>

// BLE 서비스 및 특성 UUID
BLEService sensorService("180F");
BLECharacteristic commandCharacteristic("2A19", BLEWrite, 20);
BLECharacteristic dataCharacteristic("2A1C", BLENotify, 64);

bool logging = false;                // 로깅 여부
unsigned long lastLogTime = 0;       // 마지막 로깅 시각
const unsigned long logInterval = 50; // 50ms 간격 (20Hz)

void setup() {
  Serial.begin(115200);
  while (!Serial);

  if (!IMU.begin()) {
    Serial.println("BMI270 초기화 실패!");
    while (1);
  }
  Serial.println("BMI270 초기화 성공!");
  Serial.println("time,ax,ay,az,gx,gy,gz");

  if (!BLE.begin()) {
    Serial.println("BLE 초기화 실패!");
    while (1);
  }

  BLE.setLocalName("Nano33BLE-Logger");
  BLE.setDeviceName("Nano33BLE-Logger");
  BLE.setAdvertisedService(sensorService);

  sensorService.addCharacteristic(commandCharacteristic);
  sensorService.addCharacteristic(dataCharacteristic);
  BLE.addService(sensorService);

  commandCharacteristic.setEventHandler(BLEWritten, commandReceived);

  BLE.advertise();
  Serial.println("BLE 광고 시작!");
}

void loop() {
  BLE.poll();
  unsigned long currentTime = millis();

  if (logging && (currentTime - lastLogTime >= logInterval)) {
    lastLogTime = currentTime;

    float ax = 0, ay = 0, az = 0;
    float gx = 0, gy = 0, gz = 0;

    if (IMU.accelerationAvailable()) {
      IMU.readAcceleration(ax, ay, az);
    }
    if (IMU.gyroscopeAvailable()) {
      IMU.readGyroscope(gx, gy, gz);
    }

    char buffer[256];
    snprintf(buffer, sizeof(buffer), "%lu,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f",
             currentTime, ax, ay, az, gx, gy, gz);

    dataCharacteristic.writeValue((uint8_t*)buffer, strlen(buffer));
    Serial.println(buffer);
  }
}

void commandReceived(BLEDevice central, BLECharacteristic characteristic) {
  Serial.println("✅ commandReceived() 콜백 호출됨");

  int len = characteristic.valueLength();
  String command = "";

  for (int i = 0; i < len; i++) {
    command += (char)characteristic.value()[i];
  }
  command.trim();

  Serial.print("Receive Command: ");
  Serial.println(command);

  if (command == "start") {
    logging = true;
    lastLogTime = millis();  // 시작 시 타이밍 초기화
    Serial.println("✅ Logging Start");
  } else if (command == "stop") {
    logging = false;
    Serial.println("🛑 Logging Stop");
  } else {
    Serial.print("⚠️ 알 수 없는 명령: ");
    Serial.println(command);
  }
}
