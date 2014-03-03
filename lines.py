import cv2
import numpy as np

minLineLength = 10
maxLineGap = 10

# img = cv2.imread('2014-03-02_01-53-03-RGB.png')
img = cv2.imread('2014-03-02_01-36-30.png')

blur = cv2.GaussianBlur(img, (0, 0), 10)
cv2.imshow('blur filter', blur)
img = cv2.addWeighted(img, 2, blur, -1, 0)
cv2.imshow('originalImage', img)

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

cv2.namedWindow('gray')
cv2.imshow('gray', gray)

cv2.namedWindow('edges')

def onTrackbar(test):
    param1 = cv2.getTrackbarPos('1','image')
    param2 = cv2.getTrackbarPos('2','image')
    param3 = cv2.getTrackbarPos('3','image')
    edges = cv2.Canny(gray, param1, param2)
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 70)
    # lines = None
    img2 = img.copy()
    if lines is not None:
        print "Lines"
        for rho,theta in lines[0]:
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a*rho
            y0 = b*rho
            x1 = int(x0 + 1000*(-b))
            y1 = int(y0 + 1000*(a))
            x2 = int(x0 - 1000*(-b))
            y2 = int(y0 - 1000*(a))
            cv2.line(img2,(x1,y1),(x2,y2),(0,0,255),2)
    else:
        print "No lines"
    cv2.imshow('edges', edges)
    cv2.imshow('image', img2)

cv2.namedWindow('image')
cv2.createTrackbar('1', 'image', 30, 250, onTrackbar)
cv2.createTrackbar('2', 'image', 80, 250, onTrackbar)
cv2.createTrackbar('3', 'image', 3, 5, onTrackbar)

onTrackbar(0)

cv2.waitKey(0)

exit()



