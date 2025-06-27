from low.pattern_practise.builder.meal_order_system.meal_interface import MealInterface
from enum import Enum

class ComboTypes(Enum):
    HEALTHY_VEGETARIAN = "Healthy Vegetarian"
    CLASSIC_MEAT_LOVER = "Classic Meat Lover"


class MealCombo(MealInterface):
    def __init__(self, combo_type: ComboTypes, price: float):
        self.combo_type = combo_type
        self.price = price

    def describe(self):
        return f"Combo Type: {self.combo_type.value}"

    def get_price(self):
        return self.price