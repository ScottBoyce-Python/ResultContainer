import pytest
from ResultContainer import Result, Ok, Err, ResultErr
from copy import deepcopy


# Basic Initialization Tests
def test_list_result_ok_initialization():
    result = Result.as_Ok([0, 1, 2, 3, 4])
    assert result.is_Ok is True
    assert result.is_Err is False
    assert result.unwrap() == [0, 1, 2, 3, 4]
    assert result.expect() == [0, 1, 2, 3, 4]
    assert result.raises() == Ok([0, 1, 2, 3, 4])

    with pytest.raises(ResultErr):
        result.expect_Err()


# Edge Case Initialization
def test_list_result_ok_with_empty():
    result = Result.as_Ok([])
    assert result.is_Ok is True
    assert result.unwrap() == []
    assert result.expect() == []
    assert result.raises() == Ok([])


def test_list_result_err_with_empty_string():
    result = Result.as_Err([""])  # Note this treats it as a list of error messages, so result is Err("")

    assert result.is_Err is True

    with pytest.raises(ResultErr):
        result.expect()

    with pytest.raises(ResultErr):
        result.raises()


# Iter Tests
def test_list_iter_err():
    result = Err([1, 2, 3])  # Note this treats it as a list of error messages, so result is Err("1 | 2 | 3")
    enter_loop = False
    for i in result:
        enter_loop = True  # should never be true
    assert not enter_loop


def test_list_iter_values():
    result = Ok([0, 1, 2, 3, 4])
    enter_loop = False
    i = 0
    for j in result:
        assert i == j
        i += 1
        enter_loop = True
    assert enter_loop


def test_list_iter_list_of_list():
    lst = [[0, 1], [2, 3, 4], [5, 6, 7, 8]]
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

    lst[-1][-1] = 99  # Because mutable, Ok(lst) changes too!!!
    enter_loop = False
    for i, j in enumerate(result):
        assert j == lst[i]
        enter_loop = True
    assert enter_loop


def test_list_iter_list_of_list_deepcopy():
    lst = [[0, 1], [2, 3, 4], [5, 6, 7, 8]]
    lst2 = deepcopy(lst)
    result = Result.as_Ok(lst, deepcopy=True)
    lst[-1][-1] = 99  # Change in lst does not effect Ok(deepcopy(lst))
    enter_loop = False
    for i, j in enumerate(result):
        assert j == lst2[i]
        enter_loop = True
    assert enter_loop

    assert lst != result


def test_list_result_iter():
    lst = [-2, -1, 0, 1, 2, 3]
    i = 0
    enter_loop = False
    for j in Ok(lst).iter_wrap():
        assert j.is_Ok
        assert j == lst[i]
        i += 1
        enter_loop = True
    assert enter_loop

    i = 0
    enter_loop = False
    for j in Ok(lst).iter_unwrap():
        assert j == lst[i]
        i += 1
        enter_loop = True
    assert enter_loop


def test_list_result_iter_empty():
    lst = []
    enter_loop = False
    for j in Ok(lst).iter_wrap():
        enter_loop = True
    assert not enter_loop

    enter_loop = False
    for j in Ok(lst).iter_unwrap():
        enter_loop = True
    assert not enter_loop


def test_list_result_apply_map():
    lst = [-2, -1, 0, 1, 2, 3]
    result = Ok(lst).apply_map(lambda x: 2 * x)
    assert result == Ok([-4, -2, 0, 2, 4, 6])

    result = Ok(lst).apply_map(lambda x: 2 * x, unwrap=True)
    assert result == [-4, -2, 0, 2, 4, 6]


# Method Tests
def test_list_is_ok_and():
    result = Result.as_Ok([0, 1, 2, 3, 4])
    assert result.is_Ok_and(lambda x: x[-1] == 4)
    assert result.is_Ok_and(lambda x: all(i < 10 for i in x))
    assert result.is_Ok_and(lambda x: len(x) < 10)


def test_list_result_apply():
    result = Result.as_Ok([0, 1, 2, 3, 4])
    mapped_result = result.apply(lambda x: [i * 2 for i in x])
    assert mapped_result.is_Ok is True
    assert mapped_result.unwrap() == [0, 2, 4, 6, 8]

    error_result = result.apply(lambda x: [i / 0 for i in x])  # div/0 error
    assert error_result.is_Err is True

    # error_result = Err("Result.apply exception. | ZeroDivisionError: division by zero")
    with pytest.raises(ResultErr):
        error_result.expect()

    with pytest.raises(ResultErr):
        error_result.raises()

    error_result = result.apply(lambda x: [x[i] for i in range(100)])  # index error
    assert error_result.is_Err is True

    # error_result = Err("Result.apply exception. | IndexError: list index out of range")
    with pytest.raises(ResultErr):
        error_result.expect()

    with pytest.raises(ResultErr):
        error_result.raises()

    mapped_result = Ok([-2, -1, 0, 1, 2, 3]).apply(lambda x: 10 / x)  # apply returns Err for bad function
    with pytest.raises(ResultErr):
        mapped_result.raises()


def test_list_result_map():
    result = Result.as_Ok([0, 1, 2, 3, 4])
    mapped_result = result.map(lambda x: [i * 2 for i in x])
    assert mapped_result.is_Ok is True
    assert mapped_result.unwrap() == [0, 2, 4, 6, 8]

    with pytest.raises(ZeroDivisionError):
        _ = result.map(lambda x: [i / 0 for i in x])  # div/0 error

    with pytest.raises(IndexError):
        _ = result.map(lambda x: [x[i] for i in range(100)])  # index error


def test_list_result_map_or():
    result = Result.as_Ok([0, 1, 2, 3, 4])
    with pytest.raises(TypeError):
        _ = result.map_or(100, lambda x: 10 / x)  # map fails on bad function call


def test_list_result_apply_or():
    result = Result.as_Ok([0, 1, 2, 3, 4])
    mapped_result = result.apply_or(100, lambda x: 10 / x)
    assert mapped_result.expect() == 100


def test_list_result_apply_chain():
    result = Result.as_Ok([0, 1, 2, 3, 4])
    new_result = (
        result.apply(lambda x: [i * 2 for i in x])  # Ok([0,  2,  4,  6,  8])
        .apply(lambda x: [i * 2 for i in x])  # Ok([0,  4,  8, 12, 16])
        .apply(lambda x: [i * 2 for i in x])  # Ok([0,  8, 16, 24, 32])
        .apply(lambda x: [i * 2 for i in x])  # Ok([0, 16, 32, 48, 64])
    )
    assert new_result.is_Ok is True
    assert new_result.expect() == [0, 16, 32, 48, 64]

    error_result = (
        result.apply(lambda x: Ok(x * 2))  # Ok([0,  2,  4,  6,  8])
        .apply(lambda x: Ok(1 / x))  # Converted to Err
        .apply(lambda x: Ok(x * 2))  # Appends to Err
    )
    assert error_result.is_Err is True
    with pytest.raises(ResultErr):
        error_result.expect()

    with pytest.raises(ResultErr):
        new_result = (
            result.apply(lambda x: Ok(x * 2))
            .apply(lambda x: Ok(x * 2))
            .apply(lambda x: Ok(x * 0))
            .apply(lambda x: Ok(10 / x))  # Converted to Err
            .apply(lambda x: Ok(x + 13))  # Appends to Err
            .raises()  # Raises Exception if in Err state
        )


def test_list_method_append():
    lst1 = [2, 5, 4, 3, 1, 9, 2, 8, 7, 2, 6]

    result = Ok(lst1, deepcopy=False)
    result.append(99)
    result.append(98)

    assert result == lst1  # both are mutated!

    lst2 = [2, 5, 4, 3, 1, 9, 2, 8, 7, 2, 6]

    result = Ok(lst2, deepcopy=True)
    result.append(99)
    result.append(98)

    assert result == lst2 + [99] + [98]


def test_list_method_extend():
    lst1 = [2, 5, 4, 3, 1, 9, 2, 8, 7, 2, 6]

    result = Ok(lst1, deepcopy=False)
    result.extend([99, 98])

    assert result == lst1  # both are mutated!

    lst2 = [2, 5, 4, 3, 1, 9, 2, 8, 7, 2, 6]

    result = Ok(lst2, deepcopy=True)
    result.extend([99, 98])
    assert result == lst2 + [99, 98]


def test_list_method_insert():
    lst1 = [2, 5, 4, 3, 1, 9, 2, 8, 7, 2, 6]

    result = Ok(lst1, deepcopy=False)
    result.insert(2, 99)

    assert result == lst1  # both are mutated!

    lst2 = [2, 5, 4, 3, 1, 9, 2, 8, 7, 2, 6]

    result = Ok(lst2, deepcopy=True)
    result.insert(2, 99)
    assert result == lst1
    assert result != lst2


def test_list_method_remove():
    lst1 = [2, 5, 4, 3, 1, 9, 2, 8, 7, 2, 6]

    result = Ok(lst1, deepcopy=False)
    result.remove(3)

    assert result == lst1  # both are mutated!

    lst2 = [2, 5, 4, 3, 1, 9, 2, 8, 7, 2, 6]

    result = Ok(lst2, deepcopy=True)
    result.remove(3)
    assert result == lst1
    assert result != lst2

    lst3 = [2, 5, 4, 3, 1, 9, 2, 8, 7, 2, 6]

    result = Ok(lst3, deepcopy=True)
    result.remove(99)  # converted to Err
    assert result.is_Err
    with pytest.raises(ResultErr):
        result.raises()


def test_list_method_pop():
    lst1 = [2, 5, 4, 3, 1, 9, 2, 8, 7, 2, 6]

    result = Ok(lst1, deepcopy=False)
    assert result.pop() == Ok(6)

    assert result == lst1  # both are mutated!

    lst2 = [2, 5, 4, 3, 1, 9, 2, 8, 7, 2, 6]

    result = Ok(lst2, deepcopy=True)
    assert result.pop() == Ok(6)
    assert result == lst1
    assert result != lst2

    lst3 = [2, 5, 4]

    result = Ok(lst3, deepcopy=True)

    assert result.pop(1) == Ok(5)
    assert result.pop(0) == Ok(2)
    assert result.pop() == Ok(4)
    error_result = result.pop()

    assert error_result.is_Err
    assert result.is_Err
    assert error_result is result  # error result returns self

    with pytest.raises(ResultErr):
        result.raises()


def test_list_method_clear():
    lst1 = [2, 5, 4, 3, 1, 9, 2, 8, 7, 2, 6]

    result = Ok(lst1, deepcopy=False)
    result.clear()

    assert result == lst1  # both are mutated!

    lst2 = [2, 5, 4, 3, 1, 9, 2, 8, 7, 2, 6]

    result = Ok(lst2, deepcopy=True)
    result.clear()
    assert len(result) == 0  # len() strictly enforces only returning int or raise exception
    assert result == lst1
    assert result != lst2


def test_list_method_index():
    result = Ok([2, 5, 4, 3])
    assert result.index(3) == 3
    assert result.index(4) == 2
    error_result = result.index(99)
    assert error_result.is_Err


def test_list_method_count():
    result = Ok([2, 5, 2, 8, 2])
    assert result.count(2) == 3
    assert result.count(99) == 0


def test_list_method_sort():
    ans = [1, 2, 2, 2, 3, 4, 5, 6, 7, 8, 9]
    lst1 = [2, 5, 4, 3, 1, 9, 2, 8, 7, 2, 6]

    result = Ok(lst1, deepcopy=False)
    result.sort()

    assert result == ans
    assert result == lst1  # both are mutated!

    lst2 = [2, 5, 4, 3, 1, 9, 2, 8, 7, 2, 6]

    result = Ok(lst2, deepcopy=True)
    result.sort()
    assert result == ans
    assert result == lst1
    assert result != lst2


def test_list_method_reverse():
    lst1 = [2, 5, 4, 3, 1, 9, 2, 8, 7, 2, 6]

    result = Ok(lst1, deepcopy=False)
    result.reverse()

    assert result == lst1  # both are mutated!

    lst2 = [2, 5, 4, 3, 1, 9, 2, 8, 7, 2, 6]

    result = Ok(lst2, deepcopy=True)
    result.reverse()
    assert result == lst1
    assert result != lst2


# Arithmetic Operator Overloading
def test_list_addition():
    result1 = Ok([0, 1, 2])
    result2 = Ok([3, 4, 5, 6])

    combined_result = result1 + result2
    assert combined_result.unwrap() == [0, 1, 2, 3, 4, 5, 6]

    combined_result = result2 + result1
    assert combined_result.unwrap() == [3, 4, 5, 6, 0, 1, 2]

    combined_result = result1 + [7, 8, 9]
    assert combined_result.unwrap() == [0, 1, 2, 7, 8, 9]

    combined_result = [7, 8, 9] + result1
    assert combined_result.unwrap() == [7, 8, 9, 0, 1, 2]


def test_list_multiplication():
    result1 = Ok([1])
    combined_result = result1 * 2
    assert combined_result.unwrap() == [1, 1]

    result1 = Ok([1])
    combined_result = 3 * result1
    assert combined_result.unwrap() == [1, 1, 1]

    result1 = Ok([1])
    combined_result = 3 * result1 * 2
    assert combined_result.unwrap() == [1, 1, 1, 1, 1, 1]

    result1 = Ok([1])
    result2 = Ok(5)
    combined_result = result1 * result2
    assert combined_result.unwrap() == [1, 1, 1, 1, 1]
