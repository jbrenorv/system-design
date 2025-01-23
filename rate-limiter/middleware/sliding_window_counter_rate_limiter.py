import time, threading, math

from fastapi import Request, status
from fastapi.responses import PlainTextResponse
from starlette.types import ASGIApp
from starlette.middleware.base import BaseHTTPMiddleware


class Window:
    def __init__(self):
        self.start_time = time.time()
        self.counter = 0


    def increment_counter(self):
        self.counter += 1


windows_lock = threading.Lock()
previous = Window()
current = Window()


def window_updater_fn(window_size: float, threads_event: threading.Event):
    while threads_event.is_set():
        with windows_lock:
            now = time.time()
            
            previous.start_time = now - window_size
            previous.counter = current.counter
            
            current.start_time = now
            current.counter = 0

        time.sleep(window_size)


class SlidingWindowCounterRateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, window_size: float, requests_per_window: int, threads_event: threading.Event):
        super().__init__(app)

        self.window_size = window_size
        self.requests_per_window = requests_per_window

        self.window_updater_thread = threading.Thread(target=window_updater_fn, args=(window_size, threads_event))
        self.window_updater_thread.start()


    async def dispatch(self, request: Request, call_next):
        if self.allow_request():
            return await call_next(request)
        return PlainTextResponse(status_code=status.HTTP_429_TOO_MANY_REQUESTS)
    
    
    def allow_request(self):
        with windows_lock:
            now = time.time()
            sw_start_time = now - self.window_size
            sw_percentage_overlap_pw = (current.start_time - sw_start_time) / self.window_size
            sw_counter = math.floor(current.counter + sw_percentage_overlap_pw * previous.counter)
            if sw_counter < self.requests_per_window:
                current.increment_counter()
                return True
            return False
