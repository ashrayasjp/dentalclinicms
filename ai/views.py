from django.shortcuts import render
from django.http import JsonResponse
import joblib
import os

# Load saved model, vectorizer, and label encoder
MODEL_PATH = os.path.join('ai', 'models', 'oral_disease_text_model.pkl')
VECT_PATH = os.path.join('ai', 'models', 'oral_disease_vectorizer.pkl')
ENCODER_PATH = os.path.join('ai', 'models', 'oral_disease_label_encoder.pkl')

model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECT_PATH)
label_encoder = joblib.load(ENCODER_PATH)

# Optional: Mapping disease to explanation text if you have it
# Example: {'pulpitis': 'Inflammation of dental pulp ...'}
disease_explanation = {
    "pulpitis": "Pulpitis is inflammation of the dental pulp, often caused by tooth decay.",
    "tmj-disorder": "TMJ disorder affects the jaw joint and surrounding muscles, causing pain while chewing.",
    # Add more mappings as per your dataset
}

def predict_disease(request):
    """
    Handles GET (render template) and POST (predict disease)
    """
    if request.method == "POST":
        symptom_text = request.POST.get("symptom", "").strip()
        
        # Check if input is meaningful (at least 3 words)
        if not symptom_text or len(symptom_text.split()) < 3:
            return JsonResponse({"errors": "Not enough information to predict."})

        try:
            X_input = vectorizer.transform([symptom_text])
            pred_numeric = model.predict(X_input)[0]

            disease_name = label_encoder.inverse_transform([pred_numeric])[0]
            disease_name_clean = disease_name.split(":")[0]

            # Get explanation if available
            explanation = disease_explanation.get(disease_name_clean, "Detailed information is not available for this disease.")

            return JsonResponse({
                "disease": disease_name_clean,
                "answer": explanation
            })

        except Exception as e:
            return JsonResponse({"errors": f"Prediction error: {str(e)}"})

    # GET request → render template
    return render(request, "ai/predict.html")
