from find_quantity.models.showroom import DateUtils


def test_date_util_generate_that_is_not_friday():
    FRIDAY = 4
    day = 6
    month = 12
    year = 2024

    dt = DateUtils.get_non_friday_date(month=month, day=day, year=year)

    assert dt.weekday() != FRIDAY
