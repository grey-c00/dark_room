# Object Initialization Hierarchy in Python
## `__new__`: Object Creation

This is the first step in the object creation process. __new__ is a special method responsible for creating the instance.

It's called when a new object is being created (i.e., when you invoke the class like MyClass()).

It allocates memory for the object and returns the new instance.

```commandline
def __new__(cls, *args, **kwargs):
    print("Creating an object")
    return super().__new__(cls)
    
The reason we pass cls (not self) in the __new__ method is because __new__ is a class method, not an instance method.
__new__ is called at the class level, not the instance level.
The argument cls refers to the class itself (i.e., MyClass), not the instance (self).
When __new__ is called, you are still in the process of creating the object, so you work with the class to control how the instance is created.
```


## `__init_`_: Object Initialization

After the object is created, __init__ is called to initialize the object's attributes.

This is where you typically set up instance variables (like self.name = "example").

Unlike __new__, __init__ doesn't return anything; it just modifies the already created object.

## `__call__` (if using a callable object or metaclass)

If a class has the __call__ method, it makes the instance callable, i.e., you can treat the object like a function.

This is often used in Singleton patterns or decorator patterns where an object needs to have specific behavior when called directly (e.g., obj()).

### key points:
the `__call__` method is not invoked during object initialization.
we don’t always have a `__call__` method defined in our classes — unless we explicitly define it or inherit it from a parent class that does.
so to make object callable we need to define the `__call__` method in the class or inherit from parent class.
```commandline
class_object = SomeClass()
class_object.some_function()  # this is a simple function call
class_object() # this is a call to the __call__ method
```

why there is a need to make object callable, lets take an example - 
```commandline
import time

class TimerDecorator:
    def __init__(self, func):
        self.func = func  # Store the function to be decorated

    def __call__(self, *args, **kwargs):
        start_time = time.time()           # Start timing
        result = self.func(*args, **kwargs)  # Call the original function
        end_time = time.time()             # End timing
        print(f"Execution time: {end_time - start_time:.6f} seconds")
        return result


@TimerDecorator
def slow_function():  # this is equivalenet to slow_function = TimerDecorator(slow_function) - which is an object of TimerDecorator class
    time.sleep(2)
    print("Done!")

slow_function()  # it is equivalent to calling object of TimerDecorator class, hence we need to make the class as object callable by definding __call__ method and implement it as per the need.

```

## `Metaclasses` (optional, but important for advanced control)

Metaclasses control the class creation process itself. They are the "classes" of classes.

When a class is defined, its metaclass is used to control its behavior — including its instantiation via __new__, __call__, and other methods.


# what is super()
super() is a built-in function in Python that gives you access to methods of a parent (or superclass) from within a child (or subclass). It's commonly used to extend or override behavior from the base class without rewriting the entire method.


# what does **__init__** do?
The __init__ method in Python is a special method used for initializing newly created objects. It is called automatically when a new instance of a class is created, just after the object is instantiated (i.e., after the memory for the object is allocated).

The primary purpose of __init__ is to initialize the object's attributes and perform any setup operations needed after the object is created. It is not a constructor in the traditional sense (as in C++ or Java), because the object is already created before __init__ is called. Instead, think of it as an initializer.

### Key Points:
__init__ is called automatically when an object is created using ClassName().

It takes at least one argument, self, which is the instance of the object being created.

You can pass additional arguments to __init__ when creating the object to initialize attributes.

It doesn't return anything — it only modifies the object.

# composition:
Composition in Python is another object-oriented programming (OOP) principle where a class is composed of one or more objects from other classes, rather than inheriting from them. It represents a "has-a" relationship, in contrast to inheritance's "is-a" relationship.



# Abstract methods, concrete methods, and abstract properties in Python
Read it here: https://www.geeksforgeeks.org/abstract-classes-in-python/