from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden, FileResponse
from django.contrib import messages
from django.utils.encoding import smart_str
from datetime import datetime
from .models import CustomUser, Expense, Budget
from django.db.models import Sum
from django.views.decorators.csrf import csrf_exempt
import re
import io
import base64
import matplotlib.pyplot as plt
import plotly.graph_objs as go
from plotly.offline import plot
import pandas as pd
import calendar
from reportlab.pdfgen import canvas
from sklearn.linear_model import LinearRegression
import numpy as np
from django.db.models.functions import TruncMonth
from django.db.models import Sum

# OCR and File Handling
import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes
import csv




from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, get_object_or_404
from .models import CustomUser

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from .models import VoiceExpense

import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.core.mail import send_mail
from django.utils.timezone import now
from django.db import models
from .models import VoiceExpense

from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import VoiceExpense
from django.utils.timezone import now
from django.core.mail import send_mail
from django.db.models import Sum
import json

'''@csrf_exempt
@login_required
def save_voice_expense(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        amount = float(data['amount'])
        category = data['category']

        expense = VoiceExpense.objects.create(
            user=request.user,
            amount=amount,
            category=category,
            date=now().date()
        )

        # Email Send
        send_mail(
            subject='🧾 Expense Added Successfully!',
            message=f'You added ₹{amount} on {category}.\nDate: {expense.date}',
            from_email='your_email@gmail.com',
            recipient_list=[request.user.email],
            fail_silently=False,
        )

        total = VoiceExpense.objects.filter(user=request.user).aggregate(total=Sum('amount'))['total']

        return JsonResponse({'message': f'Expense added! 💸 Total = ₹{total}'})
'''
@login_required
def voice_expense_page(request):
    total = VoiceExpense.objects.filter(user=request.user).aggregate(total=Sum('amount'))['total'] or 0
    return render(request, 'voice_expense.html', {'total': total})




# ✅ Check if admin
def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def toggle_block_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_blocked = not user.is_blocked
    user.save()
    return redirect('view_all_users')  # 👈 redirect to user list page



@user_passes_test(is_admin)
def view_all_users(request):
    users = CustomUser.objects.exclude(is_superuser=True)
    return render(request, 'view_all_users.html', {'users': users})


from .models import Expense  # replace with your app

@user_passes_test(is_admin)
def user_dashboard(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    expenses = Expense.objects.filter(user=user)
    return render(request, 'user_dashboard.html', {
        'user_obj': user,
        'expenses': expenses
    })


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib import messages

# View all users
def view_all_users(request):
    users = User.objects.all()
    return render(request, 'view_all_users.html', {'users': users})

# View a specific user's dashboard
def view_user_dashboard(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, 'user_dashboard.html', {'user': user})

# Block a user
def block_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = False
    user.save()
    messages.success(request, f"User '{user.username}' has been blocked.")
    return redirect('view_all_users')

# Unblock a user
def unblock_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = True
    user.save()
    messages.success(request, f"User '{user.username}' has been unblocked.")
    return redirect('view_all_users')



# ✅ Register
def register(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        phone = request.POST['phone']
        password = request.POST['password']

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "❌ Username already taken.")
            return render(request, 'register.html')

        user = CustomUser.objects.create_user(
            username=username, email=email, phone=phone, password=password)
        user.is_approved = False
        user.is_admin = False
        user.is_blocked = False
        user.save()

        send_mail(
            'New User Registration Request',
            f'New user:\nUsername: {username}\nPhone: {phone}\n\nApprove:\nhttp://127.0.0.1:8000/admin-approve/{user.id}/?password={settings.ADMIN_SECRET_PASSWORD}',
            settings.EMAIL_HOST_USER,
            [settings.EMAIL_HOST_USER],
        )

        return render(request, 'register_done.html', {'username': username})
    return render(request, 'register.html')


# ✅ Approve User
def approve_user(request, user_id):
    password = request.GET.get('password')
    if password != settings.ADMIN_SECRET_PASSWORD:
        return HttpResponseForbidden("❌ Invalid admin password.")

    try:
        user = CustomUser.objects.get(id=user_id)
        user.is_approved = True
        user.save()

        send_mail(
            'Welcome to Smart Expense Tracker 🎉',
            f'Hi {user.username},\n\nYour account is approved. Start tracking now!',
            settings.EMAIL_HOST_USER,
            [user.email],
        )

        return HttpResponse(f"✅ User '{user.username}' approved successfully.")
    except CustomUser.DoesNotExist:
        return HttpResponse("❌ User not found.")


# ✅ Login
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user:
            if not user.is_approved:
                return render(request, 'login.html', {'error': '❌ Account not yet approved.'})
            if user.is_blocked:
                return render(request, 'login.html', {'error': '🚫 Account is blocked.'})

            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error': '❌ Invalid credentials.'})
    return render(request, 'login.html')


# ✅ Logout
def logout_view(request):
    logout(request)
    return redirect('login')


# ✅ Dashboard View
@login_required
def dashboard(request):
    user = request.user
    if not user.is_approved or user.is_blocked:
        return HttpResponse("Access Denied")

    selected_month = request.GET.get('month')
    selected_category = request.GET.get('category')
    chart_type = request.GET.get('chart_type', 'line')

    expenses = Expense.objects.filter(user=user).order_by('-date')
    if selected_month:
        try:
            selected_month = int(selected_month)
            expenses = expenses.filter(date__month=selected_month)
        except:
            selected_month = None

    if selected_category:
        expenses = expenses.filter(category=selected_category)

    total_expense = sum(exp.amount for exp in expenses)

    # Category Chart
    category_totals = {}
    for exp in expenses:
        category_totals[exp.category] = category_totals.get(exp.category, 0) + exp.amount

    category_chart = None
    if category_totals and chart_type == "pie":
        fig, ax = plt.subplots()
        ax.pie(category_totals.values(), labels=category_totals.keys(), autopct='%1.1f%%')
        ax.axis('equal')
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        category_chart = base64.b64encode(image_png).decode('utf-8')
        plt.close()

    # Daily Trend Plot (Plotly)
    plotly_html = None
    if chart_type in ['line', 'bar'] and expenses.exists():
        df = pd.DataFrame(list(expenses.values('date', 'amount')))
        df['date'] = pd.to_datetime(df['date'])
        trend_data = df.groupby('date')['amount'].sum().reset_index()

        fig = go.Figure()
        if chart_type == 'line':
            fig.add_trace(go.Scatter(x=trend_data['date'], y=trend_data['amount'],
            mode='lines+markers', name='Daily Expense'))
        elif chart_type == 'bar':
            fig.add_trace(go.Bar(x=trend_data['date'], y=trend_data['amount'], name='Daily Expense'))

        fig.update_layout(title='Daily Expense Trend', xaxis_title='Date', yaxis_title='Amount (₹)')
        plotly_html = plot(fig, output_type='div')

    # Budget Warning
    budget_obj = Budget.objects.filter(user=user, month=selected_month).first() if selected_month else None
    current_budget = budget_obj.amount if budget_obj else 0
    remaining = current_budget - total_expense
    warning = None
    over_budget = False
    if current_budget:
        if remaining < 0:
            warning = f"⚠️ Budget exceeded by ₹{abs(remaining)}"
            over_budget = True
        elif remaining < (0.1 * current_budget):
            warning = f"⚠️ Only ₹{remaining} left in budget"

    month_options = [(i, calendar.month_name[i]) for i in range(1, 13)]
    unique_categories = list(Expense.objects.filter(user=user).values_list('category', flat=True).distinct())
    selected_month_name = calendar.month_name[selected_month] if selected_month else ""
    months, totals = get_monthly_expenses(request.user)
    prediction = predict_next_month_expense(months, totals)

    return render(request, 'dashboard.html', {
        'user': user,
        'expenses': expenses,
        'total_expense': total_expense,
        'category_chart': category_chart,
        'plotly_html': plotly_html,
        'selected_month': selected_month,
        'selected_month_name': selected_month_name,
        'month_options': month_options,
        'current_budget': current_budget,
        'warning': warning,
        'chart_type': chart_type,
        'unique_categories': unique_categories,
        'selected_category': selected_category,
        'over_budget': over_budget,
        'total_expense': sum(totals),
        'highest_category': 'Food',  # update with actual logic
        'trend': 'Increasing', 
        'next_month_prediction': prediction,

    })


# ✅ Download CSV
@login_required
def download_csv(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    df = pd.DataFrame(list(expenses.values('date', 'amount', 'category', 'description', 'payment_mode')))
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=expenses.csv'
    df.to_csv(path_or_buf=response, index=False)
    return response


# ✅ Download PDF
@login_required
def download_pdf(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    y = 800
    p.setFont("Helvetica", 12)
    p.drawString(200, y, "Expense Report")
    y -= 40

    for exp in expenses:
        p.drawString(50, y, f"{exp.date} | ₹{exp.amount} | {exp.category} | {exp.payment_mode}")
        y -= 20
        if y < 50:
            p.showPage()
            y = 800
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='expenses.pdf')


# ✅ Admin access user dashboard (hidden)
def admin_user_access(request, username, secret):
    if secret != settings.ADMIN_SECRET_PASSWORD:
        return HttpResponseForbidden("❌ Invalid access code.")
    try:
        user = CustomUser.objects.get(username=username)
        login(request, user)
        return redirect('dashboard')
    except CustomUser.DoesNotExist:
        return HttpResponse("❌ User not found.")





from django.db.models import Sum
from django.core.mail import send_mail
from django.conf import settings

def manual_expense_add(request):
    if request.method == 'POST':
        amount = request.POST['amount']
        category = request.POST['category']
        description = request.POST.get('description', '')
        date = request.POST.get('date') or datetime.today().date()
        payment_mode = request.POST['payment_mode']
        bill_file = request.FILES.get('bill_file')

        Expense.objects.create(
            user=request.user,
            amount=amount,
            category=category,
            description=description,
            date=date,
            payment_mode=payment_mode,
            bill_file=bill_file
        )

        messages.success(request, "✅ Expense added manually!")

        # 🔢 Calculate updated total expense
        total_expense = Expense.objects.filter(user=request.user).aggregate(total=Sum('amount'))['total']

        # 📬 Send detailed email
        subject = "📝 Manual Expense Added Successfully"
        message = (
            f"Hi {request.user.username},\n\n"
            f"You’ve successfully added a manual expense:\n"
            f"💸 Amount: ₹{float(amount):.2f}\n"
            f"📂 Category: {category}\n\n"
            f"💰 Total Expense Till Now: ₹{total_expense:.2f}\n\n"
            f"Thanks,\nExpense Tracker"
        )

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [request.user.email])

        return redirect('dashboard')

import pandas as pd
import os
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Expense
from django.utils.dateparse import parse_date
import datetime
from django.contrib.auth.decorators import login_required

from django.contrib.auth.decorators import login_required
import pandas as pd
import os
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Expense
import datetime

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime
from .models import Expense
from django.db.models import Sum
import pandas as pd
import os

@login_required
def upload_expense_file(request):
    if request.method == "POST" and request.FILES.get("expense_file"):
        file = request.FILES["expense_file"]

        ext = os.path.splitext(file.name)[1].lower()
        try:
            if ext in [".csv"]:
                df = pd.read_csv(file, header=None)
            elif ext in [".xlsx", ".xls"]:
                df = pd.read_excel(file, header=None)
            else:
                messages.error(request, "Unsupported file format.")
                return redirect("dashboard")
        except Exception as e:
            messages.error(request, f"File error: {str(e)}")
            return redirect("dashboard")

        created = 0

        for index, row in df.iterrows():
            row = row.dropna()
            if len(row) < 1:
                continue

            # Auto-detect amount
            amount = None
            for item in row:
                try:
                    val = float(str(item).replace(",", "").replace("₹", "").strip())
                    if val > 0:
                        amount = val
                        break
                except:
                    continue

            if amount is None:
                continue

            # Auto-detect date
            date = None
            for item in row:
                try:
                    dt = pd.to_datetime(item, errors='coerce')
                    if pd.notnull(dt):
                        date = dt.date()
                        break
                except:
                    continue

            if date is None:
                date = datetime.today().date()

            # Auto-detect category
            category = "Uncategorized"
            for item in row:
                if isinstance(item, str) and len(item) < 30:
                    if not any(x in str(item).lower() for x in ['total', 'amount', 'rs', '₹']):
                        category = item.strip().title()
                        break

            try:
                Expense.objects.create(
                    user=request.user,
                    amount=amount,
                    date=date,
                    category=category,
                    payment_mode="Cash",
                    description="Uploaded via file",
                    bill_file=file
                )
                created += 1
            except Exception as e:
                print("DEBUG: Expense creation failed:", e)
                messages.error(request, f"Error creating expense: {str(e)}")

        if created:
            # ✅ Calculate total expense
            total_expense = Expense.objects.filter(user=request.user).aggregate(total=Sum('amount'))['total']

            # ✅ Send email to user
            subject = "📂 File Upload Expense Added Successfully"
            message = (
                f"Hi {request.user.username},\n\n"
                f"{created} expense(s) have been added from your uploaded file.\n\n"
                f"💰 Total Expense Till Now: ₹{total_expense:.2f}\n\n"
                f"Thanks,\nExpense Tracker"
            )

            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [request.user.email])

            messages.success(request, f"{created} expense(s) uploaded and email sent successfully.")
        else:
            messages.warning(request, "No valid expenses found in the file.")

        return redirect("dashboard")

    return render(request, "upload_expense_file.html")


from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime
from .models import Expense

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime
from django.db.models import Sum
from .models import Expense

@login_required
def save_voice_expense(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        category = request.POST.get('category')
        description = request.POST.get('description')
        date_str = request.POST.get('date')

        # 🧪 Debugging
        print("DEBUG: Voice Expense POST received")
        print("DEBUG: Amount =", amount)
        print("DEBUG: Category =", category)
        print("DEBUG: Description =", description)
        print("DEBUG: Date string =", date_str)
        print("DEBUG: User =", request.user)

        # 🗓️ Parse date or fallback to today
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except:
            date = datetime.today().date()

        if amount and category:
            try:
                expense = Expense.objects.create(
                    user=request.user,
                    amount=float(amount),
                    category=category.strip().title(),
                    description=description or "(added via voice)",
                    date=date,
                    payment_mode='Cash'
                )
                print("DEBUG: Expense created successfully:", expense)

                # ✅ Calculate total expense
                total_expense = Expense.objects.filter(user=request.user).aggregate(total=Sum('amount'))['total']

                # ✅ Send email to user
                subject = "🎙️ Voice Expense Added Successfully"
                message = (
                    f"Hi {request.user.username},\n\n"
                    f"Your voice expense has been recorded:\n"
                    f"- Amount: ₹{amount}\n"
                    f"- Category: {category}\n"
                    f"- Date: {date}\n\n"
                    f"💰 Total Expense Till Now: ₹{total_expense:.2f}\n\n"
                    f"Thanks,\nExpense Tracker"
                )
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [request.user.email])

                messages.success(request, "🎙️ Voice Expense saved and email sent!")
            except Exception as e:
                print("DEBUG: Voice expense creation failed:", e)
                messages.error(request, f"❌ Error saving voice expense: {str(e)}")
        else:
            messages.error(request, "❌ Voice data not received!")
            return redirect("dashboard")


    # GET request → render form
    today = datetime.today().date().strftime("%Y-%m-%d")
    return render(request, "voice_expense.html", {"today": today})


# ✅ Edit Expense
@login_required
def edit_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    if request.method == "POST":
        expense.amount = request.POST['amount']
        expense.category = request.POST['category']
        expense.description = request.POST['description']
        expense.date = request.POST['date']
        expense.payment_mode = request.POST['payment_mode']
        if request.FILES.get('bill_file'):
            expense.bill_file = request.FILES.get('bill_file')
        expense.save()
        return redirect('dashboard')
    return render(request, 'edit_expense.html', {'expense': expense})


# ✅ Delete Expense
@login_required
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    if request.method == "POST":
        expense.delete()
        return redirect('dashboard')
    return render(request, 'delete_expense.html', {'expense': expense})


# ✅ Set Budget
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Sum
from django.contrib import messages
from datetime import datetime
import calendar
import requests
from django.core.mail import send_mail
from django.conf import settings
from .models import Budget, Expense

# ✅ SMS Function (Fast2SMS)
def send_sms(phone, message):
    try:
        url = "https://www.fast2sms.com/dev/bulkV2"
        payload = {
            'authorization': settings.FAST2SMS_API_KEY,
            'sender_id': 'FSTSMS',
            'message': message,
            'language': 'english',
            'route': 'q',
            'numbers': phone
        }
        headers = {'cache-control': "no-cache"}
        return requests.post(url, data=payload, headers=headers)
    except Exception as e:
        print("SMS Error:", e)

# ✅ Utility to send confirmation
def notify_user(user, message):
    if user.email:
        send_mail("📊 Budget Update", message, settings.EMAIL_HOST_USER, [user.email])
    if user.phone:
        send_sms(user.phone, message)

# ✅ Final Budget View
@login_required
def set_budget(request):
    user = request.user
    month_options = [(i, calendar.month_name[i]) for i in range(1, 13)]
    selected_month = None
    current_budget = 0

    if request.method == "POST":
        selected_month = int(request.POST['month'])
        amount = int(request.POST['amount'])

        budget_obj, created = Budget.objects.get_or_create(
            user=user,
            month=selected_month,
            defaults={'amount': amount}
        )

        if not created:
            budget_obj.amount = amount
            budget_obj.save()

        # 🔢 Get total expense for the user
        total_expense = Expense.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0

        # ✉️ Enhanced notification message
        message = (
            f"✅ Budget set for {calendar.month_name[selected_month]}: ₹{amount}\n"
            f"💰 Total Expense Till Now: ₹{total_expense:.2f}\n"
            f"🧾 You can now track your expenses against this budget."
        )
        notify_user(user, message)

        messages.success(request, f"✅ Budget for {calendar.month_name[selected_month]} updated successfully!")
        return redirect('dashboard')

    elif request.method == "GET" and 'month' in request.GET:
        selected_month = int(request.GET['month'])
        budget_obj = Budget.objects.filter(user=user, month=selected_month).first()
        if budget_obj:
            current_budget = budget_obj.amount

    return render(request, 'set_budget.html', {
        'month_options': month_options,
        'selected_month': selected_month,
        'current_budget': current_budget,
    })

# ✅ Manual Add Expense
'''@login_required

def manual_expense_add(request):
    if request.method == "POST":
        user = request.user
        amount = request.POST['amount']
        category = request.POST['category']
        description = request.POST.get('description', '')
        date = request.POST.get('date', datetime.now().date())
        payment = request.POST.get('payment_mode', 'Unknown')

        Expense.objects.create(
            user=user,
            amount=amount,
            category=category,
            description=description,
            date=date,
            payment_mode=payment,
        )

        notify_user(user, amount)
        messages.success(request, "✅ Expense added manually.")
        return redirect('dashboard')

    return render(request, 'manual_expense.html')


# ✅ Automatic File Upload & OCR Parsing


@login_required
def auto_expense_upload(request):
    if request.method == "POST":
        user = request.user
        file = request.FILES.get('bill_file')
        filename = file.name.lower()
        amount = 0

        try:
            # 🧾 CASE 1: CSV
            if filename.endswith('.csv'):
                df = pd.read_csv(file)
                for _, row in df.iterrows():
                    Expense.objects.create(
                        user=user,
                        amount=row.get('amount', 0),
                        category=row.get('category', 'Unknown'),
                        description=row.get('description', ''),
                        date=row.get('date', datetime.now().date()),
                        payment_mode=row.get('payment_mode', 'Other')
                    )

            # 📊 CASE 2: Excel
            elif filename.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file)
                for _, row in df.iterrows():
                    Expense.objects.create(
                        user=user,
                        amount=row.get('amount', 0),
                        category=row.get('category', 'Unknown'),
                        description=row.get('description', ''),
                        date=row.get('date', datetime.now().date()),
                        payment_mode=row.get('payment_mode', 'Other')
                    )

            # 📷 CASE 3: Image or PDF → OCR
            else:
                text = ""
                if filename.endswith('.pdf'):
                    pages = convert_from_bytes(file.read())
                    for page in pages:
                        text += pytesseract.image_to_string(page)
                else:
                    img = Image.open(file)
                    text = pytesseract.image_to_string(img)

                # 🔍 Extract Data Using Regex
                amt_match = re.findall(r'\₹\s?(\d+[\d,]*)', text)
                date_match = re.findall(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', text)
                category_match = re.findall(r'(Food|Rent|Electricity|Fees|Groceries|Books)', text, re.I)
                pay_match = re.findall(r'(Cash|Card|UPI|Netbanking|Paytm|GPay)', text, re.I)

                amount = amt_match[-1].replace(',', '') if amt_match else 0
                try:
                    date = datetime.strptime(date_match[-1], "%d-%m-%Y").date() if date_match else datetime.now().date()
                except:
                    date = datetime.now().date()

                Expense.objects.create(
                    user=user,
                    amount=amount,
                    category=category_match[-1].title() if category_match else 'Auto',
                    description='Auto Extracted',
                    date=date,
                    payment_mode=pay_match[-1].title() if pay_match else 'Unknown',
                    bill_file=file
                )

            messages.success(request, "✅ Auto expense processed successfully!")
            return redirect('dashboard')

        except Exception as e:
            print("File Upload Error:", e)
            messages.error(request, "❌ Error processing file.")
            return redirect('dashboard')

    return render(request, 'auto_expense_upload.html')'''

def get_monthly_expenses(user):
    expenses = (
        Expense.objects.filter(user=user)
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )
    months = [e['month'].strftime('%Y-%m') for e in expenses]
    totals = [e['total'] for e in expenses]
    return months, totals

def predict_next_month_expense(months, totals):
    if len(months) < 2:
        return None  # Not enough data

    X = np.arange(len(months)).reshape(-1, 1)
    y = np.array(totals)

    model = LinearRegression()
    model.fit(X, y)

    next_month_index = np.array([[len(months)]])
    prediction = model.predict(next_month_index)[0]
    return round(prediction, 2)


# ✅ Email-based Expense Report via webhook (optional endpoint)
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def expense_reply_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = CustomUser.objects.get(email=email)
            total = Expense.objects.filter(user=user).aggregate(total=pd.Sum('amount'))['total'] or 0
            send_mail("Your Expense Report", f"📊 Your total expense is ₹{total}", settings.EMAIL_HOST_USER, [email])
            return HttpResponse("✅ Report sent successfully.")
        except:
            return HttpResponse("❌ User not found.")
    return HttpResponseForbidden("Invalid request")



