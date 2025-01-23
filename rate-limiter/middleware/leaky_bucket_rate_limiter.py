import time, threading
from queue import Queue

from fastapi import Request, status
from fastapi.responses import PlainTextResponse
from starlette.types import ASGIApp
from starlette.middleware.base import BaseHTTPMiddleware


bucket_lock = threading.Lock()
bucket = Queue()


def leaker_fn(leaks_per_second: float, threads_event: threading.Event):
    delay_s = 1. / leaks_per_second
    while threads_event.is_set():
        with bucket_lock:
            if not bucket.empty():
                request: threading.Semaphore = bucket.get()
                request.release()
        time.sleep(delay_s)


class LeakyBucketRateLimiterMiddleware(BaseHTTPMiddleware):


    def __init__(self, app: ASGIApp, capacity: int, leaks_per_second: float, threads_event: threading.Event):
        super().__init__(app)

        self.capacity = capacity
        self.leaks_per_second = leaks_per_second
        
        self.leaker_thread = threading.Thread(target=leaker_fn, args=(leaks_per_second, threads_event))
        self.leaker_thread.start()


    async def dispatch(self, request: Request, call_next):
        semaphore = threading.Semaphore(value=0)
        
        with bucket_lock:
            if bucket.qsize() < self.capacity:
                bucket.put(semaphore)
            else:
                return PlainTextResponse(status_code=status.HTTP_429_TOO_MANY_REQUESTS)

        semaphore.acquire()

        return await call_next(request)
