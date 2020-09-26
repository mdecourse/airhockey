import sim
import time,array
import cv2, numpy
from PIL import Image as I
import ColorRecognition_multi as color

"""
0 = Auto Defense (done)
1 = Auto Attack + Defense (undone)
2 = Player + Player (Application) (undone)
3 = Auto Defense (Path Prediction) (undone)
"""
play_mode = 3
video_tranfer =0
#How much Ball_Position data save (min = 5)
data_number = 5
if data_number < 5:
    data_number = 5
    
ball_positionX = []
ball_positionY = []

wall_X_min = 35
wall_X_max = 215
wall_Y_min = 10
wall_Y_max = 465
# 0 = Stop
# 1 = Up or Right
# 2 = Down or Left
Ball_DirectionX_Movement = 0
Ball_DirectionX_Movement_last = 0
Ball_DirectionY_Movement = 0
Ball_DirectionY_Movement_last = 0
def speed( handle, speed):
    sim.simxSetJointTargetVelocity( clientID, handle, speed, sim.simx_opmode_oneshot_wait)


if __name__ == '__main__':
    sim.simxFinish(-1)
    clientID = sim.simxStart('127.0.0.1', 19997, True, True, 5000, 5)
    if clientID != -1:
        print('Connected to remote API server')
        # get vision sensor objects
        res, v0 = sim.simxGetObjectHandle(clientID, 'vs1', sim.simx_opmode_oneshot_wait)
        res, v1 = sim.simxGetObjectHandle(clientID, 'vs2', sim.simx_opmode_oneshot_wait)
        err, resolution, image = sim.simxGetVisionSensorImage(clientID, v0, 0, sim.simx_opmode_streaming)
        #get motor objects
        err,Ball_handle=sim.simxGetObjectHandle(clientID,'Ball', sim.simx_opmode_oneshot_wait)
        err,player_x_handle=sim.simxGetObjectHandle(clientID, 'player_x_joint', sim.simx_opmode_oneshot_wait)
        err,player_y_handle=sim.simxGetObjectHandle(clientID, 'player_y_joint', sim.simx_opmode_oneshot_wait)
        #main loop
        while (sim.simxGetConnectionId(clientID) != -1):
            #get vision sensor image
            start = time.time();
            err, resolution, image = sim.simxGetVisionSensorImage(clientID, v0, 0, sim.simx_opmode_buffer)
            #print(len(image))
            if err == sim.simx_return_ok:
                image_byte_array = array.array('b', image)
                image_buffer = I.frombuffer("RGB", (resolution[0],resolution[1]), bytes(image_byte_array), "raw", "RGB", 0, 1)
                img2 = numpy.asarray(image_buffer)
                #ColorRecognition
                if video_tranfer == 1:
                    ret_yellow = color.track_yellow_object(img2)
                    if ret_yellow:
                        for i in range(len(ret_yellow)):
                            #cv2.rectangle( frame, (ret_yellow[i][0]-10, ret_yellow[i][1]-10), (ret_yellow[i][0]+10,ret_yellow[i][1]+10), (0,255,255), 2)
                            yellow_y = ret_yellow[i][0]
                            yellow_x = ret_yellow[i][1]
                            #print(i,'=',ret_yellow[i])
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
                                print(ret_yellow)
                                out_range = 0
                                #cv2.rectangle( img2, (ret_yellow[0][0]-20, ret_yellow[0][1]-20), (ret_yellow[0][0]+20,ret_yellow[0][1]+20), (255,255,0), 5)
                                pts1 = numpy.float32([[ret_yellow[0][0] - out_range,ret_yellow[0][1] - out_range],
                                                            [ret_yellow[1][0] - out_range,ret_yellow[1][1] + out_range], 
                                                            [ret_yellow[2][0] + out_range,ret_yellow[2][1] - out_range], 
                                                            [ret_yellow[3][0] + out_range,ret_yellow[3][1] + out_range]])
                                #pts2 = numpy.float32([[0,0],[0,60*5],[110*5,0],[110*5,60*5]])
                                pts2 = numpy.float32([[0,0],[0,1024],[512,0],[512,1024]])
                                M = cv2.getPerspectiveTransform(pts1, pts2)
                                img2 = cv2.warpPerspective(img2, M, (512,1024))
                    else:
                        print('unfind yellow')
                # If Find Green,Blue,Red Object
                ret_green = color.track_green_object(img2)
                ret_red = color.track_red_object(img2)
                ret_blue = color.track_blue_object(img2)
                if ret_green and ret_red and ret_blue:
                    #Use Rectangle Mark Green,Blue,Red Object
                    #cv2.rectangle( img2, (wall_X_min, wall_Y_min), (wall_X_max, wall_Y_max), (0,0,255), 1)
                    cv2.rectangle( img2, (ret_green[0]-10, ret_green[1]-10), (ret_green[0]+10,ret_green[1]+10), (0,255,0), 2)
                    cv2.rectangle( img2, (ret_red[0]-10, ret_red[1] - 10), (ret_red[0]+10,ret_red[1]+10), (255,0,0), 2)
                    cv2.rectangle( img2, (ret_blue[0]-10, ret_blue[1] - 10), (ret_blue[0]+10,ret_blue[1]+10), (0,0,255), 2)
                    #Save the Ball Position
                    ball_positionX.append( ret_blue[0])
                    ball_positionY.append( ret_blue[1])
                    #If getting enough data
                    # Rx_v  > 0 => the green is at the right of the Red
                    Rx = ret_green[0] - ret_red[0]
                    # Ry_v  > 0 => the green is at the front of the Red
                    Ry = ret_green[1] - ret_red[1]
                    # Auto Defense mode
                    if play_mode == 0:
                        if Rx > 0:
                            Rx_v = Rx**2
                        else:
                            Rx_v = -(Rx**2)
                        if Ry > 0:
                            Ry_v = Ry**2
                        else:
                            Ry_v = -(Ry**2)
                        if ret_red[0] <  ret_green[0]:
                            speed(player_x_handle,-Rx_v*0.1)
                        elif ret_red[0] >  ret_green[0]:
                            speed(player_x_handle,-Rx_v*0.1)
                        else:
                            speed(player_x_handle,0)
                    #Auto Attack + Defense
                    elif play_mode == 1:
                        print('undone')
                    #Player + Player (Application)
                    elif play_mode == 2:
                        print('undone')
                    #Auto Defense (Path Prediction)
                    elif play_mode == 3:
                        if len(ball_positionX) != data_number:
                            pass
                        elif len(ball_positionY) != data_number:
                            pass
                        else :
                            #first position
                            x1 = ball_positionX[0]
                            y1 = ball_positionY[0]
                            #last position
                            #print(ball_positionX)
                            x2 = ball_positionX[data_number-1]
                            y2 = ball_positionY[data_number-1]
                            ball_directionX= ball_positionX[data_number-1] - ball_positionX[data_number-4]
                            ball_directionY= ball_positionY[data_number-1] - ball_positionY[data_number-4]
                            # 1 = Up or Right
                            # 2 = Down or Left
                            if ball_directionX < 0:
                                Ball_DirectionX_Movement = 1
                            elif ball_directionX > 0:
                                Ball_DirectionX_Movement = 2
                            else:
                                Ball_DirectionX_Movement = 0
                            if ball_directionY < 0:
                                Ball_DirectionY_Movement = 1
                            elif ball_directionY > 0:
                                Ball_DirectionY_Movement = 2
                            else:
                                Ball_DirectionY_Movement = 0
                                
                            if x1 == x2 and y1 == y2:
                                print('ball is not move')
                            else:
                                #Vertical
                                if x1 == x2: 
                                    x = numpy.arange(x2-10,x2+10)
                                    y = y1
                                #Horizontal
                                elif y1 == y2: 
                                    x = x1
                                    y = numpy.arange( y2 - 10, y2 + 10)
                                else:
                                    m = (y2-y1)/(x2-x1)
                                    if Ball_DirectionY_Movement == 1: #Up
                                        if Ball_DirectionY_Movement_last != 0 and Ball_DirectionY_Movement_last != Ball_DirectionY_Movement:
                                            for i in range(len(ball_positionY)):
                                                del ball_positionY[0]
                                        elif y2 < 140: #ball is close Red_Player wall
                                            y = wall_Y_min
                                            x = (y - y2)/m + x2
                                            if x < wall_X_min: #Ball is close Left wall
                                                x = wall_X_min
                                                y = m*(x - x2) + y2
                                                cv2.line( img2, (x2,y2), (int(x) , int(y)), (0x99,0xff,0x33), 2)
                                                m = -m
                                                y2 = y
                                                x2 = x
                                                y = y2 - 60
                                                if y < wall_Y_min:
                                                    y = wall_Y_min
                                                x = (y - y2)/m + x2
                                                if x > wall_X_max:
                                                    x = wall_X_max
                                                    y = m*(x - x2) + y2
                                                cv2.line( img2, ( int(x2),int(y2)), (int(x) , int(y)), (0x99,0xff,0x33), 2)
                                            elif x > wall_X_max: #Ball is close Right wall
                                                x = wall_X_max
                                                y = m*(x - x2) + y2
                                                cv2.line( img2, (x2,y2), (int(x) , int(y)), (0x99,0xff,0x33), 2)
                                                m = -m
                                                y2 = y
                                                x2 = x
                                                y = y2 - 60
                                                if y < wall_Y_min:
                                                    y = wall_Y_min
                                                x = (y - y2)/m + x2
                                                if x < wall_X_min:
                                                    x = wall_X_min
                                                    y = m*(x - x2) + y2
                                                cv2.line( img2, ( int(x2),int(y2)), (int(x) , int(y)), (0x99,0xff,0x33), 2)
                                            else:
                                                cv2.line( img2, (x2,y2), (int(x) , int(y)), (0x99,0xff,0x33), 2)
                                                m = -m
                                                y2 = y
                                                x2 = x
                                                y = y2 + 60
                                                x = (y - y2)/m + x2
                                                if x < wall_X_min:
                                                    x = wall_X_min
                                                    y = m*(x - x2) + y2
                                                if x > wall_X_max:
                                                    x = wall_X_max
                                                    y = m*(x - x2) + y2
                                                cv2.line( img2, ( int(x2),int(y2)), (int(x) , int(y)), (0x99,0xff,0x33), 2)
                                        else:
                                            y = y2 - 100
                                            x = (y - y2)/m + x2
                                            if Ball_DirectionX_Movement_last != 0 and Ball_DirectionX_Movement != Ball_DirectionX_Movement_last:
                                                for i in range(len(ball_positionX)):
                                                    del ball_positionX[0]
                                            elif x < wall_X_min:
                                                x = wall_X_min
                                                y = m*(x - x2) + y2
                                                cv2.line( img2, ( int(x2),int(y2)), (int(x) , int(y)), (0x99,0xff,0x33), 2)
                                                m = -m
                                                y2 = y
                                                x2 = x
                                                y = y2 - 60
                                                x = (y - y2)/m + x2
                                                cv2.line( img2, ( int(x2),int(y2)), (int(x) , int(y)), (0x99,0xff,0x33), 2)
                                            elif x > wall_X_max:
                                                x = wall_X_max
                                                y = m*(x - x2) + y2
                                                cv2.line( img2, ( int(x2),int(y2)), (int(x) , int(y)), (0x99,0xff,0x33), 2)
                                                m = -m
                                                y2 = y
                                                x2 = x
                                                y = y2 - 60
                                                x = (y - y2)/m + x2
                                                cv2.line( img2, ( int(x2),int(y2)), (int(x) , int(y)), (0x99,0xff,0x33), 2)
                                            else:
                                                cv2.line( img2, ( int(x2),int(y2)), (int(x) , int(y)), (0x99,0xff,0x33), 2)
                                        Ball_DirectionY_Movement_last = Ball_DirectionY_Movement
                                        Ball_DirectionX_Movement_last = Ball_DirectionX_Movement
                                    if Ball_DirectionY_Movement == 2: #Down
                                        if Ball_DirectionY_Movement_last != 0 and Ball_DirectionY_Movement_last != Ball_DirectionY_Movement:
                                            for i in range(len(ball_positionY)):
                                                del ball_positionY[0]
                                        elif y2 > 320: #ball is close Red_Player wall
                                            y = wall_Y_max
                                            x = (y - y2)/m + x2
                                            if x < wall_X_min: #Ball is close Left wall
                                                x = wall_X_min
                                                y = m*(x - x2) + y2
                                                cv2.line( img2, (x2,y2), (int(x) , int(y)), (0x99,0xff,0x33), 2)
                                                m = -m
                                                y2 = y
                                                x2 = x
                                                y = y2 + 60
                                                if y > wall_Y_max:
                                                    y = wall_Y_max
                                                x = (y - y2)/m + x2
                                                if x > wall_X_max:
                                                    x = wall_X_max
                                                    y = m*(x - x2) + y2
                                                cv2.line( img2, ( int(x2),int(y2)), (int(x) , int(y)), (0x99,0xff,0x33), 2)
                                            elif x > wall_X_max: #Ball is close Right wall
                                                x = wall_X_max
                                                y = m*(x - x2) + y2
                                                cv2.line( img2, (x2,y2), (int(x) , int(y)), (0x99,0xff,0x33), 2)
                                                m = -m
                                                y2 = y
                                                x2 = x
                                                y = y2 + 60
                                                if y > wall_Y_max:
                                                    y = wall_Y_max
                                                x = (y - y2)/m + x2
                                                if x < wall_X_min:
                                                    x = wall_X_min
                                                    y = m*(x - x2) + y2
                                                cv2.line( img2, ( int(x2),int(y2)), (int(x) , int(y)), (0x99,0xff,0x33), 2)
                                            else:
                                                cv2.line( img2, (x2,y2), (int(x) , int(y)), (0x99,0xff,0x33), 2)
                                                m = -m
                                                y2 = y
                                                x2 = x
                                                y = y2 - 60
                                                x = (y - y2)/m + x2
                                                if x < wall_X_min:
                                                    x = wall_X_min
                                                    y = m*(x - x2) + y2
                                                if x > wall_X_max:
                                                    x = wall_X_max
                                                    y = m*(x - x2) + y2
                                                cv2.line( img2, ( int(x2),int(y2)), (int(x) , int(y)), (0x99,0xff,0x33), 2)
                                        else:
                                            y = y2 + 100
                                            x = (y - y2)/m + x2
                                            if Ball_DirectionX_Movement_last != 0 and Ball_DirectionX_Movement != Ball_DirectionX_Movement_last:
                                                for i in range(len(ball_positionX)):
                                                    del ball_positionX[0]
                                            elif x < wall_X_min:
                                                x = wall_X_min
                                                y = m*(x - x2) + y2
                                                cv2.line( img2, ( int(x2),int(y2)), (int(x) , int(y)), (0x99,0xff,0x33), 2)
                                                m = -m
                                                y2 = y
                                                x2 = x
                                                y = y2 + 60
                                                x = (y - y2)/m + x2
                                                cv2.line( img2, ( int(x2),int(y2)), (int(x) , int(y)), (0x99,0xff,0x33), 2)
                                            elif x > wall_X_max:
                                                x = wall_X_max
                                                y = m*(x - x2) + y2
                                                cv2.line( img2, ( int(x2),int(y2)), (int(x) , int(y)), (0x99,0xff,0x33), 2)
                                                m = -m
                                                y2 = y
                                                x2 = x
                                                y = y2 + 60
                                                x = (y - y2)/m + x2
                                                cv2.line( img2, ( int(x2),int(y2)), (int(x) , int(y)), (0x99,0xff,0x33), 2)
                                            else:
                                                cv2.line( img2, ( int(x2),int(y2)), (int(x) , int(y)), (0x99,0xff,0x33), 2)
                                        Ball_DirectionY_Movement_last = Ball_DirectionY_Movement
                                        Ball_DirectionX_Movement_last = Ball_DirectionX_Movement
                                    #Path Prediction end
                                    #AutoDefense Start
                                    if Ball_DirectionY_Movement == 1:
                                        player_red_positionX = ret_red[0]
                                        player_red_positionY = ret_red[1]
                                        y = player_red_positionY
                                        x = int((y-y2)/m+x2)
                                        playerX_move_speed = (x - player_red_positionX)*-0.01
                                        if playerX_move_speed > 1:
                                            playerX_move_speed = 1
                                        elif playerX_move_speed < -1:
                                            playerX_move_speed = -1
                                        speed(player_x_handle, playerX_move_speed)
                                        print('x=', x)
                                        print(ret_green[1])
                                    elif Ball_DirectionY_Movement == 2:
                                        player_red_positionX = ret_red[0]
                                        playerX_move_speed = ((wall_X_min + wall_X_max)/2 - player_red_positionX)*-0.01
                                        if playerX_move_speed > 1:
                                            playerX_move_speed = 1
                                        elif playerX_move_speed < -1:
                                            playerX_move_speed = -1
                                        speed(player_x_handle, playerX_move_speed)
                        #play_mode  3 end
                    #Use to Test
                    else:
                        speed(player_x_handle,0)
                        speed(player_y_handle,0)
                        pass
                else:
                    if not ret_green:
                        print('Not Found Green Object')
                    if not ret_red:
                        print('Not Found Red Object')
                    if not ret_blue:
                        print('Not Found Blue Object')
                
                # vs2 display
                img2 = img2.ravel()
                sim.simxSetVisionSensorImage(clientID, v1, img2, 0, sim.simx_opmode_oneshot)
                end = time.time();
                dt = end - start;
                print('Frame took:', dt*1000.0, 'ms');
            elif err == sim.simx_return_novalue_flag:
                print("no image yet")
                pass
            else:
                print(err)
            if len(ball_positionX) > (data_number - 1):
                del ball_positionX[0]
            if len(ball_positionY) > (data_number - 1):
                del ball_positionY[0]
    else:
      print("Failed to connect to remote API Server")
      sim.simxFinish(clientID)