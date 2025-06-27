from low.pattern_practise.builder.meal_order_system.combo import MealCombo
from low.pattern_practise.builder.meal_order_system.main_course import MainCourse
from low.pattern_practise.builder.meal_order_system.side_course import SideCourse


class MealBuilder:
    def __init__(self):
        self.meal_combo = None
        self.main_course = None
        self.side_course = None

    def add_main_course(self, main_course: MainCourse):
        self.main_course = main_course

    def add_side_course(self, side_course: SideCourse):
        self.side_course = side_course

    def add_combo(self, combo: MealCombo):
        self.meal_combo = combo

    def describe_main_course(self):
        if self.main_course:
            return self.main_course.describe()
        return ""

    def build(self):
        return self


    def describe(self):




