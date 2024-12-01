from find_quantity.commands import (
    CalculateQuantitiesCommand,
    ProcessFilesCommand,
    DevideProductTo26Days,
    SplitCombinedProductsCommand
)

if __name__ == "__main__":
    try:
        c = ProcessFilesCommand().execute()
        c = CalculateQuantitiesCommand().execute()
        c = DevideProductTo26Days().execute()
        c = SplitCombinedProductsCommand().execute()
    except KeyboardInterrupt:
        print("Bye!")
