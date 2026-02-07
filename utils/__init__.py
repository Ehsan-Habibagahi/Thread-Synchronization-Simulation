from importlib import import_module

_counting_semaphore = import_module('utils.part1.Counting Semaphore')
_mutex = import_module('utils.part1.ReentrantMutex')
CountingSemaphore = _counting_semaphore.CountingSempaphore
ReentrantMutex = _mutex.ReentrantMutex
__all__ = ['CountingSemaphore']