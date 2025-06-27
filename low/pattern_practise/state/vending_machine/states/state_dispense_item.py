from low.pattern_practise.state.vending_machine.item_type import ItemType
from low.pattern_practise.state.vending_machine.states.operation_interface import VendingMachineStatesInterface


class DispenseItemState(VendingMachineStatesInterface):
    def __init__(self, vending_machine):
        self.state_name = "Dispense Item State"
        self.vending_machine = vending_machine

    def collect_cash(self, cash: int):
        raise NotImplemented("can not collect cache in dispense state")

    def select_item(self, item_type: ItemType):
        raise NotImplemented("can not select item in dispense state")

    def return_change(self):
        raise NotImplemented("can not return change in dispense state")

    def dispense_item(self):
        from low.pattern_practise.state.vending_machine.states.state_idle import IdleState

        self.vending_machine.dispense_item()
        self.vending_machine.update_machine_state(IdleState(self.vending_machine))

    def cancel_transaction(self):
        raise NotImplemented("can not cancel in transaction state")