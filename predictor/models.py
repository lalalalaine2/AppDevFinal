from django.db import models
from django.contrib.auth.models import User

class LoanPrediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    person_age = models.IntegerField()
    person_income = models.FloatField()
    person_emp_exp = models.IntegerField()
    loan_amnt = models.FloatField()
    loan_int_rate = models.FloatField()
    loan_percent_income = models.FloatField()
    cb_person_cred_hist_length = models.IntegerField()
    credit_score = models.IntegerField()
    previous_loan_defaults_on_file = models.IntegerField()
    person_gender_male = models.BooleanField()
    person_education = models.CharField(max_length=20)
    person_home_ownership = models.CharField(max_length=20)
    loan_intent = models.CharField(max_length=20)
    prediction = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Loan Prediction for {self.user.username} on {self.created_at}"

# Create your models here.
