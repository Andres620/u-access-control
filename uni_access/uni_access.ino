#include <Servo.h>

int pirPin = 7; // Pin del sensor PIR
int servoPin = 8; // Pin del servo
int redLedPin = 9; // Pin del Led Rojo
int greenLedPin = 10; // Pin del Led Verde

Servo myServo; // Crear un objeto Servo

const int debounceTime = 50; // Debounce time in milliseconds
int lastPirState = LOW;
int currentPirState = LOW;
int openDoor = 180; // Ángulo para la puerta abierta
int closeDoor = 0;  // Ángulo para la puerta cerrada

void setup() {
  pinMode(pirPin, INPUT);
  pinMode(redLedPin, OUTPUT);
  pinMode(greenLedPin, OUTPUT);
  myServo.attach(servoPin); // Adjuntar el servo al pin
  Serial.begin(9600);
  myServo.write(0);
}

void loop() {
  currentPirState = digitalRead(pirPin);
  
  // Only send a message if the state has actually changed
  if (currentPirState != lastPirState) {
    if (currentPirState == HIGH) {
      Serial.println("Movimiento detectado");
    } else {
      Serial.println("Sin movimiento");
    }
    lastPirState = currentPirState; // Update last state for next debounce cycle
  }

  // Check for incoming serial data
  if (Serial.available() > 0) {
    char receivedChar = Serial.read(); // Leer el carácter recibido

    // Verificar el carácter recibido
    if (receivedChar == 'A' || receivedChar == 'a') {
      Serial.println("Open Door"); // Enviar mensaje "Open Door" por el puerto serie
      myServo.write(openDoor);
      digitalWrite(greenLedPin, HIGH);
      digitalWrite(redLedPin, LOW);
      delay(3000);
      myServo.write(closeDoor);
      digitalWrite(redLedPin, HIGH);
      digitalWrite(greenLedPin, LOW);
    } 
  }

  delay(500); // Esperar 1 segundo antes de volver a verificar
}


