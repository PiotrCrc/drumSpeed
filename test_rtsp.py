import cv2
import numpy as np
import sys

print(sys.argv)

if __name__ == '__main__':
    
    # load source
    cap = cv2.VideoCapture(f"rtsp://{sys.argv[1]}:{sys.argv[2]}@192.168.8.20/cam/realmonitor?channel=1&subtype=0")

    while True:
        if cap.isOpened():
            ret, frame = cap.read()
  
            cv2.imshow("frame", frame)
            
            key = cv2.waitKey(10)
            
            if key == 27:
                break

    cv2.destroyAllWindows()
    cap.release()
