from functools import wraps
from pathlib import Path
import pickle


CACHE_FILE = Path(r"data\output\2. Calculate\cache.pkl")

class Cache:
    cache_file = CACHE_FILE
    enabled = True
    cache: dict = {}

    @classmethod
    def load_cache_from_disk(cls):
        if cls.cache_file.exists():
            with open(cls.cache_file, 'rb') as f:
                cls.cache = pickle.load(f)
    
    @classmethod
    def save_cache_to_disk(cls):
        with open(cls.cache_file, 'wb') as f:
            pickle.dump(cls.cache, f)
    
    def __getitem__(cls, key: tuple) -> object:
        return cls.cache[key]

    def __setitem__(cls, key: tuple, value: object) -> object:
        cls.cache[key] = value

    @classmethod
    def cached(cls, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # key = hash(args + tuple(sorted(kwargs.items())))
            key = args[1:]
            result = cls.cache.get(key) if cls.enabled else None
            if result is None:
                result = func(*args, **kwargs)
                cls.cache[key] = result
            return result   
        return wrapper


if __name__ == '__main__':

    @Cache.cached
    def fibonacci(n):
        if n < 2:
                return n
        return fibonacci(n-1) + fibonacci(n-2)
    print(fibonacci(n = 100))
