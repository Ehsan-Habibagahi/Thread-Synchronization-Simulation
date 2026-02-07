import threading
import time


class ReentrantMutex:

    def __init__(self):
        self._lock = threading.Lock()
        self._condition = threading.Condition(self._lock)
        self._owner = None
        self._count = 0  # number of times owner has acquired

    def acquire(self, blocking=True):
        """
         Lock the mutex. If already locked by current thread,
        increment lock count (reentrant behavior).
        """
        with self._condition:
            if self._owner == threading.current_thread():
                self._count += 1
                return True

            if not blocking:
                if self._owner is not None:
                    return False
            else:
                while self._owner is not None:
                    self._condition.wait()
            self._owner = threading.current_thread()
            self._count = 1
            return True

    def release(self):
        with self._condition:
            if self._owner is None:
                raise RuntimeError(
                    "release was called on not locked ReentrantMutex")
            if self._owner != threading.current_thread():
                raise RuntimeError(
                    f"releas was called by non-owner thread: owner:{self._owner}\ncurrent:{threading.current_thread()}")
            self._count -= 1
            if self._count == 0:
                self._owner = None
                self._condition.notify()

    def is_locked(self):
        with self._lock:
            return self._owner is not None

    def owned_by_current_thread(self):
        """Return True if current thread owns this mutex"""
        current_thread = threading.current_thread()
        with self._lock:
            return self._owner == current_thread
        
    def get_lock_count(self):
        # I needed to add this for debug
        with self._lock:
            return self._count
        
    # I implement CMP for easier usage of this class

    def __enter__(self):
        self.acquire()
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
        return False
