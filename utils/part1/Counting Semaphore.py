import threading
import time


class CountingSempaphore:
    "This class will be used as a module - part 1"

    def __init__(self, init_value=1):

        if init_value < 0:
            raise ValueError("must give init value>0")
        self._count = init_value
        self._lock = threading.Lock()
        self._condition = threading.Condition(self._lock)

    def acquire(self, timeout=None):
        """
        Decrease semaphore value by 1.
        Block if value would become negative.
        Return True if acquired, False if timeout.
        """
        with self._condition:
            end_time = time.time() + timeout if timeout is not None else None
            while self._count == 0:
                if timeout is not None:
                    remaining_time = end_time - time.time()
                    if remaining_time <= 0:
                        return False
                    if self._condition.wait(remaining_time):
                        return False
                else:
                    # A breif explanation is provided in report centering whey should use this
                    self._condition.wait()
            self._count -= 1
            return True

    def release(self):
        with self._condition:
            self._count += 1
            self._condition.notify()

    def get_value(self):
        with self._lock:
            return self._count
