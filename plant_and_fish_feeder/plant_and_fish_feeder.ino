String myAPIkey = "6YCDUHSJGWKFG6L0";  

const int dryA = 588;
const int wetA = 248;
const int wetB = 260;
const int dryB = 589;

#include <SoftwareSerial.h>
#include <DHT.h>;
SoftwareSerial ESP8266(2, 3); // Rx,  Tx

#define DHTTYPE DHT11
#define DHTPIN  A0

DHT dht(DHTPIN, DHTTYPE,11);
float humidity, temp_f, temp_c;  
long writingTimer = 17; 
long startTime = 0;
long waitTime = 0;


boolean relay1_st = false; 
boolean relay2_st = false; 
unsigned char check_connection=0;
unsigned char times_check=0;
boolean error;

void setup()
{
  Serial.begin(9600); 
  ESP8266.begin(9600); 
   dht.begin();
  startTime = millis(); 
  ESP8266.println("AT+RST");
  delay(2000);
  Serial.println("Connecting to Wifi");
   while(check_connection==0)
  {
    Serial.print(".");
  ESP8266.print("AT+CWJAP=\"Portami-al-Mare\",\"184318aaea\"\r\n");
  ESP8266.setTimeout(5000);
 if(ESP8266.find("WIFI CONNECTED\r\n")==1)
 {
 Serial.println("WIFI CONNECTED");
 break;
 }
 times_check++;
 if(times_check>3) 
 {
  times_check=0;
   Serial.println("Trying to Reconnect..");
  }
  }
}

void loop()
{
  waitTime = millis()-startTime;   
  if (waitTime > (writingTimer*1000)) 
  {
    readSensors();
    writeThingSpeak();
    startTime = millis();   
  }
}


void readSensors(void)
{
  temp_c = dht.readTemperature();
  humidity = dht.readHumidity();
  temp_f = (temp_c * 1.8) + 32;
  Serial.println(temp_c);
  Serial.println(temp_f);
}


void writeThingSpeak(void)
{
  int sensorA = analogRead(A1);
  int sensorB = analogRead(A2);
  int percentageHumididyA = map(sensorA, dryA, wetA, 100, 0); 
  int percentageHumididyB = map(sensorB, wetB, dryB, 100, 0);
  startThingSpeakCmd();
  Serial.println(temp_f, humidity);
  // preparacao da string GET
  String getStr = "GET /update?api_key=";
  getStr += myAPIkey;
  getStr +="&field1=";
  getStr += String(percentageHumididyA);
  //getStr +="&field2=";
  //getStr += String(percentageHumididyB);
  getStr +="&field3=";
  getStr += String(temp_f);
  getStr +="&field4=";
  getStr += String(humidity);
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
      String line = ESP8266.readStringUntil('\n');
      if (line.length() == 1) 
      { 
        messageBody = ESP8266.readStringUntil('\n');
      }
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
