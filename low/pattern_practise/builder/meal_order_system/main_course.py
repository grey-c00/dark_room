from low.pattern_practise.builder.meal_order_system.meal_interface import MealInterface

from enum import Enum

class MainCourseTypes(Enum):
    """Enum for Main Course Types"""
    PASTA = "Pasta"
    RICE = "Rice"

class MainCourse(MealInterface):
    def __init__(self, main_cousre_type: MainCourseTypes, price: float):
        self.main_course_type = main_cousre_type
        self.price = price

    def describe(self):
        return f"Main Course: {self.main_course_type.value}"

    def get_price(self):
        return self.price
