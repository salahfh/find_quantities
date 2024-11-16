from typing import Literal
from pathlib import Path
from functools import wraps
import csv


class IOTools:
    working_dir = Path('.')

    @classmethod
    def from_csv(cls, path: Path):
        '''A decorator to read to csv file.

        func (data, *args, **kwargs)
        '''
        def decorated(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                with open(cls.working_dir / path, 'r') as f:
                    reader = csv.DictReader(f)
                    data = ([row for row in reader])
                    return func(data, *args, **kwargs)
            return wrapper
        return decorated

    @classmethod
    def to_csv(cls, mode: Literal['a', 'w']):
        '''A decorator to write to csv file.

        func -> return filename, header, data
        '''
        def decorated(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                filename, header, data = func(*args, **kwargs)
                path = Path(cls.working_dir / filename)
                writer_header = True if not path.exists() else False
                with open(path, mode) as f:
                    writer = csv.writer(f, lineterminator='\n')
                    if writer_header or mode == 'w':
                        writer.writerow(header)
                    for line in data:
                        writer.writerow(line)
            return wrapper
        return decorated

