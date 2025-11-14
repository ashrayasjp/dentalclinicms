import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.naive_bayes import MultinomialNB
import joblib
import os

# Load dataset with 'text' and 'disease' columns
df = pd.read_csv('ai/open_oral_disease_dataset.csv')  # make sure it has 'disease'

# Filter out invalid entries if needed
df = df[df['validity'] == 'correct']

X_text = df['question']
y_disease = df['disease']

# Vectorize text
vectorizer = TfidfVectorizer(max_features=5000)
X_vect = vectorizer.fit_transform(X_text)

# Encode disease labels
le = LabelEncoder()
y_enc = le.fit_transform(y_disease)

# Split data
X_train, X_test, y_train, y_test = train_test_split(X_vect, y_enc, test_size=0.2, random_state=42)

# Train model
model = MultinomialNB()
model.fit(X_train, y_train)

# Save model and vectorizer
os.makedirs('ai/models', exist_ok=True)
joblib.dump(model, 'ai/models/oral_disease_text_model.pkl')
joblib.dump(vectorizer, 'ai/models/oral_disease_vectorizer.pkl')
joblib.dump(le, 'ai/models/oral_disease_label_encoder.pkl')

print("Model trained with disease labels only.")
