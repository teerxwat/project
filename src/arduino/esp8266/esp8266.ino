#include <ESP8266WiFi.h>
#include <Wire.h>
#include <Adafruit_MLX90614.h>
#include <PubSubClient.h>  // MQTT library

// const char *ssid = "thanita_2.4Ghz";
// const char *password = "aaoy2425";
// const char *mqttServer = "server-mqtt.thddns.net";
// const int mqttPort = 3333;
// const char *mqttUsername = "mqtt";
// const char *mqttPassword = "admin1234";
// const char *mqttTopic = "sensor/detect";
// const char *mqttTopicTemperature = "sensor/Temperature";
// const char *mqttTopicLED = "control/led";

const char *ssid = "ZTE 5G Home WiFi_DD9538";
const char *password = "61019205";
const char *mqttServer = "192.168.0.28";
const int mqttPort = 1883;
const char *mqttUsername = "";
const char *mqttPassword = "";
const char *mqttTopic = "sensor/detect";
const char *mqttTopicTemperature = "sensor/Temperature";
const char *mqttTopicLED = "control/led";

const int sensorPin = 14;  // IR sensor pin connected to D5
const int relayPin = 2;
#define SCL_PIN 12
#define SDA_PIN 13
#define redPin 4
#define greenPin 5
#define bluePin 16


Adafruit_MLX90614 mlx;  // Declare an instance of Adafruit_MLX90614
WiFiClient espClient;
PubSubClient client(espClient);

bool isSensorValueChanged = false;
bool isRelayOn = false;

// Object detection status
bool objectDetected = false;

float temperature = 0;

void setup() {
  Serial.begin(115200);
  pinMode(redPin, OUTPUT);
  pinMode(greenPin, OUTPUT);
  pinMode(bluePin, OUTPUT);
  pinMode(sensorPin, INPUT);
  pinMode(relayPin, OUTPUT);
  digitalWrite(relayPin, HIGH);
  setColor(255, 255, 255);
  while (!Serial)
    ;

  Wire.begin(SDA_PIN, SCL_PIN);

  if (!mlx.begin()) {
    Serial.println("Error connecting to MLX sensor. Check wiring.");
    while (1)
      ;
  }

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("Connecting to WiFi...");
  }

  Serial.println("Connected to WiFi");

  client.setServer(mqttServer, mqttPort);
  client.setCallback(callback);

  while (!client.connected()) {
    if (client.connect("ESP8266Client", mqttUsername, mqttPassword)) {
      Serial.println("Connected to MQTT broker");
      client.subscribe(mqttTopic);
      client.subscribe(mqttTopicLED);
    } else {
      Serial.print("Failed to connect to MQTT broker, rc=");
      Serial.print(client.state());
      Serial.println(" Retrying in 5 seconds...");
      delay(5000);
    }
  }
}

void displayObjectTempC() {
  // float temp = mlx.readObjectTempC()+1
  Serial.print("Object temperature = ");
  Serial.print(mlx.readObjectTempC());
  Serial.println("°C");
  String temperatureString = String(mlx.readObjectTempC(), 2);
  client.publish(mqttTopicTemperature, temperatureString.c_str());
  // if (mlx.readObjectTempC() >= 30.4 && mlx.readObjectTempC() <= 37.4) {
  //   digitalWrite(ledPin, HIGH);  // Turn on the LED
  // } else {
  //   digitalWrite(ledPin, LOW);  // Turn off the LED
  // }
}

void SensorDetect() {
  bool currentStatus = digitalRead(sensorPin);
  if (currentStatus && !objectDetected) {
    objectDetected = true;
    Serial.println("Object no longer detected: 0");
    client.publish(mqttTopic, "0");  // Publish MQTT message with value 0
  } else if (!currentStatus && objectDetected) {
    objectDetected = false;
    Serial.println("Object detected: 1");
    client.publish(mqttTopic, "1");  // Publish MQTT message with value 1
    delay(1500);
    displayObjectTempC();
  }
}

void setColor(int red, int green, int blue) {
#ifdef COMMON_ANODE
  red = 255 - red;
  green = 255 - green;
  blue = 255 - blue;
#endif
  analogWrite(redPin, red);
  analogWrite(greenPin, green);
  analogWrite(bluePin, blue);
}

void callback(char *topic, byte *payload, unsigned int length) {
  Serial.print("Message arrived on topic: ");
  Serial.println(topic);

  String message;
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.print("Payload: ");
  Serial.println(message);

  // Control the LED based on the received MQTT message
  if (strcmp(topic, mqttTopicLED) == 0) {
    if (strcmp(message.c_str(), "1") == 0) {  // สำเร็จ
      for (int i = 0; i <= 3; i++) {
        setColor(255, 0, 255);  // green
        delay(500);
        setColor(255, 255, 255);
        delay(250);
      }
      setColor(255, 0, 255);  // green
      digitalWrite(relayPin, LOW);
      delay(3000);
      digitalWrite(relayPin, HIGH);
      setColor(255, 255, 255);
    } else if (strcmp(message.c_str(), "2") == 0) {  // สำเร็จแต่ประตูไม่เปิด
      for (int i = 0; i <= 3; i++) {
        setColor(255, 0, 255);  // green
        delay(500);
        setColor(255, 255, 255);
        delay(250);
      }
      setColor(0, 255, 255);  // red
      delay(3000);
      setColor(255, 255, 255);
    } else if (strcmp(message.c_str(), "3") == 0) {  // ไม่พบข้อมูล
      for (int i = 0; i <= 3; i++) {
        setColor(0, 255, 255);  // red
        delay(500);
        setColor(255, 255, 255);
        delay(250);
      }
      setColor(0, 255, 255);  // red
      delay(3000);
      setColor(255, 255, 255);
    } else if (strcmp(message.c_str(), "4") == 0) {
      setColor(255, 255, 0);                         // blue
    } else if (strcmp(message.c_str(), "5") == 0) {  // กำลังทำงาน
      setColor(0, 0, 255);                           // blue
    } else if (strcmp(message.c_str(), "0") == 0) {  // รอทำงาน
      setColor(255, 255, 255);
    }
  }
}


void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  SensorDetect();
  delay(100);
}

void reconnect() {
  while (!client.connected()) {
    if (client.connect("ESP8266Client", mqttUsername, mqttPassword)) {
      client.subscribe(mqttTopic);
    } else {
      Serial.print("Failed to connect to MQTT broker, rc=");
      Serial.print(client.state());
      Serial.println(" Retrying in 5 seconds...");
      delay(5000);
    }
  }
}