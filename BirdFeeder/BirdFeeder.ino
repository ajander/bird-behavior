const int testPin = 0;
const int delayTime = 1000;

void setup() {
  Serial.begin(115200);
  Serial.println("Starting setup");
  Serial.println();
  pinMode(testPin, OUTPUT);
  Serial.println("Set pin 0 mode to output");
  Serial.println();
}

void loop() {
  Serial.println("Set pin high");
  Serial.println();
  digitalWrite(testPin, HIGH);
  delay(delayTime);
  Serial.println("Set pin low");
  Serial.println();
  digitalWrite(testPin, LOW);
  delay(delayTime);
}

