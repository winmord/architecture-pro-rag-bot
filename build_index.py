import glob
import json
import os
import time

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
INPUT_DIR = "./knowledge_base"
OUTPUT_DIR = "./faiss_index"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
K_TOP = 3


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    documents = []
    for fpath in sorted(glob.glob(os.path.join(INPUT_DIR, "*.txt"))):
        with open(fpath, "r", encoding="utf-8") as f:
            text = f.read().strip()
        if text:
            documents.append(Document(page_content=text, metadata={"source": os.path.basename(fpath)}))

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        add_start_index=True,
        strip_whitespace=True
    )
    chunks = splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(
        model_name=MODEL_NAME,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )

    t_start = time.time()
    vector_store = FAISS.from_documents(chunks, embeddings)
    vector_store.save_local(OUTPUT_DIR)
    t_embed = time.time() - t_start

    meta_path = os.path.join(OUTPUT_DIR, "metadata.json")

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump([c.metadata for c in chunks], f, ensure_ascii=False, indent=2)

    print(f"Количество чанков: {len(chunks)} | Время создания: {t_embed:.2f}с")

    test_queries = [
        "What happened to Aldric the Ashen Wanderer during the Ashford Purge?",
        "What are Foreign Wizards, and where did they train?",
        "What is The Weave-Collapse?"
    ]

    for q in test_queries:
        docs = vector_store.similarity_search(q, k=K_TOP)
        print(f"\nЗапрос: '{q}'")
        for i, doc in enumerate(docs, 1):
            print(f"{doc.page_content[:200]}...")


if __name__ == "__main__":
    main()
