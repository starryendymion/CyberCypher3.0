from uagents import Agent,Context, Model
from uagents.setup import fund_agent_if_low
import pandas as pd
import joblib
from typing import List
from orderPlacing import Message

negotiator = Agent(
    name="Negotiator",
    port=8001,
    seed="an interesting seed for the NegotiatorAgent",
    endpoint=["http://127.0.0.1:8001/order"],
)

fund_agent_if_low(negotiator.wallet.address())


class Item:
    def __init__(self, name, demand, inventory):
        self.name = name
        self.demand = demand
        self.inventory = inventory

class Supplier:
    def __init__(self, name, stock, prices):
        self.name = name
        self.stock = stock
        self.prices = prices

class Items(Model):
    name: str
    price: float
    quantity: int

class ItemRequest(Model):
    name: str
    quantity: int

class ItemCheckResponse(Model):
    cost: float

class BestItem(Model):
    name: str
    supplier: str
    quantity: int 

@negotiator.on_interval(period=1.0)
async def interval_Ping(ctx:Context):
    ctx.logger.info("Negotiator is live!!")

@negotiator.on_message(model=Message,replies=BestItem)
async def handle_check_Stock(ctx: Context, sender: str, msg: Message):
    ctx.logger.info(f"MEssage recieved: [{msg}]")

    df = pd.read_csv('processed_dataset.csv')

    loaded_product_dict = joblib.load('product_dict.pkl')

    items = []
    suppliers = []

    for _, row in df.iterrows():
        product_name = row['product_names']
        demand_values = loaded_product_dict[product_name]['Last_30_weeks_sales']
        inventory_first_index = row['inventory'][0]

        item = Items(product_name, demand_values, inventory_first_index)
        supplier = Supplier(product_name, row['inventory'], [row['Supplier_A'], row['Supplier_B'], row['Supplier_C']])

        items.append(item)
        suppliers.append(supplier)

    best_item = min(items, key=lambda item: min(item.demand) - item.inventory)

    min_cost = float('inf')
    chosen_supplier = None

    for supplier in suppliers:
        stock = supplier.stock[items.index(best_item)]
        if stock >= min(best_item.demand):
            cost = sum(price * min(best_item.demand) for price in supplier.prices)
            if cost < min_cost:
                min_cost = cost
                chosen_supplier = supplier.name

    if chosen_supplier is None:
        chosen_supplier = min(suppliers, key=lambda supplier: supplier.stock[items.index(best_item)] - min(best_item.demand)).name

    print(f"Chosen Supplier: {chosen_supplier}")
    print(f"Best Item: {best_item.name}")

    ctx.storage.set("BuyItem", best_item.name)
    ctx.storage.set("BuySupplier", chosen_supplier)
    ctx.storage.set("BuyQuantity", min(best_item.demand))

    await ctx.send(sender, Message(msg="Order redy to be placed"))

if __name__ == "__main__":
    negotiator.run()