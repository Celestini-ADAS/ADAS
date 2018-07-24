import numpy as np
import cv2
import math as m

def my_cos(a):
    if(a>6.28):
        factor = int(a*0.15923)
        a -= float(factor*6.28)

    if(a<0):
        factor = 1-int(a*0.15923)
        a += float(factor*6.28)
    
    if(a>1.57 and a<4.71):
        a = 3.14-a
        return ((0.42*a*a)-1)
    
    if(a>=4.17):
        a -=6.28
    return (1-(0.42*a*a)) 

def thresh(attack):
    if(attack<0.5):
        return 0
    return attack

def getAlerts(dim_X, dim_Y, ang, v,img,gray,mean):#takes the dimensions of the image, the direction of motion at each point and the speed of that point
    mid_Y = int(0.5*dim_Y) #wherever the horizon is in the image. mid_Y is not necessarily at the center of the image.
    roi_up = mid_Y #we can work with information in a small region. As in, the sky is not important to us.
    roi_down = int(0.8*dim_Y)# int(2.5*mid_Y) #we don't want to look at the hood of the car
    roi_left = 0#int(0.1*dim_X) #Not interested in what is happening 20 meters to my left or right
    roi_right = dim_X #int(0.8*dim_X)

    ref_X = np.zeros(3)
    ref_X[0] = int(0.3*dim_X)
    ref_X[1] = int(0.5*dim_X) # X axis position of camera
    ref_X[2] = int(0.7*dim_X)
    ref_Y = dim_Y #bottom of the image. Y axis position of camera
    width = roi_right-roi_left
    count = (roi_down - roi_up)*width #number of pixels in roi 

    danger = np.zeros(3) #amount of danger
    app_ang = np.zeros(3)
    attack = np.zeros(3)
    threat = np.zeros(3)

    road_Ref = img[int(0.80*img.shape[0]):int(0.90*img.shape[0]),int(0.45*img.shape[1]):int(0.55*img.shape[1])]
    avg_int = np.mean(road_Ref,axis=(0,1) )
    #print(avg_int_2)
    '''
    LOGIC : 
    ->An object approaching the car would have a velocity who's direction is towards the bottom center of the image(or in human terms,
    towards the car).
        -> component of velocity of an object towards the car 
            = (speed of point)*cos(direction of movement of the point - direction of line joining that point to the bottom center of the image)
    ->the speed of an object is higher for the same pixel movement if the object is near the horizon, to compensate for that,
      we must multiply it by a correction factor, 
        ->corrected speed = sec^2(angle of declination) * original speed. 
    ->the amount of threat posed by an individual point must be proportional to the component of the velocity towards the car
    ->the total threat in that instant is the normalized sum of the threat due to all points in the region of interest.  
    ->now also taking into account the color
    '''
    lastTotal = 1
    for i in range(roi_up, roi_down ): # rows (y's)
        for j in range(roi_left, roi_right): #columns (x's)
            #initial point is the ref point. We're drawing a line from the ref point to the point under consideration.
            correctionX = 1/my_cos( m.atan2( m.fabs(ref_X[1]-j),ref_X[1]))
            correctionX *= correctionX
            correctionY = 1/my_cos( m.atan2( (i-mid_Y),mid_Y) )
            correctionY *= correctionY
            correction = m.sqrt(correctionX**2 + correctionY**2)

            #v[i][j] -= mean
            v[i][j] /= mean
            if v[i][j] <0:
                v[i][j] = 0
            speed = v[i][j]*correction #corrected speed.
            cur_img = img[i][j]
            obj_prob = m.fabs(cur_img[0]-avg_int[0])/avg_int[0] + m.fabs(cur_img[1]-avg_int[1])/avg_int[1] + m.fabs(cur_img[2]-avg_int[2])/avg_int[2] 
            obj_prob /= 3

            threat = np.zeros(3)
            total=0
            for x in range(3):
                app_ang[x] = m.atan2( dim_Y-i, ref_X[x]-j )
                attack[x] = thresh( (my_cos(app_ang[x] - ang[i][j]) ) )**4
                threat[x] = (speed*obj_prob*attack[x])**2
                total+=threat[x]
            if(total != 0):
                threat/=total
                lastTotal=total
            else:
                threat /=lastTotal
            danger[0] += threat[0]
            danger[1] += threat[1]
            danger[2] += threat[2]
    for i in range(3):
        danger[i] /= count #normalize the danger
    return danger


initialized = False
k = 0
alert = np.zeros(3)
threshold = np.array([0.35,0.35,0.35])

def check(img, gray, prevgray): # assumes that the images are already in grayscale 
    original_img = img
    f = 6
    input_size = np.array([100,75])
    input_size = input_size.astype(int)
    
    global initialized
    global k
    global alert
    global threshold
    
    prevgray = cv2.resize(prevgray, (input_size[1],input_size[0]), cv2.INTER_LINEAR)
    gray     = cv2.resize(gray, (input_size[1],input_size[0]), cv2.INTER_LINEAR) #resizing the images
    
    flow = cv2.calcOpticalFlowFarneback(prevgray, gray,None, 0.5, 3, 15, 3, 5, 1.2, 0) #calculate flow
    
    flow_X, flow_Y = flow[:,:,0], flow[:,:,1] #the x and y components of motion.
    
    flow_X = cv2.resize(flow_X,(int(flow_X.shape[1]/f),int(flow_X.shape[0]/f)), cv2.INTER_LINEAR )#resize images 

    flow_Y = cv2.resize(flow_Y,(int(flow_Y.shape[1]/f),int(flow_Y.shape[0]/f)), cv2.INTER_LINEAR )#to reduce computation
    
    img = cv2.resize(img,(flow_X.shape[1],flow_X.shape[0]), cv2.INTER_LINEAR)
    gray = cv2.resize(gray,(img.shape[1],img.shape[0]), cv2.INTER_LINEAR)
    ang = np.arctan2(flow_Y,flow_X) #the angle of motion at each point in the image
    v = np.sqrt( np.add(np.square(flow_X),np.square(flow_Y)) ) #magnitude of motion at each point.
    mean = np.mean(v)

    current_K = getAlerts(ang.shape[1], ang.shape[0], ang, v,img, gray,mean)
    faith = 0.3
    k = (1-faith)*k + faith*current_K #danger
    for x in range(3):
        if(k[x]>threshold[x]):
            alert[x] = 1
        else:
            alert[x] = 0
    
    return alert
		
