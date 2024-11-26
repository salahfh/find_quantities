from pathlib import Path

import pytest

from find_quantity.commons import IOTools

TEST_FOLDER = Path("tests")


def clean_up(path: Path):
    if path.exists():
        path.unlink()


@pytest.fixture()
def filename():
    return Path(r"test_file.csv")


@pytest.fixture()
def data():
    return ((1, 2, 3, 4),)


@pytest.fixture()
def header():
    return ["one", "two", "three", "four"]


class TestIOTools:
    def test_writing_to_csv(self, filename, data, header):
        @IOTools.to_csv(mode="w")
        def write_data():
            return TEST_FOLDER / filename, header, data

        write_data()
        path = Path(TEST_FOLDER / filename)
        assert path.exists()
        clean_up(path=path)

    # @pytest.mark.skip('This test has been skip because this behavior has not been implemented')
    def test_reading_from_csv_with_filename_hardcoded(self, filename):
        @IOTools.from_csv(default_path=TEST_FOLDER / filename)
        def read_data(data: dict):
            return len(data)

        path = Path(TEST_FOLDER / filename)
        with open(path, "w") as f:
            f.write(",".join(["one", "two", "three", "four"]))
            f.write("\n")
            f.write(",".join(["1", "2", "3", "4"]))
            f.write("\n")

        data_length = read_data()
        assert data_length == 1
        clean_up(path=path)

    def test_reading_from_csv_with_filename_as_agument_to_function_signature(
        self, filename
    ):
        @IOTools.from_csv()
        def read_data(data: dict, path):
            return len(data)

        path = Path(TEST_FOLDER / filename)
        with open(path, "w") as f:
            f.write(",".join(["one", "two", "three", "four"]))
            f.write("\n")
            f.write(",".join(["1", "2", "3", "4"]))
            f.write("\n")

        data_length = read_data(path=TEST_FOLDER / filename)
        assert data_length == 1
        clean_up(path=path)

    def test_reading_from_csv_with_filename_as_agument_to_function_signature_and_has_default_value(
        self, filename
    ):
        @IOTools.from_csv()
        def read_data(data: dict, path=TEST_FOLDER / filename):
            return len(data)

        path = Path(TEST_FOLDER / filename)
        with open(path, "w") as f:
            f.write(",".join(["one", "two", "three", "four"]))
            f.write("\n")
            f.write(",".join(["1", "2", "3", "4"]))
            f.write("\n")

        data_length = read_data()
        assert data_length == 1

    # @pytest.mark.skip('Precedance is to the call variable over the global hard coded value')
    def test_reading_from_csv_with_filename_hardcoded_also_available_in_signature_and_passed_as_call_argument(
        self, filename
    ):
        @IOTools.from_csv(default_path=TEST_FOLDER / filename)
        def read_data(data: dict, path: Path):
            return len(data)

        # Writing to a diffent file
        path = Path(TEST_FOLDER / "test_csv2.csv")
        with open(path, "w") as f:
            f.write(",".join(["one", "two", "three", "four"]))
            f.write("\n")
            f.write(",".join(["1", "2", "3", "4"]))
            f.write("\n")

        data_length = read_data(path=path)
        assert data_length == 1
        for p in [path, TEST_FOLDER / filename]:
            clean_up(path=p)
