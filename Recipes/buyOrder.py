import CTrader

# This Recipe sends a verified order for 1 Binance token

# Step 1: Connect with Binance Client
client = CTrader.connector.connect_client('file.json')

# Step 2: Get token trade parameters via the ledger
ledger = CTrader.orderbook.build_ledger(client, ['BNBUSDT'])

# Step 3: Get the latest quote and save the best bid for 'passive execution'
price = float(CTrader.orderbook.get_quote(client, 'BNBUSDT')[1][0])

# Step 4: Send a Limit Order for 1 token of BNB with FOK time and no SL/TP.
# Order parameters are verified through the downloaded ledger which checks for minQty, minNominal etc.
order = CTrader.orderEntry.LimitOrder(client, price, 1, 0, 'BNBUSDT', 'FOK').verified_submit(ledger)