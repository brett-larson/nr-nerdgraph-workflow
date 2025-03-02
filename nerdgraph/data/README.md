# Data Directory

This directory is intended to hold various data handlers, including CSV handlers. The specific contents of this directory will vary based on the data being parsed.

## CSV Files

CSV files, whether for reading or writing, will reside in the `csv_files` directory. The modules in the `csv_files` directory provide functionality to handle CSV file operations, including reading data from CSV files and writing data to CSV files.

## Usage

To use the CSV file utilities, import the necessary functions or classes from the `csv_files` directory.

### Example

```python
from nerdgraph.data.csv_files import csv_reader, csv_writer

# Reading from a CSV file
data = csv_reader.read_csv('path/to/your/file.csv')

# Writing to a CSV file
csv_writer.write_csv('path/to/your/output.csv', data)