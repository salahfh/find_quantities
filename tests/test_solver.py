from find_quantity.solver import generate_equal_qt, generate_random_qt

# random.seed(22)


def test_equal_quantity_generator():
    sample_length = 8
    quantity_to_divide = 13
    qt = generate_equal_qt(sample_length, quantity_to_divide)

    assert isinstance(qt, list)
    assert isinstance(qt[0], int)
    assert len(qt) == sample_length
    assert sum(qt) == quantity_to_divide


def test_random_quantity_generator():
    equal_quantities = [3, 3, 3, 3, 3]

    new_quantities = generate_random_qt(
        sample_length=len(equal_quantities),
        quantity_to_divide=sum(equal_quantities),
    )

    print(sum(new_quantities), new_quantities, end="\n" * 3)

    assert len(new_quantities) == len(equal_quantities)
    assert sum(new_quantities) == sum(equal_quantities)
    assert new_quantities != equal_quantities, (new_quantities, sum(new_quantities))


if __name__ == "__main__":
    test_equal_quantity_generator()
    test_random_quantity_generator()
