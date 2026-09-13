from __future__ import annotations
import re
from pathlib import Path
import chromadb
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.chat_history import InMemoryChatMessageHistory
from app.config import CHROMA_PATH, DATA, EMBEDDING_MODEL, FIXED_CHUNK_SIZE, FIXED_CHUNK_OVERLAP, TOP_K

POLICY = DATA / "policy.md"
_FIXED = None
_SENTENCE = None
_EMBEDDINGS = None
_HISTORIES: dict[str, InMemoryChatMessageHistory] = {}


def load_documents() -> list[Document]:
    raw = POLICY.read_text(encoding="utf-8")
    docs=[]; current_title="General Policy"; buffer=[]
    for line in raw.splitlines():
        line=line.strip()
        if not line: continue
        if line.startswith("## "):
            if buffer:
                docs.append(Document(page_content=" ".join(buffer), metadata={"document_id": current_title.lower().replace(" ", "_").replace(".", ""), "source":"policy.md", "topic":current_title}))
                buffer=[]
            current_title=line[3:].strip()
        elif not line.startswith("#"):
            buffer.append(line)
    if buffer:
        docs.append(Document(page_content=" ".join(buffer), metadata={"document_id": current_title.lower().replace(" ", "_").replace(".",""), "source":"policy.md", "topic":current_title}))
    return docs


def embeddings():
    global _EMBEDDINGS
    if _EMBEDDINGS is None:
        _EMBEDDINGS = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return _EMBEDDINGS


def split_fixed(docs):
    return RecursiveCharacterTextSplitter(chunk_size=FIXED_CHUNK_SIZE, chunk_overlap=FIXED_CHUNK_OVERLAP).split_documents(docs)


def split_sentence(docs):
    out=[]
    for d in docs:
        for i, sentence in enumerate(re.split(r"(?<=[.!?])\s+", d.page_content)):
            if sentence.strip():
                out.append(Document(page_content=sentence.strip(), metadata={**d.metadata, "chunk": i}))
    return out


def build_indexes():
    global _FIXED, _SENTENCE
    docs=load_documents(); fixed=split_fixed(docs); sentence=split_sentence(docs)
    _FIXED = Chroma.from_documents(fixed, embeddings(), collection_name="ola_policy_fixed", persist_directory=CHROMA_PATH)
    _SENTENCE = Chroma.from_documents(sentence, embeddings(), collection_name="ola_policy_sentence", persist_directory=CHROMA_PATH)
    return len(docs), len(fixed), len(sentence)


def _stores():
    global _FIXED, _SENTENCE
    if _FIXED is None or _SENTENCE is None:
        build_indexes()
    return _FIXED, _SENTENCE


def retrieve(query: str, strategy: str = "fixed", k: int = TOP_K):
    fixed, sentence = _stores(); store = sentence if strategy == "sentence" else fixed
    return store.similarity_search_with_score(query, k=k)


def retrieve_top(query: str, strategy: str = "fixed", k: int = TOP_K):
    return retrieve(query, strategy, k)


def history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in _HISTORIES:
        _HISTORIES[session_id] = InMemoryChatMessageHistory()
    return _HISTORIES[session_id]


def add_document(title: str, text: str):
    # Keep Part 3 simple: add the document to both collections with the same metadata shape.
    d=Document(page_content=text, metadata={"document_id": title.lower().replace(" ","_"), "source":"api", "topic":title})
    fixed=Chroma.from_documents(split_fixed([d]), embeddings(), collection_name="ola_policy_fixed", persist_directory=CHROMA_PATH)
    sentence=Chroma.from_documents(split_sentence([d]), embeddings(), collection_name="ola_policy_sentence", persist_directory=CHROMA_PATH)
    return {"title": title, "fixed_chunks": len(split_fixed([d])), "sentence_chunks": len(split_sentence([d]))}
