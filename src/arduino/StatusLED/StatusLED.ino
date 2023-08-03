#define R_PIN 4
#define G_PIN 5
#define B_PIN 16

int temperatureLED = 0;
int ir = 0;

void setup() {
  pinMode(R_PIN, OUTPUT);
  pinMode(G_PIN, OUTPUT);
  pinMode(B_PIN, OUTPUT);
  Serial.begin(115200);
}

void alert() {
  int alert = 0;
  for (alert = 0; alert <= 5; alert++) {
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
  if (temperatureLED >= 35 && temperatureLED <= 38) {
    Serial.println("OPEN THE DOOR");
    analogWrite(R_PIN, 255);
    analogWrite(G_PIN, 0);
    analogWrite(B_PIN, 255);
    delay(10000);
  }
  Serial.println("close the door");
  analogWrite(R_PIN, 0);
  analogWrite(G_PIN, 255);
  analogWrite(B_PIN, 255);
  delay(10000);
}

void working() {
  analogWrite(R_PIN, 0);
  analogWrite(G_PIN, 0);
  analogWrite(B_PIN, 255);
}

void loop() {
}
