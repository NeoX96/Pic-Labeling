#include <Servo.h>
#include <Stepper.h>
#include <LiquidCrystal_I2C.h>

Servo servo;
int SPU = 2048;
Stepper Motor(SPU, 6, 4, 3, 5);
LiquidCrystal_I2C lcd(0x27, 16, 2); // Adresse des LCD-Moduls und die Zeichenanzahl pro Zeile und Zeilenanzahl

int previous_case = 0;    // Vorheriger Case-Wert
const int ledPin = 2;     // Pin-Nummer der LED
const int buttonPin = 12; // Pin-Nummer des Buttons

bool loopRunning = false; // Flag, um den Zustand der Loop anzuzeigen

void setup() {
    servo.attach(7);
    Motor.setSpeed(6);
    Serial.begin(9600); // Starte serielle Kommunikation mit einer Baudrate von 9600

    // Initialisiere das LCD-Modul
    lcd.begin(16, 2);
    lcd.backlight();

    pinMode(ledPin, OUTPUT);          // Setze den LED-Pin als Ausgang
    pinMode(buttonPin, INPUT_PULLUP); // Setze den Button-Pin als Eingang mit Pull-up-Widerstand
}


void loop() {
    // entprellen des Buttons
    if (debounceButton(buttonPin, 50)) {
        if (!loopRunning) {
            startLoop();
        } else {
            stopLoop();
        }
    }

    if (loopRunning) {
        if (Serial.available() > 0) {
            int eingabe = Serial.parseInt(); // Lese Integer-Wert von serieller Schnittstelle

            if (eingabe != previous_case) {
                switch (eingabe) {
                case 1:
                    servo.write(30);        // Drehe den Servo auf Position 1 (30 Grad)
                    change_lcd_text("Rot"); // Schreibe "Rot" in das Display
                    blink_led(2);           // Blinken der LED für 3 Mal
                    break;

                case 2:
                    servo.write(60);         // Drehe den Servo auf Position 2 (60 Grad)
                    change_lcd_text("Gelb"); // Schreibe "Gelb" in das Display
                    blink_led(2);            // Blinken der LED für 3 Mal
                    break;

                case 3:
                    servo.write(90);         // Drehe den Servo auf Position 3 (90 Grad)
                    change_lcd_text("Grün"); // Schreibe "Grün" in das Display
                    blink_led(2);            // Blinken der LED für 3 Mal
                    break;

                default:
                    change_lcd_text("Ungültige Eingabe")
                    blink_led(10, 50);
                    break;

                }

                previous_case = eingabe; // Speichere den aktuellen Case-Wert
            }
        }

        // Motor dauerhaft drehen lassen
        Motor.step(4096);
    }
}


void change_lcd_text(const char *text) {
    lcd.clear();         // Lösche das Display
    lcd.setCursor(0, 0); // Setze den Cursor auf die erste Zeile
    lcd.print(text);     // Schreibe den Text in das Display
}


void blink_led(int count, int delayTime = 200) {
    for (int i = 0; i < count; i++) {
        digitalWrite(ledPin, HIGH);
        delay(delayTime);
        digitalWrite(ledPin, LOW);
        delay(delayTime);
    }
}


void startLoop() {
    blink_led(5, 50);
    change_lcd_text("Sorter wird gestartet ...");
    delay(1000);
    loopRunning = true;
}


void stopLoop() {
    loopRunning = false;
    blink_led(5, 50);
    change_lcd_text("Sorter ist gestoppt");
}


bool debounceButton(int pin, int delayTime) {
    static int previousState = HIGH;
    static unsigned long debounceTime = 0;

    int currentState = digitalRead(pin);

    if (currentState != previousState) {
        debounceTime = millis();
    }

    if (millis() - debounceTime > delayTime) {
        if (currentState != previousState) {
        previousState = currentState;
        return currentState == LOW;
        }
    }
    
    return false;
}
