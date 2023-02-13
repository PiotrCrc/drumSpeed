class MeasWin:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.height = None
        self.weight = None
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
        self.height = self.y1 - self.y1
        self.weight = self.x1 - self.x2

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

    @property
    def x_0(self): return self.x1

    @property
    def y_0(self): return self.y1

    @property
    def x_1(self): return self.x2

    @property
    def y_1(self): return self.y2

    @property
    def w(self): return self.weight

    @property
    def h(self): return self.height
