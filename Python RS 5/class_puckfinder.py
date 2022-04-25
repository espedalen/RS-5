import cv2
import requests
import time
import numpy as np
from rwsuis import RWS
from pyzbar.pyzbar import decode


class puckfinder():
    def __init__(self) -> None:
        pass

    def capture_image(self):
        self.cap = cv2.VideoCapture(1)

        # Change resolution to 1280 x960
        self.cap.set(3,1280)
        self.cap.set(4,960)

        self.ret , self.frame = self.cap.read()
        return self.cap

    def init_norbert_com(self):
        
        self.norbert = RWS.RWS("http://152.94.0.38")

        self.norbert.request_rmmp() # Mastership request in manual mode
        time.sleep(10) # Give time to accept manual request
        return

        # Wait method used in Python

    def wait_for_rapid(self, var ="ready_flag"): # Wait method used in Python
        # Waits for robot to complete RAPID instructions
        # until boolean variable in RAPID is set to ’TRUE ’.
        # Default variable name is ’ready_flag ’, but others may be used .

        while self.norbert.get_rapid_variable(var) == "FALSE" and self.is_running():
            time.sleep(0.1)
            self.norbert.set_rapid_variable(var, "FALSE")
        
        return

    def set_norbert(self): # Set norbert in position to capture the first image

        self.new_robtarget = [-55, 0, 400] ## Dont know if this is correct -- Should put camera in center/directly above workobject
        # Z-element is working distance
        self.norbert.set_robtarget_translation ("{ variable name in RAPID }", self.new_robtarget ) # Remember to add variable name in rapid

        self.wait_for_rapid()

        return self.new_robtarget

    def capture_QR(self, show_img = 0):
        # Capture image
        self.img = self.capture_image()

        ###### Preprocess image ######
        # Reduce noise
        self.img = cv2.cvtColor(self.img,cv2.COLOR_BGR2GRAY)
        self.se = cv2.getStructuringElement(cv2.MORPH_RECT , (8,8))
        self.bg = cv2.morphologyEx(self.img, cv2.MORPH_DILATE, self.se)
        self.out_gray = cv2.divide(self.img, self.bg, scale=255)

        # Increase contrast

        alpha = 1.5 # Contrast control (1.0-3.0)
        beta = 0 # Brightness control (0-100)

        self.out_cont = cv2.convertScaleAbs(self.out_gray, alpha=alpha, beta=beta)

        if show_img == 1:
            cv2.imshow('Original', self.img)
            cv2.imshow('Denoised', self.out_gray)
            cv2.imshow('Contrasted', self.out_cont)

        ####### Find QR codes in image ######

        self.data = decode(self.out_cont) # QR code center
        x = (self.data.polygon[0])[0] + ((self.data.polygon[2])[0])/2
        y = (self.data.polygon[0])[1] + ((self.data.polygon[1])[1])/2
        self.center = [x,y]

        # Draw red sqaures on QR-codes ##################### <----------------- !!!!!!!!!!!!!!!!!

        # Extract position data for QR-codes

        self.center[0] = self.center[0] - (1280/2)
        self.center[1] = self.center[1] - (960/2)

        x_t = -self.center[1]
        y_t = -self.center[0]
        center_t = [x_t, y_t]

        sensor_width = 3.6288 #mm
        focal_length = 3.7 #mm
        working_distance = self.new_robtarget[2]
        resolution_width = 1280 #pixels

        # Conversion from pixels to millimeters
        FOV_width = (sensor_width/focal_length)*(working_distance+70-30)
        p2m = FOV_width/resolution_width

        self.center_puck = [x_t*p2m, y_t*p2m]

        ################### NOT FINISHED HERE (I THINK) #############################

        return self.center_puck

    def send_robtarget_and_move(self):

        safe_height = 60

        self.robtarget = [self.center_puck[0]-55, self.center_puck[1], safe_height] # subtract 55 for camera
        self.norbert.set_robtarget_translation ("{ variable name in RAPID }", self.robtarget)

        self.wait_for_rapid()
        
        return

    def turn_off_motors(self):
        
        return
