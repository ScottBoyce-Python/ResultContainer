import pytest
from ResultContainer import Result, ResultErr, Ok, Err


# Test for Result.as_Ok and Result.as_Err initialization
def test_ok_initialization():
    result1 = Result.as_Ok("Success")
    assert result1.is_Ok
    assert result1.unwrap() == "Success"

    result2 = Ok("Success")
    assert result2.is_Ok
    assert result2.unwrap() == "Success"
    assert result1 == result2


def test_err_initialization():
    result1 = Result.as_Err("Failure")
    assert result1.is_Err
    assert result1.unwrap().msg == ["Failure"]

    result2 = Err("Failure")
    assert result2.is_Err
    assert result2.unwrap().msg == ["Failure"]
    assert result1 == result2


def test_result_error_handling():
    """Test detailed error handling and propagation."""
    result = Result.as_Err("Failure")

    # Error message check
    assert result.Err_msg_contains("Failure")

    # Add message
    result.add_Err_msg("Another failure")
    assert result.Err_msg_contains("Another failure")

    # Expect error
    with pytest.raises(ResultErr):
        result.expect()

    with pytest.raises(ResultErr):
        result.raises()


# Test for adding Ok values
def test_ok_addition():
    result1 = Ok(5)
    result2 = Ok(10)
    result3 = result1 + result2
    assert result3.is_Ok
    assert result3 == 15
    assert result3.unwrap() == 15


# Test for adding Ok and Err values
def test_ok_err_addition():
    result1 = Ok(5)
    result2 = Err("Error")
    result3 = result1 + result2
    assert result3.is_Err
    assert "a + b with b as Err" in result3.unwrap().msg


# Test for adding Err values
def test_err_addition():
    result1 = Err("Failure")
    result2 = Err("Another Failure")
    result3 = result1 + result2
    assert result3.is_Err
    assert "a + b with a and b as Err" in result3.unwrap().msg


def test_ok_addition_with_zero():
    result = Ok(0) + Ok(5)
    assert result.is_Ok
    assert result.unwrap() == 5


def test_ok_addition_with_negative():
    result = Ok(-5) + Ok(10)
    assert result.is_Ok
    assert result.unwrap() == 5


def test_err_addition_with_large_values():
    result1 = Ok(10**100)
    result2 = Err("Overflow")
    result3 = result1 + result2
    assert result3.is_Err
    assert result3.Err_msg_contains("a + b with b as Err")


def test_ok_addition_with_incompatible_type():
    result1 = Ok(5)
    result2 = Ok("string")
    result3 = result1 + result2
    assert result3.is_Err
    assert result3.Err_msg_contains("TypeError")


# Test for ResultErr initialization
def test_resulterr_initialization():
    err = ResultErr("Error occurred")
    assert err.is_Err
    assert "Error occurred" in err.msg


# Test for appending error messages to ResultErr
def test_resulterr_append():
    err = ResultErr("Initial error")
    err.append("Another error")
    assert err.size == 2
    assert "Initial error" in err.msg
    assert "Another error" in err.msg


# Test for ResultErr raised
def test_resulterr_raises():
    err = ResultErr("This is a raises error")
    with pytest.raises(ResultErr):
        err.raises()


# Test for expect() with Ok result
def test_ok_expect():
    result = Ok("Success")
    value = result.expect()
    assert value == "Success"


# Test for expect() with Err result
def test_err_expect():
    result = Err("Error")
    with pytest.raises(ResultErr):
        result.expect("Something went wrong")


# Test for unwrapping Ok and Err results
def test_ok_unwrap():
    result = Ok(100)
    assert result.unwrap() == 100


def test_err_unwrap():
    result = Err("Failure")
    assert isinstance(result.unwrap(), ResultErr)
    assert result.unwrap() == ResultErr("Failure")


# Test for `map` operation with Ok result
def test_ok_map():
    result = Ok(5)
    mapped_result = result.map(lambda x: x * 2)
    assert mapped_result.is_Ok
    assert mapped_result.unwrap() == 10
    assert mapped_result == Ok(10)


# Test for `map` operation with Err result
def test_err_map():
    result = Err("Failure")
    mapped_result = result.map(lambda x: x * 2)
    assert mapped_result.is_Err
    assert "Failure" in mapped_result.unwrap().msg


# Test for `unwrap_or` with Ok result
def test_ok_unwrap_or():
    result = Ok(100)
    assert result.unwrap_or(0) == 100


# Test for `unwrap_or` with Err result
def test_err_unwrap_or():
    result = Err("Error")
    assert result.unwrap_or(0) == 0


# Test for chained results
def test_chained():
    result = Err("Error")
    a = result.map_or(1, lambda x: -1 * x)
    b = a.apply(lambda x: x / 0)
    c = b.map_or_else(lambda x: 10, lambda x: 20)
    assert a == 1
    assert b == Err("Error")  # all Errs match
    assert c == 10
    assert result.map_or(1, lambda x: -1 * x).apply(lambda x: x / 0).map_or_else(lambda x: 10, lambda x: 20) == 10


# Test for `add_Err_msg` method
def test_to_err():
    result = Ok("Success")
    result.add_Err_msg("Converted to error")
    assert result.is_Err
    assert "Converted to error" in result.unwrap().msg


# Test for `add_Err_msg` method
def test_add_err_msg():
    result = Ok("Success")
    result.add_Err_msg("Add error message")
    assert result.is_Err
    assert "Add error message" in result.unwrap().msg
    assert 1 == result.unwrap().size
    result.add_Err_msg("Add another error message")
    assert 2 == result.unwrap().size


# Test for operator overloading of addition
def test_operator_addition():
    result1 = Ok(5)
    result2 = result1 + 3
    assert result2.is_Ok
    assert result2.unwrap() == 8
    assert result2 == 8


def test_operator_addition_err():
    result1 = 5
    result2 = Err("Error")
    result3 = result1 + result2
    assert result3.is_Err
    assert "b + a with a as Err" in result3.unwrap().msg

    result1 = Err("Error")
    result2 = 5
    result3 = result1 + result2
    assert result3.is_Err
    assert "a + b with a as Err" in result3.unwrap().msg

    result1 = Ok(5)
    result2 = Err("Error")
    result3 = result1 + result2
    assert result3.is_Err
    assert "a + b with b as Err" in result3.unwrap().msg

    result1 = Err("Error")
    result2 = Ok(5)
    result3 = result1 + result2
    assert result3.is_Err
    assert "a + b with a as Err" in result3.unwrap().msg


# Test for equality of Result objects
def test_result_eq():
    result1 = Ok(10)
    result2 = Ok(10)
    assert result1 == result2

    result1 = Err(10)
    result2 = Err(10)
    assert result1 == result2


def test_result_not_eq():
    result1 = Ok(10)
    result2 = Ok(20)
    assert result1 != result2

    result1 = Err(10)
    result2 = Err(20)
    assert not (result1 != result2)  # all Err's are equal


def test_result_err_eq():
    result1 = Err("Error1")
    result2 = Err("Error2")
    assert result1 == result2


def test_ok_initialization_with_none():
    result = Ok(None)
    assert result.is_Ok
    assert result.unwrap() is None


def test_err_initialization_with_none():
    result = Err(None)
    assert result.is_Err
    assert result.unwrap().msg == ["None"]


def test_ok_initialization_with_unusual_types():
    result = Ok({"key": "value"})
    assert result.is_Ok
    assert result.unwrap() == {"key": "value"}
    assert result["key"] == Ok("value")


def test_err_initialization_with_unusual_types():
    dic = {"error": "message"}
    dic_str = str(dic)
    #
    error_result = Err(dic)
    assert error_result.is_Err
    assert error_result.unwrap().msg == [dic_str]
    key = "error"
    err = error_result[key]
    assert err.unwrap().msg == [dic_str, f'Err("{dic_str}")["{key}"] is not subscriptable']


def test_err_initialization_with_large_dict():
    large_dict = {i: i for i in range(10**6)}
    result = Err(large_dict)
    assert result.is_Err
    assert result.unwrap().msg == [str(large_dict)]


def test_operator_overloading():
    result1 = Ok(10)
    result2 = Ok(5)

    # Arithmetic
    result_sum = result1 + result2
    assert result_sum == 15
    assert result_sum == Ok(15)
    assert result_sum.unwrap() == 15
    assert result_sum.expect() == 15

    result_diff = result1 - result2
    assert result_diff == 5
    assert result_diff == Ok(5)
    assert result_diff.unwrap() == 5
    assert result_diff.expect() == 5

    # Comparison
    assert result1 > result2
    assert result1 >= result2
    assert result1 != result2
    assert result1 == Ok(10)
