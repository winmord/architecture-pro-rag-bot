import csv
import re
from datetime import datetime

from rag_bot import RAGBot


GOLDEN_FILE = "golden_questions.txt"
LOG_FILE = "logs/logs.csv"


def load_golden_questions(path):
    questions = []

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = re.split(r"\n\s*\n", content.strip())

    for block in blocks:
        lines = block.strip().split("\n")

        question = None
        expected = None

        for line in lines:
            if line.startswith("Q:"):
                question = line.replace("Q:", "", 1).strip()

            elif line.startswith("EXPECTED:"):
                expected = line.replace("EXPECTED:", "", 1).strip()

        if question and expected:
            questions.append({
                "question": question,
                "expected": expected
            })

    return questions


def extract_final_answer(full_answer):
    match = re.search(
        r"Answer:\s*(.*)",
        full_answer,
        flags=re.IGNORECASE | re.DOTALL
    )

    if match:
        return match.group(1).strip()

    return full_answer.strip()


def evaluate_answer(answer, expected):
    answer_lower = answer.lower()
    expected_lower = expected.lower()

    if expected_lower in answer_lower:
        return {
            "success": True,
            "score": 1.0
        }

    expected_words = set(expected_lower.split())
    answer_words = set(answer_lower.split())

    overlap = expected_words.intersection(answer_words)

    if len(expected_words) == 0:
        score = 0.0
    else:
        score = len(overlap) / len(expected_words)

    return {
        "success": score >= 0.5,
        "score": round(score, 2)
    }


def extract_sources(chunks):
    sources = []

    for chunk in chunks:
        text = chunk.get("text", "")

        short_text = text[:150].replace("\n", " ")

        sources.append(short_text)

    return " | ".join(sources)


def main():
    bot = RAGBot()

    questions = load_golden_questions(GOLDEN_FILE)

    with open(LOG_FILE, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)

        writer.writerow([
            "timestamp",
            "question",
            "expected_answer",
            "full_answer",
            "final_answer",
            "chunks_found",
            "retrieved_chunks_count",
            "answer_length",
            "success",
            "score",
            "sources"
        ])

        total = 0
        success_count = 0

        for item in questions:
            question = item["question"]
            expected = item["expected"]

            print(f"\nQUESTION: {question}")

            retrieved_chunks = bot.retrieve(question)

            chunks_found = len(retrieved_chunks) > 0

            full_answer = bot.ask(question)

            final_answer = extract_final_answer(full_answer)

            evaluation = evaluate_answer(final_answer, expected)

            success = evaluation["success"]
            score = evaluation["score"]

            if success:
                success_count += 1

            total += 1

            print(f"FINAL ANSWER: {final_answer}")
            print(f"SUCCESS: {success}")
            print(f"SCORE: {score}")

            writer.writerow([
                datetime.utcnow().isoformat(),
                question,
                expected,
                full_answer,
                final_answer,
                chunks_found,
                len(retrieved_chunks),
                len(final_answer),
                success,
                score,
                extract_sources(retrieved_chunks)
            ])

    print("\n==========")
    print(f"TOTAL QUESTIONS: {total}")
    print(f"SUCCESSFUL: {success_count}")
    print(f"FAILED: {total - success_count}")

    if total > 0:
        accuracy = round((success_count / total) * 100, 2)
        print(f"ACCURACY: {accuracy}%")


if __name__ == "__main__":
    main()