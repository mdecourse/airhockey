import sim
import time,array,sys
import cv2
import numpy
import imutils
from PIL import Image as I
import ColorRecognition as color
from flask import Flask, render_template, send_from_directory, Response

flask_ip = "140.130.17.108"
flask_port = 5000
vrep_port = 19997
vrep_port2 = 19999
scene_path = "Y:\tmp2\air_hockey_flask_vrep\Air_Hockey_full.ttt"

class air_Hockey():
    def __init__(self, clientID):
        kernel = numpy.ones((5,5),numpy.uint8)
        self.clientID = clientID;
        res, self.v0 = sim.simxGetObjectHandle(self.clientID, 'vs1', sim.simx_opmode_oneshot_wait)
        res, self.v1 = sim.simxGetObjectHandle(self.clientID, 'vs2', sim.simx_opmode_oneshot_wait)
        err,self.Ball_handle=sim.simxGetObjectHandle(self.clientID,'Ball', sim.simx_opmode_oneshot_wait)
        err,self.player2_x_handle=sim.simxGetObjectHandle(self.clientID, 'Com_X_joint', sim.simx_opmode_oneshot_wait)
        err,self.player2_y_handle=sim.simxGetObjectHandle(self.clientID, 'Com_Y_joint', sim.simx_opmode_oneshot_wait)
        err, resolution, image = sim.simxGetVisionSensorImage(self.clientID, self.v0, 0, sim.simx_opmode_streaming)
        print('Received Handles...');
        
        self.data_number = 5
        if self.data_number < 5:
            self.data_number = 5
        self.ball_positionX = []
        self.ball_positionY = []
        self.wall_X_min = 10
        self.wall_X_max = 248
        self.wall_Y_min = 41
        self.wall_Y_max = 450
        # 0 = Stop
        # 1 = Up or Right
        # 2 = Down or Left
        self.Ball_DirectionX_Movement = 0
        self.Ball_DirectionX_Movement_last = 0
        self.Ball_DirectionY_Movement = 0
        self.Ball_DirectionY_Movement_last = 0
        
        # Self test the camera
        print('Setting up the camera system...');
        self.lastFrame = None;
        err = 0;
        while(err != 1):
            err, self.lastFrame = self.get_image();
        print('Camera setup successful.')
   
    def get_image(self):
        err, resolution, image = sim.simxGetVisionSensorImage(self.clientID, self.v0, 0, sim.simx_opmode_streaming)
        if err == sim.simx_return_ok:
            img = numpy.array(image,dtype=numpy.uint8)
            img.resize([resolution[1],resolution[0],3])
            img = imutils.rotate_bound(img, 180)
            img = cv2.flip(img,1)
            image_ori = img
            image_ori = cv2.cvtColor(image_ori, cv2.COLOR_BGR2RGB)
            cv2.putText(image_ori, 'Original', (50,500), cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 0, 0 ), 1, cv2.LINE_AA)
            cv2.putText(img, 'Image Recognition', (50,500), cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 0, 0 ), 1, cv2.LINE_AA)
            ret_green = color.track_green_object(img)
            ret_red = color.track_red_object(img)
            ret_blue = color.track_blue_object(img)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            if ret_green and ret_red and ret_blue:
                #Use Rectangle and Text Mark Green Object
                Rec_range = 6
                cv2.rectangle( img, (ret_green[0]-Rec_range, ret_green[1]-Rec_range), (ret_green[0]+Rec_range,ret_green[1]+Rec_range), (0,255,0), 1)
                cv2.putText(img, 'Green', (ret_green[0]-25, ret_green[1]-10), cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 255, 0 ), 1, cv2.LINE_AA)
                #Use Rectangle and Text Mark Red Object
                cv2.rectangle( img, (ret_red[0]-Rec_range, ret_red[1] - Rec_range), (ret_red[0]+Rec_range,ret_red[1]+Rec_range), (0,0,200), 1)
                cv2.putText(img, 'Red', (ret_red[0]-15, ret_red[1]-10), cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 0, 255), 1, cv2.LINE_AA)
                #Use Rectangle and Text Mark Blue Object
                cv2.rectangle( img, (ret_blue[0]-Rec_range, ret_blue[1] - Rec_range), (ret_blue[0]+Rec_range,ret_blue[1]+Rec_range), (255,0,0), 1)
                cv2.putText(img, 'Blue', (ret_blue[0]-20, ret_blue[1]-10), cv2.FONT_HERSHEY_SIMPLEX,0.5, (255, 0, 0 ), 1, cv2.LINE_AA)
                Rx = ret_red[0] -  ret_blue[0]
                Ry =- (ret_red[1] -  ret_blue[1])
                #print(Ry)
                Rx_v = Rx*0.02
                if ret_blue[0] <  ret_green[0]:
                    sim.simxSetJointTargetVelocity( self.clientID, self.player2_x_handle,Rx_v , sim.simx_opmode_oneshot_wait)
                elif ret_blue[0] >  ret_green[0]:
                    sim.simxSetJointTargetVelocity( self.clientID, self.player2_x_handle, Rx_v, sim.simx_opmode_oneshot_wait)
                else:
                    sim.simxSetJointTargetVelocity( self.clientID, self.player2_x_handle, 0, sim.simx_opmode_oneshot_wait)
                if Ry >= 10 and Ry <= 100:
                    sim.simxSetJointTargetVelocity( self.clientID, self.player2_y_handle, 1, sim.simx_opmode_oneshot_wait)
                else:
                    sim.simxSetJointTargetVelocity( self.clientID, self.player2_y_handle, -1, sim.simx_opmode_oneshot_wait)
            else:
                if not ret_green:
                    print('not ret_green')
                if not ret_red:
                    print('not ret_red')
                if not ret_blue:
                    print('not ret_green')
            self.lastFrame = numpy.hstack((image_ori,img))
            return 1, self.lastFrame;
            
        elif err == sim.simx_return_novalue_flag:
            return 0, None;
        else:
            return err, None;
            
app = Flask(__name__)

def startvrep():
    sim.simxFinish(-1) # just in case, close all opened connections
    clientID = sim.simxStart(flask_ip, vrep_port, True, True, 5000, 5) # Get the client ID
    res=sim.simxLoadScene(clientID, scene_path, 0, sim.simx_opmode_blocking)
    x =sim.simxStartSimulation(clientID,sim.simx_opmode_oneshot_wait) 

    if clientID!=-1:  #check if client connection successful
        print('Connected to remote API server')
    else:
        print('Connection not successful')
        sys.exit('Could not connect')

    # Initialize car control object
    AirHockey = air_Hockey(clientID);

    #for i in range(150):
    while True:
        # Start time for image process
        err, img= AirHockey.get_image()
        ret, jpeg = cv2.imencode('.jpg', img)
        #jpeg.tobytes()
        yield (b'--frame\r\n'
        b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
    return "startvrep"

@app.route("/stopvrep")
def stopvrep():
    sim.simxStopSimulation(clientID, sim.simx_opmode_oneshot_wait) 
    sim.simxFinish(-1) # just in case, close all opened connections
    sim.simxStopSimulation(clientID, sim.simx_opmode_oneshot_wait) 
    return render_template('stopvrep.html')

@app.route("/video_feed")
def video_feed():
    return Response(startvrep(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/showimage")
def showimage():
    return '''
<html>
    <head>
        <title>Stream</title>
    </head>
    <body>
        <h1>Video Stream</h1>
        <img src="/video_feed" width="256" height="512"></img>
    </body>
</html>
'''
@app.route('/')
def index():
    # render the template (below) that will use JavaScript to read the stream
    return render_template('index.html')
    
@app.route('/move_forward')
def move_forward():
    clientID2 = sim.simxStart(flask_ip, vrep_port2, True, True, 5000, 5) # Get the client ID
    print(clientID2)
    errorCode,player_y_handle=sim.simxGetObjectHandle(clientID2, 'Pla_Y_joint', sim.simx_opmode_oneshot_wait)
    sim.simxSetJointTargetVelocity( clientID2, player_y_handle, -1, sim.simx_opmode_oneshot_wait)
    sim.simxFinish(clientID2)
    print ("move_forward")
    return ("nothing")
    
@app.route('/move_back')
def move_back():
    clientID2 = sim.simxStart(flask_ip, vrep_port2, True, True, 5000, 5) # Get the client ID
    errorCode,player_y_handle=sim.simxGetObjectHandle(clientID2, 'Pla_Y_joint', sim.simx_opmode_oneshot_wait)
    sim.simxSetJointTargetVelocity( clientID2, player_y_handle, 1, sim.simx_opmode_oneshot_wait)
    sim.simxFinish(clientID2)
    print ("move_back")
    return ("nothing")
    
@app.route('/move_left')
def move_left():
    clientID2 = sim.simxStart(flask_ip, vrep_port2, True, True, 5000, 5) # Get the client ID
    errorCode,player_x_handle=sim.simxGetObjectHandle(clientID2, 'Pla_X_joint', sim.simx_opmode_oneshot_wait)
    sim.simxSetJointTargetVelocity( clientID2, player_x_handle, 1, sim.simx_opmode_oneshot_wait)
    sim.simxFinish(clientID2)
    print ("move_left")
    return ("nothing")
    
@app.route('/move_right')
def move_right():
    clientID2 = sim.simxStart(flask_ip, vrep_port2, True, True, 5000, 5) # Get the client ID
    errorCode,player_x_handle=sim.simxGetObjectHandle(clientID2, 'Pla_X_joint', sim.simx_opmode_oneshot_wait)
    sim.simxSetJointTargetVelocity( clientID2, player_x_handle, -1, sim.simx_opmode_oneshot_wait)
    sim.simxFinish(clientID2)
    print ("move_right")
    return ("nothing")
    
@app.route('/reset')
def reset():
    clientID2 = sim.simxStart(flask_ip, vrep_port2, True, True, 5000, 5) # Get the client ID
    sim.simxStopSimulation(clientID2,sim.simx_opmode_oneshot_wait)
    time.sleep(1)
    sim.simxStartSimulation(clientID2,sim.simx_opmode_oneshot_wait)
    time.sleep(0.5)
    sim.simxFinish(clientID2)
    print ("reset")
    return ("nothing")
    
if __name__ == '__main__':
    app.run(host=flask_ip, port=flask_port)
    
