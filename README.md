# ResultContainer: Rust Result Enums in Python

<p align="left">
  <img src="https://github.com/ScottBoyce-Python/ResultContainer/actions/workflows/ResultContainer-pytest.yml/badge.svg" alt="Build Status" height="20">
</p>



The `ResultContainer` module simplifies complex error handling into clean, readable, and maintainable code structures. Error handling in Python can often become unwieldy, with deeply nested `try/except` blocks and scattered error management. The `ResultContainer` is used for situations when errors are expected and are easily handled. Inspired by [Rust’s Result<Ok, Err>](https://doc.rust-lang.org/std/result/enum.Result.html) enum, `ResultContainer` introduces a clean and Pythonic way to encapsulate success (`Ok`) and failure (`Err`) outcomes.

The `ResultContainer.Result` enum wraps a value in an `Ok` variant, until there is an exception or error raised, and then it is converted to the `Err` variant. The `Err` variant wraps a `ResultContainer.ResultErr` object that contains the error messages and traceback information. The `Result` object includes similar methods to the Rust Result Enum for inquiry about the state, mapping functions, and passing attributes/methods to the containing `value`. 

The `ResultContainer` is designed to streamline error propagation and improve code readability, `ResultContainer` is ideal for developers seeking a robust, maintainable approach to handling errors in data pipelines, API integrations, or asynchronous operations.

## Features

- **Variants for Success and Failure**: Two variants represented in a Result instance, `Ok(value)` for successful outcomes, and `Err(e)` for errors that have resulted. Provides a flexible mechanism for chaining operations on the `Ok` value while propagating errors through `Err`.
- **Attribute and Method Transparency**: Automatically passes attributes, methods, indices, and math operations to the value contained within an `Ok`, otherwise propagates the `Err(e)`.
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
then rename the file `ResultContainer/__init__.py` to  `ResultContainer/ResultContainer.py` and move `ResultContainer.py` to wherever you want to use it.

## `Result` Variants

```python
# Result is the main class and Ok and Err are constructors.
from ResultContainer import Result, Ok, Err
```

- `Ok(value)`
  - `value` is wrapped within an `Ok`.
  - Constructor: `Result.as_Ok(value)`
  - `Result.Ok` attribute returns the wrapped `value`
- `Err(e)`
  - `e` is a `ResultErr` object wrapped within an `Err`. 
  - Constructor: `Result.as_Err(error_msg)`
  - `Result.Err` attribute returns the wrapped `e`.


### Properties of the `Result` Variants

#### `Ok(value)`

- Represents success (non-error state).  
  The `value` is wrapped within the `Ok()`.
- Can be initialized with `Ok(value)`
  - `Ok(value)` &nbsp; ➥&nbsp; syntactic-sugar for &nbsp; ➥&nbsp; `Result.as_Ok(value)`
- Math operations are redirected to `value` and rewrap the solution or concatenate the errors.
  - `Ok(value1) + Ok(value2) `&nbsp; &nbsp; ➣ &nbsp; `Ok(value1 + value2)`
  - `Ok(value1) + Err(e) `&nbsp; &nbsp; ➣ &nbsp; `Err(e + "a + b with b as Err")`
  - `Err(e1) + Err(e2) `&nbsp; &nbsp; &nbsp; &nbsp; ➣ &nbsp; `Err(e1 + "a + b with a and b as Err.")`
- All attributes and methods not associated with `Result` are redirected to `value`.
  - `Ok(value).method()` is equivalent to `Ok(value.method())` and 
    `Ok(value).attrib` is equivalent to `Ok(value.attrib)`.
  - `Ok(value).raises()` does NOT become `Ok(value.raises())`  
    because `Result.raises()` is a native `Result` method.
- Comparisons redirect to comparing the wrapped `value` if `Ok`. But mixed comparisons assume: 
  `Err(e) < Ok(value)` and `Err(e1) == Err(e2)` for any `value`, `e`, `e1`, and `e2`.
  - `Ok(value1) < Ok(value2) `&nbsp; &nbsp; ➣ &nbsp; `value1 < value`
  - `Err(e) < Ok(value2) ` &nbsp; ➣ &nbsp; `True`
  - `Ok(value1) < Err(e) ` &nbsp; ➣ &nbsp; `False`
  - `Err(e1) < Err(e2) ` &nbsp; ➣ &nbsp; `False`
  - `Err(e1) <= Err(e2) ` &nbsp; ➣ &nbsp; `True`

#### `Err(e)`:

- Represents a failure (error-state) and contains `e` as a `ResultErr` object  
  that stores error messages and traceback information.
- Can be initialized with `Err(error_msg)`
  - `Err(e)` &nbsp; ➥&nbsp; syntactic-sugar for &nbsp; ➥&nbsp;  `Result.as_Err(e)`

- If an `Ok(value)` operation fails, then it is converted to an `Err(e)`, where `e` stores the error message.
- Any operation on `Err(e)` results in another error message being appended to `e`.

There are methods built into `Result` to check if an error has been raised, or the unwrap the value/error to get its contents. 

## Result Initialization

```python
# Only the first argument is required for all constructors
from ResultContainer import Result, Ok, Err

# Main object signature:
res = Result(value, success, error_msg, error_code, error_code_group, add_traceback, deepcopy) # Construct either Ok or Er

# Classmethod signatures:
res = Result.as_Ok(value, deepcopy, error_code_group)                                # Construct Ok  variant

res = Result.as_Err(error_msg, error_code, error_code_group, add_traceback)          # Construct Err variant
    
# Syntact Sugar Constructors:
res = Ok(value, deepcopy, error_code_group)                                          # Construct Ok  variant

res = Err(error_msg, error_code, error_code_group, add_traceback)                    # Construct Err variant

# Arguments:
# 
#        value                      (Any): The value to wrap in the Ok(value).
#                                          If value is a Result    object, then returns value;      ignores other args.
#                                          If value is a ResultErr object, then returns Err(value); ignores other args.
#        success         (bool, optional): True if success, False for error. Default is True.
#        error_msg        (Any, optional): If success is False:
#                                             a) and error_msg="", return Err( str(value) )
#                                             b) otherwise,        return Err( str(error_msg) ),
#                                                   if error_msg is listlike, then each item is appended as a separate message.
#                                          Default is "".
#        error_code       (int, optional): Error code associated with the error.
#                                          Default is `1` for `Unspecified`.
#                                          A dict of the currently assigned error codes are returned with `Result.error_code()`
#                                          Note, the code description does not have to match the error_msg.
#        error_code_group (int, optional): Specify the error_codes group to use for code and message flags.
#                                          Default is 1. Error codes are stored as a class variable,
#                                          so this is useful if you need different sets of error codes within a program.
#                                          Most of the time you will never need to use this feature!
#        add_traceback (bool, optional):   If True and constructing Err variant, adds traceback information to Err.
#                                          Default is True.
#        deepcopy (bool, optional):        If True, then deepcopy value before wrapping in Ok. Default is False.
#
```




## Usage

Below are examples showcasing how to create and interact with a `ResultContainer`.

### Creating a Result

```python
from ResultContainer import Result, Ok, Err

# Wrap values in Ok state:
a = Result(5)   # Default is to store as Ok (success=True).

# Explicitly wrap values in Ok state:
a = Result.as_Ok(5)

# Wrap values in Ok state, Ok(value) is equalivent to Result.as_Ok()
a = Ok(5)

# Wrap values as an error -------------------------------------------------------------------------------
a = Result(5, success=False)   # Flag says it is an error, so stored as Err("5")
                               #    Note "5" becomes the error message because error_msg was not provided.
# Explicitly wrap values in Err state:
a = Result.as_Err(5)

# Wrap values in Err state, Err(value) is equalivent to Result.as_Err()
a = Err(5)

```

### Math Operations with a Result

```python
from ResultContainer import Ok
# Addition, Subtraction, Multiplication and Division
a = Ok(5)
b = Ok(50)
c = a + b         # c = Ok(55)
d = c - 20        # d = Ok(35)
e = d * 2         # e = Ok(70)
e /= 10           # e = Ok(7)
f = e / 0         # f = Err("a / b resulted in an Exception. | ZeroDivisionError: division by zero")
g = f + 1         # g = Err("a / b resulted in an Exception. | ZeroDivisionError: division by zero | a + b with a as Err.")

# Interally unwraps the value to use its operation, then rewraps the result.
# This results in the following behaivor:
x = Ok([1, 2, 3])
y = Ok([4, 5, 6, 7])
z = x + y         # z = Ok([1, 2, 3, 4, 5, 6, 7])

```

### Wrapping Objects

```python
from ResultContainer import Result, Ok, Err
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
from ResultContainer import Result, Ok, Err
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
