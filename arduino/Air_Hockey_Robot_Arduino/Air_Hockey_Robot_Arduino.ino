#include "Configuration.h"

void loop() {
  Limit();
  Limit_S();
  yield();
  vry_data = analogRead(vry);//Read joystick_y
  y_a = ((-5.943853187337017e-09*vry_data) -0.001489921903057)*(vry_data-1013)*(vry_data-10)+150;//To cpurt the Y_speed's equation
  if (vry_data > 494 && vry_data < 530){//Range = 1023 於512為中點
    ;
  }
  else if (vry_data > 530){
    readString = "";
    Y_acc(y_a,true,stps);   //Run by joystick
    Y_Motor_s = true;
  }
  else if (vry_data < 494){
    readString = "";
    Y_acc(y_a,false,stps);  //Run by joystick
    Y_Motor_s = false;
  }
}
