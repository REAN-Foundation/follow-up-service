import asyncio
import time
import logging
import functools



def log_execution_time(func):
    if asyncio.iscoroutinefunction(func):  # Check if the function is async
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.perf_counter()  # Start time
            result = await func(*args, **kwargs)
            end_time = time.perf_counter()    # End time
            execution_time = end_time - start_time
            logging.info(f"Executed {func.__name__} in {execution_time:.4f} seconds")
            return result
        return async_wrapper
    else:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.perf_counter()  # Start time
            result = func(*args, **kwargs)
            end_time = time.perf_counter()    # End time
            execution_time = end_time - start_time
            logging.info(f"Executed {func.__name__} in {execution_time:.4f} seconds")
            return result
        return sync_wrapper
