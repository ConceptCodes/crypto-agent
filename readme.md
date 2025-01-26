# Crypto Agent


![Preview](https://i.imgur.com/gmWEgUq.png)

## Tools

| Tool                        | Description                                      | API Key Required  |
|-----------------------------|--------------------------------------------------|------------------ |
| DuckDuckGo Search           | Privacy-focused search engine                    |                   |
| Wolfram Alpha               | Computational knowledge engine                   | ✅                |
| EtherScan                   | Ethereum token information and analysis          | ✅                |
| WhitePaper Retriever        | The Ethereum White Paper Knowledge base           |                   |
| OpenSea                     | NFT marketplace                                  | ✅                |


## Agent Architecture
![Architecture](https://i.imgur.com/aPNQRyv.png)

This project features a simple [REACT](https://langchain-ai.github.io/langgraph/reference/prebuilt/#langgraph.prebuilt.chat_agent_executor.create_react_agent) agent designed to utilize various tools for answering user queries. One of the key components is the `EtherscanLoader` from the `langchain_community.document_loaders` module, which parses the Ethereum mainnet and converts the data into LangChain's `Document` objects. This loader provides options to filter and retrieve specific data, enhancing the agent's ability to deliver precise and relevant information. 

The documents are stored in a vector database. Each store becomes a retriever tool for the agent, allowing it to efficiently search and return information from Etherscan. Additionally, the agent integrates with other tools such as DuckDuckGo Search, Wolfram Alpha, and Stack Exchange to provide comprehensive answers to user queries.

The agent setup includes:
- Loading Etherscan data with filters like `eth_balance`, `internal_transaction`, `erc20_transaction`, `erc721_transaction`, `erc1155_transaction`, and `normal_transaction`.
- Creating retriever tools for each filter.

All these components work together to create a robust AI assistant capable of interacting with Ethereum data and other external sources to provide accurate and relevant information.

## Prerequisites
- Python 3.8 or higher
- Required API keys for the tools you want to use.
- Ollama installed and running locally. ([Installation Guide](https://ollama.com/download)) (Optional)
- OpenAI API key if not using Ollama. ([Sign Up](https://platform.openai.com/signup)) (Optional)


## Installation

1. Clone the repository:
    ```sh
    git clone https://conceptcodes.github.com/crypto-agent.git
    cd crypto-agent
    ```

2. Copy the `.env.example` file to `.env` and fill in your API keys.
    ```sh
    cp .env.example .env
    ```

3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Run the main script:
    ```sh
    python agent.py --address <any_ethereum_address>
    ```

2. Interact with the agent by typing your queries. Type `exit` to quit.