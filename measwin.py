import cv2
import numpy as np
from collections import defaultdict

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
    def __init__(self, measwin : MeasWin, threshold, area_min, area_max, mode = 1) -> None:
        self.mode = mode  # define constants
        self.measwin = measwin
        self.threshold = threshold
        self.area_min = area_min
        self.area_max = area_max
        self.frame = None
        self.measwin_frame = None
        self.bd_rects = None
        self.histogram = None
        self.last_histogram = None
        self.avg_spd_array = []
        self.avg_spd_100ms = 0.0
        self.avg_spd_500ms = 0.0
        self.contours = []

    def corellate_window(array_old, array_new, max_shift = 25):
        assert 2 * max_shift <= len(array_new), "max_shift should be at least 2x array len"
        assert len(array_old) == len(array_new), "arrays must be the same size"
        results = []
        for i in range(max_shift):
            results.append(np.correlate(array_old[:-max_shift],array_new[i:-max_shift+i])[0])
        return results.index(max(results))


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

        # filter contours by area
        self.contours = [contour for contour in contours if \
                    (self.area_min < cv2.contourArea(contour) < self.area_max)]

        self.bd_rects = [cv2.boundingRect(contour) for contour in self.contours]

        if show_bd_rects:
            for bd_rect in self.bd_rects:
                cv2.rectangle(self.frame,(bd_rect[0]+self.measwin.x1,
                                        bd_rect[1]+self.measwin.y1, 
                                        bd_rect[2],bd_rect[3]),(255,0,0),1)

    def calc_speed(self, show_histogram = True):
        y_dict = defaultdict(int)

        if self.mode == 0:
            for bd_rect in self.bd_rects:
                y_dict[bd_rect[1]] += bd_rect[3]
        elif self.mode == 1:
            for contour in self.contours:
                for point in contour:
                    y_dict[point.item(1)] += 1    

        self.last_histogram = self.histogram

        self.histogram = np.array([0]*self.measwin.h)
        for key, val in y_dict.items():
            self.histogram[key] = val
        
        #self.histogram = np.convolve(self.histogram, [0,2.5,5,2.5,0], 'valid')
        
        if show_histogram:
            y = 0
            for val in self.histogram:    
                cv2.line(self.frame,(self.measwin.x1, y + self.measwin.y1),
                                    (self.measwin.x1 + int(val),y + self.measwin.y1),
                                    (0,0,255),1)
                y += 1
        
        # if (self.histogram is not None) and (self.last_histogram is not None):
        #     corr = np.correlate(self.histogram,self.last_histogram, mode='full') # this need to be changed for higly similar paterns in y axis
        #     shift = np.argmax(corr) - len(self.last_histogram) + 1
        
        self.avg_spd_array.append(self.corellate_window(self.last_histogram,self.histogram, max_shift = 25)) # to be tested

        if len(self.avg_spd_array) > 25:
            self.avg_spd_array.pop(0)
            self.avg_spd_500ms = sum(self.avg_spd_array)
            self.avg_spd_100ms = sum(self.avg_spd_array[-5:])


class MeasChart():
    def __init__(self) -> None:
        self.img = np.zeros((480,640,3), dtype=np.uint8)
        self.clear()
        self.last_x = 1
        self.last_y = 240

    def draw_new_point(self,y):
        if self.last_x > 639:
            self.clear()
            self.last_x = 1
        new_point = (self.last_x+1, 240+int(y))
        cv2.line(self.img, (self.last_x,self.last_y),new_point ,(255,0,0), 1)
        self.last_x += 1
        self.last_y = new_point[1]

    def clear(self):
        cv2.rectangle(self.img,(0,0),(640,480),(255, 255, 255),-1)
        cv2.line(self.img,(0,240),(640,240),(0,0,0),1)



