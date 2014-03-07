import cv2
import numpy as np
import gevent.queue
import zerorpc
from threading import Thread

class CameraCoins:
    def __init__(self, port):
        self.camera_port = port
        self.camera = cv2.VideoCapture(self.camera_port)
        self.height, self.width, self.depth = self.get_image().shape
        self._subscribers = set()

    def get_image(self):
        # read is the easiest way to get a full image out of a VideoCapture object.
        retval, im = self.camera.read()
        return im

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
        # img = cv2.resize(img, (width/2, height/2))

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # cv2.imshow('gray', gray)

        smooth = cv2.GaussianBlur(gray, (0, 0), 5)
        # smooth = cv2.Canny(gray, 5, 40)
        # cv2.imshow('smooth', smooth)

        circles = cv2.HoughCircles(smooth, cv2.cv.CV_HOUGH_GRADIENT, 2, self.height/4, 100, 30, minRadius=10, maxRadius=self.height/2)

        if circles is not None:
            self._publish(len(circles[0]))

            for circle in circles[0]:
                cv2.circle(img, (circle[0], circle[1]), circle[2], (0, 0, 255), 3)

        cv2.imshow('image', img)
        cv2.waitKey(10)

def loop():
    while True:
        cameraCoins.loop()

if __name__ == '__main__':
    cameraCoins = CameraCoins(0)
    s = zerorpc.Server(cameraCoins)
    s.bind("tcp://0.0.0.0:4242")
    thread = Thread(target=loop)
    thread.start()
    s.run()
