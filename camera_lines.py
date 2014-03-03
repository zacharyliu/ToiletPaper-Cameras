import cv2
import numpy as np

camera_port = 2
threshold1 = 20
threshold2 = 70

camera = cv2.VideoCapture(camera_port)
camera.set(cv2.cv.CV_CAP_PROP_FPS, 10)

# global detection status
detect = False

trackbarLeft, trackbarRight = 0, 0

# Captures a single image from the camera and returns it in PIL format
def get_image():
    # read is the easiest way to get a full image out of a VideoCapture object.
    retval, im = camera.read()
    return im

# Capture one image to get dimensions
height, width, depth = get_image().shape

# Update trackbar variables
def onTrackbar(var):
    global trackbarLeft, trackbarRight
    trackbarLeft = cv2.getTrackbarPos('Left', 'lines')
    trackbarRight = cv2.getTrackbarPos('Right', 'lines')

cv2.namedWindow('lines')
cv2.createTrackbar('Left', 'lines', 0, 1000, onTrackbar)
cv2.createTrackbar('Right', 'lines', 0, 1000, onTrackbar)

while True:
    img = get_image()
    cv2.imshow('raw camera', img)

    blur = cv2.GaussianBlur(img, (0, 0), 5)
    cv2.imshow('blur filter', blur)
    img = cv2.addWeighted(img, 3, blur, -2, 0)
    cv2.imshow('sharpened', img)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imshow('gray', gray)

    edges = cv2.Canny(gray, threshold1, threshold2)
    cv2.imshow('edges', edges)

    lines = cv2.HoughLines(edges, 1, np.pi, 50)

    img2 = img.copy()

    detect = False
    if lines is not None:
        for rho, theta in lines[0]:
            # since code is only detecting vertical lines, theta is always 0
            # so rho is the x position of the detected vertical line
            if trackbarLeft < rho < trackbarRight:
                detect = True

            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a * rho
            y0 = b * rho
            x1 = int(x0 + 1000 * (-b))
            y1 = int(y0 + 1000 * (a))
            x2 = int(x0 - 1000 * (-b))
            y2 = int(y0 - 1000 * (a))
            cv2.line(img2, (x1, y1), (x2, y2), (0, 0, 255), 2)

    # draw the left and right trackbar lines
    cv2.line(img2, (trackbarLeft, 0), (trackbarLeft, height), (0, 255, 0), 2)
    cv2.line(img2, (trackbarRight, 0), (trackbarRight, height), (0, 255, 0), 2)

    if detect:
        cv2.putText(img2, "Detect", (10, height-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    else:
        cv2.putText(img2, "No Detect", (10, height-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow('lines', img2)

    if cv2.waitKey(10) == 27:
        exit()