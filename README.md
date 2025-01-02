# ResultContainer: Rust Result Enums in Python

<p align="left">
  <img src="https://github.com/ScottBoyce-Python/ResultContainer/actions/workflows/ResultContainer-pytest.yml/badge.svg" alt="Build Status" height="20">
</p>

## About

ResultContainer is a Python library inspired by [Rust’s Result](https://doc.rust-lang.org/std/result/enum.Result.html) enum, designed for robust error handling. It seamlessly supports mathematical operations, attribute access, and method chaining on `Ok(value)`, while automatically transitioning to `Err(e)` upon encountering errors, ensuring continuous error tracking and logging. Ideal for developers seeking structured and functional error management in Python.

## Description

The `ResultContainer` module simplifies complex error handling into clean, readable, and maintainable code structures. Error handling in Python can often become unwieldy, with deeply nested `try/except` blocks and scattered error management. The `ResultContainer` is used for situations when errors are expected and are easily handled. Inspired by Rust's Result<Ok, Err> enum, `ResultContainer` introduces a clean and Pythonic way to encapsulate a `Result` as a success (`Ok`) and failure (`Err`) outcomes.

The `ResultContainer` module contains two classes, `ResultErr` and `Result`. The `ResultContainer.ResultErr` class extends the Exception class to collect and store error messages and traceback information. The `ResultContainer.Result` is the enum with two variants:  `ResultContainer.Result.Ok(value)` and  `ResultContainer.Result.Err(e)`. The `Ok(value)` variant wraps any `value` as long as no exceptions occur. The  `Ok` variant cannot directly wrap another Result or ResultErr objects. However,  `Ok` can wrap another object, such as a list, that contains Result and ResultErr objects.  Methods and attributes that are not part of the Result class are automatically passed to the wrapped `value`.  For example, `Ok(value).method()` becomes `Ok(value.method())`. If an `Ok` variant operation results in raising an exception, the exception and traceback info is stored in a `ResultErr` object (`e`) and the `Ok` is converted to the `Err(e)` variant. Subsequent errors are appended to `e`. `Result` contains status inquiry methods, unwrap methods to get the stored `value` or `e`, and the ability to raise a `ResultErr` exception for the `Err(e)` variant.

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

  

## Variants

```python
# Result is the main class and Ok and Err are constructors.
from ResultContainer import Result, Ok, Err, ResultErr
```

- `Ok(value)`
  - `value` is any object to be wrapped within an `Ok`.  
  - Constructor: `Result.as_Ok(value)`
  - `Result.Ok` attribute returns the wrapped `value`
  - Can never wrap a `ResultErr` instance (it will just be converted to an `Err(value)`). 
  
- `Err(e)`
  - `e` is any object to be wrapped within an `Err`. 
    - `e` is stored as `ResultErr` Exception object.
    -  If  `not isinstance(e, ResultErr)`,  then `e = ResultErr(e)`. 
  - Constructor: `Result.as_Err(error_msg)`
  - `Result.Err` attribute returns the wrapped `e`.

### Properties of the `Result` Variants

#### `Err(e)`:

- Represents a failure (error-state).
  -  `e` is a `ResultErr` object that stores error messages and traceback information.

  - If `e` is another type, it is converted to a `ResultErr`.  
    That is, given `Err(e)` and `not isinstance(e, ResultErr)` becomes `Err( ResultErr(e) )`. 

- Can be initialized with `Err(error_msg)`, where `error_msg` can be any object (typically a str)
  - `Err(e)` &nbsp; ➥&nbsp; syntactic-sugar for &nbsp; ➥&nbsp;  `Result.as_Err(e)`

- If an `Ok(value)` operation fails, then it is converted to an `Err(e)`, where `e` stores the error message.

- Any operation on `Err(e)` results in another error message being appended to `e`.

#### `Ok(value)`

- Represents success (non-error state).  The `value` is wrapped within the `Ok()`.

- Can be initialized with `Ok(value)`
  - `Ok(value)` &nbsp; ➥&nbsp; syntactic-sugar for &nbsp; ➥&nbsp; `Result.as_Ok(value)`

- If  `value` is an instance of  `ResultErr`, then it is converted to `Err(e)`. 
  - `e = ResultErr("error message")`  
    `Ok(e)` &nbsp; ➥&nbsp; becomes &nbsp; ➥&nbsp; `Result.as_Err(e)`

- Math operations are redirected to `value` and rewrap the solution or concatenate the errors.
  - `Ok(value1) + Ok(value2) ` ➣ `Ok(value1 + value2)`
  - `Ok(value1) + Err(e1)    ` ➣ `Err(e1 + "a + b with b as Err")`
  - `Err(e1)    + Err(e2)    ` ➣ `Err(e1 + "a + b with a and b as Err.")`

- All methods and attributes not associated with `Result` are redirected to `value`.
  - `Ok(value).method()` is equivalent to `Ok(value.method())` and  
    `Ok(value).attrib  ` is equivalent to `Ok(value.attrib)`.  

  - `Ok(value).raises()` does NOT become `Ok(value.raises())`  
  because `Result.raises()` is a native `Result` method.

- Comparisons redirect to comparing the wrapped `value` if `Ok`. But mixed comparisons assume:  
  `Err(e1) < Ok(value)` and `Err(e1) == Err(e2)` for any `value`, `e1`, and `e2`.
  - `Ok(value1) <= Ok(value2) ` ➣ `value1 <= value2`
  - `Ok(value1) <  Ok(value2) ` ➣ `value1 <  value2`
  - `Err(e1)    <  Ok(value2) ` ➣ `True`
  - `Ok(value1) <  Err(e1)    ` ➣ `False`
  - `Err(e1)    <  Err(e2)    ` ➣ `False`
  - `Err(e1)    <= Err(e2)    ` ➣ `True`

  

## ResultErr Class

The `ResultErr` class is a custom exception class for error handling in the `Result` object. The `ResultErr` class captures error messages and optional traceback information. Its primary use is for identifying when a `Result` instance is an `Err` variant, which is handled automatically. It should not be necessary to use the ResultErr class directly, but select attributes and methods are presented here for background information.

### Initialization

```python
# All arguments are optional
from ResultContainer import ResultErr

# Main object signature:
e = ResultErr(msg="", add_traceback=True, max_messages=20)
#  msg            (Any, optional): Error message(s) to initialize with.
#                                  `str(msg)` is the message that is stored.
#                                  If msg is a Sequence, then each item in the Sequence is
#                                  appended as str(item) to the error messages.
#                                  Default is "", to disable error status.
#  add_traceback (bool, optional): If True, then traceback information is added to the message.
#  max_messages   (int, optional): The maximum number of error messages to store.
#                                  After this, all additional messages are ignored. Default is 20.
```

### Attributes and Methods

These are select attributes and methods built into `Result` object. 

#### Attributes

```    
size          (int): Returns the number of error messages.

is_Ok        (bool): Returns False if in error status (ie, size == 0).
is_Err       (bool): Returns True  if in error status (ie, size >  0).

Err_msg             (list[str]): List of the error messages that have been added.
Err_traceback (list[list[str]]): List of lists that contains the traceback information for each error message.
```

#### Methods

``` 
append(msg, add_traceback=True):
   Append an error message to the instance.
   
raises(add_traceback=False, error_msg=""):
    Raise a ResultErr exception if `size > 0`.
    `error_msg` is an optional note to append to the ResultErr.
    If not exception is raised, then returns itself.

str(sep=" | ", as_repr=True, add_traceback=False):
    Returns a string representation of the error messages and traceback information.
    If as_repr is True error messages are be printed inline (repr version),
    while False writes out traceback and error messages over multiple lines (str version).
    For general use, it is recomended to use the default values.

copy():
    Return a copy of the current ResultErr object.
```

  

## Result Class

### Initialization

```python
# Only the first argument is required for all constructors
from ResultContainer import Result, Ok, Err

# Main object signature:
res = Result(value, success, error_msg, add_traceback, deepcopy)  # Construct either Ok or Err

# Classmethod signatures:
res = Result.as_Ok(value, deepcopy)                               # Construct Ok  variant

res = Result.as_Err(error_msg, add_traceback)                     # Construct Err variant
    
# Syntact Sugar Constructors:
res = Ok(value, deepcopy)                                         # Construct Ok  variant

res = Err(error_msg, add_traceback)                               # Construct Err variant

# Arguments:
#  value                      (Any): The value to wrap in the Ok(value).
#                                    If value is a Result    object, then returns value;      ignores other args.
#                                    If value is a ResultErr object, then returns Err(value); ignores other args.
#  success         (bool, optional): True if success, False for error. Default is True.
#  error_msg        (Any, optional): If success is False:
#                                       a) and error_msg="", return Err( str(value) )
#                                       b) otherwise,        return Err( str(error_msg) ),
#                                             if error_msg is listlike, then each item is appended as a separate message.
#                                    Default is "".
#  add_traceback (bool, optional):   If True and constructing Err variant, adds traceback information to Err.
#                                    Default is True.
#  deepcopy (bool, optional):        If True, then deepcopy value before wrapping in Ok. Default is False.
#
```

### Attributes and Methods

These are select attributes and methods built into `Result` object. For a full listing please see the Result docstr.

#### Attributes

```    
is_Ok   (bool): True if the result is a  success.
is_Err  (bool): True if the result is an error.

Ok (any):
    If  Ok variant, then returns value in Ok(value);
    If Err variant, then raises a ResultErr exception.

Err (any):
    If  Ok variant, then raises a ResultErr exception;
    If Err variant, then returns the wrapped ResultErr.

Err_msg (list[str]):
    For the Ok(value) variant, returns [].
    For the Err(e)    variant, returns list of error messages.

Err_traceback (list[list[str]]):
    For the Ok(value) variant, returns [].
    For the Err(e)    variant, returns list of traceback lines.
```

#### Methods

``` 
raises(add_traceback=False, error_msg=""):
    If  Ok variant, then returns Ok(value);
    If Err variant, then raises a ResultErr exception.
    
unwrap():
    Return the wrapped value in Ok(value) or e in Err(e).
    
unwrap_or(default):
    Return the wrapped value in Ok(value) or return default.

expect(error_msg=""):
    If  Ok variant, then return the wrapped value in Ok(value);
    If Err variant, then raises a ResultErr exception and optionally append error_msg to it.

is_Ok_and(bool_ok_func, *args, **kwargs):
    True if Ok(value) variant and ok_func(value, *args, **kwargs) returns True, otherwise False.
      - If function call fails, then raises exception.
        
apply(ok_func, *args, **kwargs):
    Maps a function to the Result to return a new Result.
    For the Ok(value) variant, returns Ok(ok_func(value, *args, **kwargs)).
    For the Err(e)    variant, returns Err(e).
      - If ok_func fails, returns Err("Result.apply exception.").
                                       
apply_or(default, ok_func, *args, **kwargs):
    Maps a function to the Result to return a new Result.
    For the Ok(value) variant, returns Ok(ok_func(value, *args, **kwargs)).
    For the Err(e)    variant, returns Ok(default).
      - If ok_func fails, returns Ok(default).
                                       
apply_map(ok_func, unwrap=False):
    Maps a function to the elmenets in value from a Result to return 
    a new Result containing a list of the function returns.
    For the Ok(value) variant, and
        value is iterable, returns Ok(list(map(ok_func, value))).
        otherwise,         returns Ok([ok_func(value)]).
    For the Err(e) variant, returns Err(e).
      - If ok_func fails, returns Err("Result.apply_map exception.").
    If unwrap is True, then returns a list or ResultErr.

map(ok_func):
map_or(default, ok_func):
    Same functionality as apply and apply_or, 
    except that if the function call fails, raises an exception.
                                       
iter(unwrap=True, expand=False):
    Returns an iterator of the value in Ok(value).
    if unwrap is False returns iter_wrap(expand)
    if unwrap is True  returns iter_unwrap(expand)   
    Always iterates at least once for Ok, and does not iterate for Err.
                                       
iter_unwrap(expand=False):
    Returns an iterator of the value in Ok(value).
    For the Ok(value) variant,
        if value is iterable: returns iter(value)
        else:                 returns iter([value])  ➣ Only one iteration
    For the Err(e) variant, returns iter([]).
    Always iterates at least once for Ok, and does not iterate for Err.
    If expand is True, then returns list(iter_unwrap()).

iter_wrap(expand=False):
    Returns an iterator of the value in Ok(value) that wraps each iterated item in a Result. That is, 
    [item for item in Ok(value).iter_wrap()] ➣ [Result(item0), Result(item1), Result(item2), ...]
    Always iterates at least once for Ok, and does not iterate for Err.
    If expand is True, then returns list(iter_unwrap()).
                                       
add_Err_msg(error_msg, add_traceback=True)):
    For the Ok(value) variant, converts to Err(error_msg).
    For the Err(e)    variant, adds an error message.
    
update_result(value, create_new=False, deepcopy=False):
    Update Result to hold value. Either updates the current instance or creates a new one.
    Return the updated or new Result. If value is not a ResultErr type, then returns Ok(value);
    otherwise, returns Err(value).
    
copy(deepcopy=False):
    Create a copy of the Result. If deepcopy=True, the returns Result(deepcopy(value)).
    
```

  

## Usage

Below are examples showcasing how to create and interact with a `ResultContainer`.

### ResultErr Initialization

```python
from ResultContainer import ResultErr

# Initialize ResultErr instances
a = ResultErr("Error Message")
b = ResultErr(5)
c = ResultErr(["Error Message 1", "Error Message 2"])

print(a.str())  # ResultErr("Error Message")
print(b.str())  # ResultErr("5")
print(c.str())  # ResultErr("Error Message 1 | Error Message 2")

raise c         # Raises the following exception:

# Traceback (most recent call last):
#   File "example.py", line 12, in <module>
#     raise c
# ResultContainer.ResultErr: 
#   File "example.py", line 6, in <module> 
#     c = ResultErr(["Error Message 1", "Error Message 2"])
# 
#    <Error Message 1>
#    <Error Message 2>
```

### Result Initialization

```python
from ResultContainer import Result, Ok, Err, ResultErr

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

# A ResultErr instance is always wrapped by Err ---------------------------------------------------------
e = ResultErr("Error Message")   # e is an instance of ResultErr

a1 = Result(e, success=True)     # a1 == a2 == a3 == Err(e); success is ignored because isinstance(e, ResultErr)
a2 = Result.as_Ok(e)
a3 = Ok(e)
```

  

### Math Operations

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

  

### Wrapping `datetime Example

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
#   File "example.py", line 9, in <module>
#     y = x.raises()  # Raises the following exception:
#         ^^^^^^^^^^
#   File "ResultContainer\__init__.py", line 882, in raises       
#     raise self._val  # Result.Err variant raises an exception
#     ^^^^^^^^^^^^^^^
# ResultContainer.ResultErr: 
#   File "example.py", line 7, in <module>
#     x /= 0           # x = Err("a /= b resulted in an Exception. | ZeroDivisionError: division by zero")
#   File "ResultContainer\__init__.py", line 1313, in __itruediv__
#     return self._operator_overload_error(e, op, True)
# 
#    <a /= b resulted in an Exception.>
#    <ZeroDivisionError: division by zero>
#    <Result.raises() on Err>
```

  

```python
from ResultContainer import Result, Ok, Err
from datetime import datetime, timedelta

dt = Result(datetime(9999, 12, 31))

bad_dt = dt + timedelta(days=10000)

bad_dt.raises()    # Raises the following exception:
# Traceback (most recent call last):
#   File "example.py", line 8, in <module>
#     bad_dt.raises()  
#     ^^^^^^^^^^^^^^^
#   File "ResultContainer\__init__.py", line 882, in raises
#     raise self._val  # Result.Err variant raises an exception
#     ^^^^^^^^^^^^^^^
# ResultContainer.ResultErr: 
#   File "example.py", line 6, in <module>
#     bad_dt = dt + timedelta(days=10000)
# 
#    <a + b resulted in an Exception.>
#    <OverflowError: date value out of range>
#    <Result.raises() on Err>
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
