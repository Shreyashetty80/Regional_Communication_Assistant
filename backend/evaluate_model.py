import csv
import json
import pickle
import sys

sys.path.insert(0, "backend")

from nlp_preprocessing import preprocess_text


def evaluate_model():
    # Load trained model
    with open("backend/model.pkl", "rb") as f:
        vectorizer, classifier = pickle.load(f)

    # Load evaluation samples
    with open(
        "backend/data/evaluation_samples.csv",
        "r",
        encoding="utf-8"
    ) as f:
        samples = list(csv.DictReader(f))

    correct = 0

    print("\nRegional NLP Model Evaluation")
    print("=" * 50)

    for sample in samples:
        text = sample["input"]
        language = sample["language"]
        expected = sample["expected_intent"]

        processed = preprocess_text(text, language)

        prediction = classifier.predict(
            vectorizer.transform([processed])
        )[0]

        passed = prediction == expected

        if passed:
            correct += 1

        print(
            f"{sample['test_id']}: "
            f"Input={text!r} | "
            f"Expected={expected} | "
            f"Predicted={prediction} | "
            f"{'PASS' if passed else 'FAIL'}"
        )

    total = len(samples)
    accuracy = (correct / total) * 100 if total else 0

    print("=" * 50)
    print(f"Correct: {correct}/{total}")
    print(f"Accuracy: {accuracy:.2f}%")

    return accuracy


if __name__ == "__main__":
    evaluate_model()