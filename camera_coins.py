import cv2
import numpy as np

camera_port = 1

camera = cv2.VideoCapture(camera_port)

# Captures a single image from the camera and returns it in PIL format
def get_image():
    # read is the easiest way to get a full image out of a VideoCapture object.
    retval, im = camera.read()
    return im

height, width, depth = get_image().shape

while True:
    img = get_image()
    # img = cv2.resize(img, (width/2, height/2))

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imshow('gray', gray)

    smooth = cv2.GaussianBlur(gray, (0, 0), 2)
    # smooth = cv2.Canny(gray, 5, 40)
    cv2.imshow('smooth', smooth)

    circles = cv2.HoughCircles(smooth, cv2.cv.CV_HOUGH_GRADIENT, 2, height/4, 100, 50)

    if circles is not None:
        print len(circles[0])

        for circle in circles[0]:
            cv2.circle(img, (circle[0], circle[1]), circle[2], (0, 0, 255), 3)

    cv2.imshow('image', img)
    cv2.waitKey(10)
