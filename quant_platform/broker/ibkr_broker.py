from ib_insync import IB, Stock, util
from .base_broker import BaseBroker, Order
from quant_platform.utils.logger import logger

class IBKRBroker(BaseBroker):
    """
    连接本地 TWS / IB Gateway，默认端口 7497（纸交易）或 7496（实盘）。
    启动 TWS 后：Edit ▸ Global Config ▸ API ▸ 允许连接＋Trusted IP.
    """
    def __init__(self, host="127.0.0.1", port=7497, client_id=1):
        self.ib = IB()
        self.ib.connect(host, port, clientId=client_id)
        logger.info("Connected to IBKR: %s", self.ib.connectionTime())
    
    def submit(self, order: Order):
        contract = Stock(order.symbol, "SMART", "USD")
        ib_order = util.marketOrder(order.side.upper(), order.qty)
        trade = self.ib.placeOrder(contract, ib_order)
        trade.waitUntilDone()
        logger.info("IBKR %s %s@%s filled", order.side, order.qty, order.symbol)
        return {"orderId": trade.order.orderId, "status": trade.orderStatus.status}
    
    def positions(self):
        pos_dict = {}
        for p in self.ib.positions():
            if p.contract.secType == "STK":
                pos_dict[p.contract.symbol] = p.position
        return pos_dict
    
    def disconnect(self):
        self.ib.disconnect()