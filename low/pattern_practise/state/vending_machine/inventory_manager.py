from low.pattern_practise.state.vending_machine.item import Item
from low.pattern_practise.state.vending_machine.item_type import ItemType


class InventoryManager:
    def __int__(self):
        self.inventory_details = {}   # we can maintain ItemType: list[Item]

    def display_inventory(self):
        print("Available Inventory: ")
        for item_type, items in self.inventory_details.items():
            print(f"Item Type: {item_type}, count: {len(items)}")

    def add_item(self, item: Item):
        # make it thread safe
        item_type = item.get_item_type()
        if item_type in self.inventory_details:
            self.inventory_details[item_type].append(item)
        else:
            self.inventory_details[item_type] = [item]

        print(f"Item: {item.get_item_type()} has been added into inventory")

    def update_inventory(self, items: list):
        for item in items:
            self.add_item(item)

    def is_item_available(self, item_type: str) -> bool:
        return item_type in self.inventory_details and len(self.inventory_details[item_type]) > 0

    def get_item(self, item_type: str) -> bool:
         if self.is_item_available(item_type):
             item = self.inventory_details[item_type].pop(0)
             print(f"Item: {item.get_item_type()} has been removed from inventory")
             return True
         else:
             return False

    def get_item_price(self, item_type: ItemType) -> float:
        item_type = str(item_type)
        if self.is_item_available(item_type):
            item = self.inventory_details[item_type][0]
            return item.get_price()

    def dispense_item(self, item_type: ItemType):
        if item_type in self.inventory_details:
            self.inventory_details[item_type].pop(0)
            print(f"Item: {item_type} has been dispensed")
        else:
            print(f"Item: {item_type} is not available in inventory")



