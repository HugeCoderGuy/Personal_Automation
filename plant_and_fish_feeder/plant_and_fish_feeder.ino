const int dryA = 588;
const int wetA = 248;
const int wetB = 260;
const int dryB = 589;

void setup() {
  Serial.begin(9600);
  // Calibration data for each soil sensor


}

void loop() {
  // Take plant measurements and conver to percentage
  int sensorA = analogRead(A0);
  int sensorB = analogRead(A1);
  int percentageHumididyA = map(sensorA, dryA, wetA, 100, 0); 
  int percentageHumididyB = map(sensorB, wetB, dryB, 100, 0); 
  delay(100);
  Serial.println(percentageHumididyA);
//  if percentageHumididyA < 40{
//    
//  }
}
