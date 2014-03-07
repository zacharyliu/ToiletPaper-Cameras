import cv2
import numpy as np
import zerorpc
import gevent.queue
from threading import Thread

class CameraLines:
    def __init__(self, camera_port):
        self.camera_port = camera_port
        self.threshold1 = 15
        self.threshold2 = 28
        self.houghThreshold = 40

        self.camera = cv2.VideoCapture(self.camera_port)
        self.camera.set(cv2.cv.CV_CAP_PROP_FPS, 10)

        # global detection status
        self.detect = False

        self.trackbarLeft, self.trackbarRight = 328, 482

        # Capture one image to get dimensions
        self.height, self.width, self.depth = self.get_image().shape

        # Windows and trackbars
        cv2.namedWindow('lines')
        cv2.createTrackbar('Left', 'lines', self.trackbarLeft, 1000, self.onTrackbar)
        cv2.createTrackbar('Right', 'lines', self.trackbarRight, 1000, self.onTrackbar)
        cv2.createTrackbar('Hough', 'lines', self.houghThreshold, 100, self.onTrackbar)

        cv2.namedWindow('edges')
        cv2.createTrackbar('Threshold 1', 'edges', self.threshold1, 300, self.onTrackbar)
        cv2.createTrackbar('Threshold 2', 'edges', self.threshold2, 300, self.onTrackbar)

        self._subscribers = set()

    # Captures a single image from the camera and returns it in PIL format
    def get_image(self):
        # read is the easiest way to get a full image out of a VideoCapture object.
        retval, im = self.camera.read()
        return im

    # Update trackbar variables
    def onTrackbar(self, var):
        self.trackbarLeft = cv2.getTrackbarPos('Left', 'lines')
        self.trackbarRight = cv2.getTrackbarPos('Right', 'lines')
        self.threshold1 = cv2.getTrackbarPos('Threshold 1', 'edges')
        self.threshold2 = cv2.getTrackbarPos('Threshold 2', 'edges')
        self.houghThreshold = cv2.getTrackbarPos('Hough', 'lines')

    @zerorpc.stream
    def subscribe(self):
        print "Subscriber"
        try:
            queue = gevent.queue.Queue()
            self._subscribers.add(queue)
            for msg in queue:
                yield msg
        finally:
            self._subscribers.remove(queue)

    def _publish(self, msg):
        for queue in self._subscribers:
            queue.put(msg)

    def loop(self):
        img = self.get_image()
        cv2.imshow('raw camera', img)

        # blur = cv2.GaussianBlur(img, (0, 0), 5)
        # cv2.imshow('blur filter', blur)
        # img = cv2.addWeighted(img, 3, blur, -2, 0)
        # img = cv2.GaussianBlur(img, (0, 0), sigmaX=1, sigmaY=3)
        cv2.imshow('sharpened', img)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # gray = cv2.equalizeHist(gray)
        cv2.imshow('gray', gray)

        edges = cv2.Canny(gray, self.threshold1, self.threshold2)
        cv2.imshow('edges', edges)

        lines = cv2.HoughLines(edges, 1, np.pi, self.houghThreshold)

        img2 = img.copy()

        detect = False
        if lines is not None:
            for rho, theta in lines[0]:
                # since code is only detecting vertical lines, theta is always 0
                # so rho is the x position of the detected vertical line
                if theta == 0 and self.trackbarLeft < rho < self.trackbarRight:
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
        cv2.line(img2, (self.trackbarLeft, 0), (self.trackbarLeft, self.height), (0, 255, 0), 2)
        cv2.line(img2, (self.trackbarRight, 0), (self.trackbarRight, self.height), (0, 255, 0), 2)

        if detect:
            cv2.putText(img2, "Detect", (10, self.height-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
            cv2.putText(img2, "No Detect", (10, self.height-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.imshow('lines', img2)

        if cv2.waitKey(10) == 27:
            exit()

def loop():
    while True:
        cameraLines.loop()

if __name__ == '__main__':
    cameraLines = CameraLines(0)
    s = zerorpc.Server(cameraLines)
    s.bind("tcp://0.0.0.0:4243")
    thread = Thread(target=loop)
    thread.start()
    s.run()
