from rwsuis import RWS
import time

robot = RWS.RWS("{Robot’s IP}")

robot.request_rmmp() # Mastership request in manual mode
time.sleep (10) # Give time to accept manual request

new_robtarget = [0 , 0 , 400]
robot.set_robtarget_translation ("{ variable name in RAPID }" ,
new_robtarget)