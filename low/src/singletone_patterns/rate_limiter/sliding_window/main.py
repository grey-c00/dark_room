import time

from low.src.singletone_patterns.rate_limiter.sliding_window.limiter import SlidingWindowRateLimiter

print("adf")
sliding_window_limiter = SlidingWindowRateLimiter(window_max_size=3, window_time_interval_in_seconds=5)

req_id_1 = "req_1"
req_id_2 = "req_2"


sliding_window_limiter.is_request_allowed(request_id=req_id_1, request_timestamp=time.time())
sliding_window_limiter.is_request_allowed(request_id=req_id_1, request_timestamp=time.time())
sliding_window_limiter.is_request_allowed(request_id=req_id_1, request_timestamp=time.time())


sliding_window_limiter.is_request_allowed(request_id=req_id_2, request_timestamp=time.time())
sliding_window_limiter.is_request_allowed(request_id=req_id_2, request_timestamp=time.time())

time.sleep(5)
sliding_window_limiter.is_request_allowed(request_id=req_id_1, request_timestamp=time.time())
sliding_window_limiter.is_request_allowed(request_id=req_id_1, request_timestamp=time.time())
sliding_window_limiter.is_request_allowed(request_id=req_id_1, request_timestamp=time.time())
sliding_window_limiter.is_request_allowed(request_id=req_id_1, request_timestamp=time.time())


time.sleep(20)
sliding_window_limiter.stop_bg_tasks()

print("Exit successful")





