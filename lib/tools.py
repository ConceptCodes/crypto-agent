# from langchain_core.tools import tool

from langchain_core.tools import create_retriever_tool
from langchain_community.agent_toolkits.load_tools import load_tools

from lib.utils import get_retriever, get_etherscan_docs


opts = [
    "eth_balance",
    "internal_transaction",
    "erc20_transaction",
    "erc721_transaction",
    "erc1155_transaction",
    "normal_transaction",
]

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

    tools = load_tools(
        [
            "ddg-search",
            "wolfram-alpha",
            "stackexchange",
        ]
    )

    tools.extend(retriever_tools)

    return tools
