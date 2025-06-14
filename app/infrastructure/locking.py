import threading
from contextlib import contextmanager
from threading import Lock
from typing import Dict


class RWLock:

    def __init__(self):
        self._read_ready = threading.Condition(threading.Lock())
        self._readers = 0

    def acquire_read(self):
        with self._read_ready:
            self._readers += 1

    def release_read(self):
        with self._read_ready:
            self._readers -= 1
            if self._readers == 0:
                self._read_ready.notify_all()

    def acquire_write(self):
        self._read_ready.acquire()
        while self._readers > 0:
            self._read_ready.wait()

    def release_write(self):
        self._read_ready.release()


class LockManager:

    def __init__(self):
        self.locks: Dict[str, Lock] = {}

    def _get_lock(self, key: str) -> Lock:
        if key not in self.locks:
            self.locks[key] = Lock()
        return self.locks[key]

    @contextmanager
    def read_lock(self, key: str):
        lock = self._get_lock(key)
        lock.acquire()
        try:
            yield
        finally:
            lock.release()

    @contextmanager
    def write_lock(self, key: str):
        lock = self._get_lock(key)
        lock.acquire()
        try:
            yield
        finally:
            lock.release()
