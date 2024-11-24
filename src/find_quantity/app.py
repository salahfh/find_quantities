from find_quantity.commands import CalculateQuantitiesCommand, ProcessFilesCommand, ValidateQuantitiesCommand


if __name__ == '__main__':
    try:
        c = ProcessFilesCommand().execute()
        c = CalculateQuantitiesCommand().execute()
        c = ValidateQuantitiesCommand().execute()
    except KeyboardInterrupt:
        print('Bye!')
