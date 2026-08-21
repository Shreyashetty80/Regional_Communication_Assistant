import json
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

def train_intent_model():
    # 1. Load intents dataset
    with open("data/intents.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    X_patterns = []
    y_tags = []

    for intent in data["intents"]:
        for pattern in intent["patterns"]:
            X_patterns.append(pattern)
            y_tags.append(intent["tag"])

    # 2. Extract TF-IDF Features
    vectorizer = TfidfVectorizer()
    X_vectorized = vectorizer.fit_transform(X_patterns)

    # 3. Train Classifier
    classifier = MultinomialNB()
    classifier.fit(X_vectorized, y_tags)

    # 4. Save trained vectorizer and model together
    with open("model.pkl", "wb") as f:
        pickle.dump((vectorizer, classifier), f)

    print("✅ Model trained and saved as 'model.pkl' successfully!")

if __name__ == "__main__":
    train_intent_model()