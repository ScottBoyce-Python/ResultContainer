import pytest
from ResultContainer import Result, Ok, Err, ResultErr


# Basic Initialization Tests
def test_result_ok_initialization():
    result = Result.Ok(42)
    assert result.is_Ok is True
    assert result.is_Err is False
    assert result.unwrap() == 42
    assert result.expect() == Result.Ok(42)

    with pytest.raises(ResultErr):
        result.expect_Err()


def test_result_err_initialization():
    error_message = "An error occurred"
    result = Result.Err(error_message)
    assert result.is_Ok is False
    assert result.is_Err is True

    with pytest.raises(ResultErr):
        result.expect()

    with pytest.raises(ResultErr):
        result.raises()


# Edge Case Initialization
def test_result_ok_with_none():
    result = Result.Ok(None)
    assert result.is_Ok is True
    assert result.unwrap() is None
    assert result.expect() is None
    assert result.raises() == Ok(None)


def test_result_err_with_empty_string():
    result = Result.Err("")
    assert result.is_Err is True

    with pytest.raises(ResultErr):
        result.expect()

    with pytest.raises(ResultErr):
        result.raises()


# Iter Tests
def test_iter_err():
    result = Err(10)
    enter_loop = False
    for i in result:
        enter_loop = True  # should never be true
    assert not enter_loop


def test_iter_scalar():
    result = Ok(10)
    enter_loop = False
    for i in result:
        assert i == 10
        enter_loop = True
    assert enter_loop


def test_iter_list():
    lst = [0, 1, 2, 3]
    result = Result.Ok(lst)
    enter_loop = False
    i = 0
    for j in result:
        assert j == lst[i]
        i += 1
        enter_loop = True
    assert enter_loop

    enter_loop = False
    for i, j in enumerate(result):
        assert j == lst[i]
        enter_loop = True
    assert enter_loop

    lst[-1] = 99  # Because mutable, Ok(lst) changes too
    enter_loop = False
    for i, j in enumerate(result):
        assert j == lst[i]
        enter_loop = True
    assert enter_loop


# Method Tests
def test_is_ok_and():
    result = Result.Ok(10)
    assert result.is_Ok_and(lambda x: x == 10)
    assert result.is_Ok_and(lambda x: x < 11)
    assert result.is_Ok_and(lambda x: x * 2 < 21)


def test_result_apply():
    result = Result.Ok(10)
    mapped_result = result.apply(lambda x: x * 2)
    assert mapped_result.is_Ok is True
    assert mapped_result.unwrap() == 20

    error_result = Result.Err("Error").apply(lambda x: x * 2)
    assert error_result.is_Err is True

    with pytest.raises(ResultErr):
        error_result.expect()

    with pytest.raises(ResultErr):
        error_result.raises()

    with pytest.raises(ResultErr):
        # apply returns Err for bad function
        mapped_result = Ok(0).apply(lambda x: 10 / x)
        mapped_result.raises()


def test_result_map():
    result = Result.Ok(10)
    mapped_result = result.map(lambda x: x * 2)
    assert mapped_result.is_Ok is True
    assert mapped_result.unwrap() == 20

    error_result = Result.Err("Error").map(lambda x: x * 2)
    assert error_result.is_Err is True

    with pytest.raises(ResultErr):
        error_result.expect()

    with pytest.raises(ResultErr):
        error_result.raises()

    with pytest.raises(ZeroDivisionError):
        # map raises exception for bad function
        mapped_result = Ok(0).map(lambda x: 10 / x)


def test_result_map_or():
    result = Result.Ok(0)
    with pytest.raises(ZeroDivisionError):
        mapped_result = result.map_or(100, lambda x: 10 / x)  # map fails on bad function call

    error_result = Result.Err("Error Happened")
    mapped_result = error_result.map_or(99, lambda x: 10 / x)  # Immediately replaces Err with 99
    assert mapped_result.expect() == 99


def test_result_apply_or():
    result = Ok(0)
    mapped_result = result.apply_or(100, lambda x: 10 / x)
    assert mapped_result.expect() == 100

    error_result = Err("Error Happened")
    mapped_result = error_result.apply_or(99, lambda x: 10 / x)
    assert mapped_result.expect() == 99


def test_result_map_err():
    result = Result.Err("Initial error")
    mapped_error = result.map_Err(lambda e: f"{e.str()} - mapped")
    assert mapped_error.is_Err is False  # map_Err returns OK(f(e))

    ok_result = Result.Ok(10).map_Err(lambda e: f"{e.str()} - mapped")
    assert ok_result.is_Ok is True
    assert ok_result.expect() == 10


def test_result_apply_chain():
    new_result = (
        Ok(10)
        .apply(lambda x: Result.Ok(x * 2))  # Ok(20)
        .apply(lambda x: Result.Ok(x * 2))  # Ok(40)
        .apply(lambda x: Result.Ok(x * 2))  # Ok(80)
        .apply(lambda x: Result.Ok(x * 2))  # Ok(160)
    )
    assert new_result.is_Ok is True
    assert new_result.expect() == 160

    error_result = (
        Err("Error")
        .apply(lambda x: Result.Ok(x * 2))  # Appends to error
        .apply(lambda x: Result.Ok(x * 2))  # Appends to error
        .apply(lambda x: Result.Ok(x * 2))  # Appends to error
    )
    assert error_result.is_Err is True
    with pytest.raises(ResultErr):
        error_result.expect()

    result_error = Ok(10)
    # Separated
    new_result = result_error.apply(lambda x: Result.Ok(x * 2)).apply(lambda x: Result.Ok(x * 2))
    assert new_result.is_Err is False
    new_result = new_result.apply(lambda x: Result.Ok(x * 0)).apply(lambda x: Result.Ok(10 / x))
    assert new_result.is_Err is True

    with pytest.raises(ResultErr):
        new_result = (
            Ok(10)
            .apply(lambda x: Result.Ok(x * 2))  # Ok(20)
            .apply(lambda x: Result.Ok(x * 2))  # Ok(40)
            .apply(lambda x: Result.Ok(x * 0))  # Ok(40)
            .apply(lambda x: Result.Ok(10 / x))  # Raises ZeroDiv Error
            .apply(lambda x: Result.Ok(x + 1))  # Appends to error message
            .raises()  # Raises Exception if in Err state
        )


# Arithmetic Operator Overloading
def test_addition():
    result1 = Ok(10)
    result2 = Ok(20)
    combined_result = result1 + result2
    assert combined_result.unwrap() == 30

    error_result = Result.Ok(10) + Result.Err("Error")
    assert error_result.is_Err is True


def test_subtraction():
    result1 = Result.Ok(50)
    result2 = Result.Ok(20)
    combined_result = result1 - result2
    assert combined_result.unwrap() == 30

    error_result = Result.Ok(50) - Result.Err("Error")
    assert error_result.is_Err is True

    combined_result = 50 - result2
    assert combined_result.unwrap() == 30

    combined_result = result1 - 20
    assert combined_result.unwrap() == 30


def test_multiplication():
    result1 = Ok(10)
    result2 = Ok(20)
    combined_result = result1 * result2
    assert combined_result.unwrap() == 200

    combined_result = result2 * result1
    assert combined_result.unwrap() == 200

    error_result = Result.Ok(10) * Result.Err("Error")
    assert error_result.is_Err is True


# Edge Cases for Arithmetic
def test_division_by_zero():
    result = Ok(10)
    zero_result = Ok(0)
    with pytest.raises(ResultErr):
        ans = result / zero_result
        ans.raises()


def test_modulo():
    result1 = Ok(10)
    result2 = Ok(3)
    combined_result = result1 % result2
    assert combined_result.unwrap() == 1

    combined_result = result2 % result1
    assert combined_result.unwrap() == 3

    combined_result = 10 % result2
    assert combined_result.unwrap() == 1

    combined_result = result1 % 3
    assert combined_result.unwrap() == 1

    error_result = Result.Ok(10) % Result.Err("Error")
    assert error_result.is_Err is True


def test_pow():
    result1 = Ok(10)
    result2 = Ok(3)
    combined_result = result1**result2
    assert combined_result.unwrap() == 1000

    combined_result = result1**3
    assert combined_result.unwrap() == 1000

    combined_result = 10**result2
    assert combined_result.unwrap() == 1000

    error_result = Result.Ok(10) ** Result.Err("Error")
    assert error_result.is_Err is True


# Error Logging Tests
def test_error_message_integrity():
    error_message = "Critical Error"
    result = Err(error_message)
    assert result.Err_msg == ["Critical Error"]
    with pytest.raises(ResultErr):
        result.raises()


def test_error_chaining_integrity():
    error_result = Err("Initial Error")
    chained_result = error_result.map(lambda x: x * 2).map_Err(lambda e: f"{e.str()} - chained")
    assert chained_result.is_Err is False  # map_Err returns Ok(f(e))


# Integration Tests
def test_real_world_scenario():
    def divide(a, b):
        if b == 0:
            return Err("Division by zero")
        return Ok(a / b)

    result = divide(10, 2).map(lambda x: x * 5).map(lambda x: int(x))
    assert result.is_Ok is True
    assert result.expect() == 25

    error_result = divide(10, 0).map(lambda x: x * 5)
    assert error_result.is_Err is True
    with pytest.raises(ResultErr):
        error_result.expect()
