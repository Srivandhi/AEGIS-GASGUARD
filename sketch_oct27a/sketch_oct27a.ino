#define MQ2_PIN A0
#define LED_PIN 6
#define RELAY_PIN 7

int GAS_THRESHOLD = 400;

// true = abnormal/gas simulation
// false = use actual MQ-2 reading
bool SIMULATE_GAS = false;

void setup() {

  Serial.begin(9600);

  pinMode(MQ2_PIN, INPUT);
  pinMode(LED_PIN, OUTPUT);
  pinMode(RELAY_PIN, OUTPUT);

  // Initially everything OFF
  digitalWrite(LED_PIN, LOW);

  // Most Arduino relay modules are ACTIVE LOW
  digitalWrite(RELAY_PIN, HIGH);

  Serial.println("================================");
  Serial.println("      SMART GAS LEAK DETECTOR");
  Serial.println("================================");
  Serial.println("Sensor ready!");
}

void loop() {

  int gasValue = analogRead(MQ2_PIN);

  // -----------------------------
  // SIMULATE ABNORMAL CONDITION
  // -----------------------------

  if (SIMULATE_GAS) {
    gasValue = 600;
  }

  Serial.print("Gas Sensor Value: ");
  Serial.print(gasValue);

  // -----------------------------
  // GAS DETECTED
  // -----------------------------

  if (gasValue >= GAS_THRESHOLD) {

    // LED ON
    digitalWrite(LED_PIN, HIGH);

    // Relay ON → Fan ON
    digitalWrite(RELAY_PIN, LOW);

    Serial.println("  --> GAS DETECTED!");
    Serial.println("  --> LED: ON");
    Serial.println("  --> FAN: ON");

  }

  // -----------------------------
  // NORMAL CONDITION
  // -----------------------------

  else {

    // LED OFF
    digitalWrite(LED_PIN, LOW);

    // Relay OFF → Fan OFF
    digitalWrite(RELAY_PIN, HIGH);

    Serial.println("  --> NORMAL");
    Serial.println("  --> LED: OFF");
    Serial.println("  --> FAN: OFF");
  }

  delay(1000);
}