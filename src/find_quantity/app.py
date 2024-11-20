from find_quantity.commands import CalculateQuantitiesCommand, ProcessFilesCommand, ValidateQuantitiesCommand
from find_quantity.cache import Cache


if __name__ == '__main__':
    Cache.enabled = False
    Cache.load_cache_from_disk()
    try:
        # c = ProcessFilesCommand().execute()
        c = CalculateQuantitiesCommand().excute()
        c = ValidateQuantitiesCommand().excute()
    except KeyboardInterrupt:
        print('Bye!')
    finally:
        Cache.save_cache_to_disk()
