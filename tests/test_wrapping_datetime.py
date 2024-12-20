import pytest
from ResultContainer import Result, ResultErr, Ok, Err
from datetime import datetime, timedelta


# Test for creating a basic datetime object
def test_wrap_datetime():
    dt0 = datetime(2024, 12, 19, 12, 0, 0)
    dt1 = Result(dt0)
    dt2 = Result.Ok(dt0)
    dt3 = Ok(dt0)
    assert dt0 == dt1.unwrap()
    assert dt0 == dt1
    assert dt1 == dt2
    assert dt2 == dt3


# Test for creating a basic datetime object
def test_wrap_datetime_attributes():
    dt = Ok(datetime(2024, 12, 19, 12, 0, 0))
    assert dt.year == 2024
    assert dt.month == 12
    assert dt.day == 19
    assert dt.hour == 12
    assert dt.minute == 0
    assert dt.second == 0


# Test for creating a basic datetime object
def test_make_datetime_bad():
    dt = Ok(datetime(9999, 12, 31))
    invalid_dt = dt + timedelta(days=10000)
    assert invalid_dt.is_Err
    assert "OverflowError: date value out of range" in invalid_dt.unwrap().msg


# Test for elapsed time between two datetime objects
def test_elapsed_time():
    dt1 = Ok(datetime(2024, 12, 19, 12, 0, 0))
    dt2 = Ok(datetime(2024, 12, 20, 12, 0, 0))

    elapsed = dt2 - dt1  # This will return a Ok(timedelta) object
    assert isinstance(elapsed, Result)
    assert isinstance(elapsed.unwrap(), timedelta)
    assert elapsed.days == 1
    assert elapsed.seconds == 0

    # Checking hours, minutes, seconds directly
    assert elapsed.total_seconds() == 86400  # 24 hours = 86400 seconds


# Test for adding days to a datetime object
def test_add_days():
    dt = Ok(datetime(2024, 12, 19, 12, 0, 0))

    new_dt = dt + timedelta(days=5)  # new_dt is wrapped in an Ok
    assert new_dt.year == 2024
    assert new_dt.month == 12
    assert new_dt.day == 24  # Adding 5 days to 19th results in 24th

    # Test for adding negative days (subtracting days)
    new_dt_sub = dt + timedelta(days=-5)
    assert new_dt_sub.year == 2024
    assert new_dt_sub.month == 12
    assert new_dt_sub.day == 14  # Subtracting 5 days from 19th results in 14th


# Test handling of timezone-aware datetime objects
def test_timezone_aware_datetime():
    from pytz import timezone

    # Create a naive datetime object
    dt_naive = Ok(datetime(2024, 12, 19, 12, 0, 0))

    # Convert to timezone-aware datetime using pytz
    tz = Ok(timezone("UTC"))
    dt_utc = tz.localize(dt_naive.expect())

    assert dt_utc.tzinfo is not None  # Should have timezone info
    assert dt_utc.tzinfo.zone == "UTC"

    # Check the behavior when adding days to timezone-aware datetime
    dt_utc_plus_5 = dt_utc + timedelta(days=5)
    assert dt_utc_plus_5.day == 24  # 5 days added

    # Check if converting back to naive datetime works
    dt_naive_back = dt_utc_plus_5.replace(tzinfo=None)
    assert dt_naive_back.day == 24  # Day should remain the same

    # Test for comparing timezone-aware and naive datetime
    with pytest.raises(AssertionError):
        assert dt_utc == dt_naive_back  # Should raise an error because of timezone difference


# Test if the comparison works correctly for naive datetime
def test_comparison_with_naive_and_aware():
    from pytz import timezone

    tz = Ok(timezone("UTC"))

    dt_aware = tz.localize(datetime(2024, 12, 19, 12, 0, 0))
    dt_naive = Ok(datetime(2024, 12, 19, 12, 0, 0))

    with pytest.raises(AssertionError):
        assert dt_aware == dt_naive  # Naive and aware datetime comparison should raise TypeError


# Test if adding days results in the correct time
def test_add_days_time():
    dt = datetime(2024, 12, 19, 23, 59, 59)

    new_dt = Ok(dt) + timedelta(days=1)
    assert new_dt.year == 2024
    assert new_dt.month == 12
    assert new_dt.day == 20
    assert new_dt.hour == 23
    assert new_dt.minute == 59
    assert new_dt.second == 59
    assert new_dt.microsecond == 0  # Time should remain the same after adding 1 day


# Test for handling elapsed time in weeks
def test_elapsed_time_weeks():
    dt1 = Ok(datetime(2024, 12, 19, 12, 0, 0))
    dt2 = Ok(datetime(2025, 1, 19, 12, 0, 0))

    elapsed = dt2 - dt1
    assert elapsed.days == 31  # Difference of 31 days
    assert elapsed.days // 7 == 4  # Should be 4 weeks
    assert elapsed.days % 7 == 3  # 3 extra days
