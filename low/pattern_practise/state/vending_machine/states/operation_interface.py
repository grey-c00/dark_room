from abc import ABC, abstractmethod

from low.pattern_practise.state.vending_machine.item_type import ItemType


class VendingMachineStatesInterface(ABC):
    @abstractmethod
    def collect_cash(self, cash: int):
        pass

    @abstractmethod
    def select_item(self, item_type: ItemType):
        pass

    @abstractmethod
    def return_change(self):
        pass

    @abstractmethod
    def dispense_item(self):
        pass

    @abstractmethod
    def cancel_transaction(self):
        pass
