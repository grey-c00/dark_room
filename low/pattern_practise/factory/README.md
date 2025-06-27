## 🏭 Factory Design Pattern – Overview
The Factory Pattern is a creational design pattern that provides an interface for creating objects in a superclass but allows subclasses to alter the type of objects that will be created.

### Problem if not used - 
1. Violates the Open/Closed Principle (OCP)
- OCP says: "Software should be open for extension but closed for modification."
- With if-else, every time you add a new class (like Rectangle), you must modify the existing code:
- If you have if-else logic scattered in 5 places, you must change it in 5 places. That’s error-prone and harder to maintain.

2. Tight Coupling
- Your client code must know all the possible classes (Circle, Square, Rectangle...), so it becomes tightly coupled to specific implementations.
- This makes it:
- Harder to test (you can’t easily mock)
- Harder to reuse in another context
- Difficult to replace classes with new versions

