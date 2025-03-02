# Utils Directory

This directory contains utility modules that provide various helper functions and classes used throughout the application.

## Logger

The `logger` module provides a logging utility to record application events and errors. It is used to generate log files which are stored in the `logs` directory.

## Usage

To use the logger utility, import the `Logger` class from the `logger` module.

### Example

```python
from nerdgraph.utils.logger import Logger

# Initialize the logger
logger = Logger('path/to/your/logfile.log')

# Log an info message
logger.info('This is an info message')

# Log an error message
logger.error('This is an error message')