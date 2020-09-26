import numpy as np
import array
import cv2,imutils
import time,math
import ColorRecognition as color
import serial
import sys
'''
gamemode
1 = setting
2 = play
'''
gamemode = 2
arduino_connect = 1
video_auto_transfer = 1
auto_get_limit = 1
path_prediction = 1
max_data_number = 3

if arduino_connect == 1:
    COM_PORT = 'COM7'  # 請自行修改序列埠名稱
    BAUD_RATES = 115200
    ser = serial.Serial(COM_PORT, BAUD_RATES)
    
ball_position_x = []
ball_position_y = []
y_yellow_point_dis = 1180 #mm

'''
L = 500 #Max_X_Distance of Ball & Computer
M_status = 0
Ddist = L ; Cdist = 0.6*L ; Bdist = 0.2*L ; Adist = 0.02*L  #Every leval of distance
Dsp = 200 ; Csp = 135 ; Bsp = 255 ; Asp = 355
'''

ser_dis = 0
max_x,min_x,max_y,min_y = None,None,None,None
blue_x,blue_y = None,None
vel = 0

cap = cv2.VideoCapture(0)
if __name__ == '__main__':
    while(True):
        # Capture frame-by-frame
        ret, frame= cap.read()
        start_time = time.time()
        #ColorRecognition
        ret_yellow = color.track_yellow_object(frame)
        if video_auto_transfer == 1:
            if ret_yellow:
                for i in range(len(ret_yellow)):
                    #cv2.rectangle( frame, (ret_yellow[i][0]-10, ret_yellow[i][1]-10), (ret_yellow[i][0]+10,ret_yellow[i][1]+10), (0,255,255), 2)
                    #print(i,'=',ret_yellow[i])
                    pass
                if len(ret_yellow) == 4:
                    ret_yellow.sort()
                    yellow_left = [ret_yellow[0], ret_yellow[1]]
                    yellow_right = [ret_yellow[2], ret_yellow[3]]
                    if yellow_left[0][1] > yellow_left[1][1]:
                        yellow_left_bottom = yellow_left[1]
                        yellow_left_top = yellow_left[0]
                    elif yellow_left[0][1] < yellow_left[1][1]:
                        yellow_left_bottom = yellow_left[0]
                        yellow_left_top = yellow_left[1]
                        
                    if yellow_right[0][1] >= yellow_right[1][1]:
                        yellow_right_bottom = yellow_right[1]
                        yellow_right_top = yellow_right[0]
                    else:
                        yellow_right_bottom = yellow_right[0]
                        yellow_right_top = yellow_right[1]
                    ret_yellow[0] = yellow_left_bottom
                    ret_yellow[1] = yellow_left_top
                    ret_yellow[2] = yellow_right_bottom
                    ret_yellow[3] = yellow_right_top
                    if len(ret_yellow) ==4:
                        out_range = 35
                        pts1 = np.float32([[ret_yellow[0][0] - out_range,ret_yellow[0][1] - out_range],
                                                    [ret_yellow[1][0] - out_range,ret_yellow[1][1] + out_range], 
                                                    [ret_yellow[2][0] + out_range,ret_yellow[2][1] - out_range], 
                                                    [ret_yellow[3][0] + out_range,ret_yellow[3][1] + out_range]])
                        #60 110
                        pts2 = np.float32([[0,0],[0,60*5],[110*5,0],[110*5,60*5]])
                        M = cv2.getPerspectiveTransform(pts1, pts2)
                        frame = cv2.warpPerspective(frame, M, (550,300))
                        #cv2.imshow('frame10',frame)
                elif len(ret_yellow) < 4:
                    print('yellow point is less than 4')
                elif len(ret_yellow) > 4:
                    print('yellow point is more than 4')
        ret_yellow = color.track_yellow_object(frame)
        if auto_get_limit == 1:
            if ret_yellow:
                yellow_x,yellow_y =[],[]
                for i in range(len(ret_yellow)):
                    cv2.rectangle( frame, (ret_yellow[i][0]-10, ret_yellow[i][1]-10), (ret_yellow[i][0]+10,ret_yellow[i][1]+10), (0,255,255), 2)
                    yellow_x.append(ret_yellow[i][0])
                    yellow_y.append(ret_yellow[i][1])
                max_x = max(yellow_x)
                min_x = min(yellow_x)
                max_y = max(yellow_y)
                min_y = min(yellow_y)
                cv2.rectangle(frame,(max_x,max_y), (min_x,min_y), (255,255,255), 2)
                #print(max_x,min_x,max_y,min_y)
        ret_red = color.track_red_object(frame)
        ret_blue = color.track_blue_object(frame)
        ret_green = color.track_green_object(frame)
        if ret_green:
            cv2.rectangle(frame,(ret_green[0] - 10,ret_green[1]-10), (ret_green[0] + 10,ret_green[1] + 10), (0,255,0), 2)
            green_x = ret_green[0]
            green_y = ret_green[1]
        else:
            print('unfind green')
        if ret_blue and ret_red:
            cv2.rectangle(frame,(ret_blue[0] - 10,ret_blue[1]-10), (ret_blue[0] + 10,ret_blue[1] + 10), (255,0,0), 2)
            blue_x = ret_blue[0]
            blue_y = ret_blue[1]
            cv2.rectangle( frame, (ret_red[0]-10, ret_red[1]-10), (ret_red[0]+10,ret_red[1]+10), (0,0,255), 2)
            red_x = ret_red[0]
            red_y = ret_red[1]
            ball_position_x.append(blue_x)
            ball_position_y.append(blue_y)
            if len(ball_position_x)>max_data_number:
                del ball_position_x[0]
                del ball_position_y[0]
            #print('ball_position_x = ',ball_position_x)
            #print('ball_position_y = ',ball_position_y)
            
            '''
            #Test
            Subtraction_x = blue_y - red_y
            abs_x = abs(Subtraction_x)
            #Mode_1  f(L) = 355, f(0.2L) = 135, f(0.02L) = 200
            a = ((Adist-Ddist)*(Csp-Asp)-(Bdist-Ddist)*(Dsp-Asp))/(((Adist-Ddist)*(Bdist-Ddist)*Bdist)-((Bdist-Ddist)*(Adist-Ddist)*Adist))
            b = ((Adist-Ddist)*Adist*(Csp-Asp)-(Bdist-Ddist)*Bdist*(Dsp-Asp))/((Adist-Bdist)*(Bdist-Ddist)*(Adist-Ddist))
            A = (a*abs_x+b)*(abs_x-Ddist)+Asp
            Encode_A = str(A).encode()
            #Mode_2  f(0.6L) = 355, f(0.2L) = 135, f(0.02L) = 255
            c = ((Adist-Cdist)*(Csp-Asp)-(Bdist-Cdist)*(Bsp-Asp))/(((Adist-Cdist)*(Bdist-Cdist)*Bdist)-((Bdist-Cdist)*(Adist-Cdist)*Adist))
            d = ((Adist-Cdist)*Adist*(Csp-Asp)-(Bdist-Cdist)*Bdist*(Bsp-Asp))/((Adist-Bdist)*(Bdist-Cdist)*(Adist-Cdist))
            B = (c*abs_x+d)*(abs_x-Cdist)+Asp
            Encode_B = str(B).encode()
            #Mode_3  f(0.2L) = 355 , f(0.02L) = 255
            C = ((Asp-Bsp)/(Bdist-Adist))*abs_x + (Bsp-Adist*((Asp-Bsp)/(Bdist-Adist)))
            Encode_C = str(C).encode()
            S = 0 #No speed to move
            Encode_S = str(S).encode()
            if M_status == 0 :
                if Ddist > abs_x  and Cdist <=abs_x :
                    M_status = 1
                elif Cdist > abs_x  and Bdist <=abs_x :
                    M_status = 2
                elif Bdist > abs_x  and Adist <=abs_x :
                    M_status = 3
                else :
                    M_status = 0
            '''
            
        else:
            if not ret_blue:
                print('unfind blue')
                if arduino_connect == 1:
                    ser.write(b'STOP\n')
                    print("STOP")
            if not ret_red:
                print('unfind red')
        if arduino_connect == 1:
            while ser.in_waiting:
                mcu_feedback = ser.readline().decode()  # 接收回應訊息並解碼
                print('Arduino feedback :', mcu_feedback)
                
                
        #if OPEN Path Prediction
        if path_prediction == 1 and vel != 0:
            if len(ball_position_x) >= max_data_number and len(ball_position_y) >= max_data_number:
                x0,y0 = ball_position_x[0],ball_position_y[0]
                x1,y1 = ball_position_x[max_data_number-1],ball_position_y[max_data_number-1]
                vel_time = 1
                if (x1-x0) != 0 : 
                    m = (y1-y0)/(x1-x0)
                else:
                    if y1 == y0:
                        m = None
                        #print('球未移動')
                    else:
                        m = None
                        x =blue_x
                        if y1 > y0:
                             y =blue_y + vel*vel_time
                             if y > max_y:
                                y = max_y
                        if y1 < y0:
                            y =blue_y - vel*vel_time
                            if y < min_y:
                                y = min_y
                        cv2.line( frame, (blue_x,blue_y), (int(x) , int(y)), (255,255,255), 2)
                        #print('垂直移動')
                    pass
                if m != None:
                    print('m = ',m)
                    deg_ball_dir = math.atan(m)
                    theta_ball_dir = deg_ball_dir/math.pi*180
                    print('theta_ball_dir = ',theta_ball_dir)
                    # 2象限 4象限
                    if m < 0:
                        #2象限
                        if (y1-y0) >0:
                            #print('2象限')
                            x = blue_x - math.cos(deg_ball_dir)*vel*vel_time
                            y = blue_y - math.sin(deg_ball_dir)*vel*vel_time
                            #超過上牆
                            if y > max_y:
                                last_dis_y = y - max_y
                                y = max_y
                                x = (y - y1)/m + x1
                                
                                y2 = y - last_dis_y
                                m2 = -m
                                x2 = (y2 - y)/m2 + x
                                if x2 < min_x:
                                    x2 = min_x
                                    y2 = m2*(x2 - x) + y
                                cv2.line( frame, (int(x) , int(y)), (int(x2) , int(y2)), (255,255,255), 2)
                        #4象限
                            #超過左牆
                            if x < min_x:
                                last_dis_x = x - min_x
                                x = min_x
                                y = m*(x - x1) + y1
                            cv2.line( frame, (blue_x,blue_y), (int(x) , int(y)), (255,255,255), 2)
                        #4象限
                        if (y1-y0) <0:
                            #print('4象限')
                            x = blue_x + math.cos(deg_ball_dir)*vel*vel_time
                            y = blue_y + math.sin(deg_ball_dir)*vel*vel_time
                            #超過下牆
                            if y < min_y:
                                last_dis_y = y - min_y
                                y = min_y
                                x = (y - y1)/m + x1
                                
                                x = (y - y1)/m + x1
                                y2 = y - last_dis_y
                                m2 = -m
                                x2 = (y2 - y)/m2 + x
                                if x2 > max_x:
                                    x2 = max_x
                                    y2 = m2*(x2 - x) + y
                                cv2.line( frame, (int(x) , int(y)), (int(x2) , int(y2)), (255,255,255), 2)
                            #超過右牆
                            if x > max_x:
                                last_dis_x = x - max_x
                                x = max_x
                                y = m*(x - x1) + y1
                            cv2.line( frame, (blue_x,blue_y), (int(x) , int(y)), (255,255,255), 2)
                    # 1象限 3象限
                    elif m > 0:
                        #1象限
                        if (y1-y0) >0:
                            #print('1象限')
                            x = blue_x + math.cos(deg_ball_dir)*vel*vel_time
                            y = blue_y + math.sin(deg_ball_dir)*vel*vel_time
                            #超過上牆
                            if y > max_y:
                                last_dis_y = y - max_y
                                y = max_y
                                x = (y - y1)/m + x1
                                
                                y2 = y - last_dis_y
                                m2 = -m
                                x2 = (y2 - y)/m2 + x
                                if x2 > max_x:
                                    x2 = max_x
                                    y2 = m2*(x2 - x) + y
                                cv2.line( frame, (int(x) , int(y)), (int(x2) , int(y2)), (255,255,255), 2)                                
                            #超過右牆
                            if x > max_x:
                                last_dis_x = x - max_x
                                x = max_x
                                y = m*(x - x1) + y1
                            cv2.line( frame, (blue_x,blue_y), (int(x) , int(y)), (255,255,255), 2)
                        #3象限
                        if (y1-y0) <0:
                            #print('3象限')
                            x = blue_x - math.cos(deg_ball_dir)*vel*vel_time
                            y = blue_y - math.sin(deg_ball_dir)*vel*vel_time
                            #超過下牆
                            if y < min_y:
                                last_dis_y = y - min_y
                                y = min_y
                                x = (y - y1)/m + x1
                                
                                y2 = y - last_dis_y
                                m2 = -m
                                x2 = (y2 - y)/m2 + x
                                if x2 < min_x:
                                    x2 = min_x
                                    y2 = m2*(x2 - x) + y
                                cv2.line( frame, (int(x) , int(y)), (int(x2) , int(y2)), (255,255,255), 2)
                            #超過左牆
                            if x < min_x:
                                last_dis_x = x - min_x
                                x = min_x
                                y = m*(x - x1) + y1
                            cv2.line( frame, (blue_x,blue_y), (int(x) , int(y)), (255,255,255), 2)
                    
                
        #gamemode setting
        if gamemode ==1:
            pass
        #used to play
        elif gamemode == 2:
            if ret_red and ret_blue:
                pos_red_blue = ret_red[1] - ret_blue[1]+20
                pos_red_blue_y = ret_red[0] - ret_blue[0]
                if (pos_red_blue > 8):  #Right
                    #Mode_1  Range : L~0.6L
                    ser.write(b'RIGHT\n')
                    print("RIGHT")
                    
                elif (pos_red_blue < -8):  #Left
                    #Mode_1  Range : L~0.6L
                    ser.write(b'LEFT\n')
                    print("LEFT")
                elif ret_blue[0] > min_x+220:
                    if ret_red[0] < min_x + 80:
                        ser.write(b'PUSH\n')
                        print("PUSH")
                    elif ret_red[0] > min_x + 100:
                        ser.write(b'BACK\n')
                        print("BACK")
                    else:
                        ser.write(b'STOP\n')
                        print("STOP")
                elif ret_blue[0] < min_x+220 and ret_blue[0] > ret_red[0]:
                    ser.write(b'PUSH\n')
                    print("PUSH")
                else:
                    ser.write(b'STOP\n')
                    print("STOP")
                #cv2.line( frame, (min_x+90,min_y), (min_x+90 , max_y), (255,255,0), 2)
                #cv2.line( frame, (min_x+220,min_y), (min_x+220 , max_y), (255,255,0), 2)
                '''
                elif blue_x < red_x:  #UP
                    #Mode_1  Range : L~0.6L
                    ser.write(b'RIGHT\n')
                    print("RIGHT")
                elif blue_x > red_x:  #Down
                    #Mode_1  Range : L~0.6L
                    ser.write(b'Left\n')
                    print("LEFT")
                '''
                #print('pos_red_blue=',pos_red_blue)
        end_time = time.time()
        dt = end_time - start_time
        dt = int(dt*10000)/10
        if dt != 0:
            #print('time took : ',dt,'ms')
            if len(ball_position_x) > max_data_number-1:
                ball_dis_x = ball_position_x[max_data_number-1] - ball_position_x[max_data_number-2]
                ball_dis_y = ball_position_y[max_data_number-1] - ball_position_y[max_data_number-2] 
                ball_dis = math.sqrt(ball_dis_x**2+ball_dis_y**2)
                #print('ball_dis : ',ball_dis,'pix')
                vel = ball_dis / dt
                y_pix = max_y - min_y
                pix_dis = y_yellow_point_dis / y_pix
                vel = vel * pix_dis * 10
                #print('y_pix = ',y_pix)
                vel = int(vel*100)/100
        else:
            #print('0')
            vel = 0.0
        #frame = imutils.rotate_bound(frame, 90)
        cv2.line( frame, (max_x,min_y), (max_x , max_y), (255,255,0), 2)
        #frame = cv2.flip(frame,0)
        if not ret_blue:
            vel = 0.0
        cv2.putText(frame, str(vel)+'mm/s', (35,500), cv2.FONT_HERSHEY_SIMPLEX,1, (0, 255, 0 ), 2, cv2.LINE_AA)
        cv2.imshow('frame2',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        time.sleep(0.1)
    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()
