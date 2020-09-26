import time
from PIL import Image as I
import array
import cv2, numpy
    
def track_green_object(image):
    #image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    kernel = numpy.ones((5,5),numpy.uint8)
    # Blur the image to reduce noise100
    blur = cv2.GaussianBlur(image, (5,5),0)
    # Convert BGR to HSV
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
    # Threshold the HSV image for only green colors
    range_green = 10
    lower_green = numpy.array([60-range_green,50,50])
    upper_green = numpy.array([60+range_green,255,255])
    # Threshold the HSV image to get only green colors
    mask = cv2.inRange(hsv, lower_green, upper_green)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    # Blur the mask
    bmask = cv2.GaussianBlur(mask, (5,5),0)
    # Take the moments to get the centroid
    moments = cv2.moments(bmask)
    m00 = moments['m00']
    centroid_x, centroid_y = None, None
    if m00 != 0:
        centroid_x = int(moments['m10']/m00)
        centroid_y = int(moments['m01']/m00)
    # Assume no centroid
    ctr = None
    # Use centroid if it exists
    if centroid_x != None and centroid_y != None:
        ctr = (centroid_x, centroid_y)
    return ctr

def track_red_object(image):
    #image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    kernel = numpy.ones((5,5),numpy.uint8)
    # Blur the image to reduce noise100
    blur = cv2.GaussianBlur(image, (5,5),0)
    # Convert BGR to HSV
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
    # Threshold the HSV image for only green colors
    range_red = 5
    lower_red = numpy.array([0 - range_red,50,50])
    upper_red = numpy.array([0 + range_red,255,255])
    # Threshold the HSV image to get only green colors
    mask = cv2.inRange(hsv, lower_red, upper_red)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    # Blur the mask
    bmask = cv2.GaussianBlur(mask, (5,5),0)
    # Take the moments to get the centroid
    moments = cv2.moments(bmask)
    m00 = moments['m00']
    centroid_x, centroid_y = None, None
    if m00 != 0:
        centroid_x = int(moments['m10']/m00)
        centroid_y = int(moments['m01']/m00)
    # Assume no centroid
    ctr = None
    # Use centroid if it exists
    if centroid_x != None and centroid_y != None:
        ctr = (centroid_x, centroid_y)
    return ctr
    
def track_blue_object(image):
    #image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    kernel = numpy.ones((5,5),numpy.uint8)
    # Blur the image to reduce noise100
    blur = cv2.GaussianBlur(image, (5,5),0)
    # Convert BGR to HSV
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
    # Threshold the HSV image for only green colors
    range_blue = 3
    lower_blue = numpy.array([110-range_blue,50,50])
    upper_blue = numpy.array([110+range_blue,255,255])
    # Threshold the HSV image to get only green colors
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    # Blur the mask
    bmask = cv2.GaussianBlur(mask, (5,5),0)
    # Take the moments to get the centroid
    moments = cv2.moments(bmask)
    m00 = moments['m00']
    centroid_x, centroid_y = None, None
    if m00 != 0:
        centroid_x = int(moments['m10']/m00)
        centroid_y = int(moments['m01']/m00)
    # Assume no centroid
    ctr = None
    # Use centroid if it exists
    if centroid_x != None and centroid_y != None:
        ctr = (centroid_x, centroid_y)
    return ctr
def track_yellow_object(image):
    #image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    kernel = numpy.ones((2,2),numpy.uint8)
    # Blur the image to reduce noise100
    blur = cv2.GaussianBlur(image, (5,5),0)
    # Convert BGR to HSV
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
    # Threshold the HSV image for only green colors
    range_Yellow = 10
    lower_Yellow = numpy.array([30-range_Yellow,100,100])
    upper_Yellow = numpy.array([30+range_Yellow,255,255])
    # Threshold the HSV image to get only green colors
    mask = cv2.inRange(hsv, lower_Yellow, upper_Yellow)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    # Blur the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    mu = [None]*len(contours)
    for i in range(len(contours)):
        mu[i] = cv2.moments(contours[i])
    # Get the mass centers
    mc = [None]*len(contours)
    for i in range(len(contours)):
        # add 1e-5 to avoid division by zero
        mc[i] = (int(mu[i]['m10'] / (mu[i]['m00'] + 1e-5 )),int(mu[i]['m01'] / (mu[i]['m00'] + 1e-5 )))
    return mc