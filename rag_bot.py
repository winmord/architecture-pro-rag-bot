import pickle
import faiss
import requests
import numpy as np

from sentence_transformers import SentenceTransformer


EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

OLLAMA_MODEL = "gemma4:latest"
OLLAMA_URL = "http://localhost:11434/api/generate"

INDEX_PATH = "faiss_index/index.faiss"
CHUNKS_PATH = "faiss_index/index.pkl"

TOP_K = 4
MIN_SIMILARITY = 0.35


class RAGBot:
    def __init__(self):
        print("Загрузка embedding модели...")
        self.encoder = SentenceTransformer(EMBED_MODEL)

        print("Загрузка FAISS индекса...")
        self.index = faiss.read_index(INDEX_PATH)

        print("Загрузка документов...")

        with open(CHUNKS_PATH, "rb") as f:
            data = pickle.load(f)

        if isinstance(data, tuple):
            self.documents = data[0]
        else:
            self.documents = data

        print("Бот готов\n")

    def embed_query(self, query):
        embedding = self.encoder.encode(
            [query],
            normalize_embeddings=True
        )

        return np.array(embedding, dtype=np.float32)

    def extract_text(self, idx):
        try:
            if isinstance(self.documents, list):
                doc = self.documents[idx]

                if hasattr(doc, "page_content"):
                    return doc.page_content

                if isinstance(doc, dict):
                    return doc.get("text", "")

                return str(doc)

            if hasattr(self.documents, "_dict"):
                keys = list(self.documents._dict.keys())

                if idx >= len(keys):
                    return ""

                key = keys[idx]

                doc = self.documents._dict[key]

                if hasattr(doc, "page_content"):
                    return doc.page_content

                return str(doc)

            return ""

        except Exception:
            return ""

    def retrieve(self, query):
        query_vector = self.embed_query(query)

        distances, indices = self.index.search(query_vector, TOP_K)

        results = []

        for score, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue

            similarity = float(score)

            if similarity < MIN_SIMILARITY:
                continue

            text = self.extract_text(idx)

            if not text:
                continue

            results.append({
                "text": text,
                "score": similarity
            })

        return results

    def build_prompt(self, query, contexts):
        context_text = "\n\n".join(
            [
                f"[Фрагмент {i + 1}]\n{item['text']}"
                for i, item in enumerate(contexts)
            ]
        )

        few_shot_examples = """
Q: How is HyperRelay powered?
A:
1. First I search for information about HyperRelay.
2. The document states that HyperRelay uses the VoidCore energy source.
3. Therefore the answer is VoidCore.

Answer: VoidCore.

Q: What is the capital of Ti'lora?
A:
1. First I search for information about Ti'lora.
2. The document states that the capital is Sairon.
3. Therefore the answer is Sairon.

Answer: Sairon.
"""

        system_prompt = """
You are a RAG assistant.

Rules:
1. Answer ONLY using the provided context.
2. If the answer is missing in the context, say: "I don't know".
3. Always explain your reasoning step by step.
4. After reasoning provide the final answer.
5. Do not invent facts.
"""

        prompt = f"""
{system_prompt}

Context:
{context_text}

Examples:
{few_shot_examples}

Q: {query}
A:
"""

        return prompt

    def generate_answer(self, prompt):
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=300
        )

        response.raise_for_status()

        data = response.json()

        return data["response"].strip()

    def ask(self, query):
        contexts = self.retrieve(query)

        if not contexts:
            return "I don't know"

        prompt = self.build_prompt(query, contexts)

        return self.generate_answer(prompt)


def main():
    bot = RAGBot()

    print("RAG бот запущен")
    print("Введите 'exit' для выхода\n")

    while True:
        query = input("Вы: ").strip()

        if not query:
            continue

        if query.lower() in ["exit", "quit"]:
            break

        try:
            answer = bot.ask(query)

            print("\nБот:\n")
            print(answer)
            print()

        except KeyboardInterrupt:
            break

        except Exception as e:
            print("\nОшибка:")
            print(str(e))
            print()


if __name__ == "__main__":
    main()