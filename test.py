from pycoingecko import CoinGeckoAPI

cg = CoinGeckoAPI()
from dateutil import tz
import datetime


# print(price["ethereum"]["usd"])
tokens = ["WETH", "DAI", "USDC", "AAVE", "COMP", "CRV", "SUSHI", "WBTC"]

for coin in tokens:
    print(f'{coin}: {cg.get_price(ids=coin, vs_currencies="usd")}')
