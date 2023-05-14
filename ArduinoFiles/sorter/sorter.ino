#include <Servo.h>
#include <Stepper.h>
#include <LiquidCrystal.h>

Servo servo;
int SPU = 2048;
Stepper Motor(SPU, 6, 4, 3, 5);
LiquidCrystal lcd(13, 12, 11, 10, 9, 8); // Adresse des LCD-Moduls und die Zeichenanzahl pro Zeile und Zeilenanzahl

int previous_case = 0;   // Vorheriger Case-Wert
const int ledPin = 1;    // Pin-Nummer der LED
const int buttonPin = 2; // Pin-Nummer des Buttons
int eingabe = 0;

volatile bool buttonPressed = false; // Diese Variable wird in der ISR geändert
bool motorActive = false;

unsigned long lastStepTime = 0; // Zeitpunkt des letzten Schrittes
int stepInterval = 1;           // Zeit zwischen den Schritten in Millisekunden

bool loopRunning = false; // Flag, um den Zustand der Loop anzuzeigen

void setup()
{
    servo.attach(7);
    Motor.setSpeed(6);
    Serial.begin(9600); // Starte serielle Kommunikation mit einer Baudrate von 9600

    // Initialisiere das LCD-Modul
    lcd.begin(16, 2);
    bool loopRunning = false;

    // lcd write "Betriebsbereit"
    change_lcd_text("Betriebsbereit");

    pinMode(ledPin, OUTPUT); // Setze den LED-Pin als Ausgang
    digitalWrite(ledPin, LOW);

    pinMode(buttonPin, INPUT_PULLUP);                                              // // aktiviert den internen Pullup-Widerstand
    attachInterrupt(digitalPinToInterrupt(buttonPin), handleButtonPress, FALLING); // Interrupt für den Button
}

void blink_led(int count, int delayTime = 200)
{
    for (int i = 0; i < count; i++)
    {
        digitalWrite(ledPin, HIGH);
        delay(delayTime);
        digitalWrite(ledPin, LOW);
        delay(delayTime);
    }
}

bool debounceButton(int pin, int delayTime)
{
    static int previousState = HIGH;
    static unsigned long debounceTime = 0;

    int currentState = digitalRead(pin);

    if (currentState != previousState)
    {
        debounceTime = millis();
    }

    if ((millis() - debounceTime) > delayTime)
    {
        if (currentState != previousState)
        {
            previousState = currentState;

            // nur dann "true" zurückgeben, wenn der Taster gedrückt ist (der Zustand ist LOW)
            if (currentState == LOW)
            {
                return true;
            }
        }
    }

    return false;
}

void loop()
{

    if (buttonPressed)
    {
        if (loopRunning)
        {
            stopLoop();
        }
        else
        {
            startLoop();
        }
        buttonPressed = false; // Setzen Sie die Variable zurück, nachdem der Button-Druck behandelt wurde
    }

    if (loopRunning)
    {
        digitalWrite(ledPin, LOW);

        if (Serial.available() > 0)
        {
            char receivedChar = Serial.read(); // Lese ein Zeichen von der seriellen Schnittstelle

            if (receivedChar == 'M')
            {
                motorActive = true;
            }
            else
            {
                eingabe = receivedChar - '0'; // Umwandlung des Zeichens in eine Zahl

                if (eingabe != previous_case)
                {
                    switch (eingabe)
                    {
                    case 1:
                        servo.write(90);        // Drehe den Servo auf Position 1 (30 Grad)
                        change_lcd_text("Gruen"); // Schreibe "Rot" in das Display
                        Motor.step(5);
                        break;

                    case 2:
                        servo.write(120);        // Drehe den Servo auf Position 2 (60 Grad)
                        change_lcd_text("Rot"); // Schreibe "Gelb" in das Display
                        Motor.step(5);
                        break;

                    case 3:
                        servo.write(150);        // Drehe den Servo auf Position 3 (90 Grad)
                        change_lcd_text("Gelb"); // Schreibe "Grün" in das Display
                        Motor.step(5);
                        break;

                    case 4:
                        change_lcd_text("Leer");
                        Motor.step(5);
                        break;
                    }

                    previous_case = eingabe; // Speichere den aktuellen Case-Wert
                }
            }
        }

        if (motorActive && (millis() - lastStepTime > stepInterval)) {
            lastStepTime = millis();
            Motor.step(1);
        }
    }
}

void change_lcd_text(const char *text)
{
    lcd.clear();         // Lösche das Display
    lcd.setCursor(0, 0); // Setze den Cursor auf die erste Zeile
    lcd.print(text);     // Schreibe den Text in das Display
}

void startLoop()
{
    blink_led(5, 50);
    change_lcd_text("Sorter startet ...");
    loopRunning = true;
}

void stopLoop()
{
    loopRunning = false;
    motorActive = false;
    blink_led(5, 50);
    change_lcd_text("Sorter gestoppt");
}

void handleButtonPress()
{
    buttonPressed = true;
}