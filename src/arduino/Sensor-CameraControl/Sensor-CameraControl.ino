#include <WiFi.h>
#include "esp_camera.h"

// IR Sensor pin
const int irSensorPin = 12;


void printIPAddress() {
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);
}

void setup() {
  // Initialize IR sensor pin as input
  pinMode(irSensorPin, INPUT);

  // Initialize camera
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = 5;
  config.pin_d1 = 18;
  config.pin_d2 = 19;
  config.pin_d3 = 21;
  config.pin_d4 = 36;
  config.pin_d5 = 39;
  config.pin_d6 = 34;
  config.pin_d7 = 35;
  config.pin_xclk = 32;
  config.pin_pclk = 22;
  config.pin_vsync = 25;
  config.pin_href = 23;
  config.pin_sscb_sda = 26;
  config.pin_sscb_scl = 27;
  config.pin_pwdn = 33;
  config.pin_reset = -1;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_SVGA;
  config.jpeg_quality = 10;
  config.fb_count = 2;

  // Initialize camera
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera initialization failed with error 0x%x", err);
    return;
  }

  // Connect to Wi-Fi
  // TODO: Add your Wi-Fi credentials
  WiFi.begin("thanita_2.4Ghz", "aaoy2425");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }

  Serial.println("Connected to WiFi");
  printIPAddress();
}

void loop() {
  // Read the state of the IR sensor
  int irSensorState = digitalRead(irSensorPin);

  // Check if IR sensor is triggered
  if (irSensorState == HIGH) {
    // Perform an action when IR sensor is triggered
    // For example, capture a photo
    camera_fb_t *fb = NULL;
    fb = esp_camera_fb_get();
    if (fb) {
      // Process the captured photo here
      // You can send it to a server, display it on a screen, etc.
      // Example: Print the photo size to the serial monitor
      Serial.print("Photo size: ");
      Serial.print(fb->len);
      Serial.println(" bytes");
      esp_camera_fb_return(fb);
    }
  }

  delay(100); // Adjust the delay as per your requirements
}
