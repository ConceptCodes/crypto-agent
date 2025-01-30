import os
import argparse
import streamlit as st

from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
import chromadb

from lib.llm import llm
from lib.tools import get_tools
from lib.prompt import system_message
from lib.utils import (
    display_step,
    get_random_thread_id,
    log_error,
    is_address,
)

chromadb.api.client.SharedSystemClient.clear_system_cache()


def get_args():
    parser = argparse.ArgumentParser(description="Crypto Agent")
    parser.add_argument(
        "-a",
        "--address",
        type=str,
        help="Ethereum account address",
        required=False,
    )

    args = parser.parse_args()

    address = args.address or os.getenv("ACCOUNT_ADDRESS")

    if address is None:
        parser.error(
            "Please provide an Ethereum account address using -a or --address."
        )

    if not is_address(address):
        parser.error("Please provide a valid Ethereum account address.")

    if args.address:
        os.environ["ACCOUNT_ADDRESS"] = args.address


def display_header():
    st.title("Crypto Agent")
    st.write("A Crypto AI assistant powered by LangGraph and LangChain.")
    st.write("#### Account Address")
    st.write(f"**{os.getenv('ACCOUNT_ADDRESS')}**")


if __name__ == "__main__":
    get_args()
    display_header()

    checkpointer = MemorySaver()
    tools = get_tools()

    # st.write("#### Tools")
    # tool_data = [{"Name": tool.name, "Description": tool.description} for tool in tools]
    # st.table(tool_data)

    langgraph_agent_executor = create_react_agent(
        model=llm, tools=tools, checkpointer=checkpointer, state_modifier=system_message
    )

    thread_id = get_random_thread_id()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    while True:
        try:
            user_input = st.chat_input("Ask me anything...")
            if user_input:
                st.session_state.messages.append(
                    {"role": "user", "content": user_input}
                )
                for step in langgraph_agent_executor.stream(
                    {"messages": [HumanMessage(content=user_input)]},
                    config={"configurable": {"thread_id": thread_id}},
                ):
                    display_step(step)
                    st.session_state.messages.append({"role": "agent", "content": step})
                    st.write("---")

                for message in st.session_state.messages:
                    if message["role"] == "user":
                        st.chat_message("user", message["content"])
                    else:
                        st.chat_message("agent", message["content"])

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            log_error(e)
            break
