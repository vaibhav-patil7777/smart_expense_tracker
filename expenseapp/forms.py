from django import forms

class UploadExpenseForm(forms.Form):
    file = forms.FileField(label="Upload Your Expense File")
