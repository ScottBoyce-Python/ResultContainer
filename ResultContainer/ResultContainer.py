"""
ResultContainer Module

This module defines the `Result` class and supporting `ResultErr` class,
mimicking the behavior of Rust's `Result` enum. The `Result` class represents the
result of an operation, either as a success (`Ok`) with a value or as
an error (`Err`) with associated error messages and codes.


Classes:
    - `Result`: Represents the result of an operation, containing either
                an `Ok(value)` for success or an `Err(error)` for failure.
    - `ResultErr`: A custom exception class for handling multiple
                   error messages,  corresponding error codes, and traceback information.
    - `Ok`: Syntactic  sugar for Result.Ok
    - `Err`: Syntactic sugar for Result.Err


Key Features:
    - Supports arithmetic and comparison operations for both `Ok` and `Err` values.
    - Provides a flexible mechanism for chaining operations on the `Ok` value while propagating errors through `Err`.
    - Includes detailed error handling with tracebacks, custom error codes, and the ability to append multiple error messages.
    - Implements helper methods for error propagation, transformation, and querying.

Error Handling:
    - The `ResultErr` class captures error messages, codes, and optional traceback information.
    - Errors only raise an exception when requested (`expect` or `raised` methods).

Constructors:
    Result(value, success=True, error_msg="", error_code=1, error_code_group=1):
        Main class that stores the success (Ok) or error (Err).
    ResultErr(msg="", code=1, error_code_group=1, add_traceback=True, max_messages=20):
        Exception class for managing error messages.
    Ok(value):
        Constructor for a success variant. Syntactic sugar for: `Result.Ok(value)`
    Err(error_msg, error_code=1, error_code_group=1, add_traceback=True):
        Constructor for an error variant.  Syntactic sugar for: `Result.Err(error)`

Example Usage:
    >>> success = Result.Ok("Operation succeeded")
    >>> error = Result.Err("Operation failed")
    >>> print(success)
    Ok("Operation succeeded")
    >>> print(error)
    Err("Operation failed")
    >>> print(success.unwrap())
    Operation succeeded
    >>> print(error.unwrap())
    File "./ResultContainer/ResultContainer.py", line 6, in <module>
        error = Result.Err("Operation failed")
    [1] Operation failed
    >>> error().expect()         # raises exception
    Traceback (most recent call last):
      File "<string>", line 1, in <module>
      File "./ResultContainer/ResultContainer.py", line 943, in expect
      raise self._Err
        ResultErr:
        File "./ResultContainer/ResultContainer.py", line 6, in <module>
            error_result = Err("Operation failed")
     [1] Operation failed

Module Level Imports:
    - `traceback`: Used for generating traceback information when an error occurs.

This module is designed for flexible error handling and result management in Python,
with an interface that resembles Rust's `Result` type.

"""

try:
    from ._metadata import (
        __version__,
        __author__,
        __credits__,
        __maintainer__,
        __email__,
        __license__,
        __status__,
        __url__,
        __description__,
        __copyright__,
    )
except ImportError:
    try:
        from _metadata import (
            __version__,
            __author__,
            __credits__,
            __maintainer__,
            __email__,
            __license__,
            __status__,
            __url__,
            __description__,
            __copyright__,
        )
    except ImportError:
        # _metadata.py failed to load,
        # fill in with dummy values (script may be standalone)
        __version__ = "Failed to load from _metadata.py"
        __author__ = "Scott E. Boyce"
        __credits__ = "Scott E. Boyce"
        __maintainer__ = "Scott E. Boyce"
        __email__ = "boyce@engineer.com"
        __license__ = "MIT"
        __status__ = __version__
        __url__ = "https://github.com/ScottBoyce-Python/ResultContainer"
        __description__ = "ResultContainer is a Result class that mimics the behavior of Rust's Result enum that wraps values in an Ok(value) and Err(e) variant. Math operations, attributes, and methods are passed to value in Ok(value). If an operation with the Ok(value) variant results in an error, then it is converted to an Err(e) variant. Err(e) contains one or more error messages and math operations, attributes, and methods result in appending the respective errors."
        __copyright__ = __version__

# %% --------------------------------------------------------------------------


import traceback
from collections.abc import Sequence, Iterable, KeysView, ValuesView
from copy import deepcopy as _deepcopy

__all__ = ["Result", "ResultErr", "Ok", "Err"]

EMPTY_ERROR_MSG = "UnknownError"  # Used for the case of `Err("")`

_BASE_ERROR_CODES = {
    1: "Unspecified",
    2: "Undefined",
    3: "Op_On_Error",
    4: "Apply",
    5: "Expect",
    6: "Map",
    7: "Attribute",
    8: "Attribute_Invalid",
    9: "Attribute_While_Error_State",
    10: "Method",
    11: "Function",
    12: "Math_Op",
    13: "Float_Op",
    14: "Int_Op",
}

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
}

EXCLUDE_ATTRIBUTES = {
    "ResultErr",
    "Ok",
    "Err",
    "empty_init",
    "is_Ok",
    "is_Err",
    "Err_msg",
    "Err_code",
    "Err_traceback",
    "raised",
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
    "add_Err_msg",
    "register_code",
    "error_code",
    "error_code_description",
    "str",
    "_empty_error",
    "_operator_overload_prep",
    "_success",
    "_Ok",
    "_Err",
    "_g",
}


# %% --------------------------------------------------------------------------


class ResultErrCodesDict(dict):
    """
    A custom dictionary for managing error code meanings.

    Attributes:
        int_keys (set): Set of integer keys.
        str_keys (set): Set of string keys.

    Methods:
        keys(): Returns all integer keys.
        values(): Returns all string values.
        items(): Iterates over key-value pairs.
        copy(): Creates a shallow copy of the dictionary.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the dictionary, supporting key-value pairs
        while enforcing the custom rules.
        """
        super().__init__()
        self.int_keys = set()
        self.str_keys = set()
        # Accept arguments in various forms like dicts, lists, or kwargs
        for key, value in dict(*args, **kwargs).items():
            self[key] = value

    def keys(self):
        """
        Return a dynamic KeysView reflecting int_keys.
        """
        return KeysView(self.int_keys)

    def values(self):
        """
        Return a dynamic ValuesView reflecting str_keys.
        """
        return ValuesView(self.str_keys)

    def items(self):
        """
        Iterate over int_keys and return (key, value) pairs.
        """
        for key in self.int_keys:
            yield key, self[key]

    def copy(self):
        """
        Return a shallow copy of the ResultErrCodesDict instance.
        """
        new_copy = ResultErrCodesDict()
        for key, value in self.items():
            new_copy[key] = value
        return new_copy

    def __iter__(self):
        """
        Iterate only over int_keys.
        """
        return iter(self.int_keys)

    def pop(self, *args, **kwargs):
        raise NotImplementedError("ResultErrCodesDict: Method not supported")

    def popitem(self, *args, **kwargs):
        raise NotImplementedError("ResultErrCodesDict: Method not supported")

    def reversed(self, *args, **kwargs):
        raise NotImplementedError("ResultErrCodesDict: Method not supported")

    def setdefault(self, *args, **kwargs):
        raise NotImplementedError("ResultErrCodesDict: Method not supported")

    def update(self, *args, **kwargs):
        raise NotImplementedError("ResultErrCodesDict: Method not supported")

    def __setitem__(self, key, value):
        """
        Add a new key-value pair while enforcing rules.

        Args:
            key (int or str): The key, which must be int or str.
            value (int or str): The corresponding value, which must be the opposite type of the key.
        """
        # Enforce key-type order: key is int, value is str
        if isinstance(key, str):
            key, value = value, key

        if not (isinstance(key, int) and isinstance(value, str)):
            raise ValueError("ResultErrCodesDict: Key must be int and value str, or key str and value int.")

        # Remove previous mappings if they exist
        if key in self:
            old_value = self[key]
            del self[key]
            del self[old_value]
            self._remove(key, old_value)
        if value in self:
            old_key = self[value]
            del self[value]
            del self[old_key]
            self._remove(old_key, value)

        # Add new mappings
        self.int_keys.add(key)
        self.str_keys.add(value)
        super().__setitem__(key, value)
        super().__setitem__(value, key)

    def __getitem__(self, key):
        """
        Retrieve the value associated with a key.
        - Return 2 for missing string keys.
        - Return "Undefined" for missing integer keys.

        Args:
            key (int or str): The key to look up.

        Returns:
            int or str: The corresponding value.

        Raises:
            KeyError: If the key is neither int nor str.
        """
        if key in self:
            return super().__getitem__(key)
        else:
            # Custom behavior for missing keys
            if isinstance(key, str):
                return 2
            elif isinstance(key, int):
                return "Undefined"
            else:
                raise KeyError("Key must be of type str or int.")

    def __delitem__(self, key):
        """
        Deletes both the key and its bidirectional counterpart (int ↔ str).
        """
        if key in self:
            value = self[key]
            self._remove(key, value)
            super().__delitem__(key)
            super().__delitem__(value)

    def _remove(self, key, value):
        """
        Safely remove key-value pair references from tracking sets.
        """
        if isinstance(key, str):
            key, value = value, key
        self.int_keys.remove(key)
        self.str_keys.remove(value)


# %% --------------------------------------------------------------------------


class ResultErr(Exception):
    """
    Custom exception class for error handling in the Result object.

    This class stores multiple error messages and corresponding error codes. It is used
    to encapsulate error states and operations related to error management.

    The object is assumed to be in `error status` when it contains one
    or more error messages (msg). An added error message that is "" is ignored.

    error = ResultErr(msg, code, error_code_group, add_traceback, max_messages)

    Args:
        msg  (str, optional):             Error message(s) to initialize with.
                                          Default is "", to disable error status.
        code (int, optional):             Error code(s) associated with the message(s).
                                          Recommended to a code from `ResultErr.error_codes()`.
                                          Default is 1 ("Unspecified").
        error_code_group (int, optional): Specify the error_codes group to use for code and message flags.
                                          Default is 1. Error codes are stored as a class variable,
                                          so this is useful if you need different sets of error codes within a program.
        add_traceback (bool, optional):   If True, then code traceback information is added to the message.
        max_messages (int, optional):     The maximum number of error messages to store.
                                          After this, all additional messages are ignored.
                                          Default is 20.


    Attributes:
        msg                  (list[str]): List of the error messages that have been added (does not have to match error_codes[code]).
        code                 (list[int]): List of the error codes    that have been added (does not have to match error_codes[msg]).
        traceback_info (list[list[str]]): List of lists that contains the traceback information for each error message
        size                       (int): Returns the number of error messages.
        error                     (bool): Returns true if in error status (ie, size > 0).

    Methods:
        raised(note=""):
            Raise a ResultErr exception if error messages exist
            and optionally add the note to the end of exception.

        expect(error_msg=""):
            Raise a ResultErr exception if error messages exist
            and optionally add the note to the end of exception.
            Returns an empty ResultErr.

        unwrap(*args, **kwargs):
            Returns the list of error messages stored.

        append(msg, code=1):
            Append a new error message and code.

        copy():
            Return a copy of the current ResultErr object.

        clear():
            Clear all stored error messages and codes.

        pop():
            Remove and return the last error message and code.
            If the size is reduced to zero, then changes to non-error status.

        has_msg(msg):
            Check if a specific message exists in the error messages.

        has_code(code):
            Check if a specific code exists in the error codes.

        error_code(code=None, error_code_group=None):
            Get the meaning of error codes for a specific code group.


    Example usage:
        >>>
        >>> from Result import ResultErr
        >>>
        >>> err = ResultErr()              # empty error
        >>> print(err.error)
        False
        >>> err.raised()                   # Nothing happens
        >>>
        >>> err.append("bad input")
        >>> err.raised()                   # program terminates
        ResultErr: bad input

        >>> err = ResultErr("bad input")   # Initialized with an error
        >>> print(err.error)
        True
        >>> err.raised()                   # program terminals
        ResultErr: bad input

        >>> err = ResultErr("bad input 1") # Initialized with an error
        >>> err.append("bad input 2")      # Second error message
        >>> print(err.error)
        True
        >>> err.raised()                   # program terminates
        ResultErr:
        bad input 1
        bad input 2
    """

    _g = 1
    _error_codes = {1: ResultErrCodesDict(_BASE_ERROR_CODES)}

    msg: list[str]
    code: list[int]
    traceback_info: list[list[str]]
    max_messages: int

    def __init__(self, msg="", code=1, error_code_group=1, add_traceback=True, max_messages=20, *, _levels=-2):
        """
        Initialize the ResultErr instance. If msg is "" then the object is
        initiated as a  `non-error state`, once a msg and code are added, then
        it is considered in `error state`.

        Args:
            msg  (str, list, or ResultErr, optional): Error message(s) to store.
            code (int, list[int], optional):          Error code(s) associated with the message(s).
                                                      Ignored if msg is a ResultErr object.
                                                      Default is 1 ("Unspecified").
            error_code_group (int, optional):         Identify the error_codes group to use for code and message flags.
                                                      Default is 1. Error codes are stored as a class variable,
                                                      so this is useful if you need different sets of error codes within a program.
        """
        super().__init__()
        self.max_messages = max_messages if max_messages > 1 else 1
        self.msg = []
        self.code = []
        self.traceback_info = []
        self._g = error_code_group if not isinstance(msg, ResultErr) else msg._g
        self._process_message_and_code(msg, code, _levels=_levels)

    def _process_message_and_code(self, msg, code, add_traceback=True, _levels=-2):
        """Helper to process messages and codes."""
        if add_traceback and msg != "":
            if _levels > -2:
                if _levels > -1:
                    raise RuntimeError("ResultErr._process_message_and_code has positive _levels")
                _levels = -2
            tb = traceback.format_stack(limit=5 - _levels)
            del tb[_levels:]  # drop calls to _process_message_and_code and one above it
            tb = [line for line in tb if not any(exclude in line for exclude in TRACEBACK_EXCLUDE_FILES)]
        else:
            tb = []
        if isinstance(msg, ResultErr):
            self.msg += msg.msg
            self.code += msg.code
            self.traceback_info += _deepcopy(msg.traceback_info)
        elif not isinstance(msg, str) and isinstance(msg, (Sequence, Iterable)):
            dim = len(self.msg)
            self.msg += list(map(str.strip, map(str, msg)))
            dim = len(self.msg) - dim
            self.code += list(code) if isinstance(code, Sequence) else [code] * dim
            self.traceback_info += [tb] * dim
            # self.traceback_info.extend([tb] * dim
        else:
            msg = str(msg).strip()
            if msg:
                self.msg.append(msg)
                self.code.append(code)
                self.traceback_info.append(tb)

        if len(self.msg) > self.max_messages:
            self.msg = self.msg[: self.max_messages]
            self.code = self.code[: self.max_messages]
            self.traceback_info = self.traceback_info[: self.max_messages]

    @property
    def size(self):
        """Return the number of stored error messages."""
        return len(self.msg)

    @property
    def error(self):
        """Check if the instance contains one or more error messages (if in an `error state`)."""
        return len(self.msg) > 0

    @staticmethod
    def register_code(code, description, error_code_group=None):
        """
        Register a specific code and description for the group number error_code_group.
        This code is stored at the class level so it effects all instances for a specific group.
        If error_code_group is None, then uses the group assigned to self.
        """
        g = ResultErr._g if error_code_group is None else error_code_group
        if g not in ResultErr._error_codes:
            ResultErr._error_codes[g] = ResultErrCodesDict(_BASE_ERROR_CODES)
        ec = ResultErr._error_codes[g]
        # if code in ec:
        #     raise TypeError(
        #         "ResultErr.register_code: code already defined. Codes are:\n[code] description\n"
        #         + "\n".join(f"[{code:>3s}] {msg}" for code, msg in self.error_codes.items())
        #         + "\n"
        #     )
        ec[code] = description

    def error_code(self, code=None, error_code_group=None):
        """
        Get an error code and description for a specific code group.

        Args:
            code  (int, str, optional):        If code is an int, then returns the corresponding description for it.
                                               If code is a  str, then returns the corresponding int code.
                                               If set to None, then returns a reflective dictionary with key:value pairs:
                                               `code:description` and `description:code`
            error_code_group (int, optional):  Specify error_codes group. If specified as None,
                                               then uses the code group associated with the instance.
                                               If group does not exist, then raises an error.
        """
        group = self._g if error_code_group is None else error_code_group
        error_group = self.__class__._error_codes[group]
        if code is None:
            return error_group
        return error_group[code]

    def error_code_description(self, description=None, error_code_group=None):
        g = self._g if error_code_group is None else error_code_group
        if description is None:
            return self.__class__._error_codes[g]
        return self.__class__._error_codes[g][description]

    def raised(self, note=""):
        """
        Raise a ResultErr exception if there are error messages.

        Args:
            note (str): Optional note to append to the error.
        """
        if len(self.msg) > 0:
            if note != "":
                self.append(str(note), add_traceback=False)
            raise self

    def expect(self, error_msg=""):
        self.raised(error_msg)
        return ResultErr()

    def unwrap(self, *args, **kwargs):
        """Returns the list of error messages stored."""
        return self.msg.copy()

    def append(self, msg, code=1, add_traceback=True, *, _levels=-2):
        """
        Append an error message and its code to the instance.

        Args:
            msg  (str, list, or ResultErr, optional): Error message(s) to append.
            code (int, list[int], optional):          Error code(s) associated with the message(s).
                                                      Ignored if msg is a ResultErr object.
                                                      Default is 1 ("Unspecified").
        """
        if len(self.msg) < self.max_messages:
            self._process_message_and_code(msg, code, add_traceback, _levels=_levels)

    def set_max_messages(self, max_messages):
        """Set the maximum number of error messages that are kept."""
        if max_messages < 1:
            self.max_messages = 1
        else:
            self.max_messages = max_messages

        if len(self.msg) > self.max_messages:
            self.msg = self.msg[: self.max_messages]
            self.code = self.code[: self.max_messages]

    def copy(self):
        """Return a copy of the ResultErr instance."""
        return ResultErr(self)

    def clear(self):
        """Clear all stored error messages and reset the instance to non-error status."""
        self.msg.clear()
        self.code.clear()

    def pop(self):
        """Remove and return the last stored error message and its code."""
        return self.code.pop(), self.msg.pop()

    def has_msg(self, msg):
        """Check if a specific message exists in the error messages."""
        return msg in self.msg

    def has_code(self, code):
        """Check if a specific code exists in the error codes."""
        return code in self.code

    @staticmethod
    def _str_code(code):
        return "{:>5}".format(f"[{code}]")

    def str(self, sep=" | ", as_repr=True, add_traceback=False):
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
                s = ("".join(self.traceback_info[0]) + f"\n{self._str_code(self.code[0])} {self.msg[0]}").strip()
                return f"ResultErr(\n{s}\n)" if as_repr else f"\n{s}\n"
            else:
                s = "".join(
                    [
                        "".join(tb) + f"\n{self._str_code(c)} {m}"
                        for c, m, tb in zip(self.code, self.msg, self.traceback_info)
                    ]
                )
                if len(self.traceback_info[0]) > 0:
                    s = "\n" + s
                return f"ResultErr({s}\n)" if as_repr else s

        if self.size == 1:
            s = f"{self._str_code(self.code[0])} {self.msg[0]}".strip()
            return f"ResultErr({s})" if as_repr else s

        if sep == "\n":
            s = "\n".join(f"{self._str_code(c)} {m}" for c, m in zip(self.code, self.msg))
            return f"ResultErr({s}\n)" if as_repr else s.strip()
        s = sep.join(f"{self._str_code(c)} {m}" for c, m in zip(self.code, self.msg)).strip()
        return f"ResultErr({s})" if as_repr else s

    def __str__(self):
        if self.size < 1:
            return ""
        return self.str("\n", False, True)

    def __repr__(self):
        if self.size == 0:
            return "ResultErr()"
        return f'ResultErr("{self.str().strip()}")'

    def __hash__(self) -> int:
        return hash(self.str())

    def __len__(self):
        return len(self.msg)

    def __iter__(self):
        return iter(zip(self.code, self.msg))

    def __copy__(self):
        return self.copy()

    def __deepcopy__(self, unused=None):
        return self.copy()

    def __contains__(self, code):
        return code in self.code

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
            other = other.code
        elif isinstance(other, Result):
            if other.is_Ok:
                return False
            other = other._Err.code
        return self.code == other


# %% --------------------------------------------------------------------------


class Result:
    """
    A Result class that mimics the behavior of Rust's Result enum.

    This class represents either a success case (`Ok`) with a value or an error case (`Err`).

    The Ok(value) variant supports common python math operations
    as long as both parts do not contain the Err variant and are compatible.
    For example, Ok(5) + 1 -> Ok(6)

    However, error states will propagate and add messages, such as
    Err(5)     -> Err("5") and
    Err(5) + 1 -> Err("5 | a += b with a as Err.")

    The Ok(value) variant supports attributes and methods associated with value.
    That is, `Ok(value).method()` is equivalent to `Ok(value.method())`
    and      `Ok(value).attrib`   is equivalent to `Ok(value.attrib)`.

    However, `Err(error).method()` and `Err(error).attrib` will return the Err
    with an appended message of:
                                f"VAR.{name} with VAR as Err variant"
    to it. Not `name` is replaced wit the attribute or method used.

    res = Result(value, success, error_msg, error_code, error_code_group)

    Args:
        value                (Any):       The value to wrap in the Result.Ok().
        success   (bool, optional):       True if success, False for error. Default is True.
        error_msg  (Any, optional):       If success is False:
                                             a) and error_msg="", set Err to str(value)
                                             b) otherwise,        set Err to error_msg.
        error_code (int, optional):       Error code associated with the error.
                                          Default is `1` for `Unspecified`.
                                          A list of common error codes and descriptions
                                          are in `ResultErr.error_codes`.
                                          The code description does not have to match the error_msg.
        error_code_group (int, optional): Specify the error_codes group to use for code and message flags.
                                          Default is 1. Error codes are stored as a class variable,
                                          so this is useful if you need different sets of error codes within a program.

    Constructors:
        res = Result.Ok(value)                     # Initialize as Ok variant.
        res = Result.Err(error_msg, error_code=1)  # Initialize as Err variant.
        res = Result.empty_init()                  # Initialize as empty object that is set
                                                   #    later with the Ok or Err attributes.
                                                   #    Raises an error for all other methods

    Attributes:
        is_Ok    (bool): True if the result is a  success.
        is_Err   (bool): True if the result is an error.

        Err_msg (list[str]):
            For the Ok(value)  variant, returns `[]`.
            For the Err(error) variant, returns list of error messages.
                Equivalent to `Err(error).unwrap().msg`

        Err_code (list[int]):
            For the Ok(value)  variant, returns `[]`.
            For the Err(error) variant, returns list of error codes.
                Equivalent to `Err(error).unwrap().code`

        Err_traceback (list[list[str]]):
            For the Ok(value)  variant, returns `[]`.
            For the Err(error) variant, returns list of traceback lines.
                Equivalent to `Err(error).unwrap().traceback_info`

    Methods:

        unwrap():
            Return the wrapped value in Ok(value) or error in Err(error).

        unwrap_or(default):
            Return the wrapped value in Ok(value) or return default.

        expect(error_msg=""):
            If  Ok variant, then returns value from value;
            If Err variant, then raise Err and optionally append error_msg to it.

        expect_Err(ok_msg=""):
            If  Ok variant, then raise ResultErr(ok_msg);
            If Err variant, then returns error in Err(error), which is type ResultErr.

        raised(error_msg="", exception=None):
            If  Ok variant, then returns Ok(value);
            If Err variant, then raise Err and optionally include `from exception`.
            Useful for check during chained operations

        is_Ok_and(ok_func, *args, **kwargs):
            True if Ok(value) variant and ok_func(value, *args, **kwargs) returns True,
            otherwise False.
              - If function call fails, then raises exception.

        apply(ok_func, *args, **kwargs):
            Maps a function to the Result to return a new Result.
            For the Ok(value)  variant, returns `Result.Ok(ok_func(value, *args, **kwargs))`.
            For the Err(error) variant, returns `Result.Err(error)`.
              - If ok_func fails, returns `Result.Err("Result.apply exception.)`.

        apply_or(default, ok_func, *args, **kwargs):
            Maps a function to the Result to return a new Result.
            For the Ok(value)  variant, returns `Result.Ok(ok_func(value, *args, **kwargs))`.
            For the Err(error) variant, returns `Result.Ok(default)`.
              - If ok_func fails, returns `Result(default)`.

        apply_or_else(err_func, ok_func, *args, **kwargs):
            Maps a function to the Result to return a new Result.
            For the Ok(value)  variant, returns `Result.Ok( ok_func(value, *args, **kwargs))`.
            For the Err(error) variant, returns `Result.Ok(err_func(error, *args, **kwargs))`.
              - If ok_func fails, returns `Result.Ok(err_func(value, *args, **kwargs))`
              - If ok_func and err_func fail, returns `Result.Err("Result.apply_or_else exception.)`.

        apply_Err(err_func, *args, **kwargs):
            Maps a function to the Result to return a new Result.
            For the Ok(value)  variant, returns `Result.Ok(ok_func(value, *args, **kwargs))`.
            For the Err(error) variant, returns `Result.Err(error)`.
              - If err_func fails, returns `Result.Err("Result.apply exception.)`.

        map(ok_func):
            Maps a function to the Result to return a new Result.
            For the Ok(value)  variant, returns `Result.Ok(ok_func(value))`.
            For the Err(error) variant, returns `Result.Err(error)`.
              - If function call fails, then raises exception.

        map_or(default, ok_func):
            Maps a function to the Result to return a new Result.
            For the Ok(value)  variant, returns `Result.Ok(ok_func(value))`.
            Otherwise                   returns `Result.Ok(Default)`.

        map_or_else(err_func, ok_func):
            Maps a function to the Result.Err, otherwise return Result.
            For the Ok(value)  variant, returns `Result.Ok(ok_func(value))`.
            For the Err(error) variant, returns `Result.Ok(err_func(error))`.

        map_Err(err_func):
            Maps a function to the Result.Err and another function to Result.Ok.
            For the Ok(value)  variant, returns `Ok(value).copy()`.
            For the Err(error) variant, returns `Result.Ok(err_func(error))`.
              - If function call fails, raises `Result.Err("Result.map_err exception.)`.

        iter():
            Returns an iterator of the value in Ok(value).
            For the Ok(value)  variant,
                if value is iterable: returns `iter(value)`
                else:                 returns `iter([value])`  -> Only one iteration
            For the Err(error) variant, returns `iter([])`.
            This setup always iterates at least once for Ok()
            and does not iterate for Err().
            Note, this process will consume an iterable if it does not store values.

        add_Err_msg(error_msg, error_code=1, add_traceback=True)):
            For the Ok(value)  variant, converts to Err(error_msg).
            For the Err(error) variant, adds an error message.

        update_result(value, create_new=False, deepcopy=False):
            Update Result to hold value. Either updates the current instance or creates a new one.
            Return the new Result. If value is not a ResultErr type, then returns Ok(value);
            otherwise, returns Err(value).

        copy(deepcopy=False):
            Create a copy of the Result.
            If deepcopy=True, the returns Result(deepcopy(value)).

        register_code(code, description, error_code_group=None):
            Register a specific code and description for the group number error_code_group.

        error_code(code=None, error_code_group=None):
            Get an error code and description for a specific code group.

    Example Usage:
        >>> result = Result.Ok("Success")
        >>> print(result)                  # Outputs: Ok("Success")
        >>> x = result.unwrap()            # x = "Success"
        >>> print(result.expect())         # Outputs: Success  -> same output with unwrap()

        >>> error = Result.Err("Failure")
        >>> print(error)                   # Outputs: Err("Failure")
        >>> x = error.unwrap()             # x = ResultErr("Failure")
        >>> error.expect()                 # Raises ResultErr("Failure")

        >>> x = Ok(5)
        >>> y = Ok(6)
        >>> print(x + y)                   # Outputs: Ok(11)
        >>> print(x / 0)                   # Outputs: Err("a /= b resulted in an Exception. | ZeroDivisionError: division by zero")
        >>> print(x.apply(lambda a: a**2)) # Outputs: Ok(25)
        >>> z = x / 0
        >>> print(z.apply(lambda a: a**2)) # Outputs: Err("a /= b resulted in an Exception. | ZeroDivisionError: division by zero | Result.apply applied in Error State.")

    """

    ResultErr = ResultErr
    _success: bool
    _Ok: object
    _Err: ResultErr
    _g: int

    def __init__(
        self,
        value,
        success=True,
        error_msg="",
        error_code=1,
        error_code_group=1,
        add_traceback=True,
        *,
        _empty_init=False,
        _levels=-3,
    ):
        self._g = error_code_group
        if success and isinstance(value, ResultErr):
            success = False
        if _empty_init:
            self._success = None
            self._Ok = ""
            self._Err = ""
        elif isinstance(value, Result):
            self._g = value._g
            self._success = value._success
            self._Ok = value if self._success else ""
            self._Err = value._Err.copy() if not self._success else ResultErr()
        elif success:
            self._success = True
            self._Ok = value
            self._Err = ResultErr()
        else:
            self._success = False
            self._Ok = ""
            if error_msg == "" and value == "":
                error_msg = EMPTY_ERROR_MSG
            self._Err = (
                ResultErr(error_msg, error_code, self._g, add_traceback, _levels=_levels)
                if error_msg != ""
                else ResultErr(value, error_code, self._g, add_traceback, _levels=_levels)
            )

    @classmethod
    def Ok(cls, value):
        return cls(value)

    @classmethod
    def Err(cls, error_msg, error_code=1, error_code_group=1):
        return cls(EMPTY_ERROR_MSG, False, error_msg, error_code, error_code_group, _levels=-4)

    @classmethod
    def empty_init(cls):
        return cls("", _empty_init=True)

    @property
    def is_Ok(self):
        self._empty_error()
        return self._success

    @property
    def is_Err(self):
        self._empty_error()
        return not self._success

    @property
    def Err_msg(self):
        if self._success:
            return []
        return self._Err.msg

    @property
    def Err_code(self):
        if self._success:
            return []
        return self._Err.code

    @property
    def Err_traceback(self):
        if self._success:
            return []
        return self._Err.traceback_info

    def unwrap(self):
        self._empty_error()
        return self._Ok if self._success else self._Err

    def unwrap_or(self, default):
        self._empty_error()
        return self._Ok if self._success else default

    def expect(self, error_msg="", error_code=5):  # 5 -> ResultErr.error_code("Expect")
        self._empty_error()
        if self._success:
            return self._Ok
        if error_msg != "":
            self.add_Err_msg(error_msg, error_code, add_traceback=False)
        raise self._Err

    def expect_Err(self, ok_msg="", error_code=5):  # 5 -> ResultErr.error_code("Expect")
        self._empty_error()
        if not self._success:
            return self._Err
        err = ResultErr("Result.expect_err() is Ok.", error_code, self._g, add_traceback=False)
        err.append(ok_msg, add_traceback=False)
        raise ResultErr(err)

    def raised(self, error_msg="", exception: Exception = None):
        self._empty_error()
        if not self._success:
            if error_msg != "":
                self.add_Err_msg(error_msg, 1, add_traceback=False)
            if exception is None:
                raise self._Err
            raise self._Err from exception
        return self

    def is_Ok_and(self, bool_ok_func, *args, **kwargs):
        self._empty_error()
        return self._success and bool_ok_func(self._Ok, *args, **kwargs)

    def apply(self, ok_func, *args, **kwargs):
        self._empty_error()
        if self._success:
            try:
                return Result(ok_func(self._Ok, *args, **kwargs), error_code_group=self._g)
            except Exception as e:
                err = Result.Err("Result.apply exception.", self.error_code("Apply"))
                err.add_Err_msg(f"{type(e).__name__}: {e}", self.error_code("Apply"), add_traceback=False)
                return err
        res = Result.Err(self._Err)
        res.add_Err_msg("Result.apply on Err.", self.error_code("Apply"))
        return res

    def apply_or(self, default, ok_func, *args, **kwargs):
        self._empty_error()
        if self._success:
            try:
                return Result(ok_func(self._Ok, *args, **kwargs), error_code_group=self._g)
            except Exception:
                pass
        return Result(default, error_code_group=self._g)

    def apply_or_else(self, err_func, ok_func, *args, **kwargs):
        self._empty_error()
        if self._success:
            try:
                return Result(ok_func(self._Ok, *args, **kwargs), error_code_group=self._g)
            except Exception:
                try:
                    return Result(err_func(self._Ok, *args, **kwargs), error_code_group=self._g)
                except Exception:
                    err = ResultErr("Result.apply_or_else exception.", self.error_code("Apply"), self._g, False)
        else:
            err = self._Err
        try:
            return Result(err_func(err, *args, **kwargs), error_code_group=self._g)
        except Exception as e:
            err = Result.Err("Result.apply_or_else exception.", self.error_code("Apply"))
            err.add_Err_msg(f"{type(e).__name__}: {e}", self.error_code("Apply"), add_traceback=False)
            return err

    def apply_Err(self, err_func, *args, **kwargs):
        self._empty_error()
        if self._success:
            return self.copy()
        try:
            return Result.Ok(err_func(self._Err, *args, **kwargs))
        except Exception as e:
            err = self.copy()
            err.add_Err_msg("Result.apply_err exception.", self.error_code("Map"), add_traceback=True)
            err.add_Err_msg(f"{type(e).__name__}: {e}", self.error_code("Map"), add_traceback=False)
            return err

    def map(self, ok_func):
        self._empty_error()
        if self._success:
            return Result(ok_func(self._Ok), error_code_group=self._g)
        res = Result.Err(self._Err)
        res.add_Err_msg("Result.map on Err.", self.error_code("Map"))
        return res

    def map_or(self, default, ok_func):
        self._empty_error()
        if not self._success:
            return Result(default, error_code_group=self._g)
        return Result(ok_func(self._Ok), error_code_group=self._g)

    def map_or_else(self, err_func, ok_func):
        self._empty_error()
        if self._success:
            return Result(ok_func(self._Ok), error_code_group=self._g)
        return Result(err_func(self._Err), error_code_group=self._g)

    def map_Err(self, err_func):
        self._empty_error()
        if self._success:
            return self.copy()
        return Result.Ok(err_func(self._Err), error_code_group=self._g)

    def iter(self):
        self._empty_error()
        if self._success:
            if isinstance(self._Ok, Iterable):
                return iter(self._Ok)
            return iter([self._Ok])
        return iter([])

    def add_Err_msg(self, error_msg, error_code=1, add_traceback=True):
        """Convert to error status and append error message and code."""
        if self._success:
            if error_msg == "" and self._Ok == "":
                error_msg = EMPTY_ERROR_MSG
            elif error_msg == "":
                error_msg = str(self._Ok)
            self._success = False
            self._Ok = ""
            self._Err = ResultErr("", 1, self._g)
        if error_msg != "":
            self._Err.append(error_msg, error_code, add_traceback, _levels=-4)

    def update_result(self, value, create_new=False, deepcopy=False):
        if create_new:
            if deepcopy:
                return Result(deepcopy(value), error_code_group=self._g)
            return Result(value, error_code_group=self._g)
        elif isinstance(value, ResultErr):
            self._success = False
            self._Ok = ""
            self._Err = value
        else:
            self._success = True
            self._Ok = value
            self._Err = ResultErr()
        return self

    def copy(self, deepcopy=False):
        if self._success is None:
            return Result.empty_init()
        if self._success and deepcopy:
            return Result(_deepcopy(self._Ok), error_code_group=self._g)
        return Result(self)

    def register_code(self, code, description, error_code_group=None):
        """
        Register a specific code and description for the group number error_code_group.
        This code is stored at the class level so it effects all instances for a specific group.
        If error_code_group is None, then uses the group assigned to self.
        """
        group = self._g if error_code_group is None else error_code_group
        ResultErr.register_code(code, description, group)

    def error_code(self, code=None, error_code_group=None):
        """
        Get an error code and description for a specific code group.

        Args:
            code  (int, str, optional):        If code is an int, then returns the corresponding description for it.
                                               If code is a  str, then returns the corresponding int code.
                                               If set to None, then returns a reflective dictionary with key:value pairs:
                                               `code:description` and `description:code`
            error_code_group (int, optional):  Specify error_codes group. If specified as None,
                                               then uses the code group associated with the instance.
                                               If group does not exist, then raises an error.
        """
        group = self._g if error_code_group is None else error_code_group
        ResErr = ResultErr("", 1, group)
        return ResErr.error_code(code)

    def error_code_description(self, description=None, error_code_group=None):
        group = self._g if error_code_group is None else error_code_group
        ResErr = ResultErr("", 1, group)
        return ResErr.error_code(description)

    def str(self):
        if self._success is None:
            return "Result(Empty)"
        elif self._success:
            if isinstance(self._Ok, str):
                return f'Ok("{self._Ok}")'
            return f"Ok({self._Ok})"
        else:
            return f'Err("{" | ".join(f"{m}" for m in self._Err.msg)}")'

    def _empty_error(self):
        if self._success is None:
            raise ResultErr(
                "Result object is empty!\nIt must be associated with an Ok(value) or Err(e) to use any methods.",
                add_traceback=False,
            )

    def _operator_overload_prep(self, b, operation: str):
        self._empty_error()

        if isinstance(b, ResultErr):
            b = Result(b, False)  # b is error so return error

        if isinstance(b, Result):
            b._empty_error()
            if not self._success and not b._success:
                err = Result(self._Err, False, add_traceback=False)
                err.add_Err_msg(
                    f"{operation} with a and b as Err.", self.error_code("Op_On_Error"), add_traceback=False
                )
                return True, err
            if not b._success:
                err = Result(b._Err, False, add_traceback=False)
                err.add_Err_msg(f"{operation} with b as Err.", self.error_code("Op_On_Error"), add_traceback=False)
                return True, err
            if self._success:
                return False, b._Ok  # no error

        if not self._success:
            err = Result(self._Err, False, add_traceback=False)
            err.add_Err_msg(f"{operation} with a as Err.", self.error_code("Op_On_Error"), add_traceback=False)
            return True, err
        return False, b  # no error

    def _operator_overload_error(self, e, operation: str, apply_to_self: bool):
        if apply_to_self:
            self.add_Err_msg(f"{operation} resulted in an Exception.", add_traceback=False)
            self.add_Err_msg(f"{type(e).__name__}: {e}", self.error_code("Math_Op"), add_traceback=False)
            return self
        err = Result(f"{operation} resulted in an Exception.", False, _levels=-5)
        err.add_Err_msg(f"{type(e).__name__}: {e}", self.error_code("Math_Op"), add_traceback=False)
        return err

    def __str__(self):
        # return f"Err(\"{' | '.join(f"[{c}] {m}" for c, m in zip(self._Err.code, self._Err.msg))}\")"
        return self.str()

    def __repr__(self):
        return self.str()

    def __bool__(self):
        if self._success:
            return bool(self._Ok)
        return False

    def __hash__(self) -> int:
        if self._success:
            return hash(self._Ok)  # Hash the value stored in ok
        return hash(self.str())

    def __contains__(self, value):
        if isinstance(value, Result):
            value = value.unpack()

        if not self._success:
            if isinstance(value, ResultErr):
                return self._Err == value
            return False

        if isinstance(value, ResultErr):
            return False

        value_seq = isinstance(value, (Sequence, Iterable))
        ok_seq = isinstance(self._Ok, (Sequence, Iterable))

        if not ok_seq or (ok_seq and value_seq):
            return value == self._Ok
        return value in self._Ok  # value is a scalar and Ok is a sequence

    def __getattr__(self, name):
        """
        Handles unknown attributes by forwarding them to the value in Ok(value).
        If Err(error) variant, then appends AttributeError error message.

        Parameters:
            name (str): The name of the missing attribute.

        Returns:
            The result of the attribute wrapped as a Result or modifies underlying value.
        """
        if name in EXCLUDE_ATTRIBUTES:
            self.add_Err_msg(
                f"{name} is an excluded attribute/method. Did you forget () on a method or put () on an attrib. If Ok(x.{name}) is what you want, then do Ok(x).expect().{name}",
                self.error_code("Attribute"),
            )
            return self

        if self.is_Err:
            self.add_Err_msg(f"VAR.{name} with VAR as Err variant", self.error_code("Attribute_While_Error_State"))
            return self
        try:
            # Forward any unknown attribute to value in Ok(value) component
            attr = getattr(self._Ok, name)
            if attr is None:
                return
            if callable(attr):

                def method(*args, **kwargs):
                    try:
                        res = attr(*args, **kwargs)
                        return Result(res) if res is not None else None
                    except Exception as e:
                        return Result.Err(f"VAR.{name}() raised {e}", self.error_code("Method"))

                return method
            if isinstance(attr, Result):
                return attr
            return Result(attr)
        except AttributeError:
            self.add_Err_msg(f"VAR.{name} raised an AttributeError", self.error_code("Attribute"))
            return self

    def __iter__(self):
        return self.iter()

    def __iadd__(self, other):  # addition with assignment, a += b
        op = "a += b"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            self.add_Err_msg(other)
            return self
        try:
            self._Ok += other
            return self
        except Exception as e:
            return self._operator_overload_error(e, op, True)

    def __add__(self, other):  # add operation, a + b
        op = "a + b"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            return other
        try:
            return Result(self._Ok + other)
        except Exception as e:
            return self._operator_overload_error(e, op, False)

    def __radd__(self, other):  # reflective add operation, b + a
        op = "b + a"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            return other
        try:
            return Result(other + self._Ok)
        except Exception as e:
            return self._operator_overload_error(e, op, False)

    def __isub__(self, other):  # subtraction with assignment, a -= b
        op = "a -= b"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            self.add_Err_msg(other)
            return self
        try:
            self._Ok -= other
            return self
        except Exception as e:
            return self._operator_overload_error(e, op, True)

    def __sub__(self, other):  # subtraction operation, a - b
        op = "a - b"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            return other
        try:
            return Result(self._Ok - other)
        except Exception as e:
            return self._operator_overload_error(e, op, False)

    def __rsub__(self, other):  # reflective subtraction operation, b - a
        op = "b - a"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            return other
        try:
            return Result(other - self._Ok)
        except Exception as e:
            return self._operator_overload_error(e, op, False)

    def __imul__(self, other):  # multiplication with assignment, a *= b
        op = "a *= b"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            self.add_Err_msg(other)
            return self
        try:
            self._Ok *= other
            return self
        except Exception as e:
            return self._operator_overload_error(e, op, True)

    def __mul__(self, other):  # multiplication operation, a * b
        op = "a * b"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            return other
        try:
            return Result(self._Ok * other)
        except Exception as e:
            return self._operator_overload_error(e, op, False)

    def __rmul__(self, other):  # reflective multiplication operation, b * a
        op = "b * a"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            return other
        try:
            return Result(other * self._Ok)
        except Exception as e:
            return self._operator_overload_error(e, op, False)

    def __itruediv__(self, other):  # division with assignment, a /= b
        op = "a /= b"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            self.add_Err_msg(other)
            return self
        try:
            self._Ok /= other
            return self
        except Exception as e:
            return self._operator_overload_error(e, op, True)

    def __truediv__(self, other):  # division operation, a / b
        op = "a / b"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            return other
        try:
            return Result(self._Ok / other)
        except Exception as e:
            return self._operator_overload_error(e, op, False)

    def __rtruediv__(self, other):  # reflective division operation, b / a
        op = "b / a"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            return other
        try:
            return Result(other / self._Ok)
        except Exception as e:
            return self._operator_overload_error(e, op, False)

    def __ifloordiv__(self, other):  # floor division with assignment, a //= b
        op = "a //= b"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            self.add_Err_msg(other)
            return self
        try:
            self._Ok //= other
            return self
        except Exception as e:
            return self._operator_overload_error(e, op, True)

    def __floordiv__(self, other):  # floor division operation, a // b
        op = "a // b"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            return other
        try:
            return Result(self._Ok // other)
        except Exception as e:
            return self._operator_overload_error(e, op, False)

    def __rfloordiv__(self, other):  # reflective floor division operation, b // a
        op = "b // a"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            return other
        try:
            return Result(other // self._Ok)
        except Exception as e:
            return self._operator_overload_error(e, op, False)

    def __imod__(self, other):  # modulus with assignment, a %= b
        op = "a %= b"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            self.add_Err_msg(other)
            return self
        try:
            self._Ok %= other
            return self
        except Exception as e:
            return self._operator_overload_error(e, op, True)

    def __mod__(self, other):  # modulus operation, a % b
        op = "a % b"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            return other
        try:
            return Result(self._Ok % other)
        except Exception as e:
            return self._operator_overload_error(e, op, False)

    def __rmod__(self, other):  # reflective modulus operation, b % a
        op = "b % a"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            return other
        try:
            return Result(other % self._Ok)
        except Exception as e:
            return self._operator_overload_error(e, op, False)

    def __ipow__(self, other):  # exponentiation with assignment, a **= b
        op = "a **= b"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            self.add_Err_msg(other)
            return self
        try:
            self._Ok **= other
            return self
        except Exception as e:
            return self._operator_overload_error(e, op, True)

    def __pow__(self, other):  # exponentiation operation, a ** b
        op = "a ** b"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            return other
        try:
            return Result(self._Ok**other)
        except Exception as e:
            return self._operator_overload_error(e, op, False)

    def __rpow__(self, other):  # reflective exponentiation operation, b ** a
        op = "b ** a"
        errored, other = self._operator_overload_prep(other, op)
        if errored:
            return other
        try:
            return Result(other**self._Ok)
        except Exception as e:
            return self._operator_overload_error(e, op, False)

    def __int__(self):  # To get called by built-in int() method to convert a type to an int.
        self._empty_error()
        if self._success:
            try:
                return Result(int(self._Ok))
            except Exception as e:
                self.add_Err_msg("Result(int(a)) resulted in an Exception.")
                self.add_Err_msg(f"{type(e).__name__}: {e}", self.error_code("Int_Op"), add_traceback=False)
        else:
            self.add_Err_msg("int(Result(a)) with a as Err.", self.error_code("Op_On_Error"))
        return self

    def __float__(self):  # To get called by built-in float() method to convert a type to float.
        self._empty_error()
        if self._success:
            try:
                return Result(float(self._Ok))
            except Exception as e:
                self.add_Err_msg("Result(float(a)) resulted in an Exception.")
                self.add_Err_msg(f"{type(e).__name__}: {e}", self.error_code("Float_Op"), add_traceback=False)
        else:
            self.add_Err_msg("float(Result(a)) with a as Err.", self.error_code("Op_On_Error"))
        return self

    def __lt__(self, other):  # compare self < other.
        # Assumes Err() < Ok() and Err(a) == Err(b)
        self._empty_error()
        if isinstance(other, ResultErr):
            other = Result(other, False)
        elif not isinstance(other, Result):
            other = Result(other, True)

        if self.is_Ok and other.is_Ok:
            return self._Ok < other._Ok
        return other.is_Ok

    def __le__(self, other):  # compare self <= other.
        # Assumes Err() < Ok() and Err(a) == Err(b)
        self._empty_error()
        if isinstance(other, ResultErr):
            other = Result(other, False)
        elif not isinstance(other, Result):
            other = Result(other, True)

        if self.is_Ok and other.is_Ok:
            return self._Ok <= other._Ok
        return other.is_Ok or (self.is_Err and other.is_Err)

    def __gt__(self, other):  # compare self > other.
        # Assumes Err() < Ok() and Err(a) == Err(b)
        self._empty_error()
        if isinstance(other, ResultErr):
            other = Result(other, False)
        elif not isinstance(other, Result):
            other = Result(other, True)

        if self.is_Ok and other.is_Ok:
            return self._Ok > other._Ok
        return self.is_Ok

    def __ge__(self, other):  # compare self >= other.
        # Assumes Err() < Ok() and Err(a) == Err(b)
        self._empty_error()
        if isinstance(other, ResultErr):
            other = Result(other, False)
        elif not isinstance(other, Result):
            other = Result(other, True)

        if self.is_Ok and other.is_Ok:
            return self._Ok >= other._Ok
        return self.is_Ok or (self.is_Err and other.is_Err)

    def __eq__(self, other):  # compare self == other.
        # Assumes Ok(a) == Ok(b) if a == b, but Err(a) == Err(b) for any a or b.
        self._empty_error()
        if isinstance(other, ResultErr):
            other = Result(other, False)
        elif not isinstance(other, Result):
            other = Result(other, True)

        if self.is_Ok and other.is_Ok:
            return self._Ok == other._Ok
        return self.is_Err and other.is_Err

    def __ne__(self, other):  # compare self != other.
        # Assumes Ok(a) == Ok(b) if a == b, but Err(a) == Err(b) for any a or b.
        self._empty_error()
        if isinstance(other, ResultErr):
            other = Result(other, False)
        elif not isinstance(other, Result):
            other = Result(other, True)

        if self.is_Ok and other.is_Ok:
            return self._Ok != other._Ok
        return self.is_Ok or other.is_Ok


class Ok:
    """
    Constructor class that returns a Result.Ok(value).

    Example:
        >>> result = Ok(42)
        >>> print(result.unwrap())  # Outputs: 42
    """

    def __new__(self, value):
        return Result(value)


class Err:
    """
    Constructor class that returns a Result.Err(error).

    Example:
        >>> error = Err("Error message")
        >>> print(error.unwrap())         # Outputs: ResultErr("Error message")
    """

    def __new__(self, error_msg, error_code=1, error_code_group=1, add_traceback=True):
        return Result("UnknownError", False, error_msg, error_code, error_code_group, add_traceback, _levels=-4)


# %% --------------------------------------------------------------------------


if __name__ == "__main__":
    # Demonstration of basic functionality
    # Methods for creating an Ok variant (all three produce the same result):
    success_result = Result("Operation was successful")
    success_result = Result.Ok("Operation was successful")
    success_result = Ok("Operation was successful")

    # Methods for creating an Err variant (all three produce the same result):
    error_result = Result(None, False, "Something went wrong")  # long method of init
    error_result = Result.Err("Something went wrong")
    error_result = Err("Operation failed")

    print("Success Result:", success_result)
    print("Error Result:", error_result.unwrap())
    error_result.expect()

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

    assert err + 5 == ["bad input", "a + b with a as Err."]
    assert err + 5 == Err(["bad input", "a + b with a as Err."])

    print("program completed successfully")
