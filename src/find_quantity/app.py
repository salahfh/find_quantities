from find_quantity.commands import CalculateQuantitiesCommand
from find_quantity.cache import Cache


if __name__ == '__main__':
    Cache.load_cache_from_disk()
    try:
        # c = ProcessFilesCommand().execute()
        c = CalculateQuantitiesCommand().excute()
    except KeyboardInterrupt:
        print('Bye!')
    finally:
        Cache.save_cache_to_disk()
