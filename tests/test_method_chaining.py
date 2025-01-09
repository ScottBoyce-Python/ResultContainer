import pytest
from ResultContainer import Result, Ok, Err, ResultErr


def test_error_chaining_integrity():
    error_result = Err("Initial Error")
    chained_result = error_result.map(lambda x: x * 2).map_Err(lambda e: f"{e.str()} - chained")
    assert chained_result.is_Err is False  # map_Err returns Ok(f(e))


def test_result_repeated_ok_chain():
    new_result = (
        Ok(10)
        .apply(lambda x: Ok(x * 2))  # Ok(20)
        .apply(lambda x: Ok(x * 2))  # Ok(40)
        .apply(lambda x: Ok(x * 2))  # Ok(80)
        .apply(lambda x: Ok(x * 2))  # Ok(160)
    )
    assert new_result.is_Ok is True
    assert new_result.expect() == 160

    result = Ok(10)
    new_result = result.apply(lambda x: Result.as_Ok(x * 2)).apply(lambda x: Result.as_Ok(x * 2))

    assert new_result.is_Err is False
    assert new_result.is_Ok is True
    assert new_result == 40


def test_result_repeated_err_chain():
    error_result = (
        Err("Error")
        .apply(lambda x: Ok(x * 2))  # Appends to error
        .apply(lambda x: Ok(x * 2))  # Appends to error
        .apply(lambda x: Ok(x * 2))  # Appends to error
    )
    assert error_result.is_Err is True

    with pytest.raises(ResultErr):
        error_result.expect()

    with pytest.raises(ResultErr):
        error_result.raises()


def test_result_repeated_ok_err_chain():
    result = Ok(10)

    new_result = result.apply(lambda x: Result.as_Ok(x * 2)).apply(lambda x: Result.as_Ok(x * 2))

    assert new_result.is_Err is False

    new_result = new_result.apply(lambda x: Result.as_Ok(x * 0)).apply(lambda x: Result.as_Ok(10 / x))

    assert new_result.is_Err is True

    with pytest.raises(ResultErr):
        new_result = (
            Ok(10)
            .apply(lambda x: Ok(x * 2))  #  Ok(20)
            .apply(lambda x: Ok(x * 2))  #  Ok(40)
            .apply(lambda x: Ok(x * 0))  #  Ok(40)
            .apply(lambda x: Ok(10 / x))  # Raises ZeroDiv Error
            .apply(lambda x: Ok(x + 1))  #  Appends to error message
            .expect()  #                    Raises Exception if in Err state
        )

    with pytest.raises(ResultErr):
        new_result = (
            Ok(10)
            .apply(lambda x: Ok(x * 2))  #  Ok(20)
            .apply(lambda x: Ok(x * 2))  #  Ok(40)
            .apply(lambda x: Ok(x * 0))  #  Ok(40)
            .apply(lambda x: Ok(10 / x))  # Raises ZeroDiv Error
            .apply(lambda x: Ok(x + 1))  #  Appends to error message
            .raises()  #                    Raises Exception if in Err state
        )


def test_result_method_map_chain():
    from math import sqrt

    def plus11(x):
        return x + 11

    def pow2(x):
        return x**2

    def neg(x):
        return -x

    a = Ok(5)
    b = None

    with pytest.raises(ValueError):
        b = a.map(pow2).map(plus11).map(sqrt).map(neg).map(sqrt)
        # 5 -> 25 -> 36 -> 6 -> -6 -> raise ValueError

    with pytest.raises(ValueError):
        b = a.map(pow2).map(plus11).map(sqrt).map(neg).map_or(None, sqrt)
        # 5 -> 25 -> 36 -> 6 -> -6 -> raise ValueError

    assert b is None


def test_result_method_map_chain_lambda():
    from math import sqrt
    # plus11 = lambda x: x + 11
    # pow2   = lambda x: x**2
    # neg    = lambda x: -x

    a = Ok(5)
    b = None

    with pytest.raises(ValueError):
        b = (
            a.map(lambda x: x**2)  # Ok(5) -> Ok(25)
            .map(lambda x: x + 11)  #      -> Ok(36)
            .map(sqrt)  #                  -> Ok(6)
            .map(lambda x: -x)  #          -> Ok(-6)
            .map(sqrt)  #                  -> raise ValueError
        )

    with pytest.raises(ValueError):
        b = (
            a.map(lambda x: x**2)  # Ok(5) -> Ok(25)
            .map(lambda x: x + 11)  #      -> Ok(36)
            .map(sqrt)  #                  -> Ok(6)
            .map(lambda x: -x)  #          -> Ok(-6)
            .map_or(None, sqrt)  #         -> raise ValueError
        )

    assert b is None


def test_result_method_apply_chain():
    from math import sqrt

    def div(numerator, denominator):
        return numerator / denominator

    def plus11(x, *args):
        # *args not used, but needed because apply_or_else(efunc, ofunc) requires
        # both functions to have the same arg length, see `apply_or_else(plus11, div, 0)` or `.apply_or_else(plus11, div, 2)`
        return x + 11

    def pow2(x):
        return x**2

    def neg(x, *args):
        # *args not used, but needed because apply_or_else(efunc, ofunc) requires
        # both functions to have the same arg length, see `.apply_or_else(neg, div, 0)`
        return -x

    a = Ok(5)

    b = (
        a.apply(pow2)  # Ok(5) -> Ok(25)
        .apply(plus11)  #       -> Ok(36)
        .apply(sqrt)  #         -> Ok(6)
        .apply(neg)  #          -> Ok(-6)
        .apply(sqrt)  #         -> Err("Result.apply exception | ValueError: math domain error")
    )

    c = (
        a.apply(pow2)  #   Ok(5) -> Ok(25)
        .apply(plus11)  #        -> Ok(36)
        .apply(sqrt)  #          -> Ok(6)
        .apply(neg)  #           -> Ok(-6)
        .apply_or(None, sqrt)  # -> Ok(None)
    )

    d = (
        a.apply(pow2)  #          Ok(5) -> Ok(25)
        .apply(plus11)  #               -> Ok(36)
        .apply(sqrt)  #                 -> Ok(6)
        .apply(neg)  #                  -> Ok(3)
        .apply_or_else(plus11, sqrt)  # -> Ok(5)
    )

    e = (
        a.apply(pow2)  # Ok(5) -> Ok(25)
        .apply(plus11)  #      -> Ok(36)
        .apply(sqrt)  #        -> Ok(6)
        .apply(div, 2)  #      -> Ok(3)
        .apply(div, 0)  #      -> Err("Result.apply exception | ZeroDivisionError: float division by zero")
    )
    # 5 -> 25 -> 36 -> 6 -> 3 -> Err("Result.apply exception | ZeroDivisionError: float division by zero")

    f = (
        a.apply(pow2)  #            Ok(5) -> Ok(25)
        .apply(plus11)  #                 -> Ok(36)
        .apply(sqrt)  #                   -> Ok(6)
        .apply(div, 2)  #                 -> Ok(3)
        .apply_or_else(plus11, div, 0)  # -> Ok(14)
    )

    g = (
        a.apply(pow2)  #            Ok(5) -> Ok(25)
        .apply(plus11)  #                 -> Ok(36)
        .apply(sqrt)  #                   -> Ok(6)
        .apply_or_else(neg, div, 0)  #    -> Ok(-6)
        .apply_or_else(plus11, div, 2)  # -> Ok(-3)
    )

    assert a.is_Ok and a == Ok(5)
    assert b.is_Err and b.Err_msg_contains("ValueError")
    assert c.is_Ok and c == Ok(None)
    assert d.is_Ok and d == Ok(5)
    assert e.is_Err and e.Err_msg_contains("ZeroDivisionError")
    assert f.is_Ok and f == Ok(14)
    assert g.is_Ok and g == Ok(-3)


def test_result_method_apply_chain_lambda():
    from math import sqrt
    # div    = lambda x, y: x / y
    # plus11 = lambda x: x + 11
    # pow2   = lambda x: x**2
    # neg    = lambda x: -x

    a = Ok(5)

    b = (
        a.apply(lambda x: x**2)  # Ok(5) -> Ok(25)
        .apply(lambda x: x + 11)  #      -> Ok(36)
        .apply(sqrt)  #                  -> Ok(6)
        .apply(lambda x: -x)  #          -> Ok(-6)
        .apply(sqrt)  #                  -> Err("Result.apply exception | ValueError: math domain error")
    )

    c = (
        a.apply(lambda x: x**2)  # Ok(5) -> Ok(25)
        .apply(lambda x: x + 11)  #      -> Ok(36)
        .apply(sqrt)  #                  -> Ok(6)
        .apply(lambda x: -x)  #          -> Ok(-6)
        .apply_or(None, sqrt)  #         -> Ok(None)
    )

    d = (
        a.apply(lambda x: x**2)  #          Ok(5) -> Ok(25)
        .apply(lambda x: x + 11)  #               -> Ok(36)
        .apply(sqrt)  #                           -> Ok(6)
        .apply(lambda x: -x)  #                   -> Ok(-6)
        .apply_or_else(lambda x: x + 11, sqrt)  # -> Ok(5)
    )

    e = (
        a.apply(lambda x: x**2)  # Ok(5) -> Ok(25)
        .apply(lambda x: x + 11)  #      -> Ok(36)
        .apply(sqrt)  #                  -> Ok(6)
        .apply(lambda x, y: x / y, 2)  # -> Ok(3)
        .apply(lambda x, y: x / y, 0)  # -> Err("Result.apply exception | ZeroDivisionError: float division by zero")
    )

    f = (
        a.apply(lambda x: x**2)  #                              Ok(5) -> Ok(25)
        .apply(lambda x: x + 11)  #                                   -> Ok(36)
        .apply(sqrt)  #                                               -> Ok(6)
        .apply(lambda x, y: x / y, 2)  #                              -> Ok(3)
        .apply_or_else(lambda x, y: x + 11, lambda x, y: x / y, 0)  # -> Ok(14)
    )

    g = (
        a.apply(lambda x: x**2)  #                              Ok(5) -> Ok(25)
        .apply(lambda x: x + 11)  #                                   -> Ok(36)
        .apply(sqrt)  #                                               -> Ok(6)
        .apply_or_else(lambda x, y: -x, lambda x, y: x / y, 0)  #     -> Ok(-6)
        .apply_or_else(lambda x, y: x + 11, lambda x, y: x / y, 2)  # -> Ok(-3)
    )

    assert a.is_Ok and a == Ok(5)
    assert b.is_Err and b.Err_msg_contains("ValueError")
    assert c.is_Ok and c == Ok(None)
    assert d.is_Ok and d == Ok(5)
    assert e.is_Err and e.Err_msg_contains("ZeroDivisionError")
    assert f.is_Ok and f == Ok(14)
    assert g.is_Ok and g == Ok(-3)
