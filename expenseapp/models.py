from django.db import models
from django.contrib.auth.models import AbstractUser

# ✅ Custom User Model
class CustomUser(AbstractUser):
    phone = models.CharField(max_length=15)
    is_approved = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)

    def __str__(self):
        return self.username

# ✅ Expense Model
# models.py

class Expense(models.Model):
    # Remove CATEGORY_CHOICES

    PAYMENT_MODE_CHOICES = [
        ("Cash", "Cash"),
        ("UPI", "UPI"),
        ("Card", "Card"),
        ("NetBanking", "NetBanking"),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.FloatField()
    
    # 🔁 Change this:
    # category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    # 👉 To this:
    category = models.CharField(max_length=100)  # 🆗 now accepts any text input

    description = models.TextField(blank=True, null=True)
    date = models.DateField()
    payment_mode = models.CharField(max_length=50, choices=PAYMENT_MODE_CHOICES)
    bill_file = models.FileField(upload_to='bills/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - ₹{self.amount} on {self.date}"

# ✅ Monthly Budget Model
class Budget(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    month = models.IntegerField()  # 1-12 for Jan-Dec
    amount = models.FloatField()

    class Meta:
        unique_together = ('user', 'month')

    def __str__(self):
        return f"{self.user.username} - Budget for {self.month}: ₹{self.amount}"



class VoiceExpense(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.FloatField()
    category = models.CharField(max_length=100)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - ₹{self.amount} on {self.category}"
