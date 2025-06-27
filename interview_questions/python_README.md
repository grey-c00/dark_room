## what is Flask?
Flask is a lightweight web framework for Python used to build web applications and APIs. It's known for being simple, flexible, and minimal—great for beginners and professionals alike.

### can we RESTFull APIs using Flask?
### can we RESTless APIs using Flask?


## copy vs deep copy

### 🔁 Shallow Copy: 
A shallow copy creates a new object, but does not recursively copy the inner (nested) objects. Instead, it copies references to those inner objects.

Behavior:
- Outer container is a new object ✅
- Nested objects are shared (same memory reference) ❗
- less memory usage


### 🌀 Deep Copy
A deep copy creates a new object, and recursively copies all inner objects as well — so nothing is shared between the original and copy.

🧠 Behavior:
- Outer container is new ✅
- All nested containers and values are also new ✅
- More memory usages


### 🔍 When to Use:
Use Case	                            Copy Type	                Why?
Flat lists/dictionaries	                Shallow copy	            Faster, no need to copy inner objects
Nested lists/dicts/objects	            Deep copy	                Ensures independence from original
Performance-sensitive copies	        Shallow copy	            Less memory and faster
Avoiding side effects with nested data	Deep copy	                Prevent bugs from shared references



## How dictionary works in Python?
Python dictionaries are implemented as hash tables. A hash table allows very fast lookup, insertion, and deletion on average.
### 🔑 Key Concepts:
#### Hashing

When you add a key to the dictionary, Python computes a hash value for that key using the built-in hash() function.

The hash value is an integer that determines where the key-value pair should be stored in the internal array.

#### Buckets / Slots

Internally, the dictionary has an array of slots (also called buckets).

Each slot can store one key-value pair or be empty.

#### Indexing

The hash value is transformed into an index into the slots array, typically by taking hash % size_of_array.

The key-value pair is stored at that index if it’s free.

#### Collision Handling

If two keys hash to the same index (a collision), Python uses open addressing with probing (specifically, perturbation probing) to find another free slot.

The dictionary keeps probing sequential slots in a deterministic way until it finds an empty slot.


### 🔥 Python Dictionary Features:
Dynamic resizing: As the dict fills up, Python grows the internal array and rehashes keys to keep lookup efficient.

Order preservation (since Python 3.7): Internally maintains insertion order by storing entries in a linked array alongside the hash table.


## how to handle large dataset in PySpark
1. Use DataFrames: PySpark DataFrames are optimized for large datasets and provide a high-level API for data manipulation.
2. Use Partitioning: Partition your data to distribute it across the cluster, allowing parallel processing.
3. Use Caching: Cache intermediate results to avoid recomputing them, which can save time on large datasets.
4. Use Broadcast Variables: For small datasets that need to be used across multiple nodes, use broadcast variables to reduce data transfer overhead.
5. Use Efficient File Formats: Use columnar formats like Parquet or ORC for better performance and compression.
6. Avoid Shuffles: Operations like groupBy, join, distinct cause shuffles — expensive data movement between nodes. Minimize these or optimize join keys, use broadcast joins for small tables:
7. Filter Early: Apply filters as early as possible to reduce the amount of data processed in subsequent operations.


## How would you design a system for processing millions of records per day using Python?
To process millions of records daily:

- Use PySpark or Dask for heavy batch jobs
- Use Kafka + Faust/Spark Streaming for real-time
- Store data in Parquet/S3 or a scalable DB
- Schedule jobs using Airflow
- Monitor and log everything


##  Explain list comprehension. How does it differ from using a loop?
List comprehension is a compact way to create lists.
```
squares = [x*x for x in range(10)]
```
🔹 It’s:

- More concise
- Often faster than for loops
- More readable (when not overused)

## What's the difference between is and ==?
- == compares values (equality)
- `is` compares identity (i.e., whether two objects are the same in memory)
```commandline
a = [1, 2]
b = [1, 2]
a == b  # True
a is b  # False

```

## How are mutable and immutable types handled in Python?
- Mutable types (e.g., list, dict) can be changed in place.
- Immutable types (e.g., int, str, tuple) cannot be modified after creation.

This affects how variables reference objects and behave in functions.


##When would you use a set instead of a list?
Use a set when:
- You need to ensure uniqueness
- You need fast membership checks (in is O(1) in sets)

Lists preserve order, sets do not (prior to Python 3.7+).

## How do dictionaries maintain insertion order in Python 3.7+?
Since Python 3.7, dicts preserve insertion order as an implementation detail (now guaranteed).

Internally, Python uses a combined hash table + insertion-order array to store keys.


## What is a context manager and how is it implemented (with statement)?
A context manager manages setup and teardown logic (like opening/closing files).
```commandline
with open('file.txt') as f:
    data = f.read()

```
You can define custom ones using a class with __enter__ and __exit__, or with the contextlib module.


## How do you handle large files/data in Python?
Use generators and stream processing to avoid memory overload:

```commandline
with open('large.txt') as f:
    for line in f:
        process(line)

```
Use tools like Pandas with chunksize, Dask, or PySpark for large datasets.

## How do you write unit tests in Python?
Use the unittest or pytest module.
```commandline
import unittest

class TestAdd(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)

if __name__ == '__main__':
    unittest.main()

```


## What are common Python code smells or anti-patterns?
Repeated code instead of functions (violates DRY)

Using mutable default arguments

Catching broad exceptions: except Exception: instead of specific ones

Writing long functions instead of modular code

Overuse of global variables
