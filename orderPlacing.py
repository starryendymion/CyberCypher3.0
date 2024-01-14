from uagents import Agent,Context, Model
from uagents.setup import fund_agent_if_low

from supplierA import BuyRequest, BuyRequestResponse

orderPlacingAgent = Agent(
    name="OrderPlacer",
    port=8000,
    seed="an interesting seed for the orderplacingagent",
    endpoint=["http://127.0.0.1:8000/order"],
)

class Message(Model):
    msg: str

class OrderQueryResponse(Model):
    msg: str

NegotiatorAgentAddress = "agent1qd2lqedpqpuf9v9gse6ckeczt3zmk7223008mp238eq5z6wfld5jyzcdssh"
AddressSupplierA = "agent1qg0r0xmts543u09zy4sf27qq2t6m4g7ykme2tt9h7rzyfg7ku2zqcmcn50k"
AddressSupplierB = "agent1qdr4u0fjx8rv8lpy5yuelr7fqwx85a9snqqzkw5j4ax6kzjsh8wdzwpxg42"
AddressSupplierC = "agent1qwyvqg9rjy3xekdveh28vz9ttvd7yur7wv0q076wxu6fnxhl0w78v8hvvgp"

@orderPlacingAgent.on_interval(period=2.0)
async def place_order(ctx: Context):
    
    try:
        await ctx.send(NegotiatorAgentAddress, Message(msg="Check Orders"))
        ctx.logger.info("Checking orders Currently")
    except Exception as e:
        print(f"Error occurred during await: {e}")

@orderPlacingAgent.on_message(BuyRequestResponse)
async def handleBuyRequestResponse(ctx:Context, sender:str, msg: BuyRequestResponse):
    ctx.logger.info("Received message from %s: %s", sender, msg.status)
    ctx.logger.info("Order status: "+msg.status)

@orderPlacingAgent.on_message(Message)
async def handle_Response_message(ctx: Context, sender:str, msg: OrderQueryResponse):
    ctx.logger.info("Received message from %s: %s", sender, msg.msg)

    if ctx.storage.get("BuySupplier") == "A":
        await ctx.send(AddressSupplierA, BuyRequest(item=ctx.storage.get("BuyItem"), quantity=ctx.storage.get("BuyQuantity")))
    elif ctx.storage.get("BuySupplier") == "B":
        await ctx.send(AddressSupplierB, BuyRequest(item=ctx.storage.get("BuyItem"), quantity=ctx.storage.get("BuyQuantity")))
    elif ctx.storage.get("BuySupplier") == "C":
        await ctx.send(AddressSupplierC, BuyRequest(item=ctx.storage.get("BuyItem"), quantity=ctx.storage.get("BuyQuantity")))

    
fund_agent_if_low(orderPlacingAgent.wallet.address())

if __name__ == "__main__":
    orderPlacingAgent.run()

