///////////// Libraries /////////////
#include <SoftwareSerial.h>
#include <DHT.h>;
#include <Adafruit_NeoPixel.h>
#include <ArduinoJson.h>
#include <LiquidCrystal.h>



///////////// Variable Decleratio /////////////


/// ESP WIFI
SoftwareSerial ESP8266(10, 11); // Rx,  Tx

String myAPIkey = "6YCDUHSJGWKFG6L0";
//String iq_air_key = "7cf2a06d-08f8-470d-9da2-7d63e31db776";
//String aqi_url = "http://api.waqi.info/feed/Alameda/?token=6b47ef379c416b27e36c33d9e9d4095789221068";
//String weatherbit_key = "47b0a5c7a0ba4c9bb10b4c6161315faa";


// LCD Setup
const int rs = 48, en = 49, d4 = 53, d5 = 52, d6 = 51, d7 = 50;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);
#define LCD_Backlight 3 // 15. BL1 - Backlight +                                Emitter of 2N3904, Collector to VCC, Base to D10 via 10K resistor


// setup DHT Sensor
#define DHTTYPE     DHT11
#define DHTPIN      46
DHT dht(DHTPIN, DHTTYPE,11);

#define LIGHTP      A15

//variable declaration
byte humidity, temp_f, temp_c;
byte house_plants = 0;
byte jap_maple = 0;
unsigned int light;
byte writingTimer = 17;
unsigned long startTime = 0;
unsigned long waitTime = 0;


boolean relay1_st = false;
boolean relay2_st = false;
unsigned char check_connection=0;
unsigned char times_check=0;
boolean error;

/// Buttons and lights
uint16_t hue =  0;
bool pixel_state;
#define LED    6
byte     button_switch =                       18; // external interrupt pin
byte     tree_switch =                         19; // external interrupt pin
byte     house_switch =                        20; // external interrupt pin

#define switched                            true // value if the button switch has been pressed
#define triggered                           true // controls interrupt handler
#define interrupt_trigger_type            FALLING// interrupt triggered on a RISING input
#define debounce                              10 // time to wait in milli secs

volatile  bool interrupt_process_status = {
  !triggered                                     // start with no switch press pending, ie false (!triggered)
};
volatile  bool tree_interrupt_process_status = {
  !triggered                                     // start with no switch press pending, ie false (!triggered)
};
volatile  bool house_interrupt_process_status = {
  !triggered                                     // start with no switch press pending, ie false (!triggered)
};
bool initialisation_complete =            false; // inhibit any interrupts until initialisation is complete


// Declare our NeoPixel strip object:
#define LED_COUNT 4
Adafruit_NeoPixel strip(LED_COUNT, LED);

///////////// Program Initialization /////////////
void setup()
{
  Serial.begin(9600);
  ESP8266.begin(9600);
  dht.begin();

  bool pixel_state = false;
  strip.begin();
  strip.show(); // Initialize all pixels to 'off'

  // setup LCD
  lcd.begin(16, 2);

  // button setup
  pinMode(button_switch, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(button_switch),
                  button_interrupt_handler,
                  interrupt_trigger_type);

  // plant buttons setup
  attachInterrupt(digitalPinToInterrupt(tree_switch),
                  button_interrupt_handler_tree,
                  interrupt_trigger_type);
  attachInterrupt(digitalPinToInterrupt(house_switch),
                  button_interrupt_handler_house,
                  interrupt_trigger_type);

  // Wifi setup
  startTime = millis();
  ESP8266.println("AT+RST");
  delay(2000);
  Serial.println("Connecting to Wifi");
  lcd.print(" Connecting to");
  lcd.setCursor(0,1);
  lcd.print("      Wifi...");
   while(check_connection==0)
  {
    Serial.print(".");
  ESP8266.print("AT+CWJAP=\"Portami-al-Mare\",\"184318aaea\"\r\n");
  ESP8266.setTimeout(5000);
  if(ESP8266.find("WIFI CONNECTED\r\n")==1)
{
    Serial.println("WIFI CONNECTED");
    lcd.clear();
    lcd.print("WIFI CONNECTED");
    lcd.setCursor(0,1);
    lcd.print("       :)");
 break;
 }
 times_check++;
 if(times_check>3)
 {
  times_check=0;
   Serial.println("Trying to Reconnect..");
  }
  }
  initialisation_complete = true; // open interrupt processing for business

}

void loop()
{
  waitTime = millis()-startTime;
  if (waitTime > (writingTimer*1000))
  {
    readSensors();
    lcd.clear();
    lcd.print("    API CALL");
    writeThingSpeak();
    //writeAQIapi();

    startTime = millis();
  }

  // test button switch and process if pressed
  if (read_button() == switched) {
    // button on/off cycle now complete, so flip LED between HIGH and LOW
    pixel_state = !pixel_state;
    lcd.clear();
    lcd.print("Jellyfish On!");

  } if (pixel_state == true) {
    uint32_t rgbcolor = strip.ColorHSV(hue);
    strip.fill(rgbcolor);
    strip.show();
    hue += 25;
    // Prevet overflow of hue variable
    if (hue >= 65534) {
      hue = 0;
    }
  } else {
    lcd.clear();
    lcd.print("Jellyfish Off!");
    strip.fill(0, 0, 0);
    strip.show();
  }

  if (read_button_tree == switched) {
    jap_maple = 100;
     }

  if (read_button_tree == switched) {
    house_plants = 100;
    }
  if (jap_maple == 100 or house_plants == 100){
    writeThingSpeakPlants();
    jap_maple = 0;
    house_plants = 0;
    }

  // Save some energy by turning off the LCD at night
  if (light <= 100) {
    lcd.clear();
    lcd.print("Goodnight Sweet");
    lcd.setCursor(0,1);
    lcd.print("     Prince     ");
    for (int i = 0; i <= 250; i += 1) {
      analogWrite(LCD_Backlight, i);
    }
    lcd.noDisplay();
  }
  else {
    analogWrite(LCD_Backlight, 128);

    lcd.display();
    lcd.clear();
    lcd.print(" I Have Awaken! ");
    lcd.setCursor(0,1);
    lcd.print("       :)       ");
    delay(1000);
  }

}

///////////// Function Declaration /////////////

/// ESP8266 Wifi fuctios
void readSensors(void)
{
  temp_c = dht.readTemperature();
  humidity = dht.readHumidity();
  temp_f = (temp_c * 1.8) + 32;
  light = analogRead(LIGHTP);

  Serial.println(temp_c);
  Serial.println(temp_f);
  Serial.println(light);
}


void writeThingSpeak(void)
{
  startThingSpeakCmd();
  // preparacao da string GET
  String getStr = "GET /update?api_key=";
  getStr += myAPIkey;
  getStr +="&field3=";
  getStr += String(temp_f);
  getStr +="&field4=";
  getStr += String(humidity);
  getStr += "\r\n\r\n";
  GetThingspeakcmd(getStr);
}

void writeThingSpeakPlants(void)
{
  startThingSpeakCmd();
  String getStr = "GET /update?api_key=";
  getStr += myAPIkey;
  getStr +="&field5=";
  getStr += String(house_plants);
  getStr +="&field6=";
  getStr += String(jap_maple);
  getStr += "\r\n\r\n";
  GetThingspeakcmd(getStr);
}

void startThingSpeakCmd(void)
{
  ESP8266.flush();
  String cmd = "AT+CIPSTART=\"TCP\",\"";
  cmd += "184.106.153.149"; // api.thingspeak.com IP address
  cmd += "\",80";
  ESP8266.println(cmd);
  Serial.print("Start Commands: ");
  Serial.println(cmd);

  if(ESP8266.find("Error"))
  {
    Serial.println("AT+CIPSTART error");
    return;
  }
}

String GetThingspeakcmd(String getStr)
{
  String cmd = "AT+CIPSEND=";
  cmd += String(getStr.length());
  ESP8266.println(cmd);
  Serial.println(cmd);

  if(ESP8266.find(">"))
  {
    ESP8266.print(getStr);
    Serial.println(getStr);
    delay(500);
    String messageBody = "";
    while (ESP8266.available())
    {
      Serial.println(ESP8266.readStringUntil('\n')); 

//      String line = ESP8266.readStringUntil('\n');
//      if (line.length() == 1)
//      {
//        messageBody = ESP8266.readStringUntil('\n');
//      }
    }
    Serial.print("MessageBody received: ");
    Serial.println(messageBody);
    return messageBody;
  }
  else
  {
    ESP8266.println("AT+CIPCLOSE");
    Serial.println("AT+CIPCLOSE");
  }
}


// AQI API Call
void writeAQIapi(void)
{
  startAQIapi();
  // preparacao da string GET
  //String getStr = "GET /feed/Alameda/?token=6b47ef379c416b27e36c33d9e9d4095789221068";
  //String getStr = "GET /aq/observation/latLong/current/?format=text/csv&latitude=37.7878&longitude=-122.2744&distance=1&API_KEY=33628645-4EE3-4D27-A826-479EDB82E726";
  //getStr += "\r\n\r\n";
  //Serial.print(getStr);
  GetAQIapi();
}


void startAQIapi(void)
{
  ESP8266.flush();
  String cmd = "AT+CIPSTART=\"TCP\",\"";
  //cmd += "134.67.21.55"; //airow.gov
  //cmd += "13.230.108.239"; //iqair
  //cmd += "192.155.89.79"; //weatherbit
  //cmd += "104.98.206.72";
  cmd += "3.20.208.175"; //airowapi.gov
  cmd += "\",80";
  ESP8266.println(cmd);
  Serial.print("Start Commands: ");
  Serial.println(cmd);

  if(ESP8266.find("Error"))
  {
    Serial.println("AT+CIPSTART error");
    return;
  }
}

// SERIAL.WRITEEE VS SEREIAL PRIT
String GetAQIapi(void)
{
  //String getStr = "GET /aq/observation/zipCode/current/?format=application/json&zipCode=94501&distance=3&API_KEY=33628645-4EE3-4D27-A826-479EDB82E726";

  String cmd = "AT+CIPSEND=";   
  //int getStr_l = getStr.length();
  //cmd += String(getStr_l);  ///////ISSUE WITH LEGTH
  cmd += "130";
  ESP8266.println(cmd);
  Serial.println(cmd);
  if(ESP8266.find(">"))
  {
    ESP8266.print("GET /aq/observation/zipCode/current/?format=application/json&zipCode=94501&distance=3&API_KEY=33628645-4EE3-4D27-A826-479EDB82E726");
    Serial.println("GET /aq/observation/zipCode/current/?format=application/json&zipCode=94501&distance=3&API_KEY=33628645-4EE3-4D27-A826-479EDB82E726");
    delay(500);
    String messageBody = "";
    while (ESP8266.available())
    {
      Serial.println(ESP8266.readStringUntil('\n')); 
      //messageBody += ESP8266.readStringUntil('\n');
      String line = ESP8266.readStringUntil('\n');
      if (line.length() == 1)
      {
        messageBody = ESP8266.readStringUntil('\n');
        Serial.println(messageBody);
      }
    }
    Serial.print("MessageBody received: ");
    Serial.println(messageBody);
    //DeserializationError error = deserializeJson(doc, messageBody);

    // Test if parsing succeeds.
//    if (error) {
//    Serial.print(F("deserializeJson() failed: "));
//    Serial.println(error.f_str());
//    return;
//  }
    return messageBody;
  }
  
  else
  {
    ESP8266.println("AT+CIPCLOSE");
    Serial.println("AT+CIPCLOSE");
  }
}




// Button interrupt functions
//
// ISR for handling interrupt triggers arising from associated button switch
//
void button_interrupt_handler()
{
  if (initialisation_complete == true)
  { //  all variables are initialised so we are okay to continue to process this interrupt
    if (interrupt_process_status == !triggered) {
      // new interrupt so okay start a new button read process -
      // now need to wait for button release plus debounce period to elapse
      // this will be done in the button_read function
      if (digitalRead(button_switch) == LOW) {
        // button pressed, so we can start the read on/off + debounce cycle wich will
        // be completed by the button_read() function.
        interrupt_process_status = triggered;  // keep this ISR 'quiet' until button read fully completed
        Serial.print("the button works!");
      }
    }
  }
} // end of button_interrupt_handler
void button_interrupt_handler_tree()
{
  if (initialisation_complete == true)
  { //  all variables are initialised so we are okay to continue to process this interrupt
    if (interrupt_process_status == !triggered) {
      // new interrupt so okay start a new button read process -
      // now need to wait for button release plus debounce period to elapse
      // this will be done in the button_read function
      if (digitalRead(tree_switch) == LOW) {
        // button pressed, so we can start the read on/off + debounce cycle wich will
        // be completed by the button_read() function.
        tree_interrupt_process_status = triggered;  // keep this ISR 'quiet' until button read fully completed
      }
    }
  }
} // end of button_interrupt_handler
void button_interrupt_handler_house()
{
  if (initialisation_complete == true)
  { //  all variables are initialised so we are okay to continue to process this interrupt
    if (interrupt_process_status == !triggered) {
      // new interrupt so okay start a new button read process -
      // now need to wait for button release plus debounce period to elapse
      // this will be done in the button_read function
      if (digitalRead(house_switch) == LOW) {
        // button pressed, so we can start the read on/off + debounce cycle wich will
        // be completed by the button_read() function.
        house_interrupt_process_status = triggered;  // keep this ISR 'quiet' until button read fully completed
      }
    }
  }
} // end of button_interrupt_handler

bool read_button() {
  int button_reading;
  // static variables because we need to retain old values between function calls
  static bool     switching_pending = false;
  static long int elapse_timer;
  if (interrupt_process_status == triggered) {
    // interrupt has been raised on this button so now need to complete
    // the button read process, ie wait until it has been released
    // and debounce time elapsed
    button_reading = digitalRead(button_switch);
    if (button_reading == LOW) {
      // switch is pressed, so start/restart wait for button relealse, plus end of debounce process
      switching_pending = true;
      elapse_timer = millis(); // start elapse timing for debounce checking
    }
    if (switching_pending && button_reading == HIGH) {
      // switch was pressed, now released, so check if debounce time elapsed
      if (millis() - elapse_timer >= debounce) {
        // dounce time elapsed, so switch press cycle complete
        switching_pending = false;             // reset for next button press interrupt cycle
        interrupt_process_status = !triggered; // reopen ISR for business now button on/off/debounce cycle complete
        return switched;                       // advise that switch has been pressed
      }
    }
  }
  return !switched; // either no press request or debounce period not elapsed
} // end of read_button function

// Tree read butto
bool read_button_tree() {
  int button_reading;
  // static variables because we need to retain old values between function calls
  static bool     switching_pending = false;
  static long int elapse_timer;
  if (tree_interrupt_process_status == triggered) {
    // interrupt has been raised on this button so now need to complete
    // the button read process, ie wait until it has been released
    // and debounce time elapsed
    button_reading = digitalRead(tree_switch);
    if (button_reading == LOW) {
      // switch is pressed, so start/restart wait for button relealse, plus end of debounce process
      switching_pending = true;
      elapse_timer = millis(); // start elapse timing for debounce checking
    }
    if (switching_pending && button_reading == HIGH) {
      // switch was pressed, now released, so check if debounce time elapsed
      if (millis() - elapse_timer >= debounce) {
        // dounce time elapsed, so switch press cycle complete
        switching_pending = false;             // reset for next button press interrupt cycle
        tree_interrupt_process_status = !triggered; // reopen ISR for business now button on/off/debounce cycle complete
        return switched;                       // advise that switch has been pressed
      }
    }
  }
  return !switched; // either no press request or debounce period not elapsed
} // end of read_button function

// houseplat read fuctio
bool read_button_house() {
  int button_reading;
  // static variables because we need to retain old values between function calls
  static bool     switching_pending = false;
  static long int elapse_timer;
  if (house_interrupt_process_status == triggered) {
    // interrupt has been raised on this button so now need to complete
    // the button read process, ie wait until it has been released
    // and debounce time elapsed
    button_reading = digitalRead(house_switch);
    if (button_reading == LOW) {
      // switch is pressed, so start/restart wait for button relealse, plus end of debounce process
      switching_pending = true;
      elapse_timer = millis(); // start elapse timing for debounce checking
    }
    if (switching_pending && button_reading == HIGH) {
      // switch was pressed, now released, so check if debounce time elapsed
      if (millis() - elapse_timer >= debounce) {
        // dounce time elapsed, so switch press cycle complete
        switching_pending = false;             // reset for next button press interrupt cycle
        interrupt_process_status = !triggered; // reopen ISR for business now button on/off/debounce cycle complete
        return switched;                       // advise that switch has been pressed
      }
    }
  }
  return !switched; // either no press request or debounce period not elapsed
} // end of read_button function
