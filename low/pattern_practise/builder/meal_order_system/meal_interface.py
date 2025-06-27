from abc import ABC, abstractmethod

class MealInterface:
    @abstractmethod
    def describe(self):
        """Describe the meal"""
        pass

    @abstractmethod
    def get_price(self):
        """Get the price of the meal"""
        pass




