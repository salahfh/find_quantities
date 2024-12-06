import csv
import inspect
from functools import wraps
from pathlib import Path
from typing import Callable, Literal

import yaml

from find_quantity.configs import config


def get_default_args(func: Callable) -> dict:
    signature = inspect.signature(func)
    return {
        k: v.default
        for k, v in signature.parameters.items()
        if v.default is not inspect.Parameter.empty
    }


def choose_call_arg(
    target_arg: str, func: Callable, kwargs: dict, hardcoded_value: Path
) -> str:
    """Chose the value for the call argument.

    The value supplied in the call takes precedance over the default.
    Works only with kwargs."""
    v = (
        kwargs.get(target_arg, None)
        or get_default_args(func).get(target_arg)
        or hardcoded_value
    )
    assert v is not None, f"{target_arg} must supplied."
    return v


class IOTools:
    @classmethod
    def from_csv(cls, default_path: Path = None):
        """A decorator to read to csv file.

        func (data, *args, **kwargs)
        path: is optional in the decorator but become mandatory in the function signature
        """

        def decorated(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # path = default_path
                # if path is None:    # the default path arg should be also evaluated
                path = Path(choose_call_arg("path", func, kwargs, default_path))
                with open(path, "r") as f:
                    fieldnames = [field.strip() for field in next(f).split(config.CSV_SEPERATOR)]
                    reader = csv.DictReader(f,
                                            fieldnames=fieldnames,
                                            delimiter=config.CSV_SEPERATOR)
                    data = [row for row in reader]
                    return func(data, *args, **kwargs)

            return wrapper

        return decorated

    @classmethod
    def to_csv(cls, mode: Literal["a", "w"]):
        """A decorator to write to csv file.

        func -> return filename, header, data
        """

        def decorated(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                path, header, data = func(*args, **kwargs)
                writer_header = True if not path.exists() else False
                with open(path, mode) as f:
                    writer = csv.writer(f, lineterminator="\n", delimiter=config.CSV_SEPERATOR)
                    if writer_header or mode == "w":
                        writer.writerow(header)
                    for line in data:
                        writer.writerow(line)

            return wrapper

        return decorated


    # BUG: If you put path before data in the decorated function it'll crash

    def from_yml(default_path: Path = None):
        '''Read yaml file'''
        def decorated(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                path = Path(choose_call_arg("path", func, kwargs, default_path))
                with open(path, "r") as f:
                    data = yaml.safe_load(f)
                    return func(data, *args, **kwargs)

            return wrapper
        return decorated