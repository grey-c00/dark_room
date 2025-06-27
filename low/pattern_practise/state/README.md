## 🧱 What Is the State Pattern?
The State Pattern allows an object to change its behavior when its internal state changes, as if the object has changed its class.

Instead of using if-else or switch-case blocks to handle state transitions, the State Pattern delegates behavior to state-specific classes.

## 📦 Core Idea
You encapsulate state-specific behavior in separate state classes and delegate the current behavior to the object’s current state.

## 📌 Motivation
Imagine a media player:
    States: Playing, Paused, Stopped

Buttons behave differently depending on the state:

Pressing "Play" while playing might do nothing.

Pressing "Pause" while playing pauses the song.

Without the State Pattern, you'd have messy conditionals:

## ✅ When to Use the State Pattern
When an object must change its behavior depending on its internal state.

When conditional logic based on state becomes too complex and hard to manage.

When you want to encapsulate state-specific behavior and isolate it from the main logic.

## 🧠 Real-World Analogies
Traffic lights: Green → Yellow → Red. Each state knows what to do next.

ATMs: Card inserted → PIN entered → Transaction selected.

Vending machines: Insert coin → Select item → Dispense → Idle.