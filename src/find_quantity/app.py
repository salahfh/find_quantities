import find_quantity.configs as C
import find_quantity.transformer_csv as T
from find_quantity.commands import (
    CalculateQuantitiesCommand,
    ProcessFilesCommand,
    DevideProductTo26Days,
    SplitCombinedProductsCommand,
    SetupFolderStructure,
)

WELCOME_MESSAGE = f"""
{'*'*30}
Running Find Showrooms Quantities
{'*'*30}
"""


def main() -> None:
    print(WELCOME_MESSAGE)
    try:
        SetupFolderStructure().execute()
        ProcessFilesCommand().execute()
        CalculateQuantitiesCommand().execute()
        DevideProductTo26Days().execute()
        SplitCombinedProductsCommand().execute()
    except FileNotFoundError as e:
        print(e)
        print(
            f"Make sure you have data in the input files {C.config.RAW_SHOWROOMS_DATA} and {C.config.RAW_PRODUCTS_DATA}"
        )
    except T.ProductDuplicatedException as e:
        e.print_products()
    except KeyboardInterrupt:
        print("Bye!")


if __name__ == "__main__":
    main()
