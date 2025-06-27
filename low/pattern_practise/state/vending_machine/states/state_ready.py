from low.pattern_practise.state.vending_machine.item_type import ItemType
from low.pattern_practise.state.vending_machine.states.operation_interface import VendingMachineStatesInterface
# from low.pattern_practise.state.vending_machine.states.state_idle import IdleState
from low.pattern_practise.state.vending_machine.states.state_return_change import ReturnChangeState
from low.pattern_practise.state.vending_machine.vending_machine import VendingMachine


class ReadyState(VendingMachineStatesInterface):
    def __init__(self, vending_machine: VendingMachine):
        self.state_name = "Ready state"
        self.vending_machine = vending_machine

    def collect_cash(self, cash: int):
        raise NotImplemented("can not collect cache again, cache is already collected")

    def select_item(self, item_type: ItemType):
        # consider that whatever item, we select that will be available
        print("item selected, moving to dispense item stage...")
        self.vending_machine.select_item(item_type)
        self.vending_machine.update_machine_state(ReturnChangeState(self.vending_machine))

    def return_change(self):
        raise NotImplemented("return change action is not allowed in ready state, either press cancel to get full refund")

    def dispense_item(self):
        raise NotImplemented("Dispense item action is not allowed in ready state")

    def cancel_transaction(self):
        self.vending_machine.cancel_transaction()
        # self.vending_machine.update_machine_state(IdleState(self.vending_machine))