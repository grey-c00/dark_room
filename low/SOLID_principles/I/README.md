In the SOLID principles, the "I" stands for the Interface Segregation Principle (ISP).

## 🧱 Interface Segregation Principle (ISP)
Definition:

Clients should not be forced to depend on interfaces they do not use.

### ✅ What It Means:
Split large, fat interfaces into smaller, specific ones.

A class should only implement methods it actually uses.

Avoid forcing a class to implement irrelevant or unused behavior.


### ❌ Violation Example:
```commandline
class Machine:
    def print(self): pass
    def scan(self): pass
    def fax(self): pass

class OldPrinter(Machine):
    def print(self): print("Printing")
    def scan(self): raise NotImplementedError("Scan not supported")
    def fax(self): raise NotImplementedError("Fax not supported")

# Here, OldPrinter is forced to implement scan and fax even though it doesn't support them. This violates ISP.

```


### ✅ Following ISP (Segregated Interfaces):
```commandline
class Printer:
    def print(self): pass

class Scanner:
    def scan(self): pass

class FaxMachine:
    def fax(self): pass

class SimplePrinter(Printer):
    def print(self):
        print("Printing...")

class AllInOnePrinter(Printer, Scanner, FaxMachine):
    def print(self):
        print("Printing...")
    def scan(self):
        print("Scanning...")
    def fax(self):
        print("Faxing...")
```
### 🧠 Real-World Analogy:
Think of a universal remote with 50 buttons — if your TV only uses 5 of them, it’s better to have a custom remote with just those 5.


### ✅ Benefits:
Promotes high cohesion and low coupling

Easier to understand, maintain, and test

Prevents "empty method" smells

