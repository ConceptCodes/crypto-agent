from typing import Annotated

from langchain_core.tools import tool
from langchain_core.tools import create_retriever_tool
from langchain_community.agent_toolkits.load_tools import load_tools
from pycoingecko import CoinGeckoAPI


from lib.utils import get_retriever, get_etherscan_docs, get_whitepaper_docs, split_docs


opts = [
    "eth_balance",
    "internal_transaction",
    "erc20_transaction",
    "erc721_transaction",
    "erc1155_transaction",
    "normal_transaction",
]

cg = CoinGeckoAPI()

# TODO: create custom tools to interact w/ smart contracts

@tool
def get_coin_price_in_usd(
    coin_name: Annotated[str, "the name of the coin. ie bitcoin, ethereum, monero"]
) -> str:
    """Get the price of a cryptocurrency in USD."""
    price = cg.get_price(ids=coin_name, vs_currencies="usd")
    if price is None:
        return f"Could not find the price of {coin_name}."
    return f"The price of {coin_name} is ${price[coin_name]['usd']}."


def get_tools() -> list:
    docs = [get_etherscan_docs(filter) for filter in opts]
    print("\n")
    retrievers = [get_retriever(doc, filter) for filter, doc in zip(opts, docs)]

    retriever_tools = [
        create_retriever_tool(
            retriever,
            f"retrieve_etherscan_docs_{filter}",
            f"Search and return information from Etherscan to answer questions related to {filter.replace('_', ' ')}.",
        )
        for filter, retriever in zip(opts, retrievers)
    ]

    whitepaper_docs = get_whitepaper_docs()
    whitepaper_docs = split_docs(whitepaper_docs)
    whitepaper_retriever = get_retriever(whitepaper_docs, "whitepaper")
    whitepaper_retriever_tool = create_retriever_tool(
        whitepaper_retriever,
        "retrieve_whitepaper_docs",
        "Search and return information from the Ethereum whitepaper to answer questions related to the whitepaper.",
    )

    tools = load_tools(
        [
            "ddg-search",
            "wolfram-alpha",
        ]
    )

    tools.extend(retriever_tools)
    tools.append(whitepaper_retriever_tool)
    tools.append(get_coin_price_in_usd)

    return tools
