#vision and coms back end
import vision
from vision import * #imports all the functions defined by me as well as all the libraries i have imported for it(numpy and all)
import COMS
from COMS import * # same
# i already have : serial,numpy(as np),cv2,math(as m)

#initialize coms
V2V = com_handler()
V2V._init_('COM8',230400,40)

phone = com_handler()
phone.initialize('COM?',BAUD,48)

cap = cv2.videoCapture(0)
#initialize
ret,img = cap.read()
prev_gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

broadcast_Rx = np.zeros(5)

state = np.zeros(6) # state array. lon,lat,speed,direction,time_stamp(RTC),acceleration along direction of movement.

def check_Relevance(state,broadcast_Rx):
	L=2

	A_X = -m.cos(state[3])
	A_Y = -m.sin(state[3])

	Xr = state[0]
	Xs = broadcast_Rx[0]
	Yr = state[1]
	Ys = broadcast_Rx[1]
	dX = Xr-Xs
	dY = Yr-Ys
	D = m.sqrt(dX**2 + dY**2)
	Ms = tan(state[3])
	Mr = dY/dX
	T = (Mr - Ms)/(1 + Mr*Ms)
	if(A_X*dX>0 and A_Y*dY>0):
		V = 1.5/D
		if(m.fabs(T) < m.fabs(V)):
			return 1
	return 0

while True:
	
	if(phone.check_recv()): #if new information from phone has been received
		state = phone.read() #update the state
	
	if(V2V.check_recv()):#if an alert has arrived, 
		broadcast_Rx = V2V.read()#get the alert data
		if(check_Relevance(state,broadcast_Rx)):
			give_user_alert_somehow()

	ret,img = cap.read()
	gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
	alert = check(img,gray,prev_gray)
	prev_gray = gray
	if(alert):
		give_user_alert_somehow() #define this ples
		if(alert>some_threshold or state[5]<-7): #if optical flow threat is too great or deceleration is more than 7m/s^	
			V2V.send(state[:-1])


