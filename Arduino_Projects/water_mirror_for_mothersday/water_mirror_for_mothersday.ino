#define watermirror     A0
#define a               2
#define b               3
#define c               4
#define d               5
#define e               6
#define f               7
#define g               8
const int dryA = 595;
const int wetA = 248;
volatile int output;
int sensorA;


void setup() {
  Serial.begin(9600);
  Serial.print("doe with setup");
  // seven segment setup
  pinMode(a, OUTPUT);  //A
  pinMode(b, OUTPUT);  //B
  pinMode(c, OUTPUT);  //C
  pinMode(d, OUTPUT);  //D
  pinMode(e, OUTPUT);  //E
  pinMode(f, OUTPUT);  //F
  pinMode(g, OUTPUT);  //G
  
  for (int i = 2; i<=7; i++) {
    digitalWrite(i, HIGH);
    Serial.println(i);
    delay(500 );
  }
  
  turnOff();
  Serial.print("doe with setup");
}

void loop() {
  // put your main code here, to run repeatedly:
  sensorA = analogRead(watermirror);
  output = map(sensorA, dryA, wetA, 0, 10); 
  
  // update the digit
  turnOff();
  displayDigit(output);
 
  delay(250);

  
}

void displayDigit(int digit)
{
 //Conditions for displaying segment a
 if(digit!=1 && digit != 4)
 digitalWrite(a,HIGH);
 
 //Conditions for displaying segment b
 if(digit != 5 && digit != 6)
 digitalWrite(b,HIGH);
 
 //Conditions for displaying segment c
 if(digit !=2)
 digitalWrite(c,HIGH);
 
 //Conditions for displaying segment d
 if(digit != 1 && digit !=4 && digit !=7)
 digitalWrite(d,HIGH);
 
 //Conditions for displaying segment e 
 if(digit == 2 || digit ==6 || digit == 8 || digit==0)
 digitalWrite(e,HIGH);
 
 //Conditions for displaying segment f
 if(digit != 1 && digit !=2 && digit!=3 && digit !=7)
 digitalWrite(f,HIGH);
 if (digit!=0 && digit!=1 && digit !=7)
 digitalWrite(g,HIGH);
 
}

void turnOff()
{
  digitalWrite(a,LOW);
  digitalWrite(b,LOW);
  digitalWrite(c,LOW);
  digitalWrite(d,LOW);
  digitalWrite(e,LOW);
  digitalWrite(f,LOW);
  digitalWrite(g,LOW);
}
