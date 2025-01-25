from langchain_ollama import OllamaEmbeddings, ChatOllama

from lib.constants import LLM_MODEL, EMBEDDING_MODEL


llm = ChatOllama(model=LLM_MODEL)
embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
