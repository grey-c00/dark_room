from low.pattern_practise.builder.meal_order_system.meal_interface import MealInterface
from enum import Enum

class SideCourseType(Enum):
    """Enum for Side Course Types"""
    FRIES = "Fries"
    SALAD = "Salad"
    ROLLS = "Rolls"


class SideCourse(MealInterface):
    def __init__(self, side_course_type: SideCourseType, price: float):
        self.side_course_type = side_course_type
        self.price = price

    def describe(self):
        return f"Side Course: {self.side_course_type}"

    def get_price(self):
        return self.price