import numpy as np
import joblib
from django.shortcuts import render, redirect
from django.contrib import messages
import os
from .models import LoanPrediction
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm

# Load your model once
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
model_path = os.path.join(BASE_DIR, 'loan_approval_model.pkl')
try:
    loaded_data = joblib.load(model_path)
    if isinstance(loaded_data, dict):
        model = loaded_data.get('model')  # If model is stored in a dictionary
    else:
        model = loaded_data  # If model is stored directly
    
    if not hasattr(model, 'predict'):
        raise AttributeError("Invalid model format")
        
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {str(e)}")
    model = None

@login_required
def home(request):
    return render(request, 'predictor/home.html')

@login_required
def predict(request):
    if request.method == 'POST':
        try:
            # First check if model is loaded properly
            if model is None:
                messages.error(request, "Model not loaded properly. Please contact administrator.")
                return render(request, 'predictor/predict.html', {'show_result': False})

            # Check model has required methods
            if not hasattr(model, 'predict') or not hasattr(model, 'predict_proba'):
                messages.error(request, "Invalid model format. Please contact administrator.")
                return render(request, 'predictor/predict.html', {'show_result': False})

            # Collect data from form
            person_age = int(request.POST['person_age'])
            person_income = float(request.POST['person_income'])
            person_emp_exp = float(request.POST['person_emp_exp'])
            loan_amnt = float(request.POST['loan_amnt'])
            loan_int_rate = float(request.POST['loan_int_rate'])
            loan_percent_income = float(request.POST['loan_percent_income'])
            cb_person_cred_hist_length = int(request.POST['cb_person_cred_hist_length'])
            credit_score = float(request.POST['credit_score'])
            previous_loan_defaults_on_file = int(request.POST['previous_loan_defaults_on_file'])
            person_gender_male = int(request.POST['person_gender_male'])
            person_education = request.POST['person_education']
            person_home_ownership = request.POST['person_home_ownership']
            loan_intent = request.POST['loan_intent']

            # Manual one-hot or label encoding (adjust based on model training)
            education_map = {'High School': 0, 'Bachelor': 1, 'Master': 2, 'Doctorate': 3}
            ownership_map = {'RENT': 0, 'OWN': 1, 'OTHER': 2}
            intent_map = {'EDUCATION': 0, 'PERSONAL': 1, 'MEDICAL': 2, 'VENTURE': 3, 'HOMEIMPROVEMENT': 4}

            # Feature vector as expected by the model
            features = np.array([
                person_age,
                person_income,
                person_emp_exp,
                loan_amnt,
                loan_int_rate,
                loan_percent_income,
                cb_person_cred_hist_length,
                credit_score,
                previous_loan_defaults_on_file,
                person_gender_male,
                education_map.get(person_education, 0),
                ownership_map.get(person_home_ownership, 0),
                intent_map.get(loan_intent, 0),
            ]).reshape(1, -1)

            # Get prediction and confidence (if model has `predict_proba`)
            prediction = model.predict(features)[0]
            probability = round(float(model.predict_proba(features)[0][1 if prediction == 1 else 0]) * 100, 2)

            # Save the prediction to database
            LoanPrediction.objects.create(
                user=request.user,
                person_age=person_age,
                person_income=person_income,
                person_emp_exp=person_emp_exp,
                loan_amnt=loan_amnt,
                loan_int_rate=loan_int_rate,
                loan_percent_income=loan_percent_income,
                cb_person_cred_hist_length=cb_person_cred_hist_length,
                credit_score=credit_score,
                previous_loan_defaults_on_file=previous_loan_defaults_on_file,
                person_gender_male=bool(person_gender_male),
                person_education=person_education,
                person_home_ownership=person_home_ownership,
                loan_intent=loan_intent,
                prediction=bool(prediction)
            )

            # Define result message
            prediction_text = "Approved" if prediction == 1 else "Rejected"

            # Return form data for display
            context = {
                'prediction': prediction,
                'prediction_text': prediction_text,
                'prediction_probability': probability,
                'show_result': True,
                'input_data': {
                    'loan_amnt': loan_amnt,
                    'loan_int_rate': loan_int_rate,
                    'loan_intent': loan_intent,
                    'credit_score': credit_score,
                }
            }
            return render(request, 'predictor/prediction_result.html', context)

        except Exception as e:
            messages.error(request, f"Something went wrong: {e}")
            return render(request, 'predictor/predict.html', {'show_result': False})

    return render(request, 'predictor/predict.html', {'show_result': False})


@login_required
def dashboard(request):
    # Get user's predictions
    predictions = LoanPrediction.objects.filter(user=request.user).order_by('-created_at')
    
    # Calculate statistics
    total_predictions = predictions.count()
    approved_count = predictions.filter(prediction=True).count()
    rejected_count = total_predictions - approved_count
    
    context = {
        'predictions': predictions,
        'total_predictions': total_predictions,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
    }
    
    return render(request, 'predictor/dashboard.html', context)


# Don't add login_required to register view
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! You can now login.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
