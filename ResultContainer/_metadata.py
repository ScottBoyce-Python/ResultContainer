"""
Metadata associated with ResultContainer.py
"""

__version__ = "0.2.0"
__author__ = "Scott E. Boyce"
__credits__ = "Scott E. Boyce"
__maintainer__ = "Scott E. Boyce"
__email__ = "boyce@engineer.com"
__license__ = "MIT"
__status__ = "Development"  # set to "Prototype", "Development", "Production"
__url__ = "https://github.com/ScottBoyce-Python/ResultContainer"
__description__ = "ResultContainer is a Result class that mimics the behavior of Rust's Result enum that wraps values in an Ok(value) and Err(e) variant. Math operations, attributes, and methods are passed to value in Ok(value). If an operation with the Ok(value) variant results in an error, then it is converted to an Err(e) variant. Err(e) contains one or more error messages and math operations, attributes, and methods result in appending the respective errors."
__copyright__ = "Copyright (c) 2024 Scott E. Boyce"
