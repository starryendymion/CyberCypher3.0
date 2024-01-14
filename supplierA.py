from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low

from negotiator import ItemRequest, ItemCheckResponse, Items

supplierA = Agent(
    name="SupplierA",
    port=8002,
    seed="an interesting seed for the supplier A",
    endpoint=["http://127.0.0.1:8002/order"],
)

fund_agent_if_low(supplierA.wallet.address())

supplierA_items = {
    1: Items(name="Glass Water Tumbler Set - Acme Elite", price=30.0, quantity=450),
    2: Items(name="Smart Kit With Bag", price=75.0, quantity=225),
    3: Items(name="Peek A Boo Chocochip Cookies Pack Of 4", price=45.0, quantity=300),
    4: Items(name="Potato Regular Offer", price=90.0, quantity=270),
    5: Items(name="Embassy Juice set of 6", price=24.0, quantity=540),
    6: Items(name="Kadak Tea Classic Blend", price=15.0, quantity=750),
    7: Items(name="Frozen Green Peas", price=36.0, quantity=360),
}

for (number, status) in supplierA_items.items():
    supplierA.storage.set(number, status.dict())

@supplierA.on_message(model=ItemRequest, replies=ItemCheckResponse)
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

class BuyRequest(Model):
    name: str
    quantity: int

class BuyRequestResponse(Model):
    status: bool

@supplierA.on_message(model=BuyRequest, replies=BuyRequestResponse)
async def handleBuyRequest(ctx: Context, sender: str, msg: BuyRequest):
    ctx.logger.info("Buy Request Recieved from "+sender)

    sold = False
    for item in ctx.storage.data:
        if item.name == msg.name:
            if item.quantity >= msg.quantity:
                item.quantity = item.quantity - msg.quantity
                ctx.storage.set(item.name, item.dict())
                ctx.logger.info("Item sold to "+sender)
                sold = True
            else:
                ctx.logger.info("Item not available for "+sender)

    await ctx.send(sender, BuyRequestResponse(status=sold))

@supplierA.on_interval(period=1.0)
async def interval_Ping(ctx:Context):
    ctx.logger.info("SupplierA is live!!")

if __name__ == "__main__":
    supplierA.run()
