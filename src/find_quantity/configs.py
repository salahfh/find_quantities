import logging
from dataclasses import dataclass, fields
from pathlib import Path


logger = logging.getLogger("find_quantity.cli")


@dataclass
class Config:
    PROJECT_FOLDER: Path = Path.home() / "find_quantities"
    RAW_PRODUCTS_DATA: Path = PROJECT_FOLDER / "produits.csv"
    RAW_SHOWROOMS_DATA: Path = PROJECT_FOLDER / "showrooms.csv"
    STEP_ONE_TRANSFORM_PATH: Path = PROJECT_FOLDER / "output" / "1-Transform"
    STEP_TWO_CALCULATE_PATH: Path = PROJECT_FOLDER / "output" / "2-Calculate"
    STEP_THREE_VALIDATE_PATH: Path = PROJECT_FOLDER / "output" / "3-Validate"
    MERGE_CONFIG_PATH: Path = PROJECT_FOLDER / 'product_merge_rules.yml'
    CLEAN_BEFORE_EACH_RUN: bool = True
    CSV_SEPERATOR: str = ';'
    DAYS: int = 26
    YEAR: int = 2024        # Changed with -y via cli arg

    def create_folders(self):
        for attr in fields(self):
            path_v = self.__getattribute__(attr.name)
            if isinstance(path_v, Path):
                if not path_v.suffix and not path_v.exists():
                    path_v.mkdir(exist_ok=True, parents=True)
                    logger.info(f"Creating folder {path_v} ...")

    def clean_up(self):
        for dir in [
            self.STEP_ONE_TRANSFORM_PATH,
            self.STEP_TWO_CALCULATE_PATH,
            self.STEP_THREE_VALIDATE_PATH,
        ]:
            if dir.exists():
                [f.unlink() for f in dir.glob("*")]
    
    def copy_merge_configs(self):
        import importlib.resources
        import shutil
        import find_quantity

        package_files = importlib.resources.files(find_quantity)
        merge_conf_template = package_files / "templates" /"product_merge_rules.yml"
        if not self.MERGE_CONFIG_PATH.exists():
            shutil.copy(
                merge_conf_template,
                self.MERGE_CONFIG_PATH)


config = Config()
