from find_quantity.commands import (
    CalculateQuantitiesCommand,
    ProcessFilesCommand,
    ValidateQuantitiesCommand,
    DevideProductTo26Days,
)

if __name__ == "__main__":
    try:
        # c = ProcessFilesCommand().execute()
        # c = CalculateQuantitiesCommand().execute()
        c = DevideProductTo26Days().execute()
        # c = ValidateQuantitiesCommand().execute()
    except KeyboardInterrupt:
        print("Bye!")
