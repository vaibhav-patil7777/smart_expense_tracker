from django.test import TestCase

# Create your tests here.
import smtplib

try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('your-email@gmail.com', 'your-app-password')
    server.sendmail(
        'your-email@gmail.com',
        'recipient@example.com',
        'Subject: Test\n\nThis is a test email from Vaibhav\'s Django app!'
    )
    server.quit()
    print("✅ Email sent successfully.")
except Exception as e:
    print("❌ Email sending failed:", e)
