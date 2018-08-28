#vision and coms back end
import vision
from vision import * #imports all the functions defined by me as well as all the libraries i have imported for it(numpy and all)
import COMS
from COMS import * # same
# i already have : serial,numpy(as np),cv2,math(as m)

#initialize coms
V2V = com_handler()
V2V._init_('/dev/ttyUSB1',230400,40)

phone = com_handler()
phone.initialize('/dev/ttyUSB0',230400,40)
#cap = np.load('Test1.npy') # test video stored in numpy format because opencv in raspi didn't work with .MOV files.

cap = cv2.VideoCapture(1) 
#initialize stuff for vision 
img = cap[0][0]
prev_gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

broadcast_Rx = np.zeros(5)

state = np.zeros(5)
def check_Relevance(state,broadcast_Rx):
	L=2
	A_X = -m.cos(state[3]*0.01745)
	A_Y = -m.sin(state[3]*0.01745)

	Xr = state[0]
	Xs = broadcast_Rx[0]
	Yr = state[1]
	Ys = broadcast_Rx[1]
	dX = (Xr-Xs)*111692.84
	dY = (Yr-Ys)*111692.84 # convert into meters 
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
	try:
		if(V2V.check_recv()):#if an alert has arrived, 
			broadcast_Rx = V2V.read()#get the alert data
			if(check_Relevance(state,broadcast_Rx)):
				print('ALEEEERRTTTTTT!!!!')
				phone.send(np.ones(5))

		ret,img = cap.read()
		gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
		alert = check(img,gray,prev_gray)
		prev_gray = gray

		if(alert.any()):
			cv2.putText(img,'ALERT!', 
			bottomLeftCornerOfText_Center, 
			font, 
			fontScale,
			fontColor,
			lineType)
			cv2.imshow('window',img)
		else:
		    cv2.imshow('window',img)


		if(alert.any()):
			print('ALEEEERRTTTTTT!!!!') #define this ples
			if(alert.any() or state[4]<(-1)): #if optical flow threat is too great or deceleration is more than 7m/s^	
				V2V.send(state) # send everything except the last info which is the deceleration because we can only broadcast 40 bytes at a time(For now)

		ch = 0xFF & cv2.waitKey(5) #press ESC key to exit
		if ch == 27:
		    break
    except:
    	i = 0
cv2.destroyAllWindows() 	
