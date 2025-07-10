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
```python
a = [1, 2]
b = [1, 2]
print(a == b)  # True
print(a is b)  # False

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
```python
with open('file.txt') as f:
    data = f.read()

```
You can define custom ones using a class with __enter__ and __exit__, or with the contextlib module.


## How do you handle large files/data in Python?
Use generators and stream processing to avoid memory overload:

```python
def process(line):
    # Process each line
    pass

with open('large.txt') as f:
    for line in f:
        process(line)

```
Use tools like Pandas with chunksize, Dask, or PySpark for large datasets.

## How do you write unit tests in Python?
Use the unittest or pytest module.
```python
import unittest

def add(a, b):
   return a + b

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

## what is lambda function?
A lambda function in Python is a small, anonymous function — meaning it doesn’t have a name like regular functions defined using def.
```
lambda arguments: expression
```
### Common Use Cases
1. With map():
    ```
    nums = [1, 2, 3, 4]
    squares = list(map(lambda x: x * x, nums))
    ```
2. With filter():
    ```
    evens = list(filter(lambda x: x % 2 == 0, nums))
    ```
3. With sorted() for custom sorting:
```python
pairs = [(1, 'b'), (2, 'a'), (3, 'c')]
sorted_pairs = sorted(pairs, key=lambda x: x[1])

```
   

## Memory management in Python

Python uses its private heap space to manage the memory. Basically, all the objects and data structures are stored in the private heap space. Even the programmer can not access this private space as the interpreter takes care of this space. Python also has an inbuilt garbage collector, which recycles all the unused memory and frees the memory and makes it available to the heap space.




## Is Python a compiled language or an interpreted language
Please remember one thing, whether a language is compiled or interpreted or both is not defined in the language standard. In other words, it is not a properly of a programming language. Different Python distributions (or implementations) choose to do different things (compile or interpret or both). However the most common implementations like CPython do both compile and interpret, but in different stages of its execution process.

Compilation: When you write Python code and run it, the source code (.py files) is first compiled into an intermediate form called bytecode (.pyc files). This bytecode is a lower-level representation of your code, but it is still not directly machine code. It’s something that the Python Virtual Machine (PVM) can understand and execute.

Interpretation: After Python code is compiled into bytecode, it is executed by the Python Virtual Machine (PVM), which is an interpreter. The PVM reads the bytecode and executes it line-by-line at runtime, which is why Python is considered an interpreted language in practice.

Some implementations, like PyPy, use Just-In-Time (JIT) compilation, where Python code is compiled into machine code at runtime for faster execution, blurring the lines between interpretation and compilation.

## How can you concatenate two lists in Python?
1. Using the + operator:
2. Using the extend() method:
```python
a = [1, 2, 3]
b = [4, 5, 6]
res = a + b
print(res)


a = [1, 2, 3]
b = [4, 5, 6]
a.extend(b)
print(a)
```

## Difference between for loop and while loop in Python
- For loop: Used when we know how many times to repeat, often with lists, tuples, sets, or dictionaries.
- While loop: Used when we only have an end condition and don’t know exactly how many times it will repeat.

```python
for i in range(5):
    print(i)

c = 0
while c < 5:
    print(c)
    c += 1
```


## How do you floor a number in Python?
To floor a number in Python, you can use the `math.floor()` function, which returns the largest integer less than or equal to the given number.

floor()method in Python returns the floor of x i.e., the largest integer not greater than x. 

Also, The method ceil(x) in Python returns a ceiling value of x i.e., the smallest integer greater than or equal to x.

```python
import math

n = 3.7
F_num = math.floor(n)

print(F_num)
```


## What is the difference between / and // in Python?
/ represents precise division (result is a floating point number) whereas // represents floor division (result is an integer). For Example:

```python
print(5//2)  # output: 2
print(5/2)   # output: 2.5
```


## Is Indentation Required in Python?

Yes, indentation is required in Python. A Python interpreter can be informed that a group of statements belongs to a specific block of code by using Python indentation. Indentations make the code easy to read for developers in all programming languages but in Python, it is very important to indent the code in a specific order.


## Can we Pass a function as an argument in Python?
Yes, Several arguments can be passed to a function, including objects, variables (of the same or distinct data types) and functions. Functions can be passed as parameters to other functions because they are objects. Higher-order functions are functions that can take other functions as arguments.

```python
def add(x, y):
    return x + y

def apply_func(func, a, b):
    return func(a, b)

print(apply_func(add, 3, 5))

# output: 8
```

## What is a dynamically typed language?
- In a dynamically typed language, the data type of a variable is determined at runtime, not at compile time.
- No need to declare data types manually; Python automatically detects it based on the assigned value.
- Examples of dynamically typed languages: Python, JavaScript.
- Examples of statically typed languages: C, C++, Java.
- Dynamically typed languages are easier and faster to code.
- Statically typed languages are usually faster to execute due to type checking at compile time.

```python
x = 10       # x is an integer
print(type(x)) # <class 'int'>
x = "Hello"  # Now x is a string
print(type(x)) # class 'str'>
```
Here, the type of x changes at runtime based on the assigned value hence it shows dynamic nature of Python.

## What is pass in Python?
- The pass statement is a placeholder that does nothing.
- It is used when a statement is syntactically required but no code needs to run.
- Commonly used when defining empty functions, classes or loops during development.

```python
def fun():
    pass  # Placeholder, no functionality yet

# Call the function
fun()
```
Here, fun() does nothing, but the code stays syntactically correct.


## How are arguments passed by value or by reference in Python?
- Python’s argument-passing model is neither “Pass by Value” nor “Pass by Reference” but it is “Pass by Object Reference”. 
- Depending on the type of object you pass in the function, the function behaves differently. Immutable objects show “pass by value” whereas mutable objects show “pass by reference”.

You can check the difference between pass-by-value and pass-by-reference in the example below:

```python
def call_by_val(x):
    x = x * 2
    return x


def call_by_ref(b):
    b.append("D")
    return b


a = ["E"]
num = 6

# Call functions
call_by_val(num)
call_by_ref(a)

# Print after function calls
print("Updated value after call_by_val:", num) # num remains unchanged, its 6 only
print("Updated list after call_by_ref:", a) # a is updated to ['E', 'D'] because lists are mutable
```


## What is a lambda function?
A lambda function is an anonymous function. This function can have any number of parameters but, can have just one statement.

In the example, we defined a lambda function(upper) to convert a string to its upper case using upper().
```python
s1 = 'GeeksforGeeks'

s2 = lambda func: func.upper()
print(s2(s1))  # Output: GEEKSFORGEEKS
```

## What is List Comprehension? Give an Example.
List comprehension is a way to create lists using a concise syntax. It allows us to generate a new list by applying an expression to each item in an existing iterable (such as a list or range). This helps us to write cleaner, more readable code compared to traditional looping techniques.

For example, if we have a list of integers and want to create a new list containing the square of each element, we can easily achieve this using list comprehension.
```python
a = [2,3,4,5]
res = [val ** 2 for val in a]
print(res) # [4, 9, 16, 25]
```

## What are *args and **kwargs?
- 
*args: The special syntax *args in function definitions is used to pass a variable number of arguments to a function. Python program to illustrate *args for a variable number of arguments:
```python
def fun(*argv):
    for arg in argv:
        print(arg)

fun('Hello', 'Welcome', 'to', 'GeeksforGeeks')
```


**kwargs: The special syntax **kwargs in function definitions is used to pass a variable length argument list. We use the name kwargs with the double star **.

```python
def fun(**kwargs):
    for k, val in kwargs.items():
        print("%s == %s" % (k, val))


# Driver code
fun(s1='Geeks', s2='for', s3='Geeks')
```


## What is a break, continue and pass in Python? 
- Break statement is used to terminate the loop or statement in which it is present. After that, the control will pass to the statements that are present after the break statement, if available.
- Continue is also a loop control statement just like the break statement. continue statement is opposite to that of the break statement, instead of terminating the loop, it forces to execute the next iteration of the loop.
- Pass means performing no operation or in other words, it is a placeholder in the compound statement, where there should be a blank left and nothing has to be written there.

##  What is the difference between a Set and Dictionary?
- A Python Set is an unordered collection data type that is iterable, mutable and has no duplicate elements. Python’s set class represents the mathematical notion of a set.
- Syntax: Defined using curly braces {} or the set() function.
`my_set = {1, 2, 3}`

- Dictionary in Python is an ordered (since Py 3.7) [unordered (Py 3.6 & prior)] collection of data values, used to store data values like a map, which, unlike other Data Types that hold only a single value as an element, Dictionary holds key:value pair. Key-value is provided in the dictionary to make it more optimized.
- Syntax: Defined using curly braces {} with key-value pairs.
`my_dict = {'a': 1, 'b': 2, 'c': 3}`


## What are Built-in data types in Python?
The following are the standard or built-in data types in Python:

- Numeric: The numeric data type in Python represents the data that has a numeric value. A numeric value can be an integer, a floating number, a Boolean, or even a complex number.
- Sequence Type: The sequence Data Type in Python is the ordered collection of similar or different data types. There are several sequence types in Python:
  - Python String
  - Python List
  - Python Tuple
  - Python range
- Mapping Types: In Python, hashable data can be mapped to random objects using a mapping object. There is currently only one common mapping type, the dictionary and mapping objects are mutable.
  - Python Dictionary
- Set Types: In Python, a Set is an unordered collection of data types that is iterable, mutable and has no duplicate elements. The order of elements in a set is undefined though it may consist of various elements.

## What is the difference between a Mutable datatype and an Immutable data type?
- Mutable data types can be edited i.e., they can change at runtime. Eg – List, Dictionary, etc.
- Immutable data types can not be edited i.e., they can not change at runtime. Eg – String, Tuple, etc.

### Mutable Data Types
These can be changed after creation — you can modify, add, or remove elements without creating a new object.

✅ Key Features:
   - Contents can be modified in-place. 
   - Their memory address (id) remains the same after modification.

🔹 Examples in Python:
   - list 
   - dict 
   - set 
   - bytearray

Example:
```python
my_list = [1, 2, 3]
print(id(my_list))     # Original memory address
my_list.append(4)
print(my_list)         # [1, 2, 3, 4]
print(id(my_list))     # Same memory address

```

### Immutable Data Types
These cannot be changed after creation — any modification creates a new object.

Key Features:
   - Contents cannot be modified once set. 
   - Changing the value results in a new memory address.

🔹 Examples in Python:
   - int 
   - float 
   - str 
   - tuple 
   - frozenset 
   - bytes

Example:
```python
x = "hello"
print(id(x))        # Memory address of original string
x += " world"
print(x)            # "hello world"
print(id(x))        # New memory address — new object created

```


### Why It Matters
Performance & Safety: Immutable objects are safer in multi-threaded environments.

Hashability: Immutable objects can be used as dictionary keys or in sets (str, tuple), while mutable ones generally cannot (list, dict).


Mutable objects can be changed in-place, while immutable objects cannot be changed after they are created.

| Feature                                 | Mutable        | Immutable                    |
|-----------------------------------------|----------------|------------------------------|
| Can modify internal content (in-place)? | ✅ Yes          | ❌ No                         |
| Memory address after "change"           | Stays the same | Changes (new object created) |
| Can be used as dict key or in sets?     | ❌ Usually no   | ✅ Yes (must be hashable)     |
| Thread-safe by design?                  | ❌ No           | ✅ Yes                        |


What "in-place" vs. "new object" means:

```python
lst = [1, 2]
print(id(lst))  # e.g., 140305388017280
lst.append(3)
print(lst)      # [1, 2, 3]
print(id(lst))  # same ID — modified in-place



s = "hi"
print(id(s))    # e.g., 140305387747376
s += " there"
print(s)        # "hi there"
print(id(s))    # different ID — new object

```

The change in memory address is a consequence of immutability, not the definition.



Example: Tuples with Mutable Inside

```python
t = (1, [2, 3])
t[1].append(4)  # Modifying list inside the tuple
print(t)        # (1, [2, 3, 4])

```

The tuple is immutable, but it holds a mutable list that was changed in-place.

So immutability can be shallow — the container doesn't change, but its contents might.


Consider other example:
```python
tpl = ([1],2,3)
print(id(tpl))
tpl[0].append(6)
print(id(tpl))
print(tpl)
```
What happened here? 
- tpl is a tuple, which is immutable. 
- But tpl[0] refers to a list, which is mutable. 
- When you do tpl[0].append(6), you’re modifying the list in-place, not the tuple itself. 
- So:
  - The tuple's identity (id(tpl)) does not change. 
  - The contents of the list inside it have changed.
- Tuple itself is still immutable → You cannot do something like tpl[1] = 9 (this will raise a TypeError). 
- Mutable object inside the tuple can still be changed → Lists, dicts, sets, etc., if stored inside.
- So has the tuple changed? 
  - Technically: No. The tuple’s structure (what objects it points to) hasn't changed. 
  - Logically: It looks like it changed, because one of its elements is mutable and was altered.
  - The tuple just holds pointers (references). 
  - The list object was modified, but the tuple still points to the same list.
  - A tuple is immutable, but it can hold mutable objects, which can be changed if accessed.

## What is a Variable Scope in Python?
The location where we can find a variable and also access it if required is called the scope of a variable.

- Python Local variable: Local variables are those that are initialized within a function and are unique to that function. A local variable cannot be accessed outside of the function.
- Python Global variables: Global variables are the ones that are defined and declared outside any function and are not specified to any function.
- Module-level scope: It refers to the global objects of the current module accessible in the program.
- Outermost scope: It refers to any built-in names that the program can call. The name referenced is located last among the objects in this scope.

## How is a dictionary different from a list?
A list is an ordered collection of items accessed by their index, while a dictionary is an unordered collection of key-value pairs accessed using unique keys. Lists are ideal for sequential data, whereas dictionaries are better for associative data. For example, a list can store [10, 20, 30], whereas a dictionary can store {"a": 10, "b": 20, "c": 30}.

## What is the difference between a list and a tuple?
A list is mutable (can be changed) and defined with square brackets [], while a tuple is immutable (cannot be changed) and defined with parentheses (). Lists allow for dynamic resizing, while tuples have a fixed size. For example, a list can be [1, 2, 3], and a tuple can be (1, 2, 3). Lists are generally used for collections of items that may change, while tuples are used for fixed collections of items.


## what is a Python module?
A Python module is a file containing Python code that can define functions, classes, and variables. It allows for code organization and reuse across different programs. Modules can be imported into other Python scripts using the `import` statement, enabling access to the defined functions and classes.


## What is a Python package?
A Python package is a way of organizing related modules into a directory hierarchy. It allows for better code organization and modularity. A package is simply a directory containing an `__init__.py` file (which can be empty) and one or more module files. Packages can be imported using the `import` statement, allowing access to the modules within the package.


## What is the difference between a module and a package in Python?
A module is a single file containing Python code, while a package is a directory that contains multiple modules and an `__init__.py` file. Modules are used for organizing code into reusable components, while packages allow for grouping related modules together in a structured way. In essence, a package is a collection of modules.


## What is the difference between a class and an object in Python?
A class is a blueprint or template for creating objects, defining their properties and behaviors. An object is an instance of a class, created based on the class definition. Classes encapsulate data and functionality, while objects represent specific instances of that class with their own unique state. For example, a `Car` class defines properties like `color` and `model`, while an object like `my_car` is an instance of the `Car` class with specific values for those properties.


##  What is docstring in Python?
Python documentation strings (or docstrings) provide a convenient way of associating documentation with Python modules, functions, classes and methods.

- Declaring Docstrings: The docstrings are declared using ”’triple single quotes”’ or “””triple double quotes””” just below the class, method, or function declaration. All functions should have a docstring.
- Accessing Docstrings: The docstrings can be accessed using the __doc__ method of the object or using the help function.


## What is the difference between a function and a method in Python?
A function is a standalone block of code that performs a specific task and can be called independently. It is defined using the `def` keyword. A method, on the other hand, is a function that is associated with an object (an instance of a class) and is called on that object. Methods are defined within a class and can access the object's attributes and other methods. For example, `len()` is a built-in function, while `list.append()` is a method of the list class.


## How is Exceptional handling done in Python?

An exception is an error that occurs during the execution of a program, disrupting its normal flow. Python provides a robust mechanism for handling exceptions, allowing developers to manage errors gracefully without crashing the program.

There are 3 main keywords i.e. try, except and finally which are used to catch exceptions:

- try: A block of code that is monitored for errors.
- except: Executes when an error occurs in the try block.
- finally: Executes after the try and except blocks, regardless of whether an error occurred. It’s used for cleanup tasks.

Example:
```python
n = 10
try:
    res = n / 0  # This will raise a ZeroDivisionError
    
except ZeroDivisionError:
    print("Can't be divided by zero!")
```

## what are the common built-in exceptions in Python?
Common built-in exceptions in Python include:
- `ValueError`: Raised when a function receives an argument of the right type but inappropriate value.
- `TypeError`: Raised when an operation or function is applied to an object of inappropriate type.
- `IndexError`: Raised when trying to access an index that is out of range for a list or tuple.
- `KeyError`: Raised when trying to access a dictionary with a key that does not exist.
- `FileNotFoundError`: Raised when trying to open a file that does not exist.
- `ZeroDivisionError`: Raised when attempting to divide by zero.
- `AttributeError`: Raised when an invalid attribute reference is made.
- `ImportError`: Raised when an import statement fails to find the module or object being imported.
- `NameError`: Raised when a local or global name is not found.
- `RuntimeError`: Raised when an error occurs that does not fall into any other category.
- `StopIteration`: Raised to signal the end of an iterator.
- `AssertionError`: Raised when an assert statement fails.
- `MemoryError`: Raised when an operation runs out of memory.

Example:
```python
int("abc")  # Trying to convert a string to an int
# ValueError: invalid literal for int() with base 10: 'abc'

new_val = "abc" + 5  # Trying to add a string and an integer
# TypeError: can only concatenate str (not "int") to str
```

## What is the difference between Python Arrays and Lists?
- Arrays (when talking about the array module in Python) are specifically used to store a collection of numeric elements that are all of the same type. This makes them more efficient for storing large amounts of data and performing numerical computations where the type consistency is maintained.
- Syntax: Need to import the array module to use arrays.
   ```python
   from array import array
   arr = array('i', [1, 2, 3, 4])  # Array of integers
   ```
- Lists are more flexible than arrays in that they can hold elements of different types (integers, strings, objects, etc.). They come built-in with Python and do not require importing any additional modules.
- Lists support a variety of operations that can modify the list.

## What is the difference between xrange and range functions?
range() and xrange() are two functions that could be used to iterate a certain number of times in for loops in Python. 

- In Python 3, there is no xrange, but the range function behaves like xrange. 
- In Python 2 
  - range() – This returns a range object, which is an immutable sequence type that generates the numbers on demand. 
  - xrange() – This function returns the generator object that can be used to display numbers only by looping. The only particular range is displayed on demand and hence called lazy evaluation.

## What is Dictionary Comprehension? Give an Example
Dictionary Comprehension is a syntax construction to ease the creation of a dictionary based on the existing iterable.

```python
keys = ['a','b','c','d','e']
values = [1,2,3,4,5]  

# this line shows dict comprehension here  
d = { k:v for (k,v) in zip(keys, values)}  

# We can use below too
# d = dict(zip(keys, values))  

print (d) # {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5}
```

## Is Tuple Comprehension possible in Python? If yes, how and if not why?
Tuple comprehensions are not directly supported, Python's existing features like generator expressions and the tuple() function provide flexible alternatives for creating tuples from iterable data.

`(i for i in (1, 2, 3))`

Tuple comprehension is not possible in Python because it will end up in a generator, not a tuple comprehension.

## iterators vs generators
### Iterators
An iterator is an object that implements the iterator protocol, which consists of the methods `__iter__()` and `__next__()`. It allows you to traverse through a collection (like a list or a dictionary) without exposing the underlying structure.
```python
class MyIterator:
    def __init__(self, data):
        self.data = data
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index < len(self.data):
            result = self.data[self.index]
            self.index += 1
            return result
        else:
            raise StopIteration
```
### Generators
A generator is a special type of iterator that is defined using a function with the `yield` keyword. When called, it returns an iterator object but does not execute the function immediately. Instead, it generates values on-the-fly as you iterate over it.
```python  
def my_generator(data):
    for item in data:
        yield item 
```

### Key Differences
| Feature                | Iterator                          | Generator                          |
|------------------------|-----------------------------------|------------------------------------|
| Definition             | Object implementing `__iter__()` and `__next__()` methods | Function using `yield` to produce values |
| Memory Usage           | Stores the entire collection in memory | Generates values on-the-fly, more memory efficient |


## Differentiate between List and Tuple?
Let’s analyze the differences between List and Tuple:

- List 
  - Lists are Mutable datatype.
  - Lists consume more memory
  - The list is better for performing operations, such as insertion and deletion.
  - The implication of iterations is Time-consuming
  
- Tuple 
  - Tuples are Immutable datatype. 
  - Tuple consumes less memory as compared to the list 
  - A Tuple data type is appropriate for accessing the elements 
  - The implication of iterations is comparatively Faster

## Which sorting technique is used by sort() and sorted() functions of python?
Python uses the Tim Sort algorithm for sorting. It’s a stable sorting whose worst case is O(N log N). It’s a hybrid sorting algorithm, derived from merge sort and insertion sort, designed to perform well on many kinds of real-world data.


## What are Decorators?
Decorators are a powerful and flexible way to modify or extend the behavior of functions or methods, without changing their actual code. A decorator is essentially a function that takes another function as an argument and returns a new function with enhanced functionality.

Decorators are often used in scenarios such as logging, authentication and memorization, allowing us to add additional functionality to existing functions or methods in a clean, reusable way.


## How do you debug a Python program?
- Using pdb module: pdb is a built-in module that allows you to set breakpoints and step through the code line by line. You can start the debugger by adding import pdb; pdb.set_trace() in your code where you want to begin debugging.
- Using logging Module:For more advanced debugging, the logging module provides a flexible way to log messages with different severity levels (INFO, DEBUG, WARNING, ERROR, CRITICAL).


## What are Iterators in Python?
In Python, iterators are used to iterate a group of elements, containers like a list. Iterators are collections of items and they can be a list, tuples, or a dictionary. Python iterator implements __itr__ and the next() method to iterate the stored elements. We generally use loops to iterate over the collections (list, tuple) in Python.


## What are Generators in Python?
In Python, the generator is a way that specifies how to implement iterators. It is a normal function except that it yields expression in the function. It does not implement __itr__ and __next__ method and reduces other overheads as well.

If a function contains at least a yield statement, it becomes a generator. The yield keyword pauses the current execution by saving its states and then resumes from the same when required.


## Does Python supports multiple Inheritance?
When a class is derived from more than one base class it is called multiple Inheritance. The derived class inherits all the features of the base case.

Python does support multiple inheritances, unlike Java.

## What is Polymorphism in Python?
Polymorphism means the ability to take multiple forms. Polymorphism allows different classes to be treated as if they are instances of the same class through a common interface. This means that a method in a parent class can be overridden by a method with the same name in a child class, but the child class can provide its own specific implementation. This allows the same method to operate differently depending on the object that invokes it. Polymorphism is about overriding, not overloading; it enables methods to operate on objects of different classes, which can have their own attributes and methods, providing flexibility and reusability in the code.



## Define encapsulation in Python?
Encapsulation is the process of hiding the internal state of an object and requiring all interactions to be performed through an object’s methods. This approach:

- Provides better control over data.
- Prevents accidental modification of data.
- Promotes modular programming.
- Python achieves encapsulation through public, protected and private attributes.

## How do you do data abstraction in Python?
Data Abstraction is providing only the required details and hides the implementation from the world. The focus is on exposing only the essential features and hiding the complex implementation behind an interface. It can be achieved in Python by using interfaces and abstract classes.


## What is slicing in Python?
Python Slicing is a string operation for extracting a part of the string, or some part of a list. With this operator, one can specify where to start the slicing, where to end and specify the step. List slicing returns a new list from the existing list.

```python
substring = s[start : end : step]

```


## What is a namespace in Python?
A namespace in Python refers to a container where names (variables, functions, objects) are mapped to objects. In simple terms, a namespace is a space where names are defined and stored and it helps avoid naming conflicts by ensuring that names are unique within a given scope.

Types of Namespaces:

- Built-in Namespace: Contains all the built-in functions and exceptions, like print(), int(), etc. These are available in every Python program.
- Global Namespace: Contains names from all the objects, functions and variables in the program at the top level.
- Local Namespace: Refers to names inside a function or method. Each function call creates a new local namespace.


## What is PIP?
PIP is an acronym for Python Installer Package which provides a seamless interface to install various Python modules. It is a command-line tool that can search for packages over the internet and install them without any user interaction.

## What is a zip function?
The `zip()` function in Python is used to combine multiple iterables (like lists or tuples) into a single iterable of tuples. Each tuple contains elements from the input iterables at the same index. If the input iterables are of different lengths, `zip()` stops creating tuples when the shortest iterable is exhausted.


## What are Pickling and Unpickling?
- Pickling: The pickle module converts any Python object into a byte stream (not a string representation). This byte stream can then be stored in a file, sent over a network, or saved for later use. The function used for pickling is pickle.dump().
- Unpickling: The process of retrieving the original Python object from the byte stream (saved during pickling) is called unpickling. The function used for unpickling is pickle.load().

## What is the difference between @classmethod, @staticmethod and instance methods in Python?
1. Instance Method operates on an instance of the class and has access to instance attributes and takes self as the first parameter.
2. Class Method directly operates on the class itself and not on instance, it takes cls as the first parameter and defined with `@classmethod` decorator.
3. Static Method does not operate on an instance or the class and takes no self or cls as an argument and is defined with `@staticmethod` decorator.

## What is __init__() in Python and how does self play a role in it?
- `__init__()` is Python's equivalent of constructors in OOP, called automatically when a new object is created. It initializes the object's attributes with values but doesn’t handle memory allocation.
- Memory allocation is handled by the `__new__()` method, which is called before `__init__()`.
- The self parameter in `__init__()` refers to the instance of the class, allowing access to its attributes and methods.
- self must be the first parameter in all instance methods, including `__init__()`

## Write a code to display the current time?
```python
import time

current_time= time.localtime(time.time())
print ("Current time is", current_time)
```


## What are Access Specifiers in Python?
Python uses the ‘_’ symbol to determine the access control for a specific data member or a member function of a class. A Class in Python has three types of Python access modifiers:

- Public Access Modifier: The members of a class that are declared public are easily accessible from any part of the program. All data members and member functions of a class are public by default.
  - Default for all variables and methods. 
  - Accessible from anywhere — inside or outside the class.
  ```python
   class Person:
       def __init__(self):
           self.name = "Alice"  # public
   
   p = Person()
   print(p.name)  # ✅ Works fine
   
   ```
- Protected Access Modifier (Convention only): The members of a class that are declared protected are only accessible to a class derived from it. All data members of a class are declared protected by adding a single underscore '_' symbol before the data members of that class.
  - Prefix with a single underscore: _variable 
  - Indicates it should not be accessed from outside the class or its subclasses — but it can be. 
  - It’s a soft convention, not enforced by the interpreter.
  ```python
   class Person:
       def __init__(self):
           self._age = 30  # protected (by convention)
   
   p = Person()
   print(p._age)  # ⚠️ Allowed, but not recommended
   
   ```
- Private Access Modifier: The members of a class that are declared private are accessible within the class only, the private access modifier is the most secure access modifier. Data members of a class are declared private by adding a double underscore ‘__’ symbol before the data member of that class.
  - Prefix with double underscore: __variable 
  - Triggers name mangling, so the variable name gets changed internally to prevent accidental access. 
  - Still accessible if you know the mangled name, so not truly private — just harder to access.
  ```python
   class Person:
       def __init__(self):
           self.__salary = 5000  # private
   
   p = Person()
   # print(p.__salary)       # ❌ AttributeError
   print(p._Person__salary)   # ✅ Works (name mangling)
   
   ```
  

Summary: 

| Access Level | Syntax   | Accessible Outside Class? | Enforced?        | Notes                       |
|--------------|----------|---------------------------|------------------|-----------------------------|
| Public       | `name`   | ✅ Yes                     | ❌ No             | Default                     |
| Protected    | `_name`  | ✅ Yes (discouraged)       | ❌ No             | Convention only             |
| Private      | `__name` | ❌ No (without mangling)   | ⚠️ Name mangling | Use for internal attributes |


## What are unit tests in Python?
Unit Testing is the first level of software testing where the smallest testable parts of the software are tested. This is used to validate that each unit of the software performs as designed. The unit test framework is Python’s xUnit style framework. The White Box Testing method is used for Unit testing.

## Python Global Interpreter Lock (GIL)?
Python Global Interpreter Lock (GIL) is a type of process lock that is used by Python whenever it deals with processes. Generally, Python only uses only one thread to execute the set of written statements. The performance of the single-threaded process and the multi-threaded process will be the same in Python and this is because of GIL in Python. We can not achieve multithreading in Python because we have a global interpreter lock that restricts the threads and works as a single thread.


## What are Function Annotations in Python?
- Function Annotation is a feature that allows you to add metadata to function parameters and return values. This way you can specify the input type of the function parameters and the return type of the value the function returns.
- Function annotations are arbitrary Python expressions that are associated with various parts of functions. These expressions are evaluated at compile time and have no life in Python’s runtime environment. Python does not attach any meaning to these annotations. They take life when interpreted by third-party libraries, for example, mypy.

Example:
```python
def greet(name: str, age: int) -> str:
    return f"Hello, {name}. You are {age} years old."

greet("Alice", "25")  # This still runs, but type checkers will warn

```


## What are Exception Groups in Python?
The latest feature of Python 3.11, Exception Groups. The ExceptionGroup can be handled using a new except* syntax. The * symbol indicates that multiple exceptions can be handled by each except* clause.

ExceptionGroup is a collection/group of different kinds of Exception. Without creating Multiple Exceptions we can group together different Exceptions which we can later fetch one by one whenever necessary, the order in which the Exceptions are stored in the Exception Group doesn’t matter while calling them.


```python
exceptions = [ZeroDivisionError(), FileNotFoundError(), NameError()]
try:
    raise ExceptionGroup("multiple errors", exceptions)
except* ZeroDivisionError:
    print("Handled ZeroDivisionError")
except* FileNotFoundError:
    print("Handled FileNotFoundError")
except* NameError:
    print("Handled NameError")

```


## What is Python Switch Statement?
From version 3.10 upward, Python has implemented a switch case feature called “structural pattern matching”. You can implement this feature with the match and case keywords. Note that the underscore symbol is what you use to define a default case for the switch statement in Python.

Note: Before Python 3.10 Python doesn't support match Statements.

```python
def classify(x):
    match x:
        case "a":
            return "Letter A"
        case "b":
            return "Letter B"
        case _:
            return "Other"

```


## How to get corresponding ascii value of a character in Python?
`ord(<char>)` function can be used to do so.

```python
def char_to_ascii(char):
    return ord(char)
F_num = char_to_ascii('A')
```

## List basic operations


## set basic operation

## string basic operations

## dictionary basic operations




