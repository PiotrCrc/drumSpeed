import cv2
import numpy as np
import sys
from measwin import MeasWin, SpeedCalc, MeasChart
from fpsmeas import FpsMeas
from threading import Thread
import time

class VideoGet:
    def __init__(self, src=0):
        self.fps_meas = FpsMeas(array_size=30)
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False
        self.new_frame = False

    def start(self):    
        Thread(target=self.get, args=()).start()
        return self

    def get(self):
        while not self.stopped:
            if not self.grabbed:
                self.stop()
            else:
                #time.sleep(0.030)
                (self.grabbed, self.frame) = self.stream.read()
                self.new_frame = self.grabbed
                self.fps_meas.time_since_last()

    def stop(self):
        self.stopped = True

def _(_):
    pass

def filter_contours(contours, min_area : int, max_area : int):
    result = []
    for contour in contours:
        if min_area < cv2.contourArea(contour) < max_area:
            result.append(contour)
    return(result)

def boundrect2rect(br,offset_x = 0,offset_y = 0):
    x,y,w,h = br
    return((x+offset_x,y+offset_y,w,h))

if __name__ == '__main__':
    mw = MeasWin(435,100,735,600)
    sc = SpeedCalc(mw,35,2000,8000)
    fps = FpsMeas(array_size=30)
    mc = MeasChart()

    cv2.namedWindow('thr')
    cv2.namedWindow('chart')
    cv2.namedWindow('frame')
    cv2.createTrackbar('Threshold', 'thr', 0, 255, sc.set_threshold)
    cv2.createTrackbar('Area_max', 'frame', 0, 10000, sc.set_area_max)
    cv2.createTrackbar('Area_min', 'frame', 0, 10000, sc.set_area_min)

    cv2.setTrackbarPos('Threshold', 'thr', 50)
    cv2.setTrackbarPos('Area_max', 'frame', 8000)
    cv2.setTrackbarPos('Area_min', 'frame', 1000)

    def click_event(event, x, y, flags, params):
        if event == cv2.EVENT_LBUTTONDOWN:
            print(f"down at : {x}, {y}")
            mw.new_first_corner(x,y)
        elif event == cv2.EVENT_LBUTTONUP:
            print(f"up at : {x}, {y}")
            mw.new_second_corner(x,y)
            sc.set_mw(mw)

    # load source
    # cap = cv2.VideoCapture(0)
    # cap = cv2.VideoCapture(f"rtsp://{sys.argv[1]}:{sys.argv[2]}@192.168.8.20/cam/realmonitor?channel=1&subtype=1")
    vg = VideoGet(f"rtsp://{sys.argv[1]}:{sys.argv[2]}@192.168.8.20/cam/realmonitor?channel=1&subtype=0")
    #vg = VideoGet("20221107_110104.mp4")
    vg.start()

    my_filter = []
    frame_time = 0
    frame_time_last = 0

    first_run = True

    while True:
        area_max_value = cv2.getTrackbarPos('Area_max', 'frame')
        area_min_value = cv2.getTrackbarPos('Area_min', 'frame')
        if first_run:
            cv2.setTrackbarPos('Threshold', 'thr', 50)
            cv2.setTrackbarPos('Area_max', 'frame', 8000)
            cv2.setTrackbarPos('Area_min', 'frame', 1000)
            fps.set_act()
            
            first_run = False
        if vg.new_frame:
            vg.new_frame = False
            ret, frame = vg.grabbed, vg.frame

            if ret:     
                sc.prepare_measwin_frame(frame)
                sc.find_rects()
                sc.calc_speed()
                # cropped = frame[mw.y1:mw.y2,mw.x1:mw.x2]
                # cropped_gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
                # _, threshold = cv2.threshold(cropped_gray, threshold_value, 255, 1 )
                # # Calculate frame duration 
                # frame_time_last = frame_time
                # frame_time = cap.get(cv2.CAP_PROP_POS_MSEC) 

            
            # contours, hierarchy = cv2.findContours(threshold, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            
            # y_points = []                  
            # contours = filter_contours(contours,area_min_value,area_max_value)                             # clear y_point list
            # for contour in contours:
            #     boundingRect = cv2.boundingRect(contour);
                
            #     if (boundingRect[3] > 35):                          # filter contours based on height

            #         cv2.rectangle(frame,boundrect2rect(boundingRect,mw.x1,mw.y1),(255,0,0),1) # display
            #         y_points.append(boundingRect[1])                # add to list of y points
                        
            # histogram = []                                              # clear "histogram" of y points
            # for y in range(0,mw.h):
            #     histogram.append(y_points.count(y))
            #     cv2.line(frame,(0,y),(y_points.count(y)*3,y),(0,0,255),1)     # display histogram
                
            # histogram = np.array (histogram)                            # convert to numpy array

            # histogram = np.convolve(histogram, np.ones(3), 'valid')     # convolution to smoth histogram
            
            # my_filter_last = my_filter.copy()        ilter.copy()                           # copy values from last iteration
            # my_filter = []                          # copy values from last iteration
            # my_filter = []                                              # clear table for results
            
            # calculate points were value drops for the first time since was 0
            # temp_value = 0
            # found_max = 0
            # for x in range(len(histogram)):
            #     if histogram[x] > temp_value:
            #         temp_value = histogram[x]
            #     elif (histogram[x] < temp_value) and (found_max==0):
            #         my_filter.append(x)
            #         found_max = 1
            #     elif (found_max == 1) and (histogram[x] == 0):
            #         found_max = 0
            #         temp_value = histogram[x]
                    
            # calculate how much did the picture moved 
            # need to find a way to detect if the picture is not moving ?!
            # diff = []
            # my_filter_temp = my_filter.copy()           # must use temp because need data for next loop
            # for point_last in my_filter_last:
            #     for point in my_filter_temp:
            #         if point<point_last:                # if there is displacment calculate 
            #             my_filter_temp.remove(point)            
            #             diff.append(point-point_last)
            #             break;

            # diplaying data
            cv2.rectangle(frame,(mw.x1,mw.y1),(mw.x2,mw.y2),(0,0,255),1)
            # cv2.rectangle(frame, (x_h+10,y_l), (x_h + 200, y_l + 150), (0,0,0), -1)
            # cv2.putText(frame,text='{:.2f}px'.format(-np.average(diff))
            #             ,org=(x_h+15,y_l+25),color=(0,0 , 255)
            #             ,fontScale=1,fontFace=cv2.FONT_HERSHEY_DUPLEX)
            cv2.putText(frame,text='{:.3f}ms'.format(vg.fps_meas.avg)
                        ,org=(mw.x1+15,mw.y2+20),color=(0,0 , 255)
                        ,fontScale=1,fontFace=cv2.FONT_HERSHEY_DUPLEX)
            cv2.putText(frame,text='{: 6.1f}px/100ms'.format(sc.avg_spd_100ms)
                        ,org=(mw.x1+15,mw.y2+60),color=(0,0 , 255)
                        ,fontScale=1,fontFace=cv2.FONT_HERSHEY_DUPLEX)
            cv2.putText(frame,text='{: 6.1f}px/500ms'.format(sc.avg_spd_500ms)
                        ,org=(mw.x1+15,mw.y2+100),color=(0,0 , 255)
                        ,fontScale=1,fontFace=cv2.FONT_HERSHEY_DUPLEX)
            mc.draw_new_point(sc.avg_spd_100ms)
            # cv2.putText(frame,text='{:.2f}px/ms'.format((-np.average(diff))/(frame_time-frame_time_last))
            #             ,org=(x_h+15,y_l+95),color=(0,0 , 255)
            #             ,fontScale=1,fontFace=cv2.FONT_HERSHEY_DUPLEX)
            
            # threshold
            cv2.imshow("thr",sc.measwin_frame)

            cv2.imshow("frame", frame)

            cv2.imshow("chart",mc.img)

            # add click event
            cv2.setMouseCallback('frame', click_event)
            
            key = cv2.waitKey(1)
            
            if key == 27:
                break
        
    cv2.destroyAllWindows()
    vg.stop()
    # cap.release()


# https://stackoverflow.com/questions/60816436/open-cv-rtsp-camera-buffer-lag