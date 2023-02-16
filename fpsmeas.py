import time

class FpsMeas():
    def __init__(self,act_time: float = None, array_size: int = 10) -> None:
        self._act_time = None
        self._prev_time = None
        self.set_act(act_time)
        self._prev_time_array=[]
        self._min = 0.0
        self._max = 0.0
        self._avg = 0.0
        self._array_size = array_size
        self._stats_rdy = False

    def set_act(self,act_time: float = None):
        if act_time is None:
            self._act_time = time.time() * 1000
        else:
            self._act_time = act_time
    
    def _calc_stats(self):
        self._min = min(self._prev_time_array)
        self._max = max(self._prev_time_array)
        self._avg = sum(self._prev_time_array)/len(self._prev_time_array)

    @property
    def min(self):
        if (self._stats_rdy):
            return self._min
        else:
            return 0.0

    @property
    def max(self):
        if (self._stats_rdy):
            return self._max
        else:
            return 0.0

    @property
    def avg(self):
        if (self._stats_rdy):
            return self._avg
        else:
            return 0.0

    def _add_to_array(self,time_diff):
        self._prev_time_array.append(time_diff)
        if len(self._prev_time_array) > self._array_size:
            self._prev_time_array.pop(0)
            self._calc_stats()
            self._stats_rdy = True
    
    def time_since_last(self,act_time: float = None) -> float:
        self._prev_time = self._act_time
        self.set_act(act_time)
        result = self._act_time - self._prev_time
        self._add_to_array(result)
        return result

