import cv2

camera_port = 1
camera = cv2.VideoCapture(camera_port)

# Captures a single image from the camera and returns it in PIL format
def get_image():
    # read is the easiest way to get a full image out of a VideoCapture object.
    retval, im = camera.read()
    return im

cv2.namedWindow('camera')

while True:
    camera_capture = get_image()
    cv2.imshow('camera', camera_capture)
    if cv2.waitKey(10) == 27:
        exit()