# ADAS
The project is meant to run on a raspi (has not been tested yet but its mostly just running python scripts with some really really common dependencies. The backend files (COMS.py, vision.py) have been tested on a laptop. 
external dependencies : 
opencv (2.4 or better) (pip install python-opencv-3.2.0)
numpy (pip install numpy)
serial (pip install pyserial)

# WHAT DO:
->The ADAS.py file is the main file which uses the vision.py and COMS.py files. 
ADAS.py (not yet complete) is supposed to generate an alert for the user when the vision component(vision.py) detects a threat(collision iminent) and is supposed to broadcast an alert using communications back end(COMS.py, can use any transceiver that works on UART protocol). 

->ADAS.py also checks for the relevance of a received alert. An alert is considered relevant if it is coming from a car in front of us moving in the same direction and on the same road. 

->COMS.py is a communications back end (not really that complex or sophisticated if you take a peek, it just makes our job easier, thats it) which can handle UART communications. It has been tested for xbees in transparent mode and for RF APC220s. Look into ADAS.py for understanding how to use them.

# Further developments : 

->We haven't yet figured out how we'd transfer the position, speed, heading and acceleration data from the android phone (which will be running the GPS-IMU-android app) via the USB (serial). there is a hack that we have in mind but it is yet to be tested. Worst case scenario would be to use a bluetooth connection between the raspberry pi and the android phone which would introduce lag. This lag in the data can be compensated if the latency period is known and constant.

->Vision component is yet to be tested in a real world environment (has been tested in need for speed MOST-WANTED 2012). On a 2.4Ghz i5 processor, the vision component can easily manage 60fps. We hope we'll manage at least 15 fps on a raspi.
 
