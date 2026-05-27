#include <DHT.h>

#define DHT11PIN 2  // pin D4
#define DHTTYPE DHT11

DHT dht(DHT11PIN, DHTTYPE);

float vlaznost, temp;
const int ledPin = D7;
char incomingByte;
int pom = 0;
int rcwl_input = D1;
int pir_input = D0;
int pir_stanje = LOW, rcwl_stanje = LOW;
int rcwl_ocitanje = 0, pir_ocitanje = 0;
int ppom = 99;
unsigned long previousMillis = 0;
const unsigned long interval = 60000; // send temp/humidity every 60s

void setup() {
  Serial.begin(115200);
  dht.begin();
  pinMode(ledPin, OUTPUT);
  pinMode(rcwl_input, INPUT);
  pinMode(pir_input, INPUT);
}

void loop() {
  // Read LED command from Python via serial
  if (Serial.available() > 0) {
    incomingByte = Serial.read();
    if (incomingByte == 'H') {
      digitalWrite(ledPin, HIGH);
      delay(1000);
    }
    if (incomingByte == 'L') {
      digitalWrite(ledPin, LOW);
      delay(1000);
    }
  }

  rcwl_ocitanje = digitalRead(rcwl_input);
  pir_ocitanje  = digitalRead(pir_input);

  // Motion detection state machine
  // pom codes:
  //  0 - no motion
  //  1 - RCWL only
  //  2 - PIR only
  //  3 - both detecting
  //  4 - PIR none, RCWL finished
  //  5 - PIR detecting, RCWL finished
  //  6 - PIR finished, RCWL none
  //  7 - PIR none, RCWL detecting
  //  8 - both finished

  if (pir_ocitanje == true && rcwl_ocitanje == true) {
    pir_stanje  = HIGH;
    rcwl_stanje = HIGH;
    pom = 3;
  }
  else if (pir_ocitanje == true && rcwl_ocitanje == false) {
    if (pir_stanje == LOW && rcwl_stanje == HIGH) pom = 5;
    else if (pir_stanje == HIGH && rcwl_stanje == HIGH) pom = 5;
    else pom = 2;
    pir_stanje  = HIGH;
    rcwl_stanje = LOW;
  }
  else if (pir_ocitanje == false && rcwl_ocitanje == true) {
    if (pir_stanje == HIGH && rcwl_stanje == LOW) pom = 7;
    else pom = 1;
    pir_stanje  = LOW;
    rcwl_stanje = HIGH;
  }
  else {
    if      (pir_stanje == LOW  && rcwl_stanje == HIGH) pom = 4;
    else if (pir_stanje == HIGH && rcwl_stanje == LOW)  pom = 6;
    else if (pir_stanje == HIGH && rcwl_stanje == HIGH) pom = 8;
    else pom = 0;
    pir_stanje  = LOW;
    rcwl_stanje = LOW;
  }

  // Read DHT11
  vlaznost = dht.readHumidity();
  delay(20);
  temp = dht.readTemperature();
  delay(20);

  // Send temp/humidity every minute
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;
    if (!isnan(temp))     { Serial.print("T"); Serial.println(int(temp)); }
    if (!isnan(vlaznost)) { Serial.print("H"); Serial.println(int(vlaznost)); }
  }

  // Send motion only on change
  if (pom != ppom) {
    Serial.print("M");
    Serial.println(int(pom));
    ppom = pom;
    delay(1000);
  }
}
