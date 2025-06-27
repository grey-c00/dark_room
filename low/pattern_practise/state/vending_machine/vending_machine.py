from low.pattern_practise.state.vending_machine.inventory_manager import InventoryManager
from low.pattern_practise.state.vending_machine.item_type import ItemType
from low.pattern_practise.state.vending_machine.states.state_idle import IdleState
from low.pattern_practise.state.vending_machine.states.operation_interface import VendingMachineStatesInterface


class VendingMachine:
    def __init__(self, inventory_manager: InventoryManager, state: VendingMachineStatesInterface = IdleState):
        self.inventory_manager = inventory_manager
        self.state = state
        self.selected_item = None
        self.collected_cash = None

    def update_machine_state(self, state:VendingMachineStatesInterface):
        self.state = state
        print(f"machine is set in : {self.state.state_name}")

    def collect_cash(self, cash: int):
        self.collected_cash = cash

    def select_item(self, item_type: ItemType):
        print(f"selected item: {item_type}")
        self.selected_item = item_type

    def cancel_transaction(self):
        print(f"Transaction cancelled, returning full refund, returning money: {self.collected_cash}")
        self.collected_cash = None
        self.selected_item = None

    def return_change(self):
        item_price = self.inventory_manager.get_item_price(self.selected_item)
        if item_price > self.collected_cash:
            print("Not enough cash, please insert more cash")
            return
        change = self.collected_cash - item_price
        print(f"returning change: {change}")

    def dispense_item(self):
        item_price = self.inventory_manager.get_item_price(self.selected_item)
        if item_price > self.collected_cash:
            print("Not enough cash, please insert more cash")
            return
        self.inventory_manager.dispense_item(self.selected_item)
        print(f"item dispensed: {self.selected_item}")
        self.collected_cash = None
        self.selected_item = None


    def machine_display_inventory(self):
        self.inventory_manager.display_inventory()

    def machine_collect_cash(self, cash: int):
        self.state.collect_cash(cash)

    def machine_select_item(self, item_type: ItemType):
        self.state.select_item(item_type)

    def machine_return_change(self):
        self.state.return_change()

    def machine_dispense_item(self):
        self.state.dispense_item()

    def machine_cancel_transaction(self):
        self.state.cancel_transaction()

