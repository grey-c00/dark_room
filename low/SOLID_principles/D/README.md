In the SOLID principles, the “D” stands for the Dependency Inversion Principle.

## 🧱 Dependency Inversion Principle (DIP)
Definition:

High-level modules should not depend on low-level modules. Both should depend on abstractions.
Abstractions should not depend on details. Details should depend on abstractions.

## ✅ What It Means
Don’t hardcode concrete implementations inside your classes.

Rely on interfaces or abstract classes instead.

This allows flexible wiring of components and makes code easier to test and maintain.


## ❌ Without DIP
```commandline
class MySQLDatabase:
    def connect(self):
        print("Connecting to MySQL")

class App:
    def __init__(self):
        self.db = MySQLDatabase()  # tightly coupled!

    def run(self):
        self.db.connect()


# Now App is tightly bound to MySQL, which makes it hard to:
# swap in another database (like PostgreSQL)
# test using mocks
```

## ✅ With DIP
````commandline
from abc import ABC, abstractmethod

# Abstraction
class Database(ABC):
    @abstractmethod
    def connect(self):
        pass

# Low-level module
class MySQLDatabase(Database):
    def connect(self):
        print("Connecting to MySQL")

# High-level module
class App:
    def __init__(self, db: Database):
        self.db = db

    def run(self):
        self.db.connect()

# Inject the dependency
db = MySQLDatabase()
app = App(db)
app.run()

````
Now:

App depends on an interface (Database), not a specific implementation.
You can easily plug in a PostgreSQL Database or MockDatabase without changing the App code.


## ✅ Benefits
- Loose coupling
- Better testability (use mock implementations)
- Easier to extend or replace components

