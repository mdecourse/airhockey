#include "SCoop.h"
#define EN 8       //步進馬達使能端
#define X_DIR 5    //X軸 步進馬達方向控制
#define Y_DIR 6    //y軸 步進馬達方向控制
#define YY_DIR 7   //y軸 步進馬達方向控制
#define X_STP 2    //x軸 步進控制
#define Y_STP 3    //y軸 步進控制
#define YY_STP 4   //y軸 步進控制
#define X_LIMIT_R 9  //x軸右側 極限開關 
#define X_LIMIT_L 10 //x軸左側 極限開關
#define Y_LIMIT 11  //y軸 極限開關
#define vrx A0     //joystick-Abort
#define vry A1     //coolEn

int X_state = 0;
int Y_state = 0;
int vrx_data = 0; 
int vry_data = 0;
boolean X_Motor_s;
boolean Y_Motor_s;
String readString;
int x_a = 0;
int y_a = 0; 
int stps = 20;
int Limit_Situasion = 1;

void setup() {
  mySCoop.start();
  Serial.begin(115200);
  pinMode(X_DIR, OUTPUT);
  pinMode(X_STP, OUTPUT);
  pinMode(Y_DIR, OUTPUT);
  pinMode(Y_STP, OUTPUT);
  pinMode(YY_DIR, OUTPUT);
  pinMode(YY_STP, OUTPUT);
  pinMode(EN, OUTPUT);
  pinMode(X_LIMIT_R, INPUT);
  pinMode(X_LIMIT_L, INPUT);
  pinMode(Y_LIMIT, INPUT);
  digitalWrite(EN, LOW);
  //X_Motor_s = true;
  //Y_Motor_s = true;
}
