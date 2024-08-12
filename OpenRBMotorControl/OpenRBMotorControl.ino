#include <Dynamixel2Arduino.h>

#define DXL_SERIAL   Serial1
#define NICLA_SERIAL Serial3

Dynamixel2Arduino dxl(DXL_SERIAL, -1);
const uint8_t DXL_ID_1 = 1;
const uint8_t DXL_ID_2 = 3;
const float DXL_PROTOCOL_VERSION = 2.0;

void setup() {
  // Laptop to OpenRB Serial
  Serial.begin(9600);
  pinMode(LED_BUILTIN, OUTPUT);
  dxl.begin(57600);
  dxl.setPortProtocolVersion(DXL_PROTOCOL_VERSION);
  //OpenRB to niclavision
  NICLA_SERIAL.begin(115200);

  digitalWrite(LED_BUILTIN, HIGH);
  Serial.println("Listening to Nicla! \n");

  //Motor Setup
  dxl.ping(DXL_ID_1);
  dxl.ping(DXL_ID_2);

  // Turn off torque when configuring items in EEPROM area
  dxl.torqueOff(DXL_ID_1);
  dxl.setOperatingMode(DXL_ID_1, OP_VELOCITY);
  dxl.torqueOn(DXL_ID_1);

  // Turn off torque when configuring items in EEPROM area
  dxl.torqueOff(DXL_ID_2);
  dxl.setOperatingMode(DXL_ID_2, OP_VELOCITY);
  dxl.torqueOn(DXL_ID_2);
}

// Variable for storing incoming data
String incoming = ""; 
int v_l = 0;
int v_r = 0;
int vel_incr = 10;

bool RUN_STATUS = false;

void loop() {
  // Check for available data and read individual characters
  
  /*while(!NICLA_SERIAL.available()) {
    Serial.println("Checking for Connection with Nicla");
    delay(5000);
  }*/
  while (NICLA_SERIAL.available()) {
    // Allow data buffering and read a single character
    delay(2); 
    char c = NICLA_SERIAL.read();
    
    // Check if the character is a newline (line-ending)
    if (c == '\n') {
      // Process the received data
      Serial.print("Message from Nicla: ");
      Serial.println(incoming);
      
      if (incoming=="Forward") {

        v_l = 60;
        v_r = -1* v_l;
        RUN_STATUS = true;
        Serial.print("Motor in forward mode \n");

      } else if (incoming == "Reverse") {

        if(RUN_STATUS) {
          v_l = -60;
          v_r = -1*v_l;
        }

      } else if (incoming == "Left") {
     
          v_l = 5;
          v_r = 50;
        
      } else if (incoming == "Right") {
        
        v_l = 50;
        v_r = 5;      

      } else if (incoming == "Stop") {
        
        RUN_STATUS = false;
        v_l = 0;
        v_r = 0;       

      } else {

        v_l = 0;
        v_r = 0;

      }

      
      dxl.setGoalVelocity(DXL_ID_1, v_l, UNIT_RPM);
      Serial.print("Present Velocity(rpm) : ");
      Serial.println(dxl.getPresentVelocity(DXL_ID_1, UNIT_RPM));

      dxl.setGoalVelocity(DXL_ID_2, v_r, UNIT_RPM);
      Serial.print("Present Velocity(rpm) : ");
      Serial.println(dxl.getPresentVelocity(DXL_ID_2, UNIT_RPM));


      // Clear the incoming data string for the next message
      incoming = ""; 
      NICLA_SERIAL.write("Message executed \n");

    } else {
      // Add the character to the incoming data string
      incoming += c; 
    }
    
    /*delay(500);
    digitalWrite(LED_BUILTIN,LOW);
    delay(500);
    digitalWrite(LED_BUILTIN, HIGH);*/
    //Serial.println("Loop Last line");
  }



  //Serial.println(incoming);
}
