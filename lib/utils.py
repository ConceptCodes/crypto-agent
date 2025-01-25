import os
import random
from datetime import datetime
from colorama import Fore, Style
from dateutil import tz
from halo import Halo
from dotenv import load_dotenv

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import EtherscanLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders.merge import MergedDataLoader
from langchain_community.document_loaders import WebBaseLoader

from lib.llm import embeddings
from lib.constants import ETHERSCAN_OFFSET, VECTORSTORE_DIR

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
    spinner = Halo(
        text=f"Load Etherscan {filter} History",
        spinner="dots",
    )
    spinner.start()

    loader = EtherscanLoader(
        os.getenv("ACCOUNT_ADDRESS"),
        filter=filter,
        offset=ETHERSCAN_OFFSET,
        sort="desc",
    )

    spinner.succeed(f"Loaded {set_color(filter, 'blue')} history from Etherscan.")

    return loader


def get_etherscan_docs(filter):
    validate_args()

    loader = get_loader(filter)
    result = loader.load()

    return result


def split_docs(docs, chunk_size=100, chunk_overlap=50):
    spinner = Halo(text="Splitting documents", spinner="dots")
    spinner.start()

    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    doc_splits = text_splitter.split_documents(docs)

    spinner.succeed(f"Split {len(docs)} documents into {len(doc_splits)} chunks.")
    return doc_splits


def get_retriever(docs, name):
    # docs = split_docs(docs)

    spinner = Halo(text=f"Creating {name} vectorstore", spinner="dots")
    spinner.start()

    vectorstore = Chroma.from_documents(
        documents=docs,
        collection_name=f"{VECTORSTORE_DIR}_{name}",
        embedding=embeddings,
    )
    retriever = vectorstore.as_retriever()

    spinner.succeed(
        f"Created {set_color(name, 'green')} vector store with {len(docs)} chunks."
    )
    return retriever


def set_color(text: str, color: str):
    color_map = {
        "blue": Fore.BLUE,
        "yellow": Fore.YELLOW,
        "red": Fore.RED,
        "green": Fore.GREEN,
        "purple": Fore.MAGENTA,
    }

    return f"{color_map.get(color, Fore.RESET)}{text}{Style.RESET_ALL}"


def log_step(step, spinner):
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
                    model = metadata.get("model", "Unknown Model")
                    created_at = format_timestamp(
                        metadata.get("created_at", "Unknown Time")
                    )
                    if content != "[No content]":
                        spinner.stop()
                        console.print(
                            Panel(
                                Text(
                                    f"\n{content}\n\n"
                                    f"{set_color('Model:', 'blue')} {model}\n"
                                    f"{set_color('Timestamp:', 'blue')} {created_at}",
                                    style="white",
                                ),
                                title="Agent Message",
                                border_style="cyan",
                            )
                        )
        elif "tools" in step:
            tool_messages = step["tools"].get("messages", [])
            for tool_message in tool_messages:
                tool_name = getattr(tool_message, "name", "Unknown Tool")
                content = getattr(tool_message, "content", "[No content]")
                spinner.stop()
                console.print(
                    Panel(
                        Text(
                            f"{set_color('Tool Used:', 'purple')} {tool_name}\n\n"
                            f"{set_color('Output:', 'purple')} {content}",
                            style="white",
                        ),
                        title="Tool Output",
                        border_style="purple",
                    )
                )
                spinner.start()
        else:
            spinner.stop()
            console.print(
                Panel(
                    Text(f"Unknown step structure:\n{step}", style="red"),
                    title="Unknown Step",
                    border_style="red",
                )
            )
            spinner.start()
    else:
        spinner.stop()
        console.print(
            Panel(
                Text(f"Unexpected step type: {step}", style="bold red"),
                title="Error",
                border_style="red",
            )
        )
        spinner.start()


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
    console.print(
        Panel(
            Text(f"An error occurred: {str(e)}", style="bold red"),
            title="Error",
        )
    )
