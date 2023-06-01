#include <LowPower.h>

// Pin Definitions
const int FRIDGE_PIN = 13;
const int FREEZER_PIN = 2;
const int BUZZER_PIN = 10;

// vars
bool fridge_state = false
bool freezer_state = false

void setup() {
    // Pin Modes
    pinMode(FRIDGE_PIN, INPUT);
    pinMode(FREEZER_PIN, INPUT);
    pinMode(BUZZER_PIN, OUTPUT);

    // Serial Communication
    Serial.begin(9600);
}

void loop() {
  fridge_state = digitalRead(FRIDGE_PIN);
  freezer_state = digitalRead(FREEZER_PIN);

  if (fridge_state || freezer_state) {
    digitalWrite(BUZZER_PIN, HIGH); 
    delay(2000)
    digitalWrite(BUZZER_PIN, LOW); 
  }

  LowPower.sleep(10000); // Sleep for 10 seconds
}