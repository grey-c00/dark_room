## 🧱 What Is the Bridge Pattern?
The Bridge Pattern is used to decouple an abstraction from its implementation, so the two can vary independently.

In simpler terms:

It "bridges" the gap between an abstract interface and the concrete implementation, allowing them to change without affecting each other.


## 📌 Motivation
Imagine you're designing a system with:

Multiple types of devices (TV, Radio)

Multiple ways to control them (RemoteControl, SmartRemote)

If you use inheritance alone, you'd end up with combinations like:

TVWithRemote

TVWithSmartRemote

RadioWithRemote

RadioWithSmartRemote

🎯 This is class explosion again — the Bridge pattern solves it differently than Decorator.

## 🧠 Real-World Analogy
Think of a remote control (the abstraction) and a TV or Radio (the implementation). The remote should work regardless of the brand of the device — we don’t want to rewrite the remote every time we create a new device.

## 🧱 Structure of Bridge Pattern
Abstraction (e.g., RemoteControl)
→ has a reference to →
Implementor (e.g., Device)

Then we can extend both abstraction and implementation independently.

```commandline
Abstraction
  |
  └── RefinedAbstraction
             |
             → Implementor
                     |
                     └── ConcreteImplementor

```


## ✅ When to Use Bridge Pattern
You want to avoid a permanent binding between abstraction and implementation.

You need to combine multiple variations of abstractions and implementations (like in cross-platform applications).

You want to switch implementations at runtime.

You’re dealing with orthogonal dimensions (like shape & color, device & control, or platform & GUI).

