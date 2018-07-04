import numpy as np
import cv2
import math as m

def white_bois(flow):
    min = 10000
    for i in range(flow.shape[0]):
        for j in range(flow.shape[1]):
            mag = m.fabs(flow[i][j])
            if mag<min:
                min = mag
    for i in range(flow.shape[0]):
        for j in range(flow.shape[1]):
            if flow[i][j]>0:
                flow[i][j] -= min
            
            elif flow[i][j]<0:
                flow[i][j] += min
    return flow


#the alert generator now also takes the color of the pixels as an argument
def getAlerts(dim_X, dim_Y, ang, v, img):#takes the dimensions of the image, the direction of motion at each point and the speed of that point
    mid_Y = int(0.35*dim_Y) #wherever the horizon is in the image. mid_Y is not necessarily at the center of the image.
    roi_up = mid_Y #we can work with information in a small region. As in, the sky is not important to us.
    roi_down = int(2*mid_Y) #we don't want to look at the hood of the car
    roi_left = int(0.2*dim_X) #Not interested in what is happening 20 meters to my left or right
    roi_right = int(0.8*dim_X)

    ref_X = int(0.5*dim_X) # X axis position of camera
    ref_Y = dim_Y #bottom of the image. Y axis position of camera
    count = (roi_down - roi_up)*(roi_right-roi_left) #number of pixels in roi 
    danger = 0 #amount of danger

    road_Ref = img[int(0.80*img.shape[0]):int(0.90*img.shape[0]),int(0.45*img.shape[1]):int(0.55*img.shape[1])]
    avg_int = np.mean(road_Ref,axis=(0,1) )
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
    visualize = np.zeros(shape = (img.shape[0],img.shape[1]))
    for i in range(roi_up, roi_down ): # rows (y's)
        for j in range(roi_left, roi_right): #columns (x's)
            #initial point is the ref point. We're drawing a line from the ref point to the point under consideration.
            app_ang = m.atan2( (ref_Y-i) , ref_X-j ) #angle at which an object would move if it was coming towards ref point(us)(approach angle)
            correction = 1/m.cos( m.atan2( (i-mid_Y)/mid_Y, 1) )

            ang[i][j] = m.atan2( correction*m.sin(ang[i][j]),m.cos(ang[i][j]) )
            attack = m.cos(app_ang - ang[i][j]) #difference between approach angle and direction of velocity is the angle of attack
            speed = v[i][j]*correction #corrected speed.
            cur_img = img[i][j]
            obj_prob = (cur_img[0]/avg_int[0]) + (cur_img[1]/avg_int[1]) + (cur_img[2]/avg_int[2]) 
            obj_prob /= 3
            danger += obj_prob*speed*m.pow(attack,6) 
    danger /= count #normalize the danger
    return danger

initialized = False
k = 0

def check(img, gray, prevgray): # assumes that the images are already in grayscale 
    global initialized
    global k
    
    prevgray = cv2.resize(prevgray, (int(prevgray.shape[1]/2),int(prevgray.shape[0]/2)), cv2.INTER_LINEAR)
    gray = cv2.resize(gray, (int(gray.shape[1]/2),int(gray.shape[0]/2)), cv2.INTER_LINEAR) #resizing the images
    if(not initialized):
        alert = False
    
    flow = cv2.calcOpticalFlowFarneback(prevgray, gray,None, 0.5, 3, 15, 3, 5, 1.2, 0) #calculate flow
    
    flow_X, flow_Y = flow[:,:,0], flow[:,:,1] #the x and y components of motion.
    
    flow_X = cv2.resize(flow_X,(int(flow_X.shape[1]/8),int(flow_X.shape[0]/8)), cv2.INTER_LINEAR )#resize images 
    flow_X = white_bois(flow_X)

    flow_Y = cv2.resize(flow_Y,(int(flow_Y.shape[1]/8),int(flow_Y.shape[0]/8)), cv2.INTER_LINEAR )#to reduce computation
    flow_Y = white_bois(flow_Y)
    
    img = cv2.resize(img,(flow_X.shape[1],flow_X.shape[0]), cv2.INTER_LINEAR)
    ang = np.arctan2(flow_Y, flow_X) #the angle of motion at each point in the image
    v = np.sqrt( np.add(np.square(flow_X),np.square(flow_Y)) ) #magnitude of motion at each point.
    
    #low pass filter to reduce false positives
    current_K = getAlerts(ang.shape[1], ang.shape[0], ang, v, img)
    
    k = 0.4*k + 0.6*current_K #danger

    if(k>1.1):
        alert = True
    else:
        alert = False
    
    return alert
		