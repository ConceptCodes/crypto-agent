import sys
import os
import argparse
import warnings
from colorama import init
from halo import Halo
from pyfiglet import figlet_format
from termcolor import cprint

from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage

from lib.llm import llm
from lib.tools import get_tools
from lib.prompt import system_message
from lib.utils import (
    log_step,
    get_random_thread_id,
    log_error,
    set_color,
    is_address,
    # ens_name_resolver,
)

init(strip=not sys.stdout.isatty())
warnings.filterwarnings("ignore", category=DeprecationWarning)


def get_args():
    parser = argparse.ArgumentParser(description="Crypto Agent")
    parser.add_argument(
        "-a",
        "--address",
        type=str,
        help="",
        required=False,
    )
    args = parser.parse_args()

    address = args.address or os.getenv("ACCOUNT_ADDRESS")

    if address is None:
        parser.error(
            "Please provide an Ethereum account address using -a or --address."
        )

    # if address.endswith(".eth"):
    #     address = ens_name_resolver(address)

    if not is_address(address):
        parser.error("Please provide a valid Ethereum account address.")

    if args.address:
        os.environ["ACCOUNT_ADDRESS"] = args.address


def setup_cli():
    cprint(
        figlet_format("Crypto Agent", font="starwars", width=100, justify="center"),
        attrs=["bold"],
    )
    print("A Crypto AI assistant powered by LangGraph and LangChain.")
    print("Type 'exit' to quit.\n")
    print(f"Account Address: {set_color(os.getenv('ACCOUNT_ADDRESS'), 'yellow')}\n")


if __name__ == "__main__":
    get_args()
    setup_cli()

    checkpointer = MemorySaver()
    tools = get_tools()

    print("\nAvailable Tools:")
    for tool in tools:
        print(f"- {set_color(tool.name, 'purple')}: {tool.description}")

    langgraph_agent_executor = create_react_agent(
        model=llm, tools=tools, checkpointer=checkpointer, state_modifier=system_message
    )

    thread_id = get_random_thread_id()

    while True:
        try:
            user_input = input("\nUser: ")
            if user_input.lower() in ["exit", "quit", "q"]:
                print("Exiting...")
                break

            if not user_input.strip():
                continue

            spinner = Halo(text="Thinking...", spinner="dots")
            for step in langgraph_agent_executor.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config={"configurable": {"thread_id": thread_id}},
            ):
                spinner.start()
                log_step(step, spinner)

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            spinner.stop()
            log_error(e)
            break
