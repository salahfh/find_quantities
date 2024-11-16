from pathlib import Path
import pytest
from find_quantity.commons import IOTools


TEST_FOLDER = Path('tests')
IOTools.working_dir = TEST_FOLDER


def clean_up(path: Path):
    if path.exists():
        path.unlink()


@pytest.fixture()
def filename():
    return Path(r'test_file.csv')


@pytest.fixture()
def data():
    return ((1, 2, 3, 4),)


@pytest.fixture()
def header():
    return ['one', 'two', 'three', 'four']


class TestIOTools:

    def test_writing_to_csv(self, filename, data, header):

        @IOTools.to_csv(mode='w')
        def write_data():
            return filename, header, data

        write_data()
        path = Path(TEST_FOLDER / filename)
        assert path.exists() == True
        clean_up(path=path)

    def test_reading_from_csv(self, filename):

        @IOTools.from_csv(path=filename)
        def read_data(data: dict):
            return len(data)

        path = Path(TEST_FOLDER / filename)
        with open(path, 'w') as f:
            f.write(','.join(['one', 'two', 'three', 'four']))
            f.write('\n')
            f.write(','.join(['1', '2', '3', '4']))
            f.write('\n')

        data_length = read_data()
        assert data_length == 1
        clean_up(path=path)
