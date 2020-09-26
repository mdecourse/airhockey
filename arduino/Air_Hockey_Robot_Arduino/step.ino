/*
M-maxspeed:130?
N-maxspeed:450
minspeed:3200
Turns:14 approximately
約600步/圈=>40mm
寬約11圈又16mm=240步,1mm=15步
*/

void Y_acc(word Micro,boolean dir,word stps){//順轉false  -頭朝下則逆轉:向後，逆轉true  -頭朝下則順轉:向前
  digitalWrite(Y_DIR,dir);
  digitalWrite(YY_DIR,dir);
  for (long int i = 0; i < stps; i++){
    if (i%3 ==0) {
      digitalWrite(Y_STP, HIGH);
      digitalWrite(YY_STP,HIGH);
      delayMicroseconds(Micro);
      digitalWrite(Y_STP, LOW);
      digitalWrite(YY_STP,LOW);
      delayMicroseconds(Micro);
    }
  }
}

void X_acc(word Micro,boolean dir,word stps){//順轉  -頭朝下則逆轉:向右，逆轉  -頭朝下則順轉:向左
  digitalWrite(X_DIR,dir);
  for (long int i = 0; i < stps; i++){
    if (i%3 ==0) {
      digitalWrite(X_STP, HIGH);
      delayMicroseconds(Micro);
      digitalWrite(X_STP, LOW);
      delayMicroseconds(Micro);
    }
  }
}
