## Basic Introduction

pandas is an open-source Python library for data manipulation and analysis.
It provides powerful data structures like:
- Series → a one-dimensional labeled array (like a column).
- DataFrame → a two-dimensional labeled table (like an Excel sheet or SQL table).

pandas makes it easy to:
- Load, clean, transform, and analyze structured data (like CSV, Excel, SQL, JSON, etc.).
- Perform operations such as filtering, grouping, aggregating, merging, joining, reshaping, and time-series handling — all efficiently.


When and Why pandas was Created:

Created by: Wes McKinney

Year: Around 2008 (while he was at AQR Capital, a quantitative investment firm)

Why it was created:
- Wes McKinney needed a fast and flexible tool to analyze financial and time-series data in Python.


At that time:
- Python had numerical libraries like NumPy, but they lacked data labels and table-like structures.
- R had powerful data analysis tools (like data.frames).
- So, pandas was built to fill that gap — combining the performance of NumPy with the usability of R.

Features:

| Feature                         | Description                                                            |
| ------------------------------- | ---------------------------------------------------------------------- |
| 🧱 **Structured Data Handling** | Works naturally with tabular (row-column) data.                        |
| ⚡ **Performance**               | Built on top of **NumPy**, so operations are vectorized and efficient. |
| 🧹 **Data Cleaning**            | Handle missing values, duplicates, and inconsistent data easily.       |
| 🔍 **Filtering & Querying**     | Powerful syntax for selecting and filtering data.                      |
| 📊 **Grouping & Aggregation**   | Supports SQL-like group-by operations for summarization.               |
| 🔄 **Integration**              | Reads/writes from CSV, Excel, SQL, JSON, Parquet, etc.                 |
| 📈 **Time Series Support**      | Built-in support for time indexing, resampling, rolling windows, etc.  |
| 🧠 **Analysis Ready**           | Works well with NumPy, Matplotlib, and scikit-learn for ML workflows.  |



pandas is built primarily on two core data structures:
1. Series
2. DataFrame


### Series
A Series is a one-dimensional labeled array — similar to a single column in Excel or a SQL table.

```python
import pandas as pd

s = pd.Series([10, 20, 30, 40], index=['a', 'b', 'c', 'd'])
print(s)

```

output:
```css
a    10
b    20
c    30
d    40
dtype: int64

```

Key points:
- Has both values and an index (labels).
- Supports vectorized operations:
    ```python
    s * 2
    ```
    gives [20, 40, 60, 80].
- Can hold any data type — int, float, string, even Python objects.


### DataFrame
A DataFrame is a two-dimensional labeled table, like a spreadsheet or a SQL table.
It’s essentially a collection of Series objects sharing the same index.

```python
data = {
    "Name": ["Alice", "Bob", "Charlie"],
    "Age": [25, 30, 35],
    "City": ["Delhi", "Mumbai", "Bangalore"]
}
df = pd.DataFrame(data)
print(df)

```
Output:
```markdown
      Name  Age       City
0    Alice   25      Delhi
1      Bob   30     Mumbai
2  Charlie   35  Bangalore

```
Each column (Name, Age, City) is a Series.

Operations examples:
```python
df["Age"].mean()        # Average age → 30.0
df[df["Age"] > 28]      # Filter rows where age > 28
df.sort_values("Age")   # Sort by age
```

## What is time series support and how does in work in Pandas?

## What is Indexing in Pandas?

In pandas, indexing refers to how rows and columns in a DataFrame or Series are identified and accessed.

You can think of it like this:

- In Excel → each row has a row number, and each column has a name (A, B, C...).
- In pandas → the index serves as the row label(s), and columns have their own labels.

An index in pandas is an object (pd.Index) that:

- Uniquely identifies rows (or columns).
- Helps with data alignment, selection, and joining.
- Can be customized, not just numbers (can be dates, strings, etc.).

example:
```python
import pandas as pd

data = {'Name': ['Alice', 'Bob', 'Charlie'], 'Age': [25, 30, 35]}
df = pd.DataFrame(data, index=['a', 'b', 'c'])

print(df)

```

output:
```css
   Name     Age
a  Alice    25
b  Bob      30
c  Charlie  35

```
Here, 'a', 'b', 'c' are custom indexes.


Why indexing is helpful:
- Faster lookups: You can quickly access rows using .loc[] or .iloc[].
- Label-based access: You can use meaningful labels instead of just numbers.
- Data alignment: When merging or adding DataFrames, pandas automatically aligns data based on the index.
- Handling time series: In time series data, the index can be a DatetimeIndex for efficient time-based slicing and resampling.


Types of indexes:

| Type              | Example                | Use Case                            |
| ----------------- | ---------------------- | ----------------------------------- |
| **Default Index** | 0, 1, 2, ...           | When you don’t specify any index    |
| **Custom Index**  | ‘a’, ‘b’, ‘c’          | When you want meaningful row labels |
| **MultiIndex**    | (Year, Month)          | When dealing with hierarchical data |
| **DatetimeIndex** | 2024-01-01, 2024-01-02 | For time series data                |


Indexing Methods:

| Method             | Description                                       |
| ------------------ | ------------------------------------------------- |
| `df.loc[]`         | Label-based indexing (using names or dates)       |
| `df.iloc[]`        | Position-based indexing (using integer positions) |
| `df.set_index()`   | Set a column as the index                         |
| `df.reset_index()` | Convert the index back to a column                |


### What is data alignment in Pandas?
In pandas, alignment of data refers to how rows and columns with the same labels are automatically matched when performing operations between Series or DataFrames.
This is one of pandas’ most powerful features — you don’t have to manually match rows; pandas does it for you using the index and column labels.

- When you perform arithmetic operations (like +, -, *, /) between two Series or DataFrames, pandas aligns them by their labels.
- If a label exists in one object but not the other, the result will have NaN for that label (unless you provide a fill_value).

🔹 Example 1: Series Alignment
```python
import pandas as pd

s1 = pd.Series([10, 20, 30], index=['a', 'b', 'c'])
s2 = pd.Series([1, 2, 3], index=['b', 'c', 'd'])

result = s1 + s2
print(result)
```

output:
```css
a     NaN   # 'a' exists only in s1
b    22.0   # 20 + 2
c    33.0   # 30 + 3
d     NaN   # 'd' exists only in s2
dtype: float64

```
✅ pandas automatically matched 'b' and 'c' by their labels.
✅ Labels that didn’t exist in both Series ('a' and 'd') became NaN.



🔹 Example 2: DataFrame Alignment
```python
df1 = pd.DataFrame({'A': [1, 2], 'B': [3, 4]}, index=['x', 'y'])
df2 = pd.DataFrame({'B': [10, 20], 'C': [30, 40]}, index=['y', 'z'])

result = df1 + df2
print(result)

```

output:
```pgsql
      A     B     C
x   NaN   NaN   NaN  # 'x' not in df2
y   NaN  14.0   NaN  # 'B' aligned, other columns NaN
z   NaN   NaN   NaN  # 'z' not in df1

```

🔹 Why Alignment Matters:
- Prevents errors when combining datasets with mismatched indexes.
- Automatic handling of missing data through NaN or fill_value.
- Simplifies operations — you don’t have to manually reorder or match rows/columns.
- Essential for time series — ensures that dates are aligned before adding, subtracting, or comparing data.

## What is ReIndexing in Pandas?
Reindexing in pandas means changing the index (row labels or column labels) of a DataFrame or Series to a new set of labels.

You can think of it as “aligning your data to a new index” — pandas will rearrange, add, or remove rows/columns as needed to match the new labels.

Reindexing is useful when:
- You want to change the order of rows or columns.
- You want to add new labels (and possibly fill missing data).
- You want to align data from different DataFrames.
- You want to ensure a consistent structure before performing joins or merges.

🔹 Example 1: Changing Row Order
```python
import pandas as pd

data = {'Name': ['Alice', 'Bob', 'Charlie'], 'Age': [25, 30, 35]}
df = pd.DataFrame(data, index=['a', 'b', 'c'])

# Reindex to a new order
new_df = df.reindex(['c', 'a', 'b'])
print(new_df)

```

output:
```css
      Name   Age
c  Charlie   35
a    Alice   25
b      Bob   30

```

🔹 Example 2: Adding New Labels

```python
new_df = df.reindex(['a', 'b', 'c', 'd'])
print(new_df)

```
output:
```css
      Name   Age
a    Alice   25
b      Bob   30
c  Charlie   35
d      NaN   NaN

```
Here, 'd' did not exist earlier, so pandas fills it with NaN (missing values).

🔹 Example 3: Reindexing Columns
```python
new_df = df.reindex(columns=['Age', 'Name', 'City'])
print(new_df)

```

output:
```css
    Age   Name  City
a   25   Alice  NaN
b   30     Bob  NaN
c   35 Charlie  NaN

```
You can reorder columns or add missing ones.


🔹 Handling Missing Data with fill_value
You can specify what value to fill for new/missing labels:
```python
new_df = df.reindex(['a', 'b', 'c', 'd'], fill_value=0)
```
This will fill missing rows with 0 instead of NaN.

### why reindexing is useful?
Reindexing is useful because it gives you control over the structure and alignment of your data — especially when combining, comparing, or preparing data for analysis.


## What is Multi-indexing in Pandas?

In pandas, MultiIndexing (or hierarchical indexing) is a way to have multiple levels of indexes on rows (and/or columns) of a DataFrame or Series.

It allows you to organize and access data in more complex structures — similar to having a table within a table — which is very useful for grouped or hierarchical data.


🔹 Why MultiIndexing is Useful

- Handles multi-level categorical data (e.g., Country → City → Store).
- Makes grouped data easy to slice and analyze without flattening.
- Enables pivot-like operations while keeping the original hierarchical structure.

You can create a MultiIndex either directly or from a DataFrame.

Example 1: MultiIndex from tuples

```python
import pandas as pd

# Define tuples for hierarchical index
index = pd.MultiIndex.from_tuples(
    [('India', 'Delhi'), ('India', 'Mumbai'), ('USA', 'New York'), ('USA', 'Chicago')],
    names=['Country', 'City']
)

# Create DataFrame
data = {'Population': [30, 20, 8, 3]}
df = pd.DataFrame(data, index=index)
print(df)

```

output:
```markdown
                 Population
Country City              
India   Delhi            30
        Mumbai           20
USA     New York          8
        Chicago           3

```

Here:
- Level 0: Country
- Level 1: City


Example 2: MultiIndex from DataFrame columns

```python
data = {
    'Country': ['India', 'India', 'USA', 'USA'],
    'City': ['Delhi', 'Mumbai', 'New York', 'Chicago'],
    'Population': [30, 20, 8, 3]
}

df = pd.DataFrame(data)
df = df.set_index(['Country', 'City']) # in this case, these columns will be removed from columns and will be considered only as indexes
print(df)
```

output:
```markdown
                 Population
Country City              
India   Delhi            30
        Mumbai           20
USA     New York          8
        Chicago           3

```


🔹 Accessing Data in MultiIndex

1. Select by first level

    ```python
    df.loc['India']

    # output

        Population
    City            
    Delhi         30
    Mumbai        20
    ```



2. Select by both levels

    ```python
    df.loc[('USA', 'Chicago')]


    # output

    Population    3
    Name: (USA, Chicago), dtype: int64

    ```

🔹 Advantages of MultiIndex
- Hierarchical data representation — no need to flatten the data.
- Flexible slicing — select entire groups or individual subgroups easily.
- Efficient aggregation — combine with .groupby(level=...) to summarize data.
- Time series & panel data — store multiple dimensions like Date → City → Store in one DataFrame.


## What is the difference between loc and iloc in Pandas?

1. loc — Label-based Indexing

- Uses labels (names) of rows and columns.
- Can select single labels, lists of labels, slices with labels, or boolean masks.
- Includes the end label in slices.


example:

```python
import pandas as pd

data = {'Name': ['Alice', 'Bob', 'Charlie'], 'Age': [25, 30, 35]}
df = pd.DataFrame(data, index=['a', 'b', 'c'])

# Select row by label
print(df.loc['b'])

```

output:
```pgsql
Name    Bob
Age      30
Name: b, dtype: object

```

Slicing with labels:
```python
df.loc['a':'b']  # includes 'b'
```


Select specific rows and columns:
```python

df.loc['a':'c', ['Name']]

```


2. iloc — Position-based Indexing

- Uses integer positions (like Python lists).
- Rows and columns are selected by integer indices.
- End of slices is exclusive, like standard Python slicing.

```python
# Select second row (index 1)
print(df.iloc[1])
```

output:

```pgsql
Name    Bob
Age      30
Name: b, dtype: object
```


Slicing by position:
```python
df.iloc[0:2]  # rows at positions 0 and 1 (excluding 2)
```


Select specific rows and columns by position:
```python
df.iloc[0:2, 0]  # first column, first two rows

```

## Memory consumption by Pandas
In pandas, memory consumption can become a concern when working with large datasets because a DataFrame stores data in RAM, and every column is a separate NumPy array under the hood. Understanding how pandas consumes memory helps write efficient and scalable code.

### How pandas Stores Data

- Each column in a DataFrame is a NumPy array.
- Each data type (dtype) has a fixed memory size:
    - int64 → 8 bytes per element
    - float64 → 8 bytes per element
    - bool → 1 byte per element
    - object (strings) → 8 bytes for the pointer + actual string in memory

- Object dtype is the most memory-heavy, especially for text data, because each element is a pointer to a Python string object.


### Factors affecting memory
1. Data types
    - Using default int64 or float64 may be unnecessary for small numbers.
    - Use smaller types when possible (int8, float32).

2. Object columns (strings)
    - Take more memory than numeric columns.
    - Consider categorical type for repeated strings:
    ```python
    df['str_col'] = df['str_col'].astype('category')

    ```
3. NaN values
    - float64 columns with NaN are still 8 bytes per element.
    - Sparse data can be stored efficiently with pd.SparseDtype.

4. Number of rows and columns
    - Memory grows linearly with both.
    - Wide DataFrames (many columns) can consume a lot of memory.


### Reducing memory usages

| Technique                            | Description                                                 |
| ------------------------------------ | ----------------------------------------------------------- |
| Downcasting numeric types            | `pd.to_numeric(df['col'], downcast='integer')` or `'float'` |
| Use `category` for repeating strings | Saves memory for text columns                               |
| Drop unnecessary columns             | Reduces DataFrame size in RAM                               |
| Chunked processing                   | Read CSV in chunks using `pd.read_csv(..., chunksize=...)`  |
| Sparse data structures               | For columns with mostly zeros or NaNs                       |


## CPU consumption by Pandas (CPU, threading, Parallel Processing) etc

- Pandas Series and DataFrame columns are built on top of NumPy arrays.
- NumPy is written in C, which allows:
    - Fast, vectorized operations
    - Memory-efficient storage (contiguous blocks in RAM)
    - Broadcasting (operations on arrays without explicit Python loops)
- Most pandas operations are single-threaded, even though NumPy may internally use BLAS/LAPACK libraries for some numeric routines.
- Simple arithmetic, filtering, and groupby operations are not parallelized across CPU cores in standard pandas.
- Pandas stores each column as a typed contiguous block → CPU can access it efficiently.
- Avoids Python object overhead for numeric columns.
- Operations are vectorized rather than using Python loops (for, while), which reduces Python interpreter overhead.
- Pandas uses masking techniques to handle NaN.
    - Instead of branching on each element, it often:
    - Uses Boolean masks for computations
- Performs calculations only on valid (non-NaN) elements.

### what is typed continuous block?
A typed continuous block is a key concept that explains why pandas (and NumPy) are so fast and memory-efficient. Let’s break it down step by step.


What does it mean:

- Each column in a pandas DataFrame is stored as a contiguous block of memory.
- “Typed” means all elements in that column have the same data type (int64, float32, bool, etc.).
- “Continuous block” means the values are stored back-to-back in memory, not scattered across different locations like normal Python objects.


Why This Matters:

1. Memory efficiency
- No overhead per element (unlike Python objects, which have extra pointers and metadata).
- For example, int64 → 8 bytes per element regardless of value.

2. CPU cache friendly
- Modern CPUs can load large chunks of memory at once (cache lines).
- Accessing contiguous memory is faster than accessing scattered Python objects.

3. Vectorized operations
- Operations like addition, multiplication, or comparison can be applied to the entire block at once.
- Implemented in C (via NumPy), which avoids Python loops.


example:

```python
import pandas as pd
import numpy as np

df = pd.DataFrame({
    'A': np.arange(1_000_000),  # int64 typed continuous block
    'B': np.random.random(1_000_000)  # float64 typed continuous block
})
```
- Column A → 1 million integers stored contiguously in memory, 8 bytes each → ~8 MB.
- Column B → 1 million floats stored similarly → ~8 MB.
- Operations like df['A'] + 10 are applied directly to the block in C, not via Python loops.


Contrast with Python Lists:
```python
lst = [1, 2, 3, 4, 5]
```

- Each element is a Python object with:
    - Object overhead (~16–24 bytes per int)
    - Pointer to actual integer data
- Elements are scattered in memory, so vectorized operations are not possible.


Summary:

| Feature         | Typed Continuous Block    | Python List                      |
| --------------- | ------------------------- | -------------------------------- |
| Memory layout   | Contiguous                | Scattered                        |
| Element type    | Same (`int64`, `float32`) | Can vary                         |
| Memory overhead | Minimal                   | High (object headers + pointers) |
| CPU efficiency  | High (vectorized ops)     | Low (Python loops needed)        |
| Example         | `df['col']` in pandas     | `[1, 2, 3]`                      |


### what is vectorization in Pandas

In pandas (and NumPy), vectorization refers to performing operations on entire arrays or columns at once, instead of looping over individual elements in Python.

It’s one of the main reasons pandas is fast.

- Instead of writing a Python for loop, you operate on the whole column or array.
- These operations are implemented in low-level C (via NumPy), so they are much faster than Python loops.

example in python:

```python
import pandas as pd

df = pd.DataFrame({'A': [1, 2, 3, 4, 5]})

# Add 10 to each element using a Python loop
df['B'] = [x + 10 for x in df['A']]
print(df)
```

output:
```css
   A   B
0  1  11
1  2  12
2  3  13
3  4  14
4  5  15
```
The addition happens element by element in Python, which is slower for large datasets.


example with vectorization:
```python
# Add 10 to entire column at once
df['C'] = df['A'] + 10
print(df)
```

output:
```python
   A   B   C
0  1  11  11
1  2  12  12
2  3  13  13
3  4  14  14
4  5  15  15
```

- The operation is applied to the whole column simultaneously.
- Implemented in C under the hood, much faster and memory-efficient.

Advantages of Vectorization:

| Feature | Vectorized Operation               | Python Loop                     |
| ------- | ---------------------------------- | ------------------------------- |
| Speed   | Fast (C-level)                     | Slow (Python interpreter)       |
| Memory  | Efficient (typed continuous block) | Less efficient (Python objects) |
| Syntax  | Simple and readable                | Verbose (`for` loops)           |
| Scaling | Works well for millions of rows    | Slower as size grows            |


Examples of Vectorized Operations in pandas:

```python
df['A'] * 2
df['A'] + df['B']

df['A'] > 3


df['A'].sum()
df['B'].mean()


df[df['A'] > 2]

```

All of these operate on the entire Series or DataFrame column at once.

### what is masking technique to handle Nan

## what is NaN and its size?
In pandas, NaN stands for “Not a Number”. It is used to represent missing or undefined data in a DataFrame or Series.

- Comes from NumPy (numpy.nan).
- Represents missing values in numeric columns (float, int after conversion, etc.).
- In pandas:
    - Numeric columns can store NaN.
    - Object/string columns can also have None or NaN.
- NaN is always treated as a float internally, even if the column originally contains integers.

example:
```python
import pandas as pd
import numpy as np

df = pd.DataFrame({
    'A': [1, 2, np.nan, 4],
    'B': ['x', None, 'y', 'z']
})
print(df)

```

output:
```css
     A     B
0  1.0     x
1  2.0  None
2  NaN     y
3  4.0     z
```



Operations with NaN:
- Any arithmetic with NaN → result is NaN
    ```python
    np.nan + 5  # results in NaN
    ```
- Check missing values with:
    ```python
    df.isna()
    df.isnull()

    ```


Memory Size of NaN:
- NaN is a floating-point value, typically a 64-bit float (float64) in NumPy/pandas.
- Memory size: 8 bytes per NaN value.
- Even if a column is mostly integers, introducing a NaN upcasts the column to float64, because int64 cannot store NaN natively.
- In a pandas DataFrame, memory for a float64 column containing NaN is 8 bytes per element, same as a normal float.


## How does Pandas works with external file sources?
When you call a function like pd.read_csv(), pd.read_parquet(), or pd.read_sql():

1. Pandas function is called → e.g., pd.read_csv('data.csv').
2. Delegates to an underlying parser/engine:
    - CSV → C engine (_csv) or Python engine
    - Excel → openpyxl / xlrd / xlsxwriter
    - JSON → built-in JSON parser or ujson
    - Parquet → pyarrow or fastparquet
    - SQL → SQLAlchemy or database driver
3. Engine reads raw data from disk/network:
    - Opens file, reads bytes
    - Handles encoding, delimiters, compression
4. Data is converted to pandas DataFrame:
    - Data types (int, float, bool, category) are inferred or specified
    - Indexes are created
    - Columns stored as typed continuous blocks (NumPy arrays)
5. Return DataFrame ready for Python-level operations



what is the format in which pandas store data?

### Memory optimization for large CSVs?
Great! Optimizing memory when working with large CSVs in Pandas is critical — especially when dealing with millions of rows or running on limited RAM.

By default, pd.read_csv() loads everything into memory with generic data types, which may be overkill (e.g., float64 when float32 is enough, or using object for strings).

1. Use dtype to explicitly set data types
    ```python
        dtypes = {
        'id': 'int32',
        'amount': 'float32',
        'status': 'category',
        'name': 'string'
    }

    df = pd.read_csv('large.csv', dtype=dtypes)

    ```
    Use category for columns with repeated values (like states, genders, etc.). It saves a lot of space.
2. Use usecols to read only required columns
    Don’t read columns you don’t need:
    ```python
    df = pd.read_csv('large.csv', usecols=['id', 'name', 'amount'])
    ```
3. Instead of keeping dates as strings, parse them:
    ```python
    df = pd.read_csv('large.csv', parse_dates=['created_at'])

    ```
    But avoid parsing dates if you don't need them immediately — it adds overhead.
4. Read in Chunks (chunksize):
    This reads the CSV in smaller parts and lets you process them one at a time:
    ```python
    chunksize = 100_000
    for chunk in pd.read_csv('large.csv', chunksize=chunksize):
        # Process chunk
        print(chunk.memory_usage(deep=True).sum())


    ```
    It does NOT load the entire CSV into memory first. Internally it:
    - Opens the file.
    - Reads ~100,000 rows.
    - Parses them into a DataFrame.
    - Yields that DataFrame.

5. Free up memory manually
    When working in notebooks or long scripts:
    ```python
    import gc

    del df
    gc.collect()
    ```

    del df → removes the reference to the DataFrame.

    gc.collect() → forces Python’s cyclic garbage collector to run immediately.

    The forced GC:
    - Scans all container objects
    - Looks for reference cycles
    - Frees unreachable cyclic objects

6. Use memory_usage() to monitor size
    ```python
    print(df.memory_usage(deep=True))
    print(f"Total: {df.memory_usage(deep=True).sum() / (1024 ** 2):.2f} MB")

    ```
7. Pandas does eager evaluation, hence, be careful with it. It is going to store everything in memory. It immediately loads and processes your data into RAM. It doesn't delay or defer computation unlike lazy evaluation.


## Questions:
1. Why indexes are useful?
2. in below df
   ```
   import pandas as pd
   data = {
    "a": ["ab", "ac", "ad", "ae"],
    "b": ["bc", "bd", "be", "bf"]
   }
   
   df = pd.Dataframe(data)

   print(df)

   print(df.loc[1])

   print(df.loc['a'])

   ```

   what will be the output?

   Sol:-
   Output will be 
   ```

   # print(df)
        a   b
    0  ab  bc
    1  ac  bd
    2  ad  be
    3  ae  bf


    # print(df.loc[1])
    a    ac
    b    bd

    # print(df.loc['a'])

    It will throw error as index 'a' does not exist.

   ```
3. 

### I have a CSV file and need to perform operations on its rows. Which approach is faster: manually reading the CSV and iterating over rows in Python, or using Pandas? Why?

Pandas is almost always faster, especially as data size grows. Here's why:
Manual CSV Reading processes rows one at a time in a pure Python loop. Each iteration carries overhead — type checking, object creation, and interpretation — because Python is an interpreted language. Data is stored as plain Python strings and lists with no optimized memory layout. For a million rows, you're doing a million Python-level iterations.
Pandas, on the other hand, has its read_csv implemented in C under the hood, so even the parsing step is faster. Data is stored in NumPy arrays — contiguous blocks of memory — rather than scattered Python objects. Most importantly, Pandas supports vectorized operations, meaning an operation like df['price'] * 1.1 doesn't loop at all; it runs a single C-level operation across the entire column at once. Even .apply(), which does iterate internally, has less overhead than a raw Python loop due to optimized data access.
The result is that Pandas is typically 10x–100x faster than manual iteration, depending on the dataset size and operation.
When manual CSV reading might still make sense:

The file is very small (a few thousand rows) and the difference is negligible
You only need a few specific rows and don't want to load everything into memory
The file is too large to fit in RAM (though pd.read_csv(chunksize=...) solves this within Pandas too)

For any non-trivial dataset, Pandas is the clear winner because it pushes computation down to C level and eliminates Python loop overhead entirely.


=::> Python is a dynamically typed, interpreted language. It has no idea at loop start that row[1] is a string, that you'll convert it to int, or that you'll multiply it. Every single operation goes through type lookup → method dispatch → object allocation → reference counting. None of this is known ahead of time.
Pandas with NumPy knows the dtype of the entire column upfront (int64, float64, etc.), so it skips all of this and runs a single C loop across raw memory with no object allocation, no type checking, and no reference counting per element. That's the fundamental difference.
