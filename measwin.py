import cv2
import numpy

class MeasWin:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.h = None
        self.w = None
        self.verify_points()
        self.calculate_w_h()
        self.new_x1 = None
        self.new_y1 = None
        self.new_x2 = None
        self.new_y2 = None

    def verify_points(self):
        if self.x1 > self.x2:
            self.x1, self.x2 = self.x2, self.x1
        if self.y1 > self.y2:
            self.y1, self.y2 = self.y2, self.y1

    def calculate_w_h(self):
        self.verify_points()
        self.h = self.y2 - self.y1
        self.w = self.x2 - self.x1

    def new_first_corner(self,x,y):
        self.new_x1 = x
        self.new_y1 = y

    def new_second_corner(self,x,y):
        if (self.new_x1 != x) and (self.new_y1 != y):  # x1 is the same as x2 and y1 is the same as y2
            self.x1 = self.new_x1
            self.y1 = self.new_y1
            self.x2 = x
            self.y2 = y
            self.calculate_w_h()

class SpeedCalc():
    def __init__(self, measwin : MeasWin, threshold, area_min, area_max) -> None:
        self.measwin = measwin
        self.threshold = threshold
        self.area_min = area_min
        self.area_max = area_max
        self.frame = None
        self.measwin_frame = None
        self.bd_rects = None
    
    def set_threshold(self, threshold):
        self.threshold = threshold

    def set_area_min(self, area_min):
        self.area_min = area_min
    
    def set_area_max(self, area_max):
        self.area_max = area_max

    def set_mw(self, measwin: MeasWin):
        self.measwin = measwin

    def prepare_measwin_frame(self,frame):
        self.frame = frame
        cropped = frame[self.measwin.y1:self.measwin.y2,
                        self.measwin.x1:self.measwin.x2]
        cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
        _, self.measwin_frame = cv2.threshold(cropped, self.threshold, 255, 1 )

    def find_rects(self, show_bd_rects = True):
        contours, _ = cv2.findContours(self.measwin_frame, 
                                        cv2.RETR_LIST, 
                                        cv2.CHAIN_APPROX_SIMPLE)

        contours = [contour for contour in contours if \
                    (self.area_min < cv2.contourArea(contour) < self.area_max)]

        self.bd_rects = [cv2.boundingRect(contour) for contour in contours]

        if show_bd_rects:
            for bd_rect in self.bd_rects:
                cv2.rectangle(self.frame,(bd_rect[0]+self.measwin.x1,
                                          bd_rect[1]+self.measwin.y1, 
                                          bd_rect[2],bd_rect[3]),(255,0,0),1)

    def calc_speed(self, show_histogram = True):
        y_points = []
        for bd_rect in self.bd_rects:
            y_points.append(bd_rect[1])
        
        histogram = []

        for y in range(self.measwin.h):
            y_count = y_points.count(y)
            histogram.append(y_count)
            if show_histogram:
                cv2.line(self.frame,(self.measwin.x1, y + self.measwin.y1),
                                    (self.measwin.x1 + y_count*5,y + self.measwin.y1),
                                    (0,0,255),1)
        
        