In SOLID principles, the “L” stands for the Liskov Substitution Principle (LSP).

## Liskov Substitution Principle (LSP)
Definition:

Objects of a superclass should be replaceable with objects of its subclasses without affecting the correctness of the program.

This was introduced by Barbara Liskov in 1987.

✅ In Simple Terms:
If class S is a subclass of class T, then objects of type T should be replaceable with objects of type S without breaking the program logic.

#### **In other terms:** child class should not narrow down parent class' functionality.

❌ Violation Example:
```commandline
class Bird:
    def fly(self):
        pass

class Sparrow(Bird):
    def fly(self):
        print("Sparrow flying")

class Ostrich(Bird):
    def fly(self):  # Ostriches can’t fly!
        raise Exception("Ostrich can't fly!")


def make_it_fly(bird: Bird):
    bird.fly()

# Now if you do:

make_it_fly(Sparrow())  # OK
make_it_fly(Ostrich())  # 💥 Exception — violates LSP

```

✅ How to Fix This
Use proper abstractions:
```commandline
class Bird:
    pass

class FlyingBird(Bird):
    def fly(self):
        pass

class Sparrow(FlyingBird):
    def fly(self):
        print("Sparrow flying")

class Ostrich(Bird):
    def walk(self):
        print("Ostrich walking")

# Now, only FlyingBirds are expected to fly(), and you don’t violate LSP.


```



### 🎯 Key Idea:
Subtypes must honor the contract of their base types — behaviorally.

If a derived class changes:

input/output expectations,

side effects,

or postconditions,

…it violates LSP.