import find_quantity.configs as C
from find_quantity.commands import (
    CalculateQuantitiesCommand,
    ProcessFilesCommand,
    DevideProductTo26Days,
    SetupFolderStructure,
)
from find_quantity.cli import CliArgs

WELCOME_MESSAGE = f"""
{'*'*30}
Find Showrooms Quantity
{'*'*30}
"""


def main() -> None:
    print(WELCOME_MESSAGE)
    try:
        CliArgs().parse_args()
        SetupFolderStructure().execute()
        ProcessFilesCommand().execute()
        CalculateQuantitiesCommand().execute()
        DevideProductTo26Days().execute()
    except FileNotFoundError as e:
        print(
            e,
            f"Make sure you have data in the input files {C.config.RAW_SHOWROOMS_DATA} and {C.config.RAW_PRODUCTS_DATA}",
            sep='\n',
        )
    except KeyboardInterrupt:
        print("Bye!")


if __name__ == "__main__":
    main()
