from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np
import RPi.GPIO as GPIO
from time import sleep

trigger=10
red=29
green=31
blue=33

boot_complete=11

GPIO.setmode(GPIO.BOARD)

GPIO.setwarnings(False)

GPIO.setup(trigger,GPIO.IN)
GPIO.setup(red,GPIO.OUT)
GPIO.setup(green,GPIO.OUT)
GPIO.setup(blue,GPIO.OUT)
GPIO.setup(boot_complete,GPIO.OUT)

frame_highest_color=[]
def communicate(number):
    if(number==-1):
        GPIO.output(red,1)
        GPIO.output(green,1)
        GPIO.output(blue,1)
        print("no colour")
    elif(number==0):
        GPIO.output(red,1)
        GPIO.output(green,0)
        GPIO.output(blue,0)
        print("red")
    elif(number==1):
        GPIO.output(red,0)
        GPIO.output(green,1)
        GPIO.output(blue,0)
        print("green")
    else:
        GPIO.output(red,0)
        GPIO.output(green,0)
        GPIO.output(blue,1)
        print("blue")
    sleep(2)
    GPIO.output(red,0)
    GPIO.output(green,0)
    GPIO.output(blue,0)
    return

def get_colour_coin(colour,img):
    if (colour=="g"):
        lower = np.array([4,1,0], np.uint8)
        upper = np.array([132,103,172], np.uint8)


    elif(colour=="r"):
        lower = np.array([151,116,21], np.uint8)
        upper = np.array([173,186, 130], np.uint8)


    else:
        lower = np.array([41,136,106], np.uint8)
        upper = np.array([175,244,255], np.uint8)

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    det_color = cv2.inRange(hsv, lower, upper)
    kernal = np.ones((5, 5), "uint8")
    blue = cv2.dilate(det_color, kernal)
    res = cv2.bitwise_and(img, img, mask=det_color)

    (_, contours, hierarchy) = cv2.findContours(det_color, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    count=0
    max_area=0
    for pic, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        if (area > 150):
            count=count+1
            #x, y, w, h = cv2.boundingRect(contour)
            #img = cv2.rectangle(img, (x, y), (x + w, y + h), (22,60, 220), 3)
            max_area=area+max_area
    #cv2.imshow("Color Tracking", img)
    img = cv2.flip(img, 1)
    #cv2.imshow("Yellow", res)
    return max_area
camera = PiCamera()
camera.resolution = (608, 304)
camera.framerate = 32
threshold_area=10000
rawCapture = PiRGBArray(camera, size=(608,304))
GPIO.output(boot_complete,0)
while(True):
    GPIO.output(red,0)
    GPIO.output(green,0)
    GPIO.output(blue,0)
    if(GPIO.input(trigger)):
        frame_count=10
        frame_highest_color=[]
        for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
                frame = frame.array
                index=-1
                max_area=0
                rgb_area=[]
                p,q,r=0,0,0
                p,q,r=get_colour_coin("r",frame),get_colour_coin("g",frame),get_colour_coin("b",frame)
                rgb_area.append(p)
                rgb_area.append(q)
                rgb_area.append(r)
                print("r:",)
                print(p)
                print("g:",)
                print(q)
                print("b:",)
                print(r)
                for i in range(len(rgb_area)):
                    if(rgb_area[i]>threshold_area and max_area<rgb_area[i]):
                        index=i
                        max_area=rgb_area[i]
                key = cv2.waitKey(1)
                #print(index)
                frame_highest_color.append(index)
                rawCapture.truncate(0)
                if(frame_count==0):
                    break;
                else:
                    frame_count=frame_count-1
                    #print(frame_count)
                if key == 27:
                    break
                 
                if key == ord("q"):
                     break
    
        colour_in=max(frame_highest_color,key=frame_highest_color.count)
        #print(colour_in)
        print("#########################")
        communicate(colour_in)
