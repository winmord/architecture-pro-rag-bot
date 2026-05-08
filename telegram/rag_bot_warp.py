from flask import Flask, request, jsonify
from rag_bot import RAGBot

app = Flask(__name__)
bot = RAGBot()


@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    query = data.get("query", "")

    answer = bot.ask(query)

    return jsonify({"answer": answer})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
