#include <Wire.h>
#include <SPI.h>
#include <Adafruit_LSM9DS1.h>
#include <Adafruit_Sensor.h>  // not used in this demo but required!

// i2c
Adafruit_LSM9DS1 lsm = Adafruit_LSM9DS1();

#define LSM9DS1_SCK A5
#define LSM9DS1_MISO 12
#define LSM9DS1_MOSI A4
#define LSM9DS1_XGCS 6
#define LSM9DS1_MCS 5

unsigned long lastAccelGyroUpdate = 0;  // Tracks last update time for accel/gyro
unsigned long lastMagUpdate = 0;        // Tracks last update time for magnetometer

void setupSensor() {
    // Set accelerometer range and data rate
    lsm.setupAccel(lsm.LSM9DS1_ACCELRANGE_2G, lsm.LSM9DS1_ACCELDATARATE_952HZ);
    
    // Set magnetometer sensitivity
    lsm.setupMag(lsm.LSM9DS1_MAGGAIN_4GAUSS);
    
    // Set gyroscope range
    lsm.setupGyro(lsm.LSM9DS1_GYROSCALE_245DPS);
}

void setup() {
    Serial.begin(115200);
    while (!Serial); // Wait for Serial Monitor to open

    Serial.println("Initializing LSM9DS1 Sensor...");

    if (!lsm.begin()) {
        Serial.println("Failed to initialize LSM9DS1! Check wiring.");
        while (1);
    }
    Serial.println("LSM9DS1 Initialized!");

    setupSensor();
}

void loop() {
    unsigned long currentMillis = millis();

    // Send Accelerometer & Gyro data
    if (currentMillis - lastAccelGyroUpdate >= 1) {
        lsm.readAccel();
        lsm.readGyro();
        lastAccelGyroUpdate = currentMillis;

        Serial.write('A');  // Prefix for Accel/Gyro
        Serial.write((uint8_t*)&currentMillis, sizeof(currentMillis));
        Serial.write((uint8_t*)&lsm.accelData.x, sizeof(float));
        Serial.write((uint8_t*)&lsm.accelData.y, sizeof(float));
        Serial.write((uint8_t*)&lsm.accelData.z, sizeof(float));
        Serial.write((uint8_t*)&lsm.gyroData.x, sizeof(float));
        Serial.write((uint8_t*)&lsm.gyroData.y, sizeof(float));
        Serial.write((uint8_t*)&lsm.gyroData.z, sizeof(float));
    }

    // Send Magnetometer data separately
    if (currentMillis - lastMagUpdate >= 12) {
        lsm.readMag();
        lastMagUpdate = currentMillis;

        Serial.write('M');  // Prefix for Magnetometer
        Serial.write((uint8_t*)&currentMillis, sizeof(currentMillis));
        Serial.write((uint8_t*)&lsm.magData.x, sizeof(float));
        Serial.write((uint8_t*)&lsm.magData.y, sizeof(float));
        Serial.write((uint8_t*)&lsm.magData.z, sizeof(float));
    }
}
