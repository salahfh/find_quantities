import logging
import re
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from find_quantity.utils.commons import IOTools

logger = logging.getLogger("find_quantity.cli")


class Commands(Enum):
    AutoMergeIOProducts = "AutoMergeIOProducts"
    AutoMergeNCEProducts = "AutoMergeNCEProducts"
    AutoMergeKCGProducts = "AutoMergeKCGProducts"
    MergeBasedOnPattern = "MergeBasedOnPattern"
    CombineProducts = "CombineProducts"


@dataclass
class MergeRule:
    name: str
    command: str
    pattern: str = None
    products: list = field(default_factory=list)

    def __post_init__(self):
        try:
            self.command = Commands(self.command)
        except ValueError:
            logger.exception(
                f'"{self.command}" is not a valid command. Please edit again the merge_config.yml'
            )
            exit()


class PackageDefinitionsConstructor:
    """Generate the package defitions based on the rules defined in the configs.

    Example of package definition
    [
        ('CMD211', 'CRG14CL1N', 'CRG14CL1NCMD'),
        ('CMS542-A6IT3-O', 'CMS542-A6IT3-I'),
        ('NCE150', 'NCE150CMD'),
        ('NCE185', 'NCE185CMD'),
        ('NCE185',), ('NCE150',), ('NCE185CMD',), ('CMS542-A6IT3-I',),
    ]
    """

    def __init__(self, merge_rules: list[MergeRule]):
        self.merge_rules = merge_rules

    def make_package_definitions(
        self, product_n_articles: list[str]
    ) -> set[tuple[str]]:
        packages = set()
        for merge_rule in self.merge_rules:
            match merge_rule.command:
                case Commands.AutoMergeIOProducts:
                    pkgs = self.merge_int_i_and_ext_o_rule(product_n_articles)
                case Commands.AutoMergeNCEProducts:
                    pkgs = self.merge_based_on_pattern(
                        product_n_articles, pattern=r"^NCE\d{3}"
                    )
                case Commands.AutoMergeKCGProducts:
                    pkgs = self.merge_based_on_pattern(
                        product_n_articles, pattern=r"^KCG\d{3}"
                    )
                case Commands.CombineProducts:
                    pkgs = self.merge_products_from_predefine_list(merge_rule.products)
                case Commands.MergeBasedOnPattern:
                    pkgs = self.merge_based_on_pattern_with_product_crossing(
                        product_n_articles,
                        pattern=merge_rule.pattern,
                        cross_prod=merge_rule.products,
                    )
            packages.update(pkgs)

        # generate single packages for all products.
        for prod in product_n_articles:
            packages.add((prod,))
        return sorted(packages, reverse=True, key=lambda t: len(t))

    def merge_int_i_and_ext_o_rule(
        self, product_n_articles: list[str]
    ) -> list[list[str]]:
        stems = defaultdict(list)
        for n_art in product_n_articles:
            stem = self.__find_product_stem(n_article=n_art, prefixes=["-I", "-O"])
            if stem:
                stems[stem].append(n_art)
        return tuple(
            {tuple(v) for v in stems.values()},
        )

    def merge_based_on_pattern(
        self, product_n_articles: list[str], pattern: str
    ) -> list[list[str]]:
        matches = defaultdict(list)
        for n_art in product_n_articles:
            match = re.compile(pattern).match(n_art)
            if match:
                matches[match.group()].append(n_art)
        return tuple(
            {tuple(v) for v in matches.values()},
        )

    def merge_based_on_pattern_with_product_crossing(
        self, product_n_articles: list[str], pattern: str, cross_prod: list[str]
    ) -> list[list[str]]:
        matches = self.merge_based_on_pattern(
            product_n_articles=product_n_articles, pattern=pattern
        )
        cross_matches: list[tuple] = list()
        for m in matches:
            m = tuple(list(m) + [p for p in cross_prod])
            cross_matches.append(m)
        return cross_matches

    def merge_products_from_predefine_list(
        self, product_n_articles: list[str]
    ) -> list[list[str]]:
        return (tuple(product_n_articles),)

    def __find_product_stem(self, n_article: str, prefixes: list[str]) -> str | None:
        n_article = n_article.replace(" ", "").strip()
        if any(n_article.endswith(pfix) for pfix in prefixes):
            return n_article[:-2]
        return None


@IOTools.from_yml()
def parse_merge_configs(data: dict, path: Path) -> list[MergeRule]:
    parsed_rules = []
    for rule in data["ProductMergeRules"]:
        packages = rule.get("packages", [])
        for val in packages:
            products = val["products"]
            r = MergeRule(
                name=rule["rule"],
                command=rule["command"],
                pattern=rule.get("pattern", None),
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
    pass
