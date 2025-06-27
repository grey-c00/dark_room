from low.pattern_practise.state.vending_machine.item_type import ItemType
from low.pattern_practise.state.vending_machine.states.operation_interface import VendingMachineStatesInterface
from low.pattern_practise.state.vending_machine.states.state_dispense_item import DispenseItemState
from low.pattern_practise.state.vending_machine.states.state_idle import IdleState
from low.pattern_practise.state.vending_machine.vending_machine import VendingMachine


class ReturnChangeState(VendingMachineStatesInterface):
    def __init__(self, vending_machine: VendingMachine):
        self.state_name = "Return Change State"
        self.vending_machine = vending_machine

    def collect_cash(self, cash: int):
        raise NotImplemented("can not collect cache again, you have already selected item, press cancel if you want to re-insert money")

    def select_item(self, item_type: ItemType):
        raise NotImplemented("Item has already been selected, please wait for the item to be dispensed")

    def return_change(self):
        self.vending_machine.return_change()
        self.vending_machine.update_machine_state(DispenseItemState(self.vending_machine))
        self.vending_machine.state.dispense_item()


    def dispense_item(self):
        raise NotImplemented("Dispense item action is not allowed in ready state")

    def cancel_transaction(self):
        self.vending_machine.cancel_transaction()
        self.vending_machine.update_machine_state(IdleState(self.vending_machine))


