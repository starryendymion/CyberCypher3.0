from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low

from negotiator import ItemRequest, ItemCheckResponse, Items

supplierC = Agent(
    name="SupplierA",
    port=8004,
    seed="an interesting seed for the supplier C",
    endpoint=["http://127.0.0.1:8004/order"],
)
fund_agent_if_low(supplierC.wallet.address())


supplierC_items = {
    1: Items(name="Ec Octave Water Tumbler Set", price=8.0, quantity=180),
    2: Items(name="Chicken Nuggets", price=5.0, quantity=250),
    3: Items(name="Namkeen Khatta Meetha", price=36.0, quantity=360),
    4: Items(name="Toilet Cleaner Bt", price=54.0, quantity=180),
    5: Items(name="Soogo Aria Water Glass Set of 6- 260ml", price=18.0, quantity=600),
    6: Items(name="Glass Water Tumbler Set - Egypt", price=30.0, quantity=450),
    7: Items(name="Kadak Tea Classic Blend", price=75.0, quantity=225),
}

for (number, status) in supplierC_items.items():
    supplierC.storage.set(number, status.dict())

class BuyRequest(Model):
    name: str
    quantity: int

class BuyRequestResponse(Model):
    status: bool

@supplierC.on_message(model=ItemRequest, replies=ItemCheckResponse)
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

@supplierC.on_interval(period=1.0)
async def interval_Ping(ctx:Context):
    ctx.logger.info("SupplierA is live!!")

if __name__ == "__main__":
    supplierC.run()
