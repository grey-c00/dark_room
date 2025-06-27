## Decorators
```commandline
def my_decorator(func):
    def wrapper():
        print("Before the function runs")
        func()
        print("After the function runs")
    return wrapper

@my_decorator
def say_hello():
    print("Hello!")

say_hello()

```

what is happening here?
1. say_hello = my_decorator(say_hello)
2. say_hello() is called


# Concurrency and parallelism
Concurrency: CPU concurrently executing tasks by context switching
Parallelism: CPU executing multiple tasks at the same time using multiple cores || or consider having multiple machines

## Threading pythong module:
threading.Lock() works at the application (thread) level, not the process level.
- Controls access between threads within the same Python process.
- It does not synchronize between multiple processes.
- It's implemented in user space, using operating system-level threading primitives (like pthread_mutex under the hood in CPython).

# classmethod vs staticmethod vs instance methods
## 1. Instance Method (Default)
Defined without any decorator.

Takes self as the first argument, referring to the current object (instance).

Can access both instance attributes and class attributes.

## 2. Class Method (@classmethod)
Takes cls as the first argument, referring to the class itself (not an instance).

Can access and modify class-level variables, but not instance-level ones.

Declared using @classmethod.

## 3. Static Method (@staticmethod)
Takes no self or cls.

Behaves like a regular function, but lives in the class’s namespace.

Does not access or modify class or instance data.

# what is class level lock vs other normal lock
## Class-level Lock
🔸 Defined as a class variable:
```commandline
import threading

class Singleton:
    _lock = threading.Lock()  # Class-level lock

```
🔹 Characteristics:
- Shared by all instances of the class.
- Used to protect class-level data (e.g., a singleton instance, shared settings, class-wide caches).
- Useful when you want to ensure only one thread can access a critical section across all objects.

## Instance-level (Normal) Lock
🔸 Defined as an instance variable, typically in __init__():
```commandline
class Counter:
    def __init__(self):
        self._lock = threading.Lock()  # Instance-level lock
        self.count = 0

```
🔹 Characteristics:
- Each object gets its own lock.
- Protects instance-specific state.
- Threads can operate on different instances concurrently.

# `__str__` vs `__repr__`
The __str__ method in Python is a special (magic) method used to define the "informal" or "user-friendly" string representation of an object.

```commandline
class Book:
    def __init__(self, title, author):
        self.title = title
        self.author = author

    def __str__(self):
        return f"'{self.title}' by {self.author}"

b = Book("1984", "George Orwell")
print(b)  # Output: '1984' by George Orwell

```
Without __str__, you'd get something like:
```commandline
<__main__.Book object at 0x7f2e9c8c8f40>
```

If __str__ is not defined, Python falls back to __repr__().
