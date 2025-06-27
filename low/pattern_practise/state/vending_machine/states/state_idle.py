from low.pattern_practise.state.vending_machine.item_type import ItemType
from low.pattern_practise.state.vending_machine.states.state_ready import ReadyState
from low.pattern_practise.state.vending_machine.states.operation_interface import VendingMachineStatesInterface
from low.pattern_practise.state.vending_machine.vending_machine import VendingMachine


class IdleState(VendingMachineStatesInterface):
    def __init__(self, vending_machine: VendingMachine):
        self.state_name = "Idle State"
        self.vending_machine = vending_machine

    def collect_cash(self, cash: int):
        print("collected cash, moving to read stage...")
        self.vending_machine.collect_cash(cash)
        self.vending_machine.update_machine_state(ReadyState(self.vending_machine))

    def select_item(self, item_type: ItemType):
        raise NotImplemented("can't select item in idle state, please insert money first")

    def return_change(self):
        raise NotImplemented("return change action is not allowed in idle state")

    def dispense_item(self):
        raise NotImplemented("Dispense item action is not allowed in idle state")

    def cancel_transaction(self):
        print("Not effect of cancel transaction in idle state")