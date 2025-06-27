from abc import ABC, abstractmethod

from low.pattern_practise.decorator.coffee_machine.base_drinks.constants import *


class CoffeeInterface(ABC):
    @abstractmethod
    def get_name(self):
        pass

    @abstractmethod
    def describe(self):
        pass

    @abstractmethod
    def get_price(self):
        pass


class EspressoCoffee(CoffeeInterface):
    def __init__(self):
        self.name = espresso_name
        self.price = espresso_price

    def get_name(self):
        return self.name

    def describe(self):
        return str(self.name)

    def get_price(self):
        return self.price


class HouseBlendCoffee(CoffeeInterface):
    def __init__(self):
        self.name = house_blend_name
        self.price = house_blend_price

    def get_name(self):
        return self.name

    def describe(self):
        return str(self.name)

    def get_price(self):
        return self.price


class DarkRoastedCoffee(CoffeeInterface):
    def __init__(self):
        self.name = dark_roast_name
        self.price = dark_roast_price

    def get_name(self):
        return self.name

    def describe(self):
        return str(self.name)

    def get_price(self):
        return self.price

