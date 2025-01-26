import os
import requests
from typing import Annotated, Literal
from pycoingecko import CoinGeckoAPI
from dotenv import load_dotenv

from langchain_core.tools import tool
from langchain_core.tools import create_retriever_tool
from langchain_community.agent_toolkits.load_tools import load_tools


from lib.utils import get_retriever, get_etherscan_docs, get_whitepaper_docs, split_docs

load_dotenv()

opts = [
    "eth_balance",
    "internal_transaction",
    "erc20_transaction",
    "erc721_transaction",
    "erc1155_transaction",
    "normal_transaction",
]


@tool
def get_coin_price_in_usd(
    coin_name: Annotated[str, "the name of the coin. ie bitcoin, ethereum, monero"]
) -> str:
    """Get the price of a cryptocurrency in USD."""
    cg = CoinGeckoAPI()
    price = cg.get_price(ids=coin_name, vs_currencies="usd")
    if price is None:
        return f"Could not find the price of {coin_name}."
    return f"The price of {coin_name} is ${price[coin_name]['usd']}."


@tool
def get_nft_details(
    contract_address: Annotated[str, "the address of the NFT contract"],
    token_id: Annotated[str, "the ID of the NFT token"],
) -> str:
    """Get the details of a specific NFT."""
    url = f"https://api.opensea.io/api/v2/chain/ethereum/contract/{contract_address}/nfts/{token_id}"
    headers = {
        "accept": "application/json",
        "x-api-key": os.getenv("OPENSEA_API_KEY"),
    }

    response = requests.get(url, headers=headers)
    return response.json()


@tool
def get_nft_collection_details(
    collection_name: Annotated[str, "the name of the collection"],
) -> str:
    """Get the details of a specific NFT collection."""
    url = f"https://api.opensea.io/api/v2/collections/{collection_name}"
    headers = {
        "accept": "application/json",
        "x-api-key": os.getenv("OPENSEA_API_KEY"),
    }

    response = requests.get(url, headers=headers)
    return response.json()


@tool
def get_nft_collection_stats(
    collection_name: Annotated[str, "the name of the collection"],
) -> str:
    """Get the stats of a specific NFT collection."""
    url = f"https://api.opensea.io/api/v2/collections/{collection_name}/stats"
    headers = {
        "accept": "application/json",
        "x-api-key": os.getenv("OPENSEA_API_KEY"),
    }

    response = requests.get(url, headers=headers)
    return response.json()


@tool
def get_nft_events(
    contract_address: Annotated[str, "the address of the NFT contract"],
    token_id: Annotated[str, "the ID of the NFT token"],
    after: Annotated[
        int,
        "Filter to only include events that occurred at or after the given timestamp. The Unix epoch timstamp must be in seconds",
    ] = None,
    before: Annotated[
        int,
        "Filter to only include events that occurred before the given timestamp. The Unix epoch timstamp must be in seconds.",
    ] = None,
    event_type: Literal[
        "all", "cancel", "listing", "offer", "order", "redemption", "sale", "transfer"
    ] = "all",
    limit: Annotated[
        int, "The number of events to return. Must be between 1 and 50. Default: 50"
    ] = 50,
) -> str:
    """Get events from OpenSea for a specific NFT."""
    url = f"https://api.opensea.io/api/v2/events/chain/ethereum/contract/{contract_address}/nfts/{token_id}"
    headers = {
        "accept": "application/json",
        "x-api-key": os.getenv("OPENSEA_API_KEY"),
    }
    params = {
        "contract_address": contract_address,
        "token_id": token_id,
        "after": after,
        "before": before,
        "event_type": event_type,
        "limit": limit,
    }

    params = {k: v for k, v in params.items() if v is not None}
    response = requests.get(url, headers=headers, params=params)
    return response.json()


@tool
def get_nft_collection_events(
    collection_name: Annotated[str, "the name of the collection"],
    after: Annotated[
        int,
        "Filter to only include events that occurred at or after the given timestamp. The Unix epoch timstamp must be in seconds",
    ] = None,
    before: Annotated[
        int,
        "Filter to only include events that occurred before the given timestamp. The Unix epoch timstamp must be in seconds.",
    ] = None,
    event_type: Literal[
        "all", "cancel", "listing", "offer", "order", "redemption", "sale", "transfer"
    ] = "all",
    limit: Annotated[
        int, "The number of events to return. Must be between 1 and 50. Default: 50"
    ] = 50,
) -> str:
    """Get events from OpenSea for a specific NFT collection."""
    url = f"https://api.opensea.io/api/v2/events/collection/{collection_name}"
    headers = {
        "accept": "application/json",
        "x-api-key": os.getenv("OPENSEA_API_KEY"),
    }
    params = {
        "after": after,
        "before": before,
        "event_type": event_type,
        "limit": limit,
    }

    params = {k: v for k, v in params.items() if v is not None}
    response = requests.get(url, headers=headers, params=params)
    return response.json()


# TODO: create custom tools to interact w/ smart contracts


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
    tools.append(get_nft_details)
    tools.append(get_nft_collection_details)
    tools.append(get_nft_collection_stats)
    tools.append(get_nft_events)
    tools.append(get_nft_collection_events)

    return tools
