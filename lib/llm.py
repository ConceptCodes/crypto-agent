import os
from dotenv import load_dotenv

from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

from lib.constants import (
    OPEN_AI_LLM_MODEL,
    OPEN_AI_EMBEDDING_MODEL,
    OLLAMA_LLM_MODEL,
    OLLAMA_EMBEDDING_MODEL,
)

load_dotenv()


if os.getenv("OPENAI_API_KEY") is not None:
    llm = ChatOpenAI(model=OPEN_AI_LLM_MODEL, api_key=os.getenv("OPENAI_API_KEY"))
    embeddings = OpenAIEmbeddings(
        model=OPEN_AI_EMBEDDING_MODEL, api_key=os.getenv("OPENAI_API_KEY")
    )
else:
    llm = ChatOllama(model=OLLAMA_LLM_MODEL)
    embeddings = OllamaEmbeddings(model=OLLAMA_EMBEDDING_MODEL)
