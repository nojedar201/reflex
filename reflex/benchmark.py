import time


# define the benchmark context manager
class Benchmark:
    # constructor
    def __init__(self, name):
        # store the name of this benchmark
        self.name = name

    # enter the context manager
    def __enter__(self):
        # record the start time
        self.time_start = time.perf_counter()
        # return this object
        return self

    # exit the context manager
    def __exit__(self, exc_type, exc_value, traceback):
        # record the end time
        self.time_end = time.perf_counter()
        # calculate the duration
        self.duration = self.time_end - self.time_start
        # report the duration
        print("-"*40)
        print(f'{self.name} took {self.duration:.3f} seconds')
        # do not suppress any exception
        return False