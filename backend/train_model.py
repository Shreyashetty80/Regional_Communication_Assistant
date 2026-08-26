import json
import pickle
import os

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

from nlp_preprocessing import preprocess_text


def train_intent_model():

    # Get backend folder path
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    intents_path = os.path.join(
        BASE_DIR,
        "data",
        "intents.json"
    )

    model_path = os.path.join(
        BASE_DIR,
        "model.pkl"
    )

    # Load intents
    with open(
        intents_path,
        "r",
        encoding="utf-8"
    ) as f:
        data = json.load(f)

    texts = []
    labels = []

    # Prepare training data
    for intent in data["intents"]:

        tag = intent["tag"]

        patterns = intent.get("patterns", [])

        for pattern in patterns:

            # Handle multilingual patterns
            if isinstance(pattern, dict):

                for language, text in pattern.items():

                    processed_text = preprocess_text(
                        text,
                        language
                    )

                    texts.append(processed_text)
                    labels.append(tag)

            else:

                processed_text = preprocess_text(
                    pattern,
                    "en"
                )

                texts.append(processed_text)
                labels.append(tag)

    # TF-IDF
    vectorizer = TfidfVectorizer()

    X = vectorizer.fit_transform(texts)

    # Train classifier
    classifier = MultinomialNB()

    classifier.fit(
        X,
        labels
    )

    # Save model
    with open(
        model_path,
        "wb"
    ) as f:

        pickle.dump(
            (vectorizer, classifier),
            f
        )

    print("Model training completed successfully.")
    print(f"Training samples: {len(texts)}")
    print(f"Intents: {len(set(labels))}")
    print(f"Model saved to: {model_path}")


if __name__ == "__main__":
    train_intent_model()