from pathlib import Path
import pickle


CACHE_FILE = Path(r"data\output\2. Calculate\cache.pkl")

def save_cache_to_file(cache: dict, filename: Path=CACHE_FILE):
    with open(filename, 'wb') as f:
        pickle.dump(cache, f)

def load_cache_from_file(filename: Path=CACHE_FILE) -> dict:
    if filename.exists():
        with open(filename, 'rb') as f:
            return pickle.load(f)
    