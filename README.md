# ADAS
An alert generation-transmission system for vehicles.
The android part of this project is in the repository "GPS-IMU" (the project was too big to be uploaded as a separate file).
The project is meant to run on a raspi.

external dependencies : 

opencv (2.4 or better) (pip install python-opencv-3.2.0)

numpy (pip install numpy)

serial (pip install pyserial)

# WHAT IT DOES:
->The ADAS.py file is the main file which uses the vision.py and COMS.py files. 
ADAS.py is supposed to generate an alert for the user when the vision component(vision.py) detects a threat(collision iminent) or sudden braking(by leveraging the sensors in the mobile) and is supposed to broadcast an alert using communications back end(COMS.py, can use any transceiver that works on UART protocol). 

->ADAS.py also checks for the relevance of a received alert. An alert is considered relevant if it is coming from a car in front of us moving in the same direction and on the same road. 

->vision.py : determines whether there is a threat in a given frame by taking the image as well as the optical flow of the image as an input parameter. It generates an alert if there is a large (car-size large) object appearing to move towards the bottom center of the image. This method is highly sensitive to lighting conditions and camera position and orientation. The method also generates false positives when the car goes over a bump on the road.

->COMS.py is a communications back end (not really that complex or sophisticated if you take a peek, it just makes our job easier, thats it) which can handle UART communications. It has been tested for xbees in transparent mode and for RF APC220s. Look into ADAS.py for understanding how to use them.

# Further developments : 
-> refining the system.
