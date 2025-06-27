from low.pattern_practise.decorator.coffee_machine.base_drinks.coffee import EspressoCoffee
from low.pattern_practise.decorator.coffee_machine.add_ons.add_ons import Milk, Mocha


def test_espresso_milk():
    base_coffee = EspressoCoffee()
    coffee = Milk(base_coffee)

    print("Coffee Name: ", coffee.describe())
    print("price: ", coffee.get_price())


def test_espresso_milk_mocha():
    base_coffee = EspressoCoffee()
    coffee = Mocha(Milk(base_coffee))

    print("Coffee Name: ", coffee.describe())
    print("price: ", coffee.get_price())


def test_coffee_machine():
    test_espresso_milk()
    test_espresso_milk_mocha()


if __name__=="__main__":
    test_coffee_machine()