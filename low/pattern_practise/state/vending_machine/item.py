from low.pattern_practise.state.vending_machine.item_type import ItemType


class Item:
    def __init__(self, item_type: ItemType, item_id: str, price: int):
        self.item_type = item_type
        self.item_id = item_id
        self.price = price


    def get_price(self) -> int:
        return int(self.price)

    def get_item_id(self) -> str:
        return str(self.item_id)

    def get_item_type(self) -> str:
        return str(self.item_type)

    def __str__(self):
        return f"Item ID: {self.item_id}, Item Type: {self.item_type}, Item Price: {self.price}"


item = Item(ItemType.TEA, "123", 10)
print("first")
print(item)
print("again")
print(f"item: {print(item)} has been added")
print(item)
print(item.get_item_type())

print(type(item.get_item_type()))
print(item.get_item_type())