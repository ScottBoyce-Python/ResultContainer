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
- **Utility Methods**: Implements helper methods for error propagation, transformation, and querying (e.g., `.map()`, `.and_then()`, `.unwrap_or()`, `.expect()`) for concise and readable handling of success and error cases. 

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
import numpy as np
from ResultContainer import ResultContainer

# Create an empty deque that stores up to 10 float64 numbers
d = ResultContainer(maxsize=10, dtype=np.float64)

# Create a deque with 5 int64 zeros (the deque is initialized to maxsize with 0).
d = ResultContainer(maxsize=5, fill=0, dtype=np.int64)

# Create a deque from an array. Its maxsize is automatically set to 5.
d = ResultContainer.array([1, 2, 3, 4, 5])

# Create a deque from an array. Its maxsize is set to 5.
d = ResultContainer.array([1, 2, 3], 5)

```

### Adding to Right of The Deque

```python
d = ResultContainer(maxsize=5, dtype=np.int64)

# Put a value to the right on the deque
d.put(5)
d.put(7)
d.put(9)
print(d)              # Output: ResultContainer([5, 7, 9])
d.put(11)
d.put(13)
print(d)              # Output: ResultContainer([5, 7, 9, 11, 13])
d.put(15)  # 5 is dropped
print(d)              # Output: ResultContainer([7, 9, 11, 13, 15])

d.putter([1, 2, 3])
print(d)              # Output: ResultContainer([13, 15, 1, 2, 3])

d.putter([-1, -2, -3, -4, -5, -6, -7])
print(d)              # Output: ResultContainer([-3, -4, -5, -6, -7])

d.putter([1, 2, 3, 4, 5])
print(d)              # Output: ResultContainer([1, 2, 3, 4, 5])
```

### Adding to Left of The Deque

```python
d = ResultContainer(maxsize=5, dtype=np.int64)

# Put a value to the right on the deque
d.putleft(5)
d.putleft(7)
d.putleft(9)
print(d)              # Output: ResultContainer([9, 7, 5])
d.putleft(11)
d.putleft(13)
print(d)              # Output: ResultContainer([13, 11, 9, 7, 5])
d.putleft(15)  # 5 is dropped
print(d)              # Output: ResultContainer([15, 13, 11, 9, 7])

d.putterleft([1, 2, 3])
print(d)              # Output: ResultContainer([3, 2, 1, 15, 13])

d.putterleft([-1, -2, -3, -4, -5, -6, -7])
print(d)              # Output: ResultContainer([-7, -6, -5, -4, -3])

d.putter([1, 2, 3, 4, 5])
print(d)              # Output: ResultContainer([5, 4, 3, 2, 1])
```

### Removing Elements

```python
d = ResultContainer.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

# Remove and return the last element
print(d)              # Output: ResultContainer([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
rightmost_value = d.pop() 
print(d)              # Output: ResultContainer([1, 2, 3, 4, 5, 6, 7, 8, 9])
print(rightmost_value)# Output: 10

# Remove and return the first element
leftmost_value = d.popleft() 
print(d)              # Output: ResultContainer([2, 3, 4, 5, 6, 7, 8, 9])
print(leftmost_value) # Output: 1

# Remove and return the third element
third_value = d.drop(2) 
print(d)              # Output: ResultContainer([2, 3, 5, 6, 7, 8, 9])
print(third_value)# Output: 4

# If the number 8 and 1 are found, remove the first appearance
d.remove(8)
print(d)              # Output: ResultContainer([2, 3, 5, 6, 7, 9])
d.remove(1)           # Nothing happens
print(d)              # Output: ResultContainer([2, 3, 5, 6, 7, 9])
```

### Slicing

```python
d = ResultContainer.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], maxsize=10)

# Slice behaves like NumPy arrays, but be careful with indexes
print( d[1:4] )    # Output: [1, 2, 3]

d[1:3] = [-1, -2]     # Output: [2, 3, 4]
print(d)              # Output: ResultContainer([0, -1, -2, 3, 4, 5, 6, 7, 8, 9])

# Note that values move once maxsize is exceeded
print( d[2] )         # Output: -2
d.put(10)
print(d)              # Output: ResultContainer([-1, -2, 3, 4, 5, 6, 7, 8, 9, 10])
print( d[2] )         # Output: 3
d.put(11)
print(d)              # Output: ResultContainer([-2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
print( d[2] )         # Output: 4
d.putleft(99)
print(d)              # Output: ResultContainer([99, -2, 3, 4, 5, 6, 7, 8, 9, 10])
print( d[2] )         # Output: 3

#Be careful about the size
d = ResultContainer(maxsize=5)
d.put(5)
d.put(4)
d.put(3)
print(d)              # Output: ResultContainer([5, 4, 3])
print( d[3] )         # Raises index error!!!
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
