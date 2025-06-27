✅ What is the Single Responsibility Principle?
Definition: A class should have only one reason to change, meaning it should have only one job or responsibility.

It’s about separating concerns — each class or module should focus on a single part of the functionality.

## 🔧 Real-World Analogy
### Imagine you're designing a printer software:

- It can print documents ✅
- It can also save logs to a file ❌
- And maybe also send error reports via email ❌

➡️ This class now has multiple reasons to change:

- If the printing logic changes
- If logging format changes
- If email sending changes

This violates SRP.

## 🧠 Why SRP Matters
Easier to test (unit tests target specific functionality)
Easier to maintain and update
Encourages reuse and clear structure
Reduces bugs introduced by unrelated changes