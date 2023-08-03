#include <ESP8266WiFi.h>
#include <Wire.h>
#include <Adafruit_MLX90614.h>
#include <PubSubClient.h>  // MQTT library

const char *ssid = "thanita_2.4Ghz";
const char *password = "aaoy2425";
const char *mqttServer = "server-mqtt.thddns.net";
const int mqttPort = 3333;
const char *mqttUsername = "mqtt";
const char *mqttPassword = "admin1234";
const char *mqttTopic = "sensor/detect";
const char *mqttTopicTemperature = "sensor/Temperature";
const char *mqttTopicLED = "control/led";

const int sensorPin = 14;  // IR sensor pin connected to D5
const int relayPin = 2;    // Relay control pin connected to D8
#define SCL_PIN 12
#define SDA_PIN 13

// LED PIN
#define R_PIN 4
#define G_PIN 5
#define B_PIN 16

// LED control commands
#define LED_COMMAND_READY 1
#define LED_COMMAND_WORKING 2
#define LED_COMMAND_SUCCESSFUL 3
#define LED_COMMAND_NOT_SUCCESSFUL 4
#define LED_COMMAND_ALERT 5

int ir = 0;

bool previousIRValue = false;  // Variable to store the previous value of the IR sensor

////////////////////

Adafruit_MLX90614 mlx;  // Declare an instance of Adafruit_MLX90614
WiFiClient espClient;
PubSubClient client(espClient);

bool isSensorValueChanged = false;
bool isRelayOn = false;

// Object detection status
bool objectDetected = false;

float temperature = 0;

// Variables to manage timing
unsigned long previousSensorDetectMillis = 0;
unsigned long previousLedControlMillis = 0;
const unsigned long sensorDetectInterval = 100;  // Interval for IR sensor detection (100 milliseconds)
const unsigned long ledControlInterval = 200;    // Interval for LED control (200 milliseconds)

// LED control variables
int temperatureLED = 0;           // Define temperatureLED as a global variable
int prevTemperatureLED = -1;      // Previous value of temperatureLED
bool newCommandReceived = false;  // Global flag to indicate if a new command has been received

void setup() {
  Serial.begin(115200);
  pinMode(R_PIN, OUTPUT);
  pinMode(G_PIN, OUTPUT);
  pinMode(B_PIN, OUTPUT);
  pinMode(sensorPin, INPUT);
  pinMode(relayPin, OUTPUT);  // Set the relay pin as an output
  Wire.begin(SDA_PIN, SCL_PIN);

  if (!mlx.begin()) {
    Serial.println("Error connecting to MLX sensor. Check wiring.");
    while (1)
      ;
  }

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }

  Serial.println("Connected to WiFi");

  client.setServer(mqttServer, mqttPort);
  client.setCallback(callback);

  reconnect();  // Connect to MQTT broker

  // Subscribe to topics
  client.subscribe(mqttTopic);
  client.subscribe(mqttTopicLED);
}

void displayObjectTempC() {
  Serial.print("Object temperature = ");
  Serial.print(mlx.readObjectTempC());
  Serial.println("°C");
  String temperatureString = String(mlx.readObjectTempC(), 2);
  client.publish(mqttTopicTemperature, temperatureString.c_str());
  if (mlx.readObjectTempC() >= 30.4 && mlx.readObjectTempC() <= 37.4) {
    digitalWrite(relayPin, HIGH);  // Turn on the Relay
  } else {
    digitalWrite(relayPin, LOW);  // Turn off the Relay
  }
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
    displayObjectTempC();
    client.publish(mqttTopic, "1");  // Publish MQTT message with value 1
  }
}

void callback(char *topic, byte *payload, unsigned int length) {
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.println("Message received: " + message);

  if (strcmp(topic, mqttTopicLED) == 0) {
    temperatureLED = message.toInt();  // Update the latest received command
    if (temperatureLED != prevTemperatureLED) {
      newCommandReceived = true;  // Set the flag to indicate that a new command has been received
    }
  }
}

void reconnect() {
  while (!client.connected()) {
    if (client.connect("ESP8266Client", mqttUsername, mqttPassword)) {
      Serial.println("Connected to MQTT broker");
    } else {
      Serial.print("Failed to connect to MQTT broker, rc=");
      Serial.print(client.state());
      Serial.println(" Retrying in 5 seconds...");
      delay(5000);
    }
  }
}

void ledTask() {
  if (newCommandReceived) {
    newCommandReceived = false;  // Reset the flag

    int command = temperatureLED;  // Use the latest received command
    executeCommand(command);

    // Keep executing the command until a new command is received
    while (!newCommandReceived) {
      executeCommand(command);
      client.loop();  // Allow the PubSubClient to handle incoming messages while waiting
    }

    prevTemperatureLED = temperatureLED;  // Set prevTemperatureLED to the current value
  }
}

void alert() {
  int alert = 0;
  for (alert = 0; alert <= 3; alert++) {
    for (int intensity = 0; intensity <= 255; intensity += 15) {
      analogWrite(R_PIN, intensity);
      analogWrite(G_PIN, 255);
      analogWrite(B_PIN, 255);
      delay(10);
    }
    delay(100);
    analogWrite(R_PIN, 255);
    analogWrite(G_PIN, 255);
    analogWrite(B_PIN, 255);
    delay(100);
  }
}

void ready() {
  for (int intensity = 0; intensity <= 255; intensity += 15) {
    analogWrite(R_PIN, intensity);
    analogWrite(G_PIN, intensity);
    analogWrite(B_PIN, 255);
    delay(25);
  }
  delay(300);
  for (int intensity = 255; intensity >= 0; intensity -= 10) {
    analogWrite(R_PIN, intensity);
    analogWrite(G_PIN, intensity);
    analogWrite(B_PIN, 255);
    delay(10);
  }
  delay(100);
}

void successful() {
  int successful = 0;
  for (successful = 0; successful <= 3; successful++) {
    for (int intensity = 0; intensity <= 255; intensity += 15) {
      analogWrite(R_PIN, 255);
      analogWrite(G_PIN, intensity);
      analogWrite(B_PIN, 255);
      delay(10);
    }
    delay(100);
    analogWrite(R_PIN, 255);
    analogWrite(G_PIN, 255);
    analogWrite(B_PIN, 255);
    delay(100);
  }
  analogWrite(R_PIN, 255);
  analogWrite(G_PIN, 0);
  analogWrite(B_PIN, 255);
  delay(3000);
}

void Notsuccessful() {
  int successful = 0;
  for (successful = 0; successful <= 3; successful++) {
    for (int intensity = 0; intensity <= 255; intensity += 15) {
      analogWrite(R_PIN, 255);
      analogWrite(G_PIN, intensity);
      analogWrite(B_PIN, 255);
      delay(10);
    }
    delay(100);
    analogWrite(R_PIN, 255);
    analogWrite(G_PIN, 255);
    analogWrite(B_PIN, 255);
    delay(100);
  }
  analogWrite(R_PIN, 0);
  analogWrite(G_PIN, 255);
  analogWrite(B_PIN, 255);
  delay(3000);
}

void working() {
  analogWrite(R_PIN, 0);
  analogWrite(G_PIN, 0);
  analogWrite(B_PIN, 255);
}

void executeCommand(int command) {
  switch (command) {
    case LED_COMMAND_READY:
      ready();
      break;

    case LED_COMMAND_WORKING:
      working();
      break;

    case LED_COMMAND_SUCCESSFUL:
      successful();
      break;

    case LED_COMMAND_NOT_SUCCESSFUL:
      Notsuccessful();
      break;

    case LED_COMMAND_ALERT:
      alert();
      break;

    default:
      // Invalid command
      break;
  }

  newCommandReceived = false;  // Reset the flag after executing the command
}

void loop() {
  // Call the SensorDetect function at regular intervals
  unsigned long currentMillis = millis();
  if (currentMillis - previousSensorDetectMillis >= sensorDetectInterval) {
    previousSensorDetectMillis = currentMillis;
    SensorDetect();
  }

  // Call the ledTask function at regular intervals
  if (newCommandReceived) {
    ledTask();
  }

  // Reconnect to MQTT broker if disconnected
  if (!client.connected()) {
    reconnect();
  }
  client.loop();  // Handle incoming MQTT messages

  // Add any other code here that you want to run continuously in the loop
}
