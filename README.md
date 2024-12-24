# ResultContainer: Rust Result Enums in Python

<p align="left">
  <img src="https://github.com/ScottBoyce-Python/ResultContainer/actions/workflows/python-pytest.yml/badge.svg" alt="Build Status" height="20">
</p>


ResultContainer is a python module that contains the `Result` class that mimics the Result Result Enum. The Result Enum is used for situations when errors are expected and are easily handled, or you do not want to have lots of try/except clauses. The Result enum wraps a value in an `Ok` variant, until there is an exception or error raised, and then it is converted to the `Err` variant. 

The two Result states are:

- `Result.Ok(value)`
  - `value` is wrapped within an `Ok`.
- `Result.Err(e)`
  - `e` is an error message wrapped within an `Err`. 


#### Properties of the `Result` Variants

##### `Result.Ok(value)`

- Represents success (non-error state). The `value` is wrapped within the `Ok()`.
- Can be initialized with `Ok(value)`
  - `Ok(value)` &nbsp; ➥&nbsp; syntactic-sugar for &nbsp; ➥&nbsp; `Result.Ok(value)`
- Math operations are redirected to `value` and rewrap the solution or concatenate the errors.
  - `Ok(value1) + Ok(value2) `&nbsp; &nbsp; ➣ &nbsp; `Ok(value1 + value2)`
  - `Ok(value1) + Err(e) `&nbsp; &nbsp; ➣ &nbsp; `Err(e + "a + b with b as Err")`
  - `Err(e1) + Err(e2) `&nbsp; &nbsp; &nbsp; &nbsp; ➣ &nbsp; `Err(e1 + "a + b with a and b as Err.")`
- All attributes and methods not associated with `Result` are redirected to `value`.
  - `Ok(value).method()` is equivalent to `Ok(value.method())` and 
    `Ok(value).attrib` is equivalent to `Ok(value.attrib)`.
  - `Ok(value).raises()` does NOT become `Ok(value.raises())` because `Result.raises()` exists.
- Comparisons redirect to comparing the wrapped `value` if `Ok`. But mixed comparisons assume: 
  `Err(e) < Ok(value)` and `Err(e1) == Err(e2)` for any `value`, `e`, `e1`, and `e2`.
  - `Ok(value1) < Ok(value2) `&nbsp; &nbsp; ➣ &nbsp; `value1 < value`
  - `Err(e) < Ok(value2) ` &nbsp; ➣ &nbsp; `True`
  - `Ok(value1) < Err(e) ` &nbsp; ➣ &nbsp; `False`
  - `Err(e1) < Err(e2) ` &nbsp; ➣ &nbsp; `False`
  - `Err(e1) <= Err(e2) ` &nbsp; ➣ &nbsp; `True`

##### `Result.Err(e)`:

- Represents a failure (error-state) and contains one more more error messages.
- Can be initialized with `Err(error_msg)`
  - `Err(e)` &nbsp; ➥&nbsp; syntactic-sugar for &nbsp; ➥&nbsp;  `Result.Err(e)`

- If an `Ok(value)` operation fails, then it is converted to an `Err(e)`, where `e` stores the error message.
  - `e` contains an error message, error code, and traceback information where the error occured.
- Any operation on `Err(e)` results in another error message being appended to `e`.

There are methods built into `Result` to check if an error has been raised, or the unwrap the value/error to get its contents. 

## Features

- **Variants for Success and Failure**: Two variants, `Ok(value)` for successful outcomes, and `Err(e)` for errors that have resulted. Provides a flexible mechanism for chaining operations on the `Ok` value while propagating errors through `Err`.
- **Attribute and Method Transparency**: Automatically passes attributes, methods, and math operations to the value contained within an `Ok`, otherwise propagates the `Err(e)`.
- **Utility Methods**: Implements helper methods for error propagation, transformation, and querying (e.g., `.map()`, `.apply()`, `.unwrap_or()`, `.expect()`, `.raises()`) for concise and readable handling of success and error cases. 

## Installation
To install the module

```bash
pip install --upgrade git+https://github.com/ScottBoyce-Python/ResultContainer.git
```

or you can clone the respository with
```bash
git clone https://github.com/ScottBoyce-Python/ResultContainer.git
```
and then move the file `ResultContainer/ResultContainer.py` to wherever you want to use it.


## Usage

Below are examples showcasing how to create and interact with a `ResultContainer`.

### Creating a Result

```python
from ResultContainer import Result, Ok, Err

# Wrap values in Ok state:
a = Result(5)   # Default is to store as Ok.

# Explicitly wrap values in Ok state:
a = Result.Ok(5)

# Wrap values in Ok state, Ok(value) is equalivent to Result.Ok()
a = Ok(5)

# Wrap values as an error 
a = Result(5, False)   # Flag says it is an error, so stored as Err("5")
                       #    Note "5" is the error message and NOT the value.
# Explicitly wrap values in Err state:
a = Result.Err(5)

# Wrap values in Err state, Err(value) is equalivent to Result.Err()
a = Err(5)

```

### Math Operations with a Result

```python
# Addition, Subtraction, Multiplication and Division
a = Result.Ok(5)
b = Result.Ok(50)
c = a + b         # c = Ok(55)
d = c - 20        # d = Ok(35)
e = d * 2         # e = Ok(70)
e /= 10           # e = Ok(7)
f = e / 0         # f = Err("a / b resulted in an Exception. | ZeroDivisionError: division by zero")
g = f + 1         # g = Err("a / b resulted in an Exception. | ZeroDivisionError: division by zero | a + b with a as Err.")

```

### Wrapping Objects

```python
from datetime import datetime, timedelta

# Wrap a datetime.datetime object
dt = Ok(datetime(2024, 12, 19, 12, 0, 0))  # dt = Ok(2024-12-19 12:00:00)

# Grab the attributes
y1 = dt.year                               # y1 = Ok(2024)
y2 = dt.year.expect()                      # y2 = 2024  -> raises a ResultErr exception if not Ok.

# Use the methods
new_dt = dt + timedelta(days=5)            # new_dt = Ok(2024-12-24 12:00:00)
new_dt_sub = dt + timedelta(days=-5)       # new_dt = Ok(2024-12-14 12:00:00)

# Produce an invalid state
dt_large = Ok(datetime(9999, 12, 31))      # dt_large = Ok(9999-12-31 00:00:00)
bad_dt = dt + timedelta(days=10000)        # bad_dt = Err("a + b resulted in an Exception. | OverflowError: date value out of range")

bad_dt.raises()                            # raises a ResultErr exception
```

### Raising Errors

```python
from ResultContainer import Result, Ok, Err

# raises() is a powerful check when chaining methods. 
# It raises an exception if Err, otherwise returns the original Ok(value) 
x = Result(10)   # x = Ok(10)
y = x.raises()   # y = Ok(10)
x /= 0           # x = Err("a /= b resulted in an Exception. | ZeroDivisionError: division by zero")

y = x.raises()  # Raises the following exception:

# Traceback (most recent call last):
#   File "example.py", line 7, in <module>
#     x.raises()  
#     ^^^^^^^^^^
#   File "ResultContainer/ResultContainer.py", line 957, in raises
#     raise self._Err
# ResultErr: 
#   [1] a /= b resulted in an Exception.
#  [12] ZeroDivisionError: division by zero
```

  


```python
1 | from ResultContainer import Result, Ok, Err
2 | from datetime import datetime, timedelta
3 | 
4 | dt = Result(datetime(9999, 12, 31))
5 | 
6 | bad_dt = dt + timedelta(days=10000)
7 | 
8 | bad_dt.raises()  
# Raises the following exception.
#    Note the exception says it occured on `line 6` despite being called on `line 8`

# Traceback (most recent call last):
#   File "example.py", line 8, in <module>
#     bad_dt.raises()
#   File "ResultContainer/ResultContainer.py", line 957, in raises
#     raise self._Err
# ResultErr: 
#   File "ResultContainer/example.py", line 6, in <module>
#     bad_dt = dt + timedelta(days=10000)
#
#   [1] a + b resulted in an Exception.
#  [12] OverflowError: date value out of range
```

### Passing Functions and Chaining Operations

```python
from math import sqrt
# to use an external function, like sqrt
# It must be passed to either apply or map or extracted with expect.
# apply converts Ok to Err if the func fails, while map raises an exception.
a = Ok(9)            # Ok(9)
b = a.apply(sqrt)    # Ok(3.0)
c = Ok(-9)           # Ok(-9)
d = c.apply(sqrt)    # Err("Result.apply exception. | ValueError: math domain error")
e = sqrt(c.expect()) # raises an error

plus1 = lambda x: x + 1
a = Ok(5)
b = Ok(0)
c = (a / b).map_or(10, plus1).map_or(20, plus1).map_or(30, plus1) # c = Err() -> Ok(10) -> Ok(11) -> Ok(12)
d = (a / 0).map_or(10, plus1).map_or(20, plus1).map_or(30, plus1) # d = Err() -> Ok(10) -> Ok(11) -> Ok(12)

```



## Testing

This project uses `pytest` and `pytest-xdist` for testing. Tests are located in the `tests` folder. To run tests, install the required packages and execute the following command:

```bash
pip install pytest pytest-xdist

pytest  # run all tests, note options are set in the pyproject.toml file
```

&nbsp; 

Note, that the [pyproject.toml](pyproject.toml) contains the flags used for pytest.



## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## Author
Scott E. Boyce
