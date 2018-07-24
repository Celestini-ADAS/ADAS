#vision and coms back end
import vision
from vision import * #imports all the functions defined by me as well as all the libraries i have imported for it(numpy and all)
import COMS
from COMS import * # same
# i already have : serial,numpy(as np),cv2,math(as m)

#initialize coms
V2V = com_handler()
V2V._init_('COM4',230400,40)

phone = com_handler()
phone.initialize('dev/tty/USB0',250000,48)
cap = np.load('Test1.npy') # test video stored in numpy format because opencv in raspi didn't work with .MOV files.
#cap = cv2.VideoCapture('Test2.MOV') 
#initialize stuff for vision 
img = cap[0][0]
prev_gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

broadcast_Rx = np.zeros(5)

# state = np.zeros(6) # state array. lon,lat,speed,direction,time_stamp(RTC),acceleration along direction of movement.
state = np.array([10,10,15,45,0,1],dtype=float) # static coordinates for testing purposes
def check_Relevance(state,broadcast_Rx):
	L=2
	if((state[4]-broadcast_Rx[4])>10):
		return 0
	A_X = -m.cos(state[3]*0.01745)
	A_Y = -m.sin(state[3]*0.01745)

	Xr = state[0]
	Xs = broadcast_Rx[0]
	Yr = state[1]
	Ys = broadcast_Rx[1]
	dX = Xr-Xs
	dY = Yr-Ys
	D = m.sqrt(dX**2 + dY**2)
	Ms = m.tan(state[3]*0.01745)
	Mr = dY/dX
	T = (Mr - Ms)/(1 + Mr*Ms)
	if(A_X*dX>0 and A_Y*dY>0):
		V = 1.5/D
		if(m.fabs(T) < m.fabs(V)):
			return 1
	return 0

font                   = cv2.FONT_HERSHEY_SIMPLEX
bottomLeftCornerOfText_Center = (150,200)
bottomLeftCornerOfText_Left = (150,300)
bottomLeftCornerOfText_Right = (150,100)
fontScale              = 1
fontColor              = (0,0,255)
lineType               = 2

while 1:
	
	# if(phone.check_recv()): #if new information from phone has been received
	# 	state = phone.read() #update the state
	
	if(V2V.check_recv()):#if an alert has arrived, 
		broadcast_Rx = V2V.read()#get the alert data
		if(check_Relevance(state,broadcast_Rx)):
			print('ALEEEERRTTTTTT!!!!')

	img = cap[i][0]
	gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
	alert = check(img,gray,prev_gray)
	prev_gray = gray
	
	if(alert[1]):
		cv2.putText(img,'alert_center!', 
		bottomLeftCornerOfText_Center, 
		font, 
		fontScale,
		fontColor,
		lineType)
		cv2.imshow('window',img)
	if(alert[0]):
	    cv2.putText(img,'alert_left!', 
	    bottomLeftCornerOfText_Left, 
	    font, 
	    fontScale,
	    fontColor,
	    lineType)
	    cv2.imshow('window',img)
	if(alert[2]):
	    cv2.putText(img,'alert_right!', 
	    bottomLeftCornerOfText_Right, 
	    font, 
	    fontScale,
	    fontColor,
	    lineType)
	    cv2.imshow('window',img)
	else:
	    cv2.imshow('window',img)


	if(alert.any()):
		print('ALEEEERRTTTTTT!!!!') #define this ples
		if(alert.any() or state[5]<(-7)): #if optical flow threat is too great or deceleration is more than 7m/s^	
			V2V.send(state[:-1]) # send everything except the last info which is the deceleration because we can only broadcast 40 bytes at a time(For now)

	ch = 0xFF & cv2.waitKey(5) #press ESC key to exit
	if ch == 27:
	    break
cv2.destroyAllWindows() 	
