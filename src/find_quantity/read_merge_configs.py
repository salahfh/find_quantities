from enum import Enum
from pathlib import Path
from dataclasses import dataclass, field

import yaml


class Commands(Enum):
    AutoMergeIOProducts = "AutoMergeIOProducts"
    AutoMergeNCEProducts = "AutoMergeNCEProducts"
    AutoMergeKCGProducts = "AutoMergeKCGProducts"
    CombineProducts = "CombineProducts"


@dataclass
class MergeRule:
    name: str
    command: str
    products: list = field(default_factory=list)

    def __post_init__(self):
        try:
            self.command = Commands(self.command)
        except ValueError:
            print(
                f'"{self.command}" is not a valid command. Please edit again the merge_config.yml'
            )
            exit()


def read_merge_configs(path: Path):
    with open(path) as f:
        merge_configs = yaml.safe_load(f)
    return merge_configs


def parse_merge_configs(rules: dict) -> list[MergeRule]:
    parsed_rules = []
    for rule in rules["ProductMergeRules"]:
        packages = rule.get("packages", [])
        for val in packages:
            products = val["products"]
            r = MergeRule(
                name=rule["rule"],
                command=rule["command"],
                products=products,
            )
            parsed_rules.append(r)
        if not packages:
            r = MergeRule(
                name=rule["rule"],
                command=rule["command"],
            )
            parsed_rules.append(r)
    return parsed_rules


if __name__ == "__main__":
    merge_configs_path = Path(
        r"C:\Users\saousa\Scripts\MustafaAcc\src\find_quantity\templates\product_merge_rules.yml"
    )
    configs = read_merge_configs(merge_configs_path)
    rules = parse_merge_configs(configs)
    for rule in rules:
        print(rule)
