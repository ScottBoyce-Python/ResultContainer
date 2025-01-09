import pytest
from ResultContainer import Result, Ok, Err, ResultErr


# Basic Initialization Tests
def test_result_ok_initialization():
    result = Result.as_Ok(42)
    assert result.is_Ok is True
    assert result.is_Err is False
    assert result.unwrap() == 42
    assert result.expect() == 42
    assert result.raises() == Ok(42)

    with pytest.raises(ResultErr):
        result.expect_Err()


def test_result_err_initialization():
    error_message = "An error occurred"
    result = Result.as_Err(error_message)
    assert result.unwrap() == Err(error_message)
    assert result.is_Ok is False
    assert result.is_Err is True

    with pytest.raises(ResultErr):
        _ = result.Ok

    with pytest.raises(ResultErr):
        _ = result.expect()

    with pytest.raises(ResultErr):
        _ = result.raises()


def test_result_ok_operation():
    result = Ok(10)

    # Arithmetic operations
    result2 = Ok(20)
    result_sum = result + result2
    assert result_sum.is_Ok
    assert result_sum.unwrap() == 30

    # Chaining operations
    mapped_result = result.map(lambda x: x * 2)
    assert mapped_result.unwrap() == 20

    applied_result = result.apply(lambda x: x + 5)
    assert applied_result.unwrap() == 15


def test_result_err_operation():
    error = Err("Initial error")

    # Adding messages
    error.add_Err_msg("Additional context")
    assert "Additional context" in error.Err_msg

    # Checking tracebacks
    assert error.Err_traceback is not None

    # apply_Err method
    result = error.apply_Err(lambda e: e.append("Another error msg", False))

    assert result.Err_msg_contains("Initial error")
    assert result.Err_msg_contains("Additional context")
    assert result.Err_msg_contains("Another error msg")

    assert result.unwrap().msg == ["Initial error", "Additional context", "Another error msg"]


# Basic Initialization Tests
def test_result_ok_attribute():
    result = Ok(42)
    assert result.Ok == 42
    assert result.unwrap() == 42
    assert result.expect() == 42
    assert result.raises() == Ok(42)
    with pytest.raises(ResultErr):
        _ = result.Err


# Edge Case Initialization
def test_result_ok_with_none():
    result = Result.as_Ok(None)
    assert result.is_Ok is True
    assert result.unwrap() is None
    assert result.expect() is None
    assert result.raises() == Ok(None)


def test_result_err_with_empty_string():
    result = Result.as_Err("")
    assert result.is_Err is True

    with pytest.raises(ResultErr):
        result.expect()

    with pytest.raises(ResultErr):
        result.raises()


# Ok_and and Ok_or
def test_result_Ok_and():
    ok2 = Ok(2)
    ok4 = Ok(4)
    er6 = Err(6)
    er8 = Err(8)

    assert ok2.Ok_and(ok4) == ok4
    assert ok2.Ok_and(er8) == er8

    assert er6.Ok_and(ok4) == er6
    assert er6.Ok_and(er8) == er6


def test_result_Ok_or():
    ok2 = Ok(2)
    ok4 = Ok(4)
    er6 = Err(6)
    er8 = Err(8)

    assert ok2.Ok_or(ok4) == ok2
    assert ok2.Ok_or(er8) == ok2

    assert er6.Ok_or(ok4) == ok4
    assert er6.Ok_or(er8) == er8


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


def test_iter_and_copy():
    """Test iteration and copying functionality of Result."""
    result = Ok([1, 2, 3])

    # Iteration
    iterated = [x for x in result.iter_wrap()]
    assert iterated == [1, 2, 3]

    # Copy
    copied_result = result.copy()
    assert copied_result == result

    # Clear
    result.unwrap().clear()
    assert len(result.unwrap()) == 0


def test_iter_list():
    lst = [0, 1, 2, 3]
    result = Result.as_Ok(lst)
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


# Reverse Tests
def test_reversed_err():
    result = Err(10)
    enter_loop = False
    for i in reversed(result):
        enter_loop = True  # should never be true
    assert not enter_loop


def test_reversed_scalar():
    result = Ok(10)
    enter_loop = False
    for i in reversed(result):
        assert i == 10
        enter_loop = True
    assert enter_loop


def test_reversed_list():
    lst = [0, 1, 2, 3]
    result = Result.as_Ok(lst)
    enter_loop = False
    rev = reversed(lst)
    for j in reversed(result):
        assert j == next(rev)
        enter_loop = True
    assert enter_loop

    rev = lst[::-1]
    enter_loop = False
    for i, j in enumerate(reversed(result)):
        assert j == rev[i]
        enter_loop = True
    assert enter_loop

    lst[-1] = 99  # Because mutable, Ok(lst) changes too
    rev = lst[::-1]
    enter_loop = False
    for i, j in enumerate(reversed(result)):
        assert j == rev[i]
        enter_loop = True
    assert enter_loop

    lst = [0, 1, 2, 3]
    result = Result.as_Ok(lst, deepcopy=True)
    enter_loop = False
    rev = lst[::-1]
    lst[-1] = 99  # does not effect result or rev because of deepcopy
    for i, j in enumerate(reversed(result)):
        assert j == rev[i]
        enter_loop = True
    assert enter_loop


# Method Tests
def test_is_ok_and():
    result = Result.as_Ok(10)
    assert result.is_Ok_and(lambda x: x == 10)
    assert result.is_Ok_and(lambda x: x < 11)
    assert result.is_Ok_and(lambda x: x * 2 < 21)


def test_result_apply():
    result = Result.as_Ok(10)
    mapped_result = result.apply(lambda x: x * 2)
    assert mapped_result.is_Ok is True
    assert mapped_result.unwrap() == 20

    error_result = Result.as_Err("Error").apply(lambda x: x * 2)
    assert error_result.is_Err is True

    with pytest.raises(ResultErr):
        error_result.expect()

    with pytest.raises(ResultErr):
        error_result.raises()

    with pytest.raises(ResultErr):
        # apply returns Err for bad function
        mapped_result = Ok(0).apply(lambda x: 10 / x)
        mapped_result.raises()


def test_result_map_simple():
    """Test mapping functions on Result."""
    result = Ok(5)

    # Map
    mapped_result = result.map(lambda x: x * 2)
    assert mapped_result.unwrap() == 10

    # Map with fallback
    result = Result.as_Err("Error")
    mapped_fallback = result.map_or(100, lambda x: x * 2)
    assert mapped_fallback == 100


def test_result_map():
    result = Result.as_Ok(10)
    mapped_result = result.map(lambda x: x * 2)
    assert mapped_result.is_Ok is True
    assert mapped_result.unwrap() == 20

    error_result = Result.as_Err("Error").map(lambda x: x * 2)
    assert error_result.is_Err is True

    with pytest.raises(ResultErr):
        error_result.expect()

    with pytest.raises(ResultErr):
        error_result.raises()

    with pytest.raises(ZeroDivisionError):
        # map raises exception for bad function
        mapped_result = Ok(0).map(lambda x: 10 / x)


def test_result_map_or():
    result = Result.as_Ok(0)
    with pytest.raises(ZeroDivisionError):
        mapped_result = result.map_or(100, lambda x: 10 / x)  # map fails on bad function call

    error_result = Result.as_Err("Error Happened")
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
    result = Result.as_Err("Initial error")
    mapped_error = result.map_Err(lambda e: f"{e.str()} - mapped")
    assert mapped_error.is_Err is False  # map_Err returns OK(f(e))

    ok_result = Result.as_Ok(10).map_Err(lambda e: f"{e.str()} - mapped")
    assert ok_result.is_Ok is True
    assert ok_result.expect() == 10


# Arithmetic Operator Overloading
def test_addition():
    result1 = Ok(10)
    result2 = Ok(20)
    combined_result = result1 + result2
    assert combined_result.unwrap() == 30

    error_result = Result.as_Ok(10) + Result.as_Err("Error")
    assert error_result.is_Err is True


def test_subtraction():
    result1 = Ok(50)
    result2 = Ok(20)
    combined_result = result1 - result2
    assert combined_result.unwrap() == 30

    error_result = Ok(50) - Err("Error")
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

    error_result = Ok(10) * Err("Error")
    assert error_result.is_Err is True


# Edge Cases for Arithmetic
def test_division_by_zero():
    result = Ok(10)
    zero_result = Ok(0)
    with pytest.raises(ResultErr):
        ans = result / zero_result
        ans.raises()


def test_modulo():
    result1 = Result.as_Ok(10)
    result2 = Result.as_Ok(3)
    combined_result = result1 % result2
    assert combined_result.unwrap() == 1

    combined_result = result2 % result1
    assert combined_result.unwrap() == 3

    combined_result = 10 % result2
    assert combined_result.unwrap() == 1

    combined_result = result1 % 3
    assert combined_result.unwrap() == 1

    error_result = Result.as_Ok(10) % Result.as_Err("Error")
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

    error_result = Result.as_Ok(10) ** Result.as_Err("Error")
    assert error_result.is_Err is True


# Error Logging Tests
def test_error_message_integrity():
    error_message = "Critical Error"
    result = Err(error_message)
    assert result.Err_msg == ["Critical Error"]
    with pytest.raises(ResultErr):
        result.raises()


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
