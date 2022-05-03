#include <Adafruit_NeoPixel.h>

//////////////////////////////Pixel Setup///////////////////////////////
bool pixel_state =    false;
uint16_t hue =        0;
#define LED    6

// How many NeoPixels are attached to the Arduino?
#define LED_COUNT 60

// Declare our NeoPixel strip object:
Adafruit_NeoPixel strip(LED_COUNT, LED, NEO_GRB + NEO_KHZ800);
// Argument 1 = Number of pixels in NeoPixel strip
// Argument 2 = Arduino pin number (most are valid)
// Argument 3 = Pixel type flags, add together as needed:
//   NEO_KHZ800  800 KHz bitstream (most NeoPixel products w/WS2812 LEDs)
//   NEO_KHZ400  400 KHz (classic 'v1' (not v2) FLORA pixels, WS2811 drivers)
//   NEO_GRB     Pixels are wired for GRB bitstream (most NeoPixel products)
//   NEO_RGB     Pixels are wired for RGB bitstream (v1 FLORA pixels, not v2)
//   NEO_RGBW    Pixels are wired for RGBW bitstream (NeoPixel RGBW products)


//////////////////////////////Switch Setup//////////////////////////////

int     button_switch =                       2; // external interrupt pin

#define switched                            true // value if the button switch has been pressed
#define triggered                           true // controls interrupt handler
#define interrupt_trigger_type            RISING // interrupt triggered on a RISING input
#define debounce                              10 // time to wait in milli secs

volatile  bool interrupt_process_status = {
  !triggered                                     // start with no switch press pending, ie false (!triggered)
};
bool initialisation_complete =            false; // inhibit any interrupts until initialisation is complete

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
      if (digitalRead(button_switch) == HIGH) {
        // button pressed, so we can start the read on/off + debounce cycle wich will
        // be completed by the button_read() function.
        interrupt_process_status = triggered;  // keep this ISR 'quiet' until button read fully completed
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
    if (button_reading == HIGH) {
      // switch is pressed, so start/restart wait for button relealse, plus end of debounce process
      switching_pending = true;
      elapse_timer = millis(); // start elapse timing for debounce checking
    }
    if (switching_pending && button_reading == LOW) {
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

void setup() {
  strip.begin();
  strip.show(); // Initialize all pixels to 'off'  pinMode(button_switch, INPUT);
  attachInterrupt(digitalPinToInterrupt(button_switch),
                  button_interrupt_handler,
                  interrupt_trigger_type);
  initialisation_complete = true; // open interrupt processing for business
} // end of setup function

void loop() {
  // test buton switch and process if pressed
  if (read_button() == switched) {
    // button on/off cycle now complete, so flip LED between HIGH and LOW
    pixel_state = !pixel_state;
  } if (pixel_state = true) {
    uint32_t rgbcolor = strip.ColorHSV(hue);
    strip.fill(rgbcolor);
    hue++; 
    hue++;
    // Prevet overflow of hue variable
    if (hue = 65534) {
      hue = 0;
    }
  }
}
