import cv2
import numpy
import array
import sim
from PIL import Image as I
'''
CoppeliaSim
air_hockey_full

Green
range = 5
lower_green = numpy.array([60-range,20,20])
upper_green = numpy.array([60+range,255,255])

Red
range = 5
lower_red = numpy.array([0-range,20,20])
upper_red = numpy.array([0+range,255,255])

Blue
range = 5
lower_blue = numpy.array([100-range,20,20])
upper_blue = numpy.array([100+range,255,255])

'''
'''
range = 5
lower_blue = numpy.array([120-range,200,120])
upper_blue = numpy.array([120+range,255,160])

range = 10
lower_green = numpy.array([60-range,100,100])
upper_green = numpy.array([60+range,255,255])
'''
mode = 1
if __name__ == '__main__':
    if mode ==1:
        kernel = numpy.ones((5,5),numpy.uint8)
        sim.simxFinish(-1)
        clientID = sim.simxStart('127.0.0.1', 19997, True, True, 5000, 5)
        if clientID != -1:
            print('Connected to remote API server')
            # get vision sensor objects
            res, v0 = sim.simxGetObjectHandle(clientID, 'vs4', sim.simx_opmode_oneshot_wait)
            res, v1 = sim.simxGetObjectHandle(clientID, 'vs2', sim.simx_opmode_oneshot_wait)
            err, resolution, image = sim.simxGetVisionSensorImage(clientID, v0, 0, sim.simx_opmode_streaming)
            #get motor objects
            err,Ball_handle=sim.simxGetObjectHandle(clientID,'Ball', sim.simx_opmode_oneshot_wait)
            err,player_x_handle=sim.simxGetObjectHandle(clientID, 'player_x_joint', sim.simx_opmode_oneshot_wait)
            err,player_y_handle=sim.simxGetObjectHandle(clientID, 'player_y_joint', sim.simx_opmode_oneshot_wait)
            #main loop
            while (sim.simxGetConnectionId(clientID) != -1):
                #get vision sensor image
                err, resolution, image = sim.simxGetVisionSensorImage(clientID, v0, 0, sim.simx_opmode_buffer)
                print(len(image))
                if err == sim.simx_return_ok:
                    image_byte_array = array.array('b', image)
                    image_buffer = I.frombuffer("RGB", (resolution[0],resolution[1]), bytes(image_byte_array), "raw", "RGB", 0, 1)
                    img2 = numpy.asarray(image_buffer)
                    img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
                    hsv = cv2.cvtColor(img2, cv2.COLOR_BGR2HSV)
                    range = 5
                    lower_color = numpy.array([30-range,100,100])
                    upper_color = numpy.array([30+range,200,200])
                    mask = cv2.inRange(hsv, lower_color, upper_color)
                    opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
                    # Display the resulting frame
                    cv2.imshow('frame',mask)
                    cv2.imshow('frame2',img2)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
    elif mode == 2:
        kernel = numpy.ones((5,5),numpy.uint8)
        cap = cv2.VideoCapture(0)
        while(True):
            ret, frame= cap.read()
            # Our operations on the frame come here
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            range = 10
            lower_color = numpy.array([0-range,100,100])
            upper_color = numpy.array([0+range,255,255])
            mask = cv2.inRange(hsv, lower_color, upper_color)
            opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            # Display the resulting frame
            #cv2.imshow('frame',opening)
            cv2.imshow('frame',frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        # When everything done, release the capture
        cap.release()
        cv2.destroyAllWindows()