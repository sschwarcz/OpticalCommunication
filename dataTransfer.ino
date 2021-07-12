
// Variables will change:
int ledState = LOW;             // ledState used to set the LED

// Generally, you should use "unsigned long" for variables that hold time
// The value will quickly become too large for an int to store
unsigned long previousMillis = 0;        // will store last time LED was updated

// constants won't change:
const long interval = 100;           // interval at which to blink (milliseconds)
const long messageSpeed = 300;
const long delayedTime = 5000;
const long signalTime = 8000;
const long timeOverTarget = 300000;
String eOf = "01111111";
String message = String("0100001001101111011000010111101000100000011010010111001100100000011101000110100001100101001000000110101101101001011011100110011100100001"+eOf);
int package_size = 8;
bool sent = false;
bool started = false;
int count = 0;
void setup() {
  // set the digital pin as output:
  pinMode(4, OUTPUT);
}

void loop() {
  // here is where you'd put code that needs to be running all the time.

  // check to see if it's time to blink the LED; that is, if the difference
  // between the current time and last time you blinked the LED is bigger than
  // the interval at which you want to blink the LED.
  unsigned long currentMillis = millis();
  if(currentMillis >= signalTime){
    if (started == false && sent == false)
    {
      started = true;
      digitalWrite(4, LOW);
      delay(delayedTime);
      digitalWrite(4, HIGH);
      delay(messageSpeed-100);
      for(int i = 0; i < message.length(); i++)
        {
       if(message[i] == '1')
        {
        digitalWrite(4, HIGH);
        delay(messageSpeed);
        count++;
        }
       if(message[i]=='0') {
        digitalWrite(4, LOW);
        delay(messageSpeed);
        count++;
        }
      if(count == package_size && i < message.length()-1){
       count = 0;
      digitalWrite(4, LOW);
      delay(100);
      digitalWrite(4, HIGH);
      delay(messageSpeed-100);
        }
      }
      digitalWrite(4, LOW);
      delay(6000);
      sent = true;
      }
    }
  else if (currentMillis < signalTime && currentMillis - previousMillis >= interval) {
    // save the last time you blinked the LED
    sent = false;
    previousMillis = currentMillis;

    // if the LED is off turn it on and vice-versa:
    if (ledState == LOW) {
      ledState = HIGH;
    } else {
      ledState = LOW;
    }

    // set the LED with the ledState of the variable:
    digitalWrite(4, ledState);
  }
}
