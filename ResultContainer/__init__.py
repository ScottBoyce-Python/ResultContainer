"""
ResultContainer Module

This module defines the `Result` class and supporting `ResultErr` class,
mimicking the behavior of Rust's `Result` enum. The `Result` class represents the
result of an operation, either as a success (`Ok`) with a value or as
an error (`Err`) with associated error messages and traceback information.


Classes:
    - `Result`: Represents the result of an operation, containing either
                an `Ok(value)` for success or an `Err(error)` for failure.
    - `ResultErr`: A custom exception class for handling multiple
                   error messages and traceback information.
    - `Ok`: Syntactic  sugar for Result.as_Ok
    - `Err`: Syntactic sugar for Result.as_Err


Key Features:
    - Supports arithmetic and comparison operations for both `Ok` and `Err` values.
    - Provides a flexible mechanism for chaining operations on the `Ok` value while propagating errors through `Err`.
    - Includes detailed error handling with tracebacks and the ability to append multiple error messages.
    - Implements helper methods for error propagation, transformation, and querying.

Error Handling:
    - The `ResultErr` class captures error messages and optional traceback information.
    - Errors only raise an exception when requested (`expect` or `raises` methods).

Constructors:
    Result(value, success=True, error_msg=""):
        Main class that stores the success (Ok) or error (Err).
    ResultErr(msg="", add_traceback=True, max_messages=20):
        Exception class for managing error messages.
    Ok(value):
        Constructor for a success variant. Syntactic sugar for: `Result.as_Ok(value)`
    Err(error_msg, add_traceback=True):
        Constructor for an error variant.  Syntactic sugar for: `Result.as_Err(error)`

Example Usage:
    >>> from ResultContainer import Result, Ok, Err
    >>>
    >>> result = Result.as_Ok("Success")
    >>> print(result)
    Ok("Success")
    >>> x = result.unwrap()            # returns wrapped value so, x = "Success"
    >>> print( result.expect() )       # Same as unwrap() for Ok variant
    Success
    >>>
    >>> error = Result.as_Err("Failure")
    >>> print(error)
    Err("Failure")
    >>> x = error.unwrap()             # returns wrapped value, which is e in Err(e), so, x = ResultErr("Failure")
    >>> x = error.expect()             # For Err variant, raises exception
    Traceback (most recent call last):
      File "example.py", line 10, in <module>
        x = error.expect()             # For Err variant, raises exception
            ^^^^^^^^^^^^^^
      File "ResultContainer/__init__.py", line XYZ, in expect
        self.raises(False, error_msg)
      File "ResultContainer/__init__.py", line XYZ, in raises
        raise self._val  # Err variant raises exception
        ^^^^^^^^^^^^^^^
    ResultContainer.ResultErr:
      File "example.py", line  7, in <module>
        error = Result.as_Err("Failure")

       <Failure>

      File "example.py", line 10, in <module>
        x = error.expect()             # For Err variant, raises exception

       <Result.expect for Err variant>
       <Result.raises() on Err>
    >>>
    >>> x = Ok(5)                      # x = Result.Ok(5)
    >>> y = Ok(6)                      # y = Result.Ok(6)
    >>> print( x + y )
    Ok(11)
    >>> print( x / 0 )
    Err("a / b resulted in an Exception | ZeroDivisionError: division by zero")
    >>> print( x.apply(lambda a: a**2) )
    Ok(25)
    >>> z = x / 0                      # z = fResult.Err("a / b resulted in an Exception | ZeroDivisionError: division by zero")
    >>> print( z.Err_msg_contains("ZeroDivisionError") )
    True
    >>> print( z.apply(lambda a: a**2) )
    Err("a / b resulted in an Exception | ZeroDivisionError: division by zero | Result.apply on Err")

Module Level Imports:
    - `traceback`: Used for generating traceback information when an error occurs.

This module is designed for flexible error handling and result management in Python,
with an interface that resembles Rust's `Result` type.

"""

# %% -----------------------------------------------------------------------------------------------

__version__ = "0.3.0"
__author__ = "Scott E. Boyce"
__credits__ = "Scott E. Boyce"
__maintainer__ = "Scott E. Boyce"
__email__ = "boyce@engineer.com"
__license__ = "MIT"
__status__ = "Development"  # set to "Prototype", "Development", "Production"
__url__ = "https://github.com/ScottBoyce-Python/ResultContainer"
__description__ = (
    "ResultContainer is a Python library inspired by Rust's Result enum, designed for robust error handling. "
    "It seamlessly supports mathematical operations, attribute access, and method chaining on Ok(value), "
    "while automatically transitioning to Err(e) upon encountering errors, ensuring error tracking without exiting."
)
__copyright__ = "Copyright (c) 2025 Scott E. Boyce"

__all__ = ["Result", "Ok", "Err", "ResultErr"]


# %% -----------------------------------------------------------------------------------------------


import traceback
from collections.abc import Iterable, Sequence
from copy import deepcopy as _deepcopy


# %% -----------------------------------------------------------------------------------------------


EMPTY_ERROR_MSG = "UnknownError"  # Used for the case of `Err("")`

TRACEBACK_EXCLUDE_FILES = {
    # Python Internal Files
    "runpy.py",
    ### "threading.py",
    "_bootstrap.py",
    "_bootstrap_external.py",
    "_threading_local.py",
    ### "selectors.py",
    ### "queue.py",
    "asyncio/events.py",
    "asyncio/base_events.py",
    ### "doctest.py",
    ### "argparse.py",
    ### "inspect.py",
    #
    # Debugger-Related Files
    "pydevd.py",
    "pydevd_runpy.py",
    "pydevd_frame_eval.py",
    "bdb.py",
    "pdb.py",
    #
    # CLI and Environment Files
    "cli.py",
    ### "site-packages/",
    ### "IPython/core/interactiveshell.py",
    ### "IPython/core/async_helpers.py",
    ### "tornado/platform/asyncio.py",
    #
    # Third-Party Frameworks and Tools
    ### "flask/app.py",
    ### "django/core/handlers/",
    ### "unittest/case.py",
    ### "pytest/",
    "_hooks.py",
    "_manager.py",
    "_callers.py",
}

EXCLUDE_ATTRIBUTES = {
    "ResultErr",
    "Ok",
    "Err",
    "empty_init",
    "is_Ok",
    "is_Err",
    "Err_msg",
    "Err_traceback",
    "raises",
    "expect",
    "expect_Err",
    "unwrap",
    "unwrap_or",
    "apply",
    "apply_or",
    "apply_or_else",
    "apply_Err",
    "map",
    "map_or",
    "map_or_else",
    "map_Err",
    "iter",
    "is_Ok_and",
    "copy",
    "update_result",
    "Err_msg_contains",
    "add_Err_msg",
    "str",
    "_operator_overload_prep",
    "_success",
}

ATTRIBUTES_MISTAKES = {
    "resulterr": "ResultErr",
    "ok": "Ok",
    "err": "Err",
    "is_ok": "is_Ok",
    "is_err": "is_Err",
    "err_msg": "Err_msg",
    "err_traceback": "Err_traceback",
    "expect_err": "expect_Err",
    "apply_err": "apply_Err",
    "map_err": "map_Err",
    "err_msg_contains": "Err_msg_contains",
    "is_ok_and": "is_Ok_and",
    "add_err_msg": "add_Err_msg",
}


# %% -----------------------------------------------------------------------------------------------


class ResultErr(Exception):
    """
    Custom exception class for error handling in the Result object.

    This class stores multiple error messages and traceback information. It is used
    to encapsulate error states and operations related to error management.

    The object is assumed to be in `error status` when it contains one
    or more error messages (msg). An added error message that is "" is ignored.

    error = ResultErr(msg, add_traceback, max_messages)

    Args:
        msg  (Any, optional):           Error message(s) to initialize with.
                                        `str(msg)` is the message that is stored.
                                        #If msg is a Sequence, then each item in the Sequence is
                                        #appended as str(item) to the error messages.
                                        Default is "", to disable error status.
        add_traceback (bool, optional): If True, then traceback information is added to the message.
        max_messages (int, optional):   The maximum number of error messages to store.
                                        After this, all additional messages are ignored.
                                        Default is 20.


    Attributes:
        size                      (int): Returns the number of error messages.
        is_Ok                    (bool): Returns False if in error status (ie, size == 0).
        is_Err                   (bool): Returns True  if in error status (ie, size >  0).
        Err_msg             (list[str]): List of the error messages that have been added.
        Err_traceback (list[list[str]]): List of lists that contains the traceback information for each error message


    Methods:
        raises(add_traceback=False, error_msg=""):
            Raise a ResultErr exception if `size > 0`.
            `error_msg` is an optional note to append to the ResultErr.
            If not exception is raised, then returns itself.

        str(sep=" | ", as_repr=True, add_traceback=False):
            Returns a string representation of the error messages and traceback information.
            If as_repr is True error messages are be printed inline (repr version),
            while False writes out traceback and error messages over multiple lines (str version).

        expect(error_msg=""):
            Raise a ResultErr exception if `size > 0`.
            `error_msg` is an optional note to append to the ResultErr.
            If not exception is raised, then returns [].

        unwrap():
            Returns the list of error messages stored.

        append(msg, add_traceback=True):
            Append an error message to the instance.

        copy():
            Return a copy of the current ResultErr object.

        clear():
            Clear all stored error messages and traceback information.

        pop():
            Remove and return the last error message and traceback information.
            If the size is reduced to zero, then changes to non-error status.

        contains_msg(msg: str):
            Check if a specific message exists in the error messages.

        contains(sub_msg: str):
            Check if any of the error messages contain the sub_msg.


    Example usage:

        >>> from ResultContainer import ResultErr
        >>>
        >>> err = ResultErr()              # empty error (non-error status)
        >>> print( err.is_Err )
        False
        >>> err.raises()                   # No error, so nothing happens
        >>>
        >>> err.append("bad input")        # Add "bad input" error message and include traceback info
        >>> print( err.is_Err )
        True
        >>> print( err.str() )
        ResultErr("bad input")
        >>> err.raises()                   # program terminates due to errors
        Traceback (most recent call last):
        ...
        <bad input>
        >>>
        >>> err = ResultErr("bad input 1")                  # Initialized with an error, includes traceback info
        >>> err.append("bad input 2", add_traceback=False)  # Second error message
        >>> print( err.is_Err )
        True
        >>> print( err.str() )
        ResultErr("bad input | bad input 2")
        >>> err.raises()                   # program terminates due to errors
        Traceback (most recent call last):
        ...
        <bad input 1>
        <bad input 2>
    """

    msg: list[str]
    traceback_info: list[list[str]]
    max_messages: int

    def __init__(self, msg="", add_traceback=True, max_messages=20, *, _levels=-2):
        """
        Initialize the ResultErr instance. If msg is "" then the object is
        initiated as a  `non-error state`, once a msg is added, then
        it is considered in `error state`.

        Args:
            msg  (Any, optional):           Error message(s) to initialize with.
                                            `str(msg)` is the message that is stored.
                                            #If msg is a Sequence, then each item in the Sequence is
                                            #appended as str(item) to the error messages.
                                            Default is "", to disable error status.
            add_traceback (bool, optional): If True, then traceback information is added to the message.
            max_messages (int, optional):   The maximum number of error messages to store.
                                            After this, all additional messages are ignored.
                                            Default is 20.
        """
        super().__init__()
        self.max_messages = max_messages if max_messages > 1 else 1
        self.msg = []
        self.traceback_info = []
        self._process_error_messages(msg, _levels=_levels)

    def _process_error_messages(self, msg, add_traceback=True, _levels=-2):
        """Helper to process error messages."""
        if msg == "":
            return

        if isinstance(msg, ResultErr):
            self.msg += msg.msg
            self.traceback_info += _deepcopy(msg.traceback_info)
            self._check_max_messages()
            return

        if add_traceback:
            if _levels > -2:
                if _levels > -1:
                    raise RuntimeError("ResultErr._process_error_messages has positive _levels")
                _levels = -2
            tb = traceback.format_stack(limit=5 - _levels)
            del tb[_levels:]  # drop calls to _process_error_messages and one above it
            tb = [line for line in tb if not any(exclude in line for exclude in TRACEBACK_EXCLUDE_FILES)]
        else:
            tb = []

        # if not isinstance(msg, str) and isinstance(msg, Sequence):
        #     dim = len(self.msg)
        #     self.msg += list(map(str.strip, map(str, msg)))
        #     dim = len(self.msg) - dim
        #     self.traceback_info += [tb]
        #     self.traceback_info += [[] for i in range(dim - 1)]
        #     # self.traceback_info.extend([tb] * dim
        # else:
        msg = str(msg).strip()
        self.msg.append(msg)
        self.traceback_info.append(tb)

        self._check_max_messages()

    def _check_max_messages(self):
        if len(self.msg) > self.max_messages:
            self.msg = self.msg[: self.max_messages]
            self.traceback_info = self.traceback_info[: self.max_messages]

    @property
    def size(self) -> int:
        """Return the number of stored error messages."""
        return len(self.msg)

    @property
    def is_Ok(self) -> bool:
        return len(self.msg) == 0

    @property
    def is_Err(self) -> bool:
        return len(self.msg) > 0

    @property
    def Err_msg(self) -> list[str]:
        return [] if self.is_Ok else self.msg

    @property
    def Err_traceback(self) -> list[list[str]]:
        return [] if self.is_Ok else self.traceback_info

    def raises(self, add_traceback: bool = False, error_msg="", _levels=-3):
        """
        Raise a ResultErr exception if `size > 0`.

        Args:
            add_traceback (bool, optional): If True, appends traceback to the error message.
            error_msg      (Any, optional): Additional error note to append before raising.

        Raises:
            ResultErr: If the object is in an error state (`size > 0`).
        """
        if len(self.msg) > 0:
            if error_msg != "":
                self.append(str(error_msg), add_traceback, _levels=_levels)
            elif add_traceback:
                self.append("ResultErr.raises() with ResultErr.size > 0", _levels=_levels)
            raise self  # raises exception because ResultErr.size > 0
        return self

    def expect(self, error_msg="", *, _levels=-4) -> list:
        """Raise exception if in error state otherwise return []."""
        if error_msg == "":
            error_msg = "ResultErr.expect() with ResultErr.size > 0"
        self.raises(True, error_msg, _levels=_levels)
        return []

    def unwrap(self) -> list[str]:
        """Returns the list of error messages stored."""
        return self.msg

    def append(self, msg, add_traceback: bool = True, *, _levels=-2):
        """
        Append an error message to the instance. If

        Args:
            msg  (Any, optional): Error message to append.
            add_traceback (bool): Optional, add traceback info.
        """
        if len(self.msg) < self.max_messages:
            self._process_error_messages(msg, add_traceback, _levels=_levels)

    def set_max_messages(self, max_messages: int):
        """Set the maximum number of error messages that are kept."""
        if max_messages < 1:
            self.max_messages = 1
        else:
            self.max_messages = max_messages

        self._check_max_messages()

    def copy(self):
        """Return a copy of the ResultErr instance."""
        return ResultErr(self)

    def clear(self):
        """
        Clear the error message and traceback lists.
        This resets the instance to non-error status.
        """
        self.msg.clear()
        self.traceback_info.clear()

    def pop(self) -> (list[list[str]], list[str]):
        """Remove and return the last stored error message and its traceback info."""
        try:
            return self.msg.pop(), self.traceback_info.pop()
        except Exception:
            return [], []

    def contains_msg(self, msg: str):
        """Check if a specific message exists in the error messages."""
        return msg in self.msg

    def contains(self, sub_msg: str, ignore_case: bool = False) -> bool:
        """Check if any of the error messages contain the sub_msg.

        Args:
            sub_msg      (str): String to search for in the error messages.
            ignore_case (bool): Set to true to ignore case in the matching.

        Returns:
            bool: True if sub_msg is found, otherwise False.
        """
        if ignore_case:
            sub_msg = sub_msg.lower()
            for msg in self.msg:
                if sub_msg in msg.lower():
                    return True
        else:
            for msg in self.msg:
                if sub_msg in msg:
                    return True
        return False

    def str(self, sep: str = " | ", as_repr: bool = True, add_traceback: bool = False) -> str:
        """Return a string representation of the error messages.
        Args:
            sep             (str): Separator used for concatenating error messages.
            as_repr        (bool): Flag to indicate if string should start with `ResultErr(` and close with `)`.
            add_traceback  (bool): Flag to indicate if string should include traceback for each message.
                                   If True, then sep is set to "\n".
        """
        if self.size < 1:
            return "ResultErr()"

        if add_traceback and self.size == 1 and len(self.traceback_info[0]) < 1:
            add_traceback = False
            sep = "\n"  # Traceback does not have any values, but because it was requested, change sep to \n

        if add_traceback:  # ignores sep
            if self.size == 1:
                s = ("".join(self.traceback_info[0]) + f"\n   <{self.msg[0]}>").strip()
                return f"ResultErr(\n  {s}\n)" if as_repr else f"\n  {s}\n"
            else:
                s = ""
                not_first = False
                for m, tb in zip(self.msg, self.traceback_info):
                    if len(tb) > 0:
                        s += "\n\n" if not_first else "\n"
                        s += "".join(tb)
                        not_first = True
                    s += f"\n   <{m}>"

                return f"ResultErr({s}\n)" if as_repr else f"{s}\n"

        if self.size == 1:
            s = f"{self.msg[0]}".strip()
            return f'ResultErr("{s}")' if as_repr else s

        if sep == "\n" and self.size > 1:
            s = "\n".join(f"   {m}" for m in self.msg)
            return f"ResultErr({s}\n)" if as_repr else s.rstrip()
        s = sep.join(f"{m}" for m in self.msg).strip()
        return f'ResultErr("{s}")' if as_repr else s

    def __str__(self):
        if self.size < 1:
            return ""
        return self.str("\n", False, True)

    def __repr__(self):
        if self.size == 0:
            return "ResultErr()"
        return self.str().strip()  # f'ResultErr("{self.str().strip()}")'

    def __hash__(self) -> int:
        return hash(self.str())

    def __bool__(self):
        return len(self.msg) > 0

    def __len__(self):
        return len(self.msg)

    def __iter__(self):
        return iter(self.msg)

    def __copy__(self):
        return self.copy()

    def __deepcopy__(self, unused=None):
        return self.copy()

    def __contains__(self, sub_msg: str):
        return self.contains(sub_msg)

    def __iadd__(self, other):  # To get called on addition with assignment e.g. a +=b.
        self.append(other)
        return self

    def __add__(self, other):  # To get called on add operation using + operator
        err = self.copy()
        err.append(other)
        return err

    def __eq__(self, other):  # To get called on comparison using self == other operator.
        # Assumes Err() < Ok()
        if isinstance(other, ResultErr):
            other = other.msg
        elif isinstance(other, Result):
            if other.is_Ok:
                return False
            other = other._val.msg
        return self.msg == other


# %% -----------------------------------------------------------------------------------------------


class Result:
    """
    A Result class that mimics the behavior of Rust's Result enum.

    This class represents either a success case (`Ok`) with a value or an error case (`Err`).
    The success case is represented as `Ok(value)`,  where `value` is the wrapped object.
    The error   case is represented as `Err(error)`, where `error` is a `ResultErr` object
    containing one or more error messages and traceback information.

    The Ok(value) variant can wrap any object, except for a ResultErr type.
    Mutable objects, such as lists, are wrapped as a shared reference (assignment by reference).
    For example,
        lst = [0,1,2]
        x = Ok(lst)
        lst[-1] = 99                  # Any modifications to lst is reflected in Ok(lst)
        print(x) -> "Ok([0, 1, 99])"
    but you can impose a deepcopy to protect the contents:
        x = Ok(lst, deepcopy=True)

    The Ok(value) supports common python math operations as long as both operands
    are not the Err variant and are compatible.
    For example, Ok(5) + Ok(1) -> Ok(6)
                 Ok(5) + 1     -> Ok(6)
                 x = Ok(5)
                 x += 1        -> x == Ok(6)

    However, error states will propagate and add messages, such as
    Err(5)     -> Err("5") and
    Err(5) + 1 -> Err("5 | a += b with a as Err")
    x = Err(5)
    x += 1     -> x == Err("5 | a += b with a as Err")

    The Ok(value) variant supports attributes and methods associated with value.
    That is, `Ok(value).attrib`   is equivalent to `Ok(value.attrib)`
    and      `Ok(value).method()` is equivalent to `Ok(value.method())`.

    If `Ok(value).attrib` or `Ok(value).method()` results in an exception,
    then `Ok(value)` is converted to `Err(error)` and returned.

    The Err(error) variant only allows for attributes and methods that are part of the Result object.
    Otherwise, `Err(error).attrib` and `Err(error).method()` raises a ResultErr exception.

    res = Result(value, success, error_msg, add_traceback, deepcopy)

    Args:
        value                (Any):       The value to wrap in the Ok(value).
                                          If value is ResultErr object, then wrap in Err(value).
        success   (bool, optional):       True if success, False for error. Default is True.
        error_msg  (Any, optional):       If success is False:
                                             a) and error_msg="", set Err to str(value)
                                             b) otherwise,        set Err to error_msg,
                                                   if listlike, then each item is treated as a separate message.
        add_traceback (bool, optional):   If True and success is False, adds traceback information to Err.
        deepcopy (bool, optional):        If True, then deepcopy value before wrapping in Ok.

    Constructors:
        res = Result.as_Ok(value, deepcopy=False)  # Initialize as Ok  variant.
        res = Result.as_Err(error_msg)             # Initialize as Err variant.

    Attributes:
        is_Ok    (bool): True if the result is a  success.
        is_Err   (bool): True if the result is an error.

        Ok (any):
            If  Ok variant, then returns value in Ok(value);
            If Err variant, then raises a ResultErr exception.
            Equivalent to the expect() method.

        Err (any):
            If  Ok variant, then raises a ResultErr exception;
            If Err variant, then returns the wrapped ResultErr.
            Equivalent to the expect_Err() method.

        Err_msg (list[str]):
            For the Ok(value)  variant, returns `[]`.
            For the Err(error) variant, returns list of error messages.
                Equivalent to `Err(error).unwrap().msg`

        Err_traceback (list[list[str]]):
            For the Ok(value)  variant, returns `[]`.
            For the Err(error) variant, returns list of traceback lines.
                Equivalent to `Err(error).unwrap().traceback_info`

    Methods:

        raises(add_traceback=True, error_msg=""):
            If  Ok variant, then returns Ok(value);
            If Err variant, then raises a ResultErr exception`.
            Useful for check during chained operations

        unwrap():
            Return the wrapped value in Ok(value) or e in Err(e).

        unwrap_or(default):
            Return the wrapped value in Ok(value) or return default.

        expect(error_msg=""):
            If  Ok variant, then return the wrapped value in Ok(value);
            If Err variant, then raises a ResultErr exception and optionally append error_msg to it.
            Equivalent to the `Ok` attribute.

        expect_Err(ok_msg=""):
            If  Ok variant, then raises ResultErr(ok_msg);
            If Err variant, then returns e in Err(e), which is type ResultErr.

        is_Ok_and(bool_ok_func, *args, **kwargs):
            True if Ok(value) variant and ok_func(value, *args, **kwargs) returns True,
            otherwise False.
              - If function call fails, then raises exception.

        apply(ok_func, *args, **kwargs):
            Maps a function to the Result to return a new Result.
            For the Ok(value)  variant, returns `Ok(ok_func(value, *args, **kwargs))`.
            For the Err(error) variant, returns `Err(error)`.
              - If ok_func fails, returns `Err("Result.apply exception.)`.

        apply_or(default, ok_func, *args, **kwargs):
            Maps a function to the Result to return a new Result.
            For the Ok(value)  variant, returns `Ok(ok_func(value, *args, **kwargs))`.
            For the Err(error) variant, returns `Ok(default)`.
              - If ok_func fails, returns `Ok(default)`.

        apply_or_else(err_func, ok_func, *args, **kwargs):
            Maps a function to the Result to return a new Result.
            For the Ok(value)  variant, returns `Ok( ok_func(value, *args, **kwargs))`.
            For the Err(error) variant, returns `Ok(err_func(error, *args, **kwargs))`.
              - If ok_func fails, returns `Ok(err_func(value, *args, **kwargs))`
              - If ok_func and err_func fail, returns `Err("Result.apply_or_else exception.)`.

        apply_Err(err_func, *args, **kwargs):
            Maps a function to the Result to return a new Result.
            For the Ok(value)  variant, returns `Ok(ok_func(value, *args, **kwargs))`.
            For the Err(error) variant, returns `Err(error)`.
              - If err_func fails, returns `Err("Result.apply exception.)`.

        apply_map(ok_func, unwrap=False):
            Maps a function to the Result to return a new Result.
            For the Ok(value)  variant, returns `Ok(list(map(ok_func, value)))`.
            For the Err(error) variant, returns `Err(error)`.
              - If ok_func fails, returns `Err("Result.apply_map exception.)`.
            If unwrap is True, then returns a list or ResultErr.

        map(ok_func):
            Maps a function to the Result to return a new Result.
            For the Ok(value)  variant, returns `Ok(ok_func(value))`.
            For the Err(error) variant, returns `Err(error)`.
              - If function call fails, then raises exception.

        map_or(default, ok_func):
            Maps a function to the Result to return a new Result.
            For the Ok(value)  variant, returns `Ok(ok_func(value))`.
            Otherwise                   returns `Ok(Default)`.

        map_or_else(err_func, ok_func):
            Maps a function to the Err, otherwise return Result.
            For the Ok(value)  variant, returns `Ok(ok_func(value))`.
            For the Err(error) variant, returns `Ok(err_func(error))`.

        map_Err(err_func):
            Maps a function to the Err and another function to Ok.
            For the Ok(value)  variant, returns `Ok(value).copy()`.
            For the Err(error) variant, returns `Ok(err_func(error))`.
              - If function call fails, raises `Err("Result.map_err exception.)`.

        iter(unwrap=True, expand=False):
            Returns an iterator of the value in Ok(value).
            if unwrap is False returns iter_wrap(expand)
            if unwrap is True  returns iter_unwrap(expand)

        iter_unwrap(expand=False):
            Returns an iterator of the value in Ok(value).
            For the Ok(value)  variant,
                if value is iterable: returns `iter(value)`
                else:                 returns `iter([value])`  -> Only one iteration
            For the Err(error) variant, returns `iter([])`.
            This setup always iterates at least once for Ok() and does not iterate for Err().
            If expand is True, then returns `list(iter_unwrap())`.
            Note, this process will consume an iterable if it does not store values.

        iter_wrap(expand=False):
            Returns an iterator of the value in Ok(value) with each
            iterated item being wrapped as a Result.
            That is, each `item` is returned as `Ok(item)`,
            unless type(item) is ResultErr, then returns Err(item).
            If expand is True, then returns `list(iter_wrap())`.

        Err_msg_contains(sub_msg: str, ignore_case: bool=False):
            Returns true if Err(e) variant and sub_msg is contained in
            any of the error messages. The Ok variant returns False.

        add_Err_msg(error_msg, add_traceback=True):
            For the Ok(value)  variant, converts to Err(error_msg).
            For the Err(error) variant, adds an error message.

        update_result(value, create_new=False, deepcopy=False):
            Update Result to hold value. Either updates the current instance or creates a new one.
            Return the new Result. If value is not a ResultErr type, then returns Ok(value);
            otherwise, returns Err(value).

        copy(deepcopy=False):
            Create a copy of the Result.
            If deepcopy=True, the returns Result(deepcopy(value)).

    Example Usage:
        >>> from ResultContainer import Result
        >>>
        >>> result = Result.as_Ok("Success")
        >>> print(result)
        Ok("Success")
        >>> x = result.unwrap()            # returns wrapped value so, x = "Success"
        >>> print( result.expect() )       # Same as unwrap() for Ok variant
        Success
        >>>
        >>> error = Result.as_Err("Failure")
        >>> print(error)
        Err("Failure")
        >>> x = error.unwrap()             # returns wrapped value, which is e in Err(e), so, x = ResultErr("Failure")
        >>> x = error.expect()             # For Err variant, raises exception
        Traceback (most recent call last):
          File "example.py", line 10, in <module>
            x = error.expect()             # For Err variant, raises exception
                ^^^^^^^^^^^^^^
          File "ResultContainer/__init__.py", line XYZ, in expect
            self.raises(False, error_msg)
          File "ResultContainer/__init__.py", line XYZ, in raises
            raise self._val  # Err variant raises exception
            ^^^^^^^^^^^^^^^
        ResultContainer.ResultErr:
          File "example.py", line  7, in <module>
            error = Result.as_Err("Failure")

           <Failure>

          File "example.py", line 10, in <module>
            x = error.expect()             # For Err variant, raises exception

           <Result.expect for Err variant>
           <Result.raises() on Err>
        >>>
        >>> x = Result.as_Ok(5)            # x = Result.Ok(5)
        >>> y = Result.as_Ok(6)            # y = Result.Ok(6)
        >>> print( x + y )
        Ok(11)
        >>> print( x / 0 )
        Err("a / b resulted in an Exception | ZeroDivisionError: division by zero")
        >>> print( x.apply(lambda a: a**2) )
        Ok(25)
        >>> z = x / 0                      # z = Result.Err("a / b resulted in an Exception | ZeroDivisionError: division by zero")
        >>> print( z.Err_msg_contains("ZeroDivisionError") )
        True
        >>> print( z.apply(lambda a: a**2) )
        Err("a / b resulted in an Exception | ZeroDivisionError: division by zero | Result.apply on Err")
    """

    ResultErr = ResultErr
    _success: bool  # = not isinstance(_val, ResultErr)
    _val: object

    def __init__(
        self,
        value,
        success=True,
        error_msg="",
        add_traceback=True,
        deepcopy=False,
        *,
        _empty_init=False,
        _levels=-4,
    ):
        if isinstance(value, Result):
            self._success = value._success
            self._val = value._val
            return

        if isinstance(value, ResultErr):
            self._success = False
            self._val = value.copy()
            return

        if success not in [True, False, None]:
            raise TypeError(
                f"Result must have success as bool, but received success={success}, which is type {type(success)}"
            )

        self._success = True  # is converted to False if Err

        if _empty_init or success is None:
            self._success = None
            self._val = None
        elif success:
            self._val = _deepcopy(value) if deepcopy else value
        else:
            self._val = "" if error_msg != "" else value
            self.add_Err_msg(error_msg, add_traceback, _levels=_levels)

    @classmethod
    def as_Ok(cls, value, deepcopy: bool = False):
        return cls(value, deepcopy=deepcopy)

    @classmethod
    def as_Err(cls, error_msg, add_traceback: bool = True, *, _levels=-5):
        return cls(EMPTY_ERROR_MSG, False, error_msg, add_traceback, _levels=_levels)

    @classmethod
    def _empty_init(cls):
        return cls(EMPTY_ERROR_MSG, _empty_init=True)

    @property
    def is_Ok(self) -> bool:
        return self._success

    @property
    def is_Err(self) -> bool:
        return not self._success

    @property
    def Ok(self):
        """Attribute that is equivalent to Result.expect()

        Returns:
            value stored in Ok(value) or raise ResultErr
        """
        if not self._success:
            # Result.Ok raises error for Err variant
            # Have to operate on new instance for debugpy, otherwise the Locals inspection will convert self to Err.
            # old method: self.add_Err_msg("Result.Ok attribute for Err variant")
            err = ResultErr(self._val)
            err.append("Result.Ok attribute for Err variant", _levels=-3)
            raise err  # Ok attribute accessed while in Err state
        return self._val

    @property
    def Err(self) -> ResultErr:
        """Attribute that is equivalent to Result.expect_Err()

        Returns:
            value stored in Err(error) or raise ResultErr
        """
        if self._success:
            # Result.Err raises error for Ok variant
            # Have to operate on new instance for debugpy, otherwise the Locals inspection will convert self to Err.
            raise ResultErr("Result.Err attribute for Ok variant", _levels=-3)
        return self._val

    @property
    def Err_msg(self) -> list[str]:
        return [] if self._success else self._val.msg

    @property
    def Err_traceback(self) -> list[list[str]]:
        return [] if self._success else self._val.traceback_info

    def unwrap(self):
        return self._val

    def unwrap_or(self, default):
        return self._val if self._success else default

    def expect(self, error_msg="", *, _levels=-4):
        if self._success:
            return self._val
        self.add_Err_msg("Result.expect() for Err variant", _levels=_levels)
        self.raises(False, error_msg)

    def expect_Err(self, ok_msg="", *, _levels=-4):
        if not self._success:
            return self._val
        self.add_Err_msg("Result.expect_err() for Ok variant", _levels=_levels)
        self.raises(False, ok_msg)

    def raises(self, add_traceback: bool = True, error_msg="", *, _levels=-4):
        if self._success:
            return self
        if error_msg != "":
            self.add_Err_msg(error_msg, add_traceback, _levels=_levels)
        else:
            self.add_Err_msg("Result.raises() on Err", add_traceback, _levels=_levels)
            #
        raise self._val  # Err variant raises exception

    def getitem(self, key, default):
        if self._success:
            try:
                return Result(self._val[key])
            except Exception:
                pass
        return Result(default)

    def setitem(self, key, value, error_raises_exception=False):
        if self._success:
            try:
                self._val[key] = value
                return self
            except Exception as e:
                err = Result(
                    f"Result.Ok.setitem({key}) raises {e}",
                    success=False,
                    _levels=-5,
                )
                if error_raises_exception:
                    raise self._val
                return err
        self.add_Err_msg(f"Result.Err.setitem({key}) is not subscriptable", _levels=-4)
        return self

    def is_Ok_and(self, bool_ok_func, *args, **kwargs) -> bool:
        return self._success and bool_ok_func(self._val, *args, **kwargs)

    def apply(self, ok_func, *args, **kwargs):
        if self._success:
            try:
                return Result(ok_func(self._val, *args, **kwargs))
            except Exception as e:
                err = Result.as_Err("Result.apply exception", _levels=-6)
                err.add_Err_msg(f"{type(e).__name__}: {e}", False)
        else:
            err = Result(self._val)
            err.add_Err_msg("Result.apply on Err", _levels=-4)
        return err

    def apply_or(self, default, ok_func, *args, **kwargs):
        if self._success:
            try:
                return Result(ok_func(self._val, *args, **kwargs))
            except Exception:
                pass
        return Result(default)

    def apply_or_else(self, err_func, ok_func, *args, **kwargs):
        if self._success:
            try:
                return Result(ok_func(self._val, *args, **kwargs))
            except Exception:
                try:
                    return Result(err_func(self._val, *args, **kwargs))
                except Exception:
                    err = ResultErr(
                        "Result.apply_or_else err_func(value) and ok_func(value) raised an exception",
                        False,
                    )
        else:
            err = self._val
        try:
            return Result(err_func(err, *args, **kwargs))
        except Exception as e:
            err = Result.as_Err(
                "Result.apply_or_else ok_func(value), err_func(value), and err_func(error) raised exceptions",
                _levels=-6,
            )
            err.add_Err_msg(f"{type(e).__name__}: {e}", False)
            return err

    def apply_Err(self, err_func, *args, **kwargs):
        if self._success:
            return self.copy()
        try:
            return Result(err_func(self._val, *args, **kwargs))
        except Exception as e:
            err = self.copy()
            err.add_Err_msg("Result.apply_err exception", _levels=-4)
            err.add_Err_msg(f"{type(e).__name__}: {e}", False)
            return err

    def apply_map(self, ok_func, unwrap: bool = False):
        if unwrap:
            return self.apply_map(ok_func).unwrap()
        if self._success:
            try:
                if isinstance(self._val, Iterable):
                    return Result(list(map(ok_func, self._val)))
                return Result([ok_func(self._val)])
            except Exception as e:
                err = Result.as_Err("Result.apply_map exception", _levels=-6)
                err.add_Err_msg(f"{type(e).__name__}: {e}", False)
        else:
            err = Result(self._val)
            err.add_Err_msg("Result.apply_map on Err", _levels=-4)
        return err

    def map(self, ok_func):
        if self._success:
            return Result(ok_func(self._val))
        res = Result(self._val)
        res.add_Err_msg("Result.map on Err", _levels=-4)
        return res

    def map_or(self, default, ok_func):
        if not self._success:
            return Result(default)
        return Result(ok_func(self._val))

    def map_or_else(self, err_func, ok_func):
        if self._success:
            return Result(ok_func(self._val))
        return Result(err_func(self._val))

    def map_Err(self, err_func):
        if self._success:
            return self.copy()
        return Result(err_func(self._val))

    def iter_wrap(self, expand=False):
        if expand:
            Result(list(self.iter_wrap()))
        if self._success:
            if isinstance(self._val, Iterable):
                return iter(map(Result, self._val))
            return iter([self])
        return iter([])

    def iter_unwrap(self, expand: bool = False):
        if expand:
            return list(self.iter_unwrap())
        if self._success:
            if isinstance(self._val, Iterable):
                return iter(self._val)
            return iter([self._val])
        return iter([])

    def iter(self, unwrap: bool = True, expand: bool = False):
        if unwrap:
            return self.iter_unwrap(expand)
        return self.iter_wrap(expand)

    def Err_msg_contains(self, sub_msg: str, ignore_case: bool = False) -> bool:
        """
        Returns true if Err(e) variant and sub_msg is contained in any of
        the error messages. The Ok variant returns False.

        Args:
            sub_msg      (str): String to search for in the error messages.
            ignore_case (bool): Set to true to ignore case in the matching.

        Returns:
            bool: True if sub_msg is found, otherwise False.
        """
        return False if self._success else self._val.contains(sub_msg, ignore_case)

    def add_Err_msg(self, error_msg, add_traceback: bool = True, *, _levels=-3):
        """Convert to error status and append error message."""
        if self._success:
            if error_msg == "" and self._val == "":
                error_msg = EMPTY_ERROR_MSG
            elif error_msg == "":
                error_msg = str(self._val)
            self._success = False
            self._val = ResultErr()
        if error_msg != "":
            self._val.append(error_msg, add_traceback, _levels=_levels)

    def update_result(self, value, create_new=False, deepcopy=False):
        if create_new:
            return Result(value, deepcopy=deepcopy)
        self._val = value
        self._success = not isinstance(value, ResultErr)
        return self

    def copy(self, deepcopy=True):
        return Result(self, deepcopy=deepcopy)

    def str(self, result_repr: bool = False, value_repr: bool = False) -> str:
        """Returns a string representation of the Result.
        The following are the argument combinations and the expected string output
        for Ok(value) variant:

        result_repr, value_repr,      Return
              False,      False,         'Ok(str(value))'
              False,       True,         'Ok(repr(value))'
               True,      False,  'Result.Ok(str(value))'
               True,       True,  'Result.Ok(repr(value))'

        Note, that if value is a str, then double quote are always included.
        For Err(e) variant only result_repr is used:

        result_repr,     Return
              False,        'Err(e0 | e1 | e2 | ...)'
               True, 'Result.Err(e0 | e1 | e2 | ...)'

        Args:
            result_repr (bool, optional): If True, prepend 'Result.' to the string. Defaults to False.
            value_repr  (bool, optional): If True, run repr() on value. Defaults to False.

        Returns:
            str: _description_
        """
        if result_repr:
            return f"Result.{self.str(False, value_repr)}"

        if self._success is None:
            return "Result(Empty)"

        if self._success:
            if isinstance(self._val, str):
                return f'Ok("{self._val}")'
            val = repr(self._val) if value_repr else str(self._val)
            return f"Ok({val})"
        return f'Err("{" | ".join(f"{m}" for m in self._val.msg if m != "")}")'

    def _operator_overload_prep(self, b, operation: str, *, _levels=-5):
        # Checks and returns:
        #  a.err and b.err -> True  and a&b error
        #  b.err           -> True  and   b error
        #  a.ok            -> False and b
        #  a.err           -> True  and   a error
        #  -> False and b
        if isinstance(b, ResultErr):
            b = Result(b)  # ResultErr type automatically makes Err()

        if isinstance(b, Result):
            if not self._success and not b._success:
                err = Result(self)
                err.add_Err_msg(f"{operation} with a and b as Err", _levels=_levels)
                return True, err
            if not b._success:
                err = Result(b)
                err.add_Err_msg(f"{operation} with b as Err", _levels=_levels)
                return True, err
            if self._success:
                return False, b._val  # no error

        if not self._success:
            err = Result(self)
            err.add_Err_msg(f"{operation} with a as Err", _levels=_levels)
            return True, err
        return False, b  # no error

    def _operator_overload_error(self, e, operation: str, apply_to_self: bool, *, _levels=-5):
        if apply_to_self:
            self.add_Err_msg(f"{operation} resulted in an Exception", _levels=_levels)
            self.add_Err_msg(f"{type(e).__name__}: {e}", False)
            return self
        err = Result(EMPTY_ERROR_MSG, False, f"{operation} resulted in an Exception", _levels=_levels)
        err.add_Err_msg(f"{type(e).__name__}: {e}", False)
        return err

    def __str__(self):
        return self.str()

    def __repr__(self):
        return self.str(True, True)

    def __len__(self):
        if self._success:
            return len(self._val)
        self.add_Err_msg("len(Err) not allowed", _levels=-4)
        return 0

    def __bool__(self):
        if self._success:
            return bool(self._val)
        return False

    def __hash__(self) -> int:
        return hash(self.str())  # hash the string representation of Result

    def __enter__(self):  # Called when entering a with block.
        if not self._success:
            return self
        self._val = self._val.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, tb):  # Called when exiting a with block.
        if self._val.__exit__(exc_type, exc_value, traceback):
            # tb = traceback.format_tb(tb)
            # tb = [line for line in tb if not any(exclude in line for exclude in TRACEBACK_EXCLUDE_FILES)]
            # tb.pop()
            self.add_Err_msg(f"with block {exc_type} Exception", False)
            # self._val.traceback_info.pop()
            # self._val.traceback_info.append(tb)
            raise self._val from exc_value
        return False

        self._val.__exit__(exc_type, exc_value, traceback)

    def __contains__(self, value):
        if isinstance(value, Result):
            value = value.unwrap()

        if isinstance(value, ResultErr):
            return False if self._success else self._val == value

        if not self._success:
            return False

        if isinstance(self._val, (Sequence, Iterable)):
            return value == self._val or value in self._val
        return value == self._val

    def __getattr__(self, name):
        """
        Handles unknown attributes and methods by forwarding them to the value in Ok(value).
        For the Ok(value) variant, returns Ok(value.attrib) or Ok(value.method()).
            -If attribute is bad, or error results from method then returns Err(error).
        For the Err(error) variant or attribute name is invalid, raises ResultErr.

        Parameters:
            name (str): The name of the missing attribute.

        Returns:
            The result of the attribute wrapped as a Result or modifies underlying value.
        """
        if name in ATTRIBUTES_MISTAKES:
            self.add_Err_msg(
                f"Result.{name} is a possible case mistake. Did you mean Result.{ATTRIBUTES_MISTAKES[name]} instead?"
                f" Or did you forget () on a method or put () on an attrib."
                f" If Ok(x.{name}) is what you want, then do Ok(x).expect().{name}",
                _levels=-4,
            )
        elif name in EXCLUDE_ATTRIBUTES:
            self.add_Err_msg(
                f"{name} is an excluded attribute/method."
                f" Did you forget () on a method or put () on an attrib."
                f" If Ok(x.{name}) is what you want, then do Ok(x).expect().{name}",
                _levels=-4,
            )
        elif self.is_Err:
            self.add_Err_msg(f"VAR.{name} with VAR as Err variant", _levels=-4)

        self.raises()

        try:
            # Forward any unknown attribute to value in Ok(value) component
            attr = getattr(self._val, name)
            if attr is None:
                return
            if callable(attr):

                def method(*args, **kwargs):
                    try:
                        return Result(attr(*args, **kwargs))
                    except Exception as e:
                        self.add_Err_msg(f"VAR.{name}() raises {e}", _levels=-4)
                        return self

                return method
            if isinstance(attr, Result):
                return attr
            return Result(attr)
        except AttributeError:
            self.add_Err_msg(f"VAR.{name} raises an AttributeError", _levels=-4)
            return self

    def __getitem__(self, key):  # index return, a[index]
        if not self._success:
            err = Result(self)
            if isinstance(key, str):
                err.add_Err_msg(f'Err({repr(self._val)})["{key}"] is not subscriptable', _levels=-4)
            else:
                err.add_Err_msg(f"Err({repr(self._val)})[{key}] is not subscriptable", _levels=-4)
            return err
        try:
            return Result(self._val[key])
        except Exception as e:
            return Result(
                "",
                success=False,
                error_msg=f"Ok({self._value})[{key}] raises {e}",
                _levels=-5,
            )

    def __setitem__(self, key, value):  # set from index, a[index] = XYZ
        if self._success:
            try:
                self._val[key] = value
            except Exception as e:
                raise ResultErr(f"Ok()[{key}]=value failed.", _levels=-3) from e
        else:
            self.add_Err_msg(f"Err()[{key}] is not subscriptable", _levels=-4)

    def __iter__(self):
        return self.iter_wrap()

    def __reversed__(self):  # invoked with reversed()
        return reversed(list(self.iter_wrap()))

    def __iadd__(self, other):  # addition with assignment, a += b
        op = "a += b"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            self.add_Err_msg(other, _levels=-4)
            return self
        try:
            self._val += other
            return self
        except Exception as e:
            return self._operator_overload_error(e, op, True)

    def __add__(self, other):  # add operation, a + b
        op = "a + b"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            return other
        try:
            return Result(self._val + other)
        except Exception as e:
            return self._operator_overload_error(e, op, False)

    def __radd__(self, other):  # reflective add operation, b + a
        op = "b + a"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            return other
        try:
            return Result(other + self._val)
        except Exception as e:
            return self._operator_overload_error(e, op, False)

    def __isub__(self, other):  # subtraction with assignment, a -= b
        op = "a -= b"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            self.add_Err_msg(other, _levels=-4)
            return self
        try:
            self._val -= other
            return self
        except Exception as e:
            return self._operator_overload_error(e, op, True)

    def __sub__(self, other):  # subtraction operation, a - b
        op = "a - b"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            return other
        try:
            return Result(self._val - other)
        except Exception as e:
            return self._operator_overload_error(e, op, False)

    def __rsub__(self, other):  # reflective subtraction operation, b - a
        op = "b - a"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            return other
        try:
            return Result(other - self._val)
        except Exception as e:
            return self._operator_overload_error(e, op, False)

    def __imul__(self, other):  # multiplication with assignment, a *= b
        op = "a *= b"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            self.add_Err_msg(other, _levels=-4)
            return self
        try:
            self._val *= other
            return self
        except Exception as e:
            return self._operator_overload_error(e, op, True)

    def __mul__(self, other):  # multiplication operation, a * b
        op = "a * b"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            return other
        try:
            return Result(self._val * other)
        except Exception as e:
            return self._operator_overload_error(e, op, False)

    def __rmul__(self, other):  # reflective multiplication operation, b * a
        op = "b * a"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            return other
        try:
            return Result(other * self._val)
        except Exception as e:
            return self._operator_overload_error(e, op, False)

    def __itruediv__(self, other):  # division with assignment, a /= b
        op = "a /= b"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            self.add_Err_msg(other, _levels=-4)
            return self
        try:
            self._val /= other
            return self
        except Exception as e:
            return self._operator_overload_error(e, op, True)

    def __truediv__(self, other):  # division operation, a / b
        op = "a / b"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            return other
        try:
            return Result(self._val / other)
        except Exception as e:
            return self._operator_overload_error(e, op, False)

    def __rtruediv__(self, other):  # reflective division operation, b / a
        op = "b / a"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            return other
        try:
            return Result(other / self._val)
        except Exception as e:
            return self._operator_overload_error(e, op, False)

    def __ifloordiv__(self, other):  # floor division with assignment, a //= b
        op = "a //= b"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            self.add_Err_msg(other, _levels=-4)
            return self
        try:
            self._val //= other
            return self
        except Exception as e:
            return self._operator_overload_error(e, op, True)

    def __floordiv__(self, other):  # floor division operation, a // b
        op = "a // b"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            return other
        try:
            return Result(self._val // other)
        except Exception as e:
            return self._operator_overload_error(e, op, False)

    def __rfloordiv__(self, other):  # reflective floor division operation, b // a
        op = "b // a"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            return other
        try:
            return Result(other // self._val)
        except Exception as e:
            return self._operator_overload_error(e, op, False)

    def __imod__(self, other):  # modulus with assignment, a %= b
        op = "a %= b"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            self.add_Err_msg(other, _levels=-4)
            return self
        try:
            self._val %= other
            return self
        except Exception as e:
            return self._operator_overload_error(e, op, True)

    def __mod__(self, other):  # modulus operation, a % b
        op = "a % b"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            return other
        try:
            return Result(self._val % other)
        except Exception as e:
            return self._operator_overload_error(e, op, False)

    def __rmod__(self, other):  # reflective modulus operation, b % a
        op = "b % a"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            return other
        try:
            return Result(other % self._val)
        except Exception as e:
            return self._operator_overload_error(e, op, False)

    def __ipow__(self, other):  # exponentiation with assignment, a **= b
        op = "a **= b"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            self.add_Err_msg(other, _levels=-4)
            return self
        try:
            self._val **= other
            return self
        except Exception as e:
            return self._operator_overload_error(e, op, True)

    def __pow__(self, other):  # exponentiation operation, a ** b
        op = "a ** b"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            return other
        try:
            return Result(self._val**other)
        except Exception as e:
            return self._operator_overload_error(e, op, False)

    def __rpow__(self, other):  # reflective exponentiation operation, b ** a
        op = "b ** a"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            return other
        try:
            return Result(other**self._val)
        except Exception as e:
            return self._operator_overload_error(e, op, False)

    def __imatmul__(self, other):  # matrix multiplication with assignment, a @= b
        op = "a @= b"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            self.add_Err_msg(other, _levels=-4)
            return self
        try:
            self._val @= other
            return self
        except Exception as e:
            return self._operator_overload_error(e, op, False)

    def __matmul__(self, other):  # matrix multiplication, a @ b
        op = "a @ b"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            return other
        try:
            return Result(self._val @ other)
        except Exception as e:
            return self._operator_overload_error(e, op, False)

    def __rmatmul__(self, other):  # reverse matrix multiplication, b @ a
        op = "b @ a"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            return other
        try:
            return Result(other @ self._val)
        except Exception as e:
            return self._operator_overload_error(e, op, False)

    def __and__(self, other):  # bitwise AND, a & b
        op = "a & b"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            return other
        try:
            return Result(self._val & other)
        except Exception as e:
            return self._operator_overload_error(e, op, False)

    def __or__(self, other):  # bitwise OR, a | b
        op = "a | b"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            return other
        try:
            return Result(self._val | other)
        except Exception as e:
            return self._operator_overload_error(e, op, False)

    def __xor__(self, other):  # bitwise XOR (exclusive OR), a ^ b
        op = "a ^ b"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            return other
        try:
            return Result(self._val ^ other)
        except Exception as e:
            return self._operator_overload_error(e, op, False)

    def __invert__(self):  # bitwise NOT, ~a
        try:
            return Result(~self._val)
        except Exception as e:
            return self._operator_overload_error(e, "~a", False)

    def __lshift__(self, other):  # left bit shift, a << b
        op = "a << b"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            return other
        try:
            return Result(self._val << other)
        except Exception as e:
            return self._operator_overload_error(e, op, False)

    def __rshift__(self, other):  # right bit shift, a >> b
        op = "a >> b"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            return other
        try:
            return Result(self._val >> other)
        except Exception as e:
            return self._operator_overload_error(e, op, False)

    def __rand__(self, other):  # reverse bitwise AND, b & a
        op = "b & a"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            return other
        try:
            return Result(other & self._val)
        except Exception as e:
            return self._operator_overload_error(e, op, False)

    def __ror__(self, other):  # reverse bitwise OR, b | a
        op = "b | a"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            return other
        try:
            return Result(other | self._val)
        except Exception as e:
            return self._operator_overload_error(e, op, False)

    def __rxor__(self, other):  # reverse bitwise XOR (exclusive OR), b ^ a
        op = "b ^ a"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            return other
        try:
            return Result(other ^ self._val)
        except Exception as e:
            return self._operator_overload_error(e, op, False)

    def __rlshift__(self, other):  # reverse left bit shift, b << a
        op = "b << a"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            return other
        try:
            return Result(other << self._val)
        except Exception as e:
            return self._operator_overload_error(e, op, False)

    def __rrshift__(self, other):  # reverse right bit shift, b >> a
        op = "b >> a"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            return other
        try:
            return Result(other >> self._val)
        except Exception as e:
            return self._operator_overload_error(e, op, False)

    def __abs__(self):  # To get called by built-in abs() method to for absolute value, abs(a)
        if self._success:
            try:
                return Result(abs(self._val))
            except Exception as e:
                self.add_Err_msg("Result(abs(a)) resulted in an Exception", _levels=-4)
                self.add_Err_msg(f"{type(e).__name__}: {e}", False)
        else:
            self.add_Err_msg("Result(abs(a)) with a as Err", _levels=-4)
        return self

    def __neg__(self):  # negation, -a
        if self._success:
            try:
                return Result(-self._val)
            except Exception as e:
                self.add_Err_msg("Result(-a) resulted in an Exception", _levels=-4)
                self.add_Err_msg(f"{type(e).__name__}: {e}", False)
        else:
            self.add_Err_msg("Result(-a) with a as Err")
        return self

    def __pos__(self):  # unary positive, +a
        if self._success:
            try:
                return Result(+self._val)
            except Exception as e:
                self.add_Err_msg("Result(+a) resulted in an Exception", _levels=-4)
                self.add_Err_msg(f"{type(e).__name__}: {e}", False)
        else:
            self.add_Err_msg("Result(+a) with a as Err", _levels=-4)
        return self

    def __int__(self):  # To get called by built-in int() method to convert a type to an int.
        if self._success:
            try:
                return Result(int(self._val))
            except Exception as e:
                self.add_Err_msg("Result(int(a)) resulted in an Exception", _levels=-4)
                self.add_Err_msg(f"{type(e).__name__}: {e}", False)
        else:
            self.add_Err_msg("int(Result(a)) with a as Err", _levels=-4)
        return self

    def __float__(self):  # To get called by built-in float() method to convert a type to float.
        if self._success:
            try:
                return Result(float(self._val))
            except Exception as e:
                self.add_Err_msg("Result(float(a)) resulted in an Exception", _levels=-4)
                self.add_Err_msg(f"{type(e).__name__}: {e}", False)
        else:
            self.add_Err_msg("float(Result(a)) with a as Err", _levels=-4)
        return self

    def __lt__(self, other):  # compare self < other.
        # Assumes Err() < Ok() and Err(a) == Err(b)
        if not isinstance(other, Result):
            other = Result(other)

        if self.is_Ok and other.is_Ok:
            return self._val < other._val
        return other.is_Ok

    def __le__(self, other):  # compare self <= other.
        # Assumes Err() < Ok() and Err(a) == Err(b)
        if not isinstance(other, Result):
            other = Result(other)

        if self.is_Ok and other.is_Ok:
            return self._val <= other._val
        return other.is_Ok or (self.is_Err and other.is_Err)

    def __gt__(self, other):  # compare self > other.
        # Assumes Err() < Ok() and Err(a) == Err(b)
        if not isinstance(other, Result):
            other = Result(other)

        if self.is_Ok and other.is_Ok:
            return self._val > other._val
        return self.is_Ok

    def __ge__(self, other):  # compare self >= other.
        # Assumes Err() < Ok() and Err(a) == Err(b)
        if not isinstance(other, Result):
            other = Result(other)

        if self.is_Ok and other.is_Ok:
            return self._val >= other._val
        return self.is_Ok or (self.is_Err and other.is_Err)

    def __eq__(self, other):  # compare self == other.
        # Assumes Ok(a) == Ok(b) if a == b, but Err(a) == Err(b) for any a or b.
        if not isinstance(other, Result):
            other = Result(other)

        if self.is_Ok and other.is_Ok:
            return self._val == other._val
        return self.is_Err and other.is_Err

    def __ne__(self, other):  # compare self != other.
        # Assumes Ok(a) == Ok(b) if a == b, but Err(a) == Err(b) for any a or b.
        if not isinstance(other, Result):
            other = Result(other)

        if self.is_Ok and other.is_Ok:
            return self._val != other._val
        return self.is_Ok or other.is_Ok


# %% -----------------------------------------------------------------------------------------------


class Ok:
    """
    Constructor class that returns a Result.as_Ok(value).

    Example:
        >>> result = Ok(42)
        >>> print(result.unwrap())  # Outputs: 42
    """

    def __new__(self, value, deepcopy=False):
        return Result(value, deepcopy=deepcopy)


class Err:
    """
    Constructor class that returns a Result.as_Err(error).

    Example:
        >>> error = Err("Error message")
        >>> print(error.unwrap())         # Outputs: ResultErr("Error message")
    """

    def __new__(self, error_msg, add_traceback=True, *, _levels=-5):
        return Result(EMPTY_ERROR_MSG, False, error_msg, add_traceback, _levels=_levels)


# %% -----------------------------------------------------------------------------------------------


if __name__ == "__main__":
    # Demonstration of basic functionality
    # Methods for creating an Ok variant (all three produce the same result):
    success_result = Result("Operation was successful")
    success_result = Result.as_Ok("Operation was successful")
    success_result = Ok("Operation was successful")

    # Methods for creating an Err variant (all three produce the same result):
    error_result = Result(None, False, "Something went wrong")  # long method of init
    error_result = Result.as_Err("Something went wrong")
    error_result = Err("Operation failed")

    print("Success Result:", success_result)
    print("Error Result:", error_result.unwrap())

    try:
        value = success_result.expect()
        print("Retrieved Value:", value)
    except ResultErr as e:  # Does not occur
        print("Error:", e)

    try:
        error_result.expect()  # This will raise an error
    except ResultErr as e:
        print("Caught Error:", e.str())
        print("Caught Error:", repr(e))

    res = Ok(55)

    assert res + 5 == 60
    assert res + 5 == Ok(60)

    err = Err("bad input")

    assert err + 5 == Err(["bad input", "a + b with a as Err"])

    print("program completed successfully")
