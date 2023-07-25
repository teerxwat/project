#include <ESP8266WiFi.h>
#include <Wire.h>
#include <Adafruit_MLX90614.h>
#include <PubSubClient.h> // MQTT library

const char *ssid = "thanita_2.4Ghz";
const char *password = "aaoy2425";
const char *mqttServer = "server-mqtt.thddns.net";
const int mqttPort = 3333;
const char *mqttUsername = "mqtt";
const char *mqttPassword = "admin1234";
const char *mqttTopic = "sensor/detect";
const char *mqttTopicTemperature = "sensor/Temperature";

const int sensorPin = 14; // IR sensor pin connected to D5
const int relayPin = 2;   // Relay control pin connected to D8
#define SCL_PIN 12
#define SDA_PIN 13
#define ledPin 5

Adafruit_MLX90614 mlx; // Declare an instance of Adafruit_MLX90614
WiFiClient espClient;
PubSubClient client(espClient);

bool isSensorValueChanged = false;
bool isRelayOn = false;

// Object detection status
bool objectDetected = false;

float temperature = 0;

void setup()
{
  Serial.begin(115200);
  pinMode(sensorPin, INPUT);
  pinMode(relayPin, OUTPUT); // Set the relay pin as an output
  pinMode(ledPin, OUTPUT);   // Set the LED pin as an output
  while (!Serial)
    ;

  Wire.begin(SDA_PIN, SCL_PIN);

  if (!mlx.begin())
  {
    Serial.println("Error connecting to MLX sensor. Check wiring.");
    while (1)
      ;
  }

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED)
  {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }

  Serial.println("Connected to WiFi");

  client.setServer(mqttServer, mqttPort);
  client.setCallback(callback);

  while (!client.connected())
  {
    if (client.connect("ESP8266Client", mqttUsername, mqttPassword))
    {
      Serial.println("Connected to MQTT broker");
      client.subscribe(mqttTopic);
    }
    else
    {
      Serial.print("Failed to connect to MQTT broker, rc=");
      Serial.print(client.state());
      Serial.println(" Retrying in 5 seconds...");
      delay(5000);
    }
  }
}

void displayObjectTempC()
{
  // float temp = mlx.readObjectTempC()+1
  Serial.print("Object temperature = ");
  Serial.print(mlx.readObjectTempC());
  Serial.println("°C");
  String temperatureString = String(mlx.readObjectTempC(), 2);
  client.publish(mqttTopicTemperature, temperatureString.c_str());
  if (mlx.readObjectTempC() >= 30.4 && mlx.readObjectTempC() <= 37.4)
  {
    digitalWrite(ledPin, HIGH); // Turn on the LED
  }
  else
  {
    digitalWrite(ledPin, LOW); // Turn off the LED
  }
}

void SensorDetect()
{
  bool currentStatus = digitalRead(sensorPin);
  if (currentStatus && !objectDetected)
  {
    objectDetected = true;
    Serial.println("Object no longer detected: 0");
    client.publish(mqttTopic, "0"); // Publish MQTT message with value 0
  }
  else if (!currentStatus && objectDetected)
  {
    objectDetected = false;
    Serial.println("Object detected: 1");
    displayObjectTempC();
    client.publish(mqttTopic, "1"); // Publish MQTT message with value 1
  }
}

void callback(char *topic, byte *payload, unsigned int length)
{
  // Handle MQTT messages received (if needed)
}

void loop()
{
  if (!client.connected())
  {
    reconnect();
  }
  client.loop();
  SensorDetect();
  delay(100);
}

void reconnect()
{
  while (!client.connected())
  {
    if (client.connect("ESP8266Client", mqttUsername, mqttPassword))
    {
      client.subscribe(mqttTopic);
    }
    else
    {
      Serial.print("Failed to connect to MQTT broker, rc=");
      Serial.print(client.state());
      Serial.println(" Retrying in 5 seconds...");
      delay(5000);
    }
  }
}
