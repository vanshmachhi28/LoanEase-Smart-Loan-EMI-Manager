from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta







class CustomerQuery(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} - {self.email}"


# 🔹 LOAN TYPES (Products)
class LoanType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.interest_rate}%)"


# 🔹 LOAN APPLICATION
class Loan(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    loan_type = models.ForeignKey(LoanType, on_delete=models.CASCADE)
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2)
    tenure_years = models.PositiveIntegerField()
    credit_score = models.IntegerField(default=0)
    eligibility_score = models.IntegerField(default=0)
    risk_category = models.CharField(max_length=30, default="Not Calculated")
    
    applied_on = models.DateTimeField(default=timezone.now)
    
    
    
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, editable=False)


    income = models.FloatField(null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)

    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=20)
    ifsc_code = models.CharField(max_length=11)

    document = models.FileField(upload_to="loan_documents/", null=True, blank=True)

    is_verified = models.BooleanField(default=False)
    penalty_amount = models.FloatField(default=0)
    outstanding_balance = models.FloatField(default=0)
    due_date = models.DateField(null=True, blank=True)



    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    applied_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.loan_type:
            self.interest_rate = self.loan_type.interest_rate
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.loan_type.name} - ₹{self.loan_amount}"


    def save(self, *args, **kwargs):
        if not self.due_date:
            self.due_date = timezone.now().date() + timedelta(days=30)
        super().save(*args, **kwargs)



