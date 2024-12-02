from dataclasses import dataclass, fields
from pathlib import Path


@dataclass
class Config:
    PROJECT_FOLDER: Path = Path.home() / "find_quantities"
    RAW_PRODUCTS_DATA: Path = PROJECT_FOLDER / "produits.csv"
    RAW_SHOWROOMS_DATA: Path = PROJECT_FOLDER / "showrooms.csv"
    STEP_ONE_TRANSFORM_PATH: Path = PROJECT_FOLDER / "output" / "1-Transform"
    STEP_TWO_CALCULATE_PATH: Path = PROJECT_FOLDER / "output" / "2-Calculate"
    STEP_THREE_VALIDATE_PATH: Path = PROJECT_FOLDER / "output" / "3-Validate"
    CLEAN_BEFORE_EACH_RUN: bool = True
    CSV_SEPERATOR: str = ';'
    DAYS: int = 26

    def create_folders(self):
        for attr in fields(self):
            path_v = self.__getattribute__(attr.name)
            if isinstance(path_v, Path):
                if not path_v.suffix and not path_v.exists():
                    path_v.mkdir(exist_ok=True, parents=True)
                    print(f"Creating folder {path_v} ...")

    def clean_up(self):
        for dir in [
            self.STEP_ONE_TRANSFORM_PATH,
            self.STEP_TWO_CALCULATE_PATH,
            self.STEP_THREE_VALIDATE_PATH,
        ]:
            if dir.exists():
                [f.unlink() for f in dir.glob("*")]


config = Config()
