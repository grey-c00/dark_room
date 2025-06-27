# Builder Desing pattern

The Builder Design Pattern is a creational design pattern used to construct complex objects step by step. It separates the construction of an object from its representation, allowing the same construction process to create different representations.

Key Concepts:
It’s useful when an object has many optional parameters or complex construction logic.

It encapsulates the construction logic in a separate Builder class.

Promotes immutability and readability in object creation.

## Advantages:
Improves code readability with method chaining.

Helps manage object construction complexity.

Makes it easier to create immutable or variant objects.

## how the Builder pattern differs from using a constructor with lots of parameters?:
 the same can be implemented via constructor with lots of parameters, but it can lead to:
 
Problems:
- Easy to misorder arguments.
- Hard to tell what each argument means at the call site.
- Not flexible if you want to skip or reorder optional parts.
- Can become messy if the number of parameters grows.

## ?? How is it different from decorator pattern?
Use Decorator when…	                            ||  Use Builder when…
- You want to extend object behavior at runtime ||	You want to construct complex objects step-by-step
- You need to support combinations of features	|| You want to avoid constructor overloading
- You follow Open/Closed Principle for behavior	|| You want to separate construction and representation
