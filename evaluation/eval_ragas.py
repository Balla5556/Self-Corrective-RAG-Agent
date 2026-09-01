import json
import os
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision
from src.graph import app

def run_evaluation():
    with open("evaluation/test_dataset.json", "r") as f:
        test_data = json.load(f)

    questions = []
    answers = []
    contexts = []
    ground_truths = []

    for item in test_data:
        res = app.invoke({"question": item["question"], "iterations": 0})
        questions.append(item["question"])
        answers.append(res.get("generation", ""))
        contexts.append(res.get("documents", []))
        ground_truths.append(item["ground_truth"])

    data = {
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths
    }

    eval_dataset = Dataset.from_dict(data)
    results = evaluate(
        dataset=eval_dataset,
        metrics=[faithfulness, answer_relevancy, context_precision]
    )

    print("\n================ RAGAS EVALUATION METRICS ================")
    print(results.to_pandas())

if __name__ == "__main__":
    run_evaluation()
