import argparse
import cv2
import imutils
import datetime
import time

# TODO: add erosion before dilation
#       optimum sensitivity

# Constructing a parser
ap = argparse.ArgumentParser()

# Adding arguments
ap.add_argument("-v", "--video", help="Video Stream")
ap.add_argument("-a", "--min-area", type=int, default=500, help="minimum area size")
args = vars(ap.parse_args())

# If video argument is null, we read from webcam
if args.get("video", None) is None:
    vs = cv2.VideoCapture('http://192.168.43.1:8084/video')
    time.sleep(2.0)
# Else we read from video file provided
else:
    vs = cv2.VideoCapture(args["video"])

# First frame of the Video
firstFrame = None

while True:
    # grab the current frame and initialize the occupied/unoccupied text
    ret, frame = vs.read()
    frame = cv2.resize(frame, None, fx=0.5, fy=0.5)
    frame = frame if args.get("video", None) is None else frame[1]
    text = "Unoccupied"
    # frame = cv2.UMat(frame)
    # print(frame)
    # frame = np.array(frame)
    # Unpacking the tuple, it contains a bool and an array
    # value, img_arr = frame
    # print(frame)
    # print(type(frame))
    # for i in frame.size():
    #     frame[i] = np.float32(frame[i])
    # print(type(frame))

    # if the frame could not be grabbed, then we have reached the end of the video
    if frame is None:
        break
    # cv2.resize(frame, (200, 200))

# resize the frame, convert it to grayscale, and blur it
    # frame = imutils.resize(frame, width=500)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # gray = cv2.GaussianBlur(gray, (21, 21), 0)

# if the first frame is None, initialize it
    if firstFrame is None:
        firstFrame = gray
        continue
    # compute the absolute difference between the current frame and first frame
    frameDelta = cv2.absdiff(firstFrame, gray)
    # assign a threshold
    thresh = cv2.threshold(frameDelta, 100, 255, cv2.THRESH_BINARY)[1]

# dilate the thresholded image to fill in holes,
# then find contours on thresholded image
    thresh = cv2.dilate(thresh, None, iterations=2)
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    firstFrame = gray
    # loop over the contours
    for c in cnts:
        # if the contour is too small, ignore it
        if cv2.contourArea(c) < args["min_area"]:
            continue

# compute the bounding box for the contour, draw it on the frame,
# and update the text
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        text = "Occupied"
    # draw the text and timestamp on the frame
    cv2.putText(frame, "Room Status: {}".format(text), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

    # show the frame and record if the user presses a key
    cv2.imshow("Security Feed", frame)
    cv2.imshow("Thresh", thresh)
    # cv2.imshow("Frame Delta", frameDelta)
    key = cv2.waitKey(1) & 0xFF

# if the `q` key is pressed, break from the loop
    if key == ord("q"):
        break
