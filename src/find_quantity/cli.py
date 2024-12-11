import argparse
import logging
import textwrap

import find_quantity.configs as C

logger = logging.getLogger("find_quantity.cli")


class CliArgs:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.define_args()

    def define_args(self):
        self.parser.add_argument(
            "-y",
            "--year",
            type=int,
            default=C.config.YEAR,
            help=f"Select The year of the data. Default is {C.config.YEAR}",
        )
        self.parser.add_argument(
            "-u",
            "--update",
            action="store_true",
            help="Updates software to the latest version",
        )
        self.parser.add_argument(
            "-v",
            "--version",
            action="store_true",
            help="Prints the version",
        )

    def parse_args(self):
        args = self.parser.parse_args()

        if args.year:
            C.config.YEAR = args.year

        if args.version:
            import importlib.metadata

            version = importlib.metadata.version("find_quantity")
            logger.info(f"version {version}")
            exit()

        if args.update:
            import subprocess

            url = "git+https://github.com/salahfh/find_quantities.git"

            try:
                subprocess.run(["pip", "install", url], check=True)
                logger.info(
                    "Update finished. run find_quantity --version to confirm the new version"
                )
            except subprocess.CalledProcessError:
                logger.error("Update failed!")
            finally:
                exit()


def wrap(message: str, width: int = 80) -> str:
    return "\n".join(textwrap.wrap(message, width=width))


if __name__ == "__main__":
    cliargs = CliArgs()
    cliargs.parse_args()
