from low.pattern_practise.state.vending_machine.inventory_manager import InventoryManager
from low.pattern_practise.state.vending_machine.item import Item
from low.pattern_practise.state.vending_machine.item_type import ItemType
from low.pattern_practise.state.vending_machine.vending_machine import VendingMachine


def fill_inventory(inventory_manager: InventoryManager):
    tea_1 = Item(item_id="tea_1", price=10, item_type=ItemType.TEA)
    tea_2 = Item(item_id="tea_2", price=10, item_type=ItemType.TEA)

    inventory_manager.add_item(tea_1)
    inventory_manager.add_item(tea_2)

    return  inventory_manager

def get_sample_inventory_manger():
    inventory_manager = InventoryManager()
    inventory_manager = fill_inventory(inventory_manager)
    return inventory_manager


def test_idle_cancel():
    inventory_manager = get_sample_inventory_manger()
    vending_machine = VendingMachine(inventory_manager=inventory_manager)

    vending_machine.machine_display_inventory()

    vending_machine.machine_cancel_transaction()

def test_machine():
    test_idle_cancel()

if __name__=="__main__":
    test_machine()