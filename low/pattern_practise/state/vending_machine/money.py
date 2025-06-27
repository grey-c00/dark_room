from low.pattern_practise.state.vending_machine.money_type import MoneyType


class Money:
    def __init__(self, money_type: MoneyType, amount: int):
        # perform validation using some decorator functionality
        self.money_type = money_type
        self.amount = amount

    def get_money_amount(self):
        return self.amount

