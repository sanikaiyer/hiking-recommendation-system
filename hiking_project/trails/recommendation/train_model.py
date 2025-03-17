import joblib
from sklearn.ensemble import RandomForestClassifier  # Example model
from sklearn.datasets import make_classification

def train_model():
    # Generate example data
    X, y = make_classification(n_samples=100, n_features=5, random_state=42)

    # Initialize and train the model
    model = RandomForestClassifier()
    model.fit(X, y)

    # Define the file path
    model_path = '/Users/sanikaiyer/hikes/hiking_project/trails/models/trail_recommendation_model.pkl'
    print(f"Saving model to: {model_path}")

    # Save the model
    joblib.dump(model, model_path)
    print("Model saved successfully!")

if __name__ == '__main__':
    train_model()
