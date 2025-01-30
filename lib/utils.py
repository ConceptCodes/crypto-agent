import os
import re
import random
from datetime import datetime
from dateutil import tz
from dotenv import load_dotenv

# from ens.auto import ns


from rich.console import Console

from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import EtherscanLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

from lib.llm import embeddings
from lib.constants import ETHERSCAN_OFFSET, VECTORSTORE_DIR, WHITEPAPER_URL
import streamlit as st

load_dotenv()
console = Console(force_terminal=True)


def validate_args():
    if os.getenv("ACCOUNT_ADDRESS") is None:
        log_error(
            "Please set the ACCOUNT_ADDRESS environment variable to your Ethereum account address."
        )
        exit(1)
    if os.getenv("ETHERSCAN_API_KEY") is None:
        log_error(
            "Please set the ETHERSCAN_API_KEY environment variable to your Etherscan API key."
        )
        exit(1)


def get_loader(filter):
    loader = EtherscanLoader(
        os.getenv("ACCOUNT_ADDRESS"),
        filter=filter,
        offset=ETHERSCAN_OFFSET,
        sort="desc",
    )

    return loader


def get_etherscan_docs(filter):
    validate_args()

    loader = get_loader(filter)
    result = loader.load()

    return result


def get_whitepaper_docs():
    loader = PyPDFLoader(WHITEPAPER_URL)
    result = loader.load()
    return result


def split_docs(docs, chunk_size=100, chunk_overlap=50):
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    doc_splits = text_splitter.split_documents(docs)

    return doc_splits


def get_retriever(docs, name):
    # docs = split_docs(docs)
    vectorstore = Chroma.from_documents(
        documents=docs,
        collection_name=f"{VECTORSTORE_DIR}_{name}",
        embedding=embeddings,
    )
    retriever = vectorstore.as_retriever()

    return retriever


def display_step(step):
    """Display a step dynamically based on its type."""
    if isinstance(step, dict):
        if "agent" in step:
            agent_messages = step["agent"].get("messages", [])
            for message in agent_messages:
                if hasattr(message, "content"):
                    if message.content is None:
                        continue
                    content = message.content or "[No content]"
                    metadata = getattr(message, "response_metadata", {})
                    model = metadata.get(
                        "model", metadata.get("model_name", "Unknown Model Name")
                    )
                    created_at = format_timestamp(
                        metadata.get("created_at", datetime.now().isoformat())
                    )

                    if content != "[No content]":
                        st.write("**Agent Message**")
                        st.write(content)
                        st.write(f"Model: {model}")
                        st.write(f"Timestamp: {created_at}")
        elif "tools" in step:
            tool_messages = step["tools"].get("messages", [])
            for tool_message in tool_messages:
                tool_name = getattr(tool_message, "name", "Unknown Tool")
                content = getattr(tool_message, "content", None)

                st.write("**Tool Output**")
                st.write(f"Tool Used: {tool_name}")
                st.write(f"Output: {content}")
        else:
            st.write(f"**Unknown Step**\n\n" f"Unknown step structure:\n{step}")
    else:
        st.write(f"**Error**\n\n" f"Unexpected step type: {step}")


def format_timestamp(timestamp):
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        dt = dt.astimezone(tz.tzlocal())
        return dt.strftime("%B %d, %Y, %I:%M %p %Z")
    except ValueError:
        return timestamp


def get_random_thread_id():
    return random.randint(1, 1000000)


def log_error(e):
    st.write(f"An error occurred: {str(e)}")


# def ens_name_resolver(name: str):
#     return ns.address(name)


def is_address(address: str):
    address_regex = re.compile(r"^(0x)?[0-9a-fA-F]{40}$")
    return bool(address_regex.match(address))
