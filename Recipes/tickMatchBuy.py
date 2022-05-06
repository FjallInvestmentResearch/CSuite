import CSuite.CSuite as C

# Step 1: Connect Binance Client
client = C.BConnector.connect_client('global.json')

# Step 2: Build Ledger
ledger = C.CTrader.build_ledger(client, ['BNBUSDT'])
tickSize = float(ledger.iloc['BNBUSDT']['tickSize'])

# Step 3: Send Order
order = C.CTrader.tick_match(client=client, ticker='ADAUSDT', size=2,
                             tickSize=tickSize, distance=3, retry=25, refresh=1)
