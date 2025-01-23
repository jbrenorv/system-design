import threading

from fastapi import FastAPI
from contextlib import asynccontextmanager

from .settings import Settings
from .middleware.leaky_bucket_rate_limiter import LeakyBucketRateLimiterMiddleware
from .middleware.sliding_window_counter_rate_limiter import SlidingWindowCounterRateLimiterMiddleware


settings = Settings()
threads_event = threading.Event()
threads_event.set()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    threads_event.clear()


app = FastAPI(lifespan=lifespan)


if settings.use_sliding_window_counter > 0:
    app.add_middleware(
        SlidingWindowCounterRateLimiterMiddleware,
        window_size=settings.window_size,
        requests_per_window=settings.requests_per_window,
        threads_event=threads_event
    )
else:
    app.add_middleware(
        LeakyBucketRateLimiterMiddleware,
        capacity=settings.capacity,
        leaks_per_second=settings.leaks_per_second,
        threads_event=threads_event
    )


@app.get("/")
async def root():
    return {"message": "Hello World"}
