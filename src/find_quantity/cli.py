import importlib.metadata
import subprocess 
import argparse

import find_quantity.configs as C

class CliArgs:
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.define_args()

    def define_args(self):
        self.parser.add_argument("-y",
                            "--year",
                            type=int,
                            default=2023,
                            help="Select The year of the data")
        self.parser.add_argument("-u",
                            "--update",
                            action="store_true",
                            help="Updates software to the latest version",
                            )
        self.parser.add_argument("-v",
                            "--version",
                            action="store_true",
                            help="Prints the version",
                            )

    def parse_args(self):
        args = self.parser.parse_args()

        if args.year:
            C.config.YEAR = args.year

        if args.version:
            version = importlib.metadata.version('find_quantity')
            print(f'version {version}')
            exit()

        if args.update:
            url = "git+https://github.com/salahfh/find_quantities.git"
            subprocess.run(["pip", "install", url])
            print('Update finished')
            exit()
            


if __name__ == '__main__':
    cliargs = CliArgs()
    cliargs.parse_args()