## 📌 What is the Decorator Pattern?
The Decorator Pattern is a structural design pattern that allows you to dynamically add new behavior to objects without altering their structure. It's a flexible alternative to subclassing for extending functionality.

### ✅ Why Is It Used?
Dynamic Behavior Extension: Instead of modifying existing code or using inheritance, decorators wrap an object to add new responsibilities at runtime.

Open/Closed Principle: The pattern supports the Open/Closed Principle — classes are open for extension but closed for modification.

Flexible Design: You can stack multiple decorators together to build complex behavior from simple components.

Avoids Class Explosion: Instead of creating many subclasses for every behavior combination, decorators let you mix behaviors as needed.
### what is class explosion?
Class explosion is a design problem where you end up with a large number of classes because you're trying to represent every possible combination of features or behaviors using inheritance.

[You can not keep on creating classes for each and every possible combination]

### Benefits of use - 
1. Behaviour can be wrapped not just at the compile time but at runtime as well
2. Extend functionality without making modification in base (or some subclass) class
3. Transparent Extension of Functionality: Decorators maintain the same interface as the object they wrap, which makes them easy to use interchangeably.
4. Cross-Cutting Concerns: Ideal for modularizing cross-cutting concerns like:Logging ,Caching , Security ,Validation ,Retry logic
5. Simplifying Complex Behavior 
   - Complex behavior can be broken into simple, composable parts.
   - Each decorator adds a single concern, making the system easier to understand, test, and modify.
