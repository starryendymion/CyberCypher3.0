from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low

from negotiator import ItemRequest, ItemCheckResponse, Items

supplierB = Agent(
    name="SupplierA",
    port=8003,
    seed="an interesting seed for the supplier B",
    endpoint=["http://127.0.0.1:8003/order"],
)

fund_agent_if_low(supplierB.wallet.address())

class BuyRequest(Model):
    name: str
    quantity: int

class BuyRequestResponse(Model):
    status: bool

supplierB_items = {
    1: Items(name="Utensil Dishwash Gel Lemon Pack Of 2", price=54.0, quantity=180),
    2: Items(name="Soogo Aria Whisky Glass Set of 6-320ml", price=18.0, quantity=600),
    3: Items(name="Glass Water Tumbler Set - Embassy Cool", price=30.0, quantity=450),
    4: Items(name="Khaman Dhokla Mix", price=75.0, quantity=225),
    5: Items(name="Frozen Green Peas", price=45.0, quantity=300),
    6: Items(name="Baby Skincare Wipes", price=90.0, quantity=270),
    7: Items(name="Face Wipes Tea Tree & Neem", price=24.0, quantity=540),
}

for (number, status) in supplierB_items.items():
    supplierB.storage.set(number, status.dict())

@supplierB.on_message(model=ItemRequest, replies=ItemCheckResponse)
async def handle_order_message(ctx: Context, sender: str, msg: ItemRequest):

    ctx.loggger.info("Item Request Recieved from "+sender)

    response = ItemCheckResponse(cost=-1)  

    for item in ctx.storage.data:
        if item.name == msg.name:
            if item.quantity >= msg.quantity:
                cost = item.price * msg.quantity
                response = ItemCheckResponse(cost=cost)
            else:
                response = ItemCheckResponse(cost=-1)
    
    await ctx.send(sender, response)

    ctx.logger.info("Response sent back ")

@supplierB.on_interval(period=1.0)
async def interval_Ping(ctx:Context):
    ctx.logger.info("SupplierA is live!!")

if __name__ == "__main__":
    supplierB.run()
