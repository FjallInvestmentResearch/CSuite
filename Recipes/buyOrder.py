import CSuite

# This Recipe sends a verified order for 1 Binance token

# Step 1: Connect with Binance Client
client = CSuite.CSuite.BConnector.connector.connect_client('file.json')

# Step 2: Get token trade parameters via the ledger
ledger = CSuite.CSuite.CTrader.orderBook.build_ledger(client, ['BNBUSDT'])

# Step 3: Get the latest quote and save the best bid for 'passive execution'
price = float(CSuite.CSuite.CTrader.orderBook.get_quote(client, 'BNBUSDT')[1][0])

# Step 4: Send a Limit Order for 1 token of BNB with FOK time and no SL/TP.
# Order parameters are verified through the downloaded ledger which checks for minQty, minNominal etc.
order = CSuite.CSuite.CTrader.orderEntry.LimitOrder(client, price, 1, 0, 'BNBUSDT', 'FOK').verified_submit(ledger)
