from abc import ABC, abstractmethod

from low.pattern_practise.decorator.coffee_machine.base_drinks.coffee import CoffeeInterface


class AddOn(CoffeeInterface):
    def __init__(self, coffee: CoffeeInterface):
        self.coffee = coffee
        self.name = "NOne"
        self.price = 10

    def get_name(self):
        return self.name

    def describe(self):
        return f"{self.coffee.describe()} , {self.name}"

    def get_price(self):
        return self.coffee.get_price() + self.price


class Milk(AddOn):
    def __init__(self, coffee: CoffeeInterface):
        super().__init__(coffee)
        self.name = "Milk"
        self.price = 10


class Mocha(AddOn):
    def __init__(self, coffee: CoffeeInterface):
        super().__init__(coffee)
        self.name = "Mocha"
        self.price = 100
