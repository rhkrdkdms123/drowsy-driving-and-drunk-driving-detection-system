import time
import wiringpi as wp

# import the necessary packages
from scipy.spatial import distance as dist
from imutils.video import VideoStream
from imutils import face_utils
from threading import Thread
import numpy as np
import playsound
import argparse
import imutils
import time
import dlib
import cv2
import RPi.GPIO as GPIO

# Pin Definitions
boot_button = 28
break_button = 29
real_boot_led = 22  # green
break_led = 25  # red
boot_led = 24  # yellow
PCF = 120

# Setup Pins
wp.wiringPiSetup()
wp.pcf8591Setup(PCF, 0x48)

wp.pinMode(boot_button, wp.INPUT)
wp.pinMode(break_button, wp.INPUT)
wp.pinMode(real_boot_led, wp.OUTPUT)
wp.pinMode(break_led, wp.OUTPUT)
wp.pinMode(boot_led, wp.OUTPUT)

wp.digitalWrite(real_boot_led, wp.LOW)
wp.digitalWrite(break_led, wp.LOW)
wp.digitalWrite(boot_led, wp.LOW)

# Initial Variables
brkBtn_previous = wp.LOW
brkBtn_current = wp.LOW
btBtn_previous = wp.LOW
btBtn_current = wp.LOW

brkLED_state = wp.LOW
btLED_state = wp.LOW
is_boot = 0

BUZZER_PIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)


def sound_alarm(path):
    # play an alarm sound
    # playsound.playsound(path)
    # activate the buzzer
    GPIO.output(BUZZER_PIN, GPIO.HIGH)


def eye_aspect_ratio(eye):
    # compute the euclidean distances between the two sets of
    # vertical eye landmarks (x, y)-coordinates
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    # compute the euclidean distance between the horizontal
    # eye landmark (x, y)-coordinates
    C = dist.euclidean(eye[0], eye[3])
    # compute the eye aspect ratio
    ear = (A + B) / (2.0 * C)
    # return the eye aspect ratio
    return ear


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--shape-predictor", required=True,
                help="path to facial landmark predictor")
ap.add_argument("-a", "--alarm", type=str, default="",
                help="path alarm .WAV file")
ap.add_argument("-w", "--webcam", type=int, default=0,
                help="index of webcam on system")
args = vars(ap.parse_args())

# define two constants, one for the eye aspect ratio to indicate
# blink and then a second constant for the number of consecutive
# frames the eye must be below the threshold for to set off the
# alarm
EYE_AR_THRESH = 0.3
EYE_AR_CONSEC_FRAMES = 48
# initialize the frame counter as well as a boolean used to
# indicate if the alarm is going off
COUNTER = 0
ALARM_ON = False

# initialize dlib's face detector (HOG-based) and then create
# the facial landmark predictor
print("[INFO] loading facial landmark predictor...")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(args["shape_predictor"])

# grab the indexes of the facial landmarks for the left and
# right eye, respectively
(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

# start the video stream thread
print("[INFO] starting video stream thread...")
vs = VideoStream(src=args["webcam"]).start()
time.sleep(1.0)


# Main Loop
while True:
    brkBtn_current = wp.digitalRead(break_button)
    btBtn_current = wp.digitalRead(boot_button)
    brkLED_state = wp.digitalRead(break_led)
    btLED_state = wp.digitalRead(boot_led)

    #print(
    #    "brkBtn_current={}, btBtn_current={}, brkLED_state={}, btLED_state={}".format(
    #        brkBtn_current,
    #        btBtn_current,
    #        brkLED_state,
    #        btLED_state))

    #time.sleep(0.1)

    # break led control with break button
    if brkBtn_current:
        if brkBtn_previous == wp.LOW:
            brkLED_state = wp.digitalRead(break_led)
            wp.digitalWrite(break_led, not brkLED_state)
            brkBtn_previous = wp.HIGH
    else:
        brkBtn_previous = wp.LOW

    # boot led control with boot button
    if btBtn_current:
        if btBtn_previous == wp.LOW and brkLED_state == wp.HIGH:
            btLED_state = wp.digitalRead(boot_led)
            wp.digitalWrite(boot_led, not btLED_state)
            btBtn_previous = wp.HIGH
    else:
        btBtn_previous = wp.LOW

    # if both LEDs are HIGH, then boot the car
    is_boot = (wp.digitalRead(boot_led) ==
               wp.HIGH and wp.digitalRead(break_led) == wp.HIGH)
    wp.digitalWrite(real_boot_led, is_boot)

    if is_boot:
        alc = wp.analogRead(PCF + 0)
        print(" alc value : {}".format(alc))
        wp.analogWrite(PCF + 0, alc)

        if alc > 150:
            wp.digitalWrite(real_boot_led, wp.LOW)
            wp.digitalWrite(boot_led, wp.LOW)
            wp.digitalWrite(break_led, wp.LOW)
        # grab the frame from the threaded video file stream, resize
        # it, and convert it to grayscale
        # channels)
    frame = vs.read()
    frame = imutils.resize(frame, width=450)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # detect faces in the grayscale frame
    rects = detector(gray, 0)

    # loop over the face detections
    for rect in rects:
        # determine the facial landmarks for the face region, then
        # convert the facial landmark (x, y)-coordinates to a NumPy
        # array
        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)
        # extract the left and right eye coordinates, then use the
        # coordinates to compute the eye aspect ratio for both eyes
        leftEye = shape[lStart:lEnd]
        rightEye = shape[rStart:rEnd]
        leftEAR = eye_aspect_ratio(leftEye)
        rightEAR = eye_aspect_ratio(rightEye)
        # average the eye aspect ratio together for both eyes
        ear = (leftEAR + rightEAR) / 2.0
        # compute the convex hull for the left and right eye, then
        # visualize each of the eyes
        leftEyeHull = cv2.convexHull(leftEye)
        rightEyeHull = cv2.convexHull(rightEye)
        cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
        cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
        # check to see if the eye aspect ratio is below the blink
        # threshold, and if so, increment the blink frame counter
        if ear < EYE_AR_THRESH:
            COUNTER += 1
            # if the eyes were closed for a sufficient number of
            # then sound the alarm
            if COUNTER >= EYE_AR_CONSEC_FRAMES:
                # if the alarm is not on, turn it on
                if not ALARM_ON:
                    ALARM_ON = True
                    # check to see if an alarm file was supplied,
                    # and if so, start a thread to have the alarm
                    # sound played in the background
                    if args["alarm"] != "":
                        t = Thread(target=sound_alarm,
                                   args=(args["alarm"],))
                        t.deamon = True
                        t.start()
                # draw an alarm on the frame
                cv2.putText(frame, "DROWSINESS ALERT!", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        # otherwise, the eye aspect ratio is not below the blink
        # threshold, so reset the counter and alarm
        else:
            COUNTER = 0
            ALARM_ON = False
            GPIO.output(BUZZER_PIN, GPIO.LOW)

        # draw the computed eye aspect ratio on the frame to help
        # with debugging and setting the correct eye aspect ratio
        # thresholds and frame counters
        cv2.putText(frame, "EAR: {:.2f}".format(ear), (300, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    # show the frame
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break
# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()
