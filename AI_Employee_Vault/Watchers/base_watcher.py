import os
import time
from abc import ABC, abstractmethod

class Watcher(ABC):
    def __init__(self, interval=60):
        self.interval = interval

    @abstractmethod
    def check_for_new_items(self):
        pass

    def run(self):
        while True:
            print(f"Checking for new items at {time.ctime()}")
            self.check_for_new_items()
            time.sleep(self.interval)

if __name__ == "__main__":
    print("This is a base watcher. Please implement a concrete watcher.")
