import re
from .utils import calculate_emi, apply_penalty
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomerQuery, Loan, LoanType
from django.shortcuts import get_object_or_404
from accounts.models import UserProfile
import json
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from django.http import HttpResponse
import io
from .utils import simulate_credit_score, calculate_eligibility
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import pagesizes
from reportlab.lib.units import inch
from reportlab.platypus import TableStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from datetime import timedelta
from django.utils import timezone
import matplotlib.pyplot as plt
from groq import Groq









def home(request):
    return render(request, 'core/home.html')

@login_required(login_url='login')
def about(request):
    return render(request, 'core/about.html')

@login_required(login_url='login')
def contact(request):
    if request.method == "POST":
        CustomerQuery.objects.create(
            user=request.user,
            name=request.POST.get("name"),
            email=request.POST.get("email"),
            subject=request.POST.get("subject"),
            message=request.POST.get("message"),
        )

        messages.success(
            request,
            "Your query has been submitted successfully."
        )
        return redirect('home')

    context = {
        'name': request.user.username,
        'email': request.user.email
    }
    return render(request, 'core/contact.html', context)








def emi_calculator(request):

    context = {}

    if request.method == "POST":

        loan_amount = request.POST.get("loan_amount")
        interest_rate = request.POST.get("interest_rate")
        tenure = request.POST.get("tenure")

        # Prevent NoneType crash
        if loan_amount and interest_rate and tenure:

            loan_amount = float(loan_amount)
            interest_rate = float(interest_rate)
            tenure = int(tenure)

            emi, total_interest, total_payment, schedule = calculate_emi(
                loan_amount, interest_rate, tenure
            )

            context.update({
                "loan_amount": f"{loan_amount:,.2f}",
                "interest_rate": f"{interest_rate:.2f}",
                "tenure": tenure,
                "emi": f"{emi:,.2f}",
                "total_interest": f"{total_interest:,.2f}",
                "total_payment": f"{total_payment:,.2f}",
                "schedule": json.dumps(schedule)
            })



    return render(request, "core/emi.html", context)






@login_required(login_url='login')
def apply_loan(request):

    if request.method == "POST":

        loan_type_id = request.POST.get("loan_type")
        loan_amount = request.POST.get("loan_amount")
        tenure = request.POST.get("tenure")
        income = request.POST.get("income")
        age = request.POST.get("age")
        bank_name = request.POST.get("bank_name")
        account_number = request.POST.get("account_number")
        ifsc_code = request.POST.get("ifsc_code")
        document = request.FILES.get("document")

        # ---------- BASIC VALIDATION ----------
        if not all([loan_type_id, loan_amount, tenure, income, age,
                    bank_name, account_number, ifsc_code]):
            messages.error(request, "All fields are required.")
            return redirect("apply_loan")

        # ---------- REGEX VALIDATION ----------
        if not re.match(r"^[A-Za-z ]{3,50}$", bank_name):
            messages.error(request, "Invalid Account Holder Name.")
            return redirect("apply_loan")

        if not re.match(r"^[0-9]{9,18}$", account_number):
            messages.error(request, "Invalid Account Number.")
            return redirect("apply_loan")

        if not re.match(r"^[A-Z]{4}0[A-Z0-9]{6}$", ifsc_code):
            messages.error(request, "Invalid IFSC Code.")
            return redirect("apply_loan")

        # Convert safely
        loan_amount = float(loan_amount)
        tenure = int(tenure)
        income = float(income)
        age = int(age)

        credit_score = simulate_credit_score()

        eligibility_score, risk_category = calculate_eligibility(
            income, age, credit_score, loan_amount
        )

        loan_type = LoanType.objects.get(id=loan_type_id)

        Loan.objects.create(
    user=request.user,
    loan_type=loan_type,
    interest_rate=loan_type.interest_rate,   # 🔥 FIX
    loan_amount=loan_amount,
    tenure_years=tenure,
    income=income,
    age=age,
    bank_name=bank_name,
    account_number=account_number,
    ifsc_code=ifsc_code,
    credit_score=credit_score,
    eligibility_score=eligibility_score,
    risk_category=risk_category,
    outstanding_balance=loan_amount,
    document=document
)

        messages.success(request, "Loan Application Submitted Successfully!")
        return redirect('my_loans')

    loan_types = LoanType.objects.all()
    return render(request, 'core/apply_loan.html', {'loan_types': loan_types})











@login_required
def agent_dashboard(request):

    if request.user.userprofile.role != "AGENT":
        return redirect('home')

    loans = Loan.objects.all()

    for loan in loans:
        apply_penalty(loan)

    total_loans = Loan.objects.count()
    approved_loans = Loan.objects.filter(status="Approved").count()
    rejected_loans = Loan.objects.filter(status="Rejected").count()
    pending_loans = Loan.objects.filter(status="Pending").count()

    return render(request, 'core/agent_dashboard.html', {
        'loans': loans,
        'total_loans': total_loans,
        'approved_loans': approved_loans,
        'rejected_loans': rejected_loans,
        'pending_loans': pending_loans,
    })




@login_required
def update_loan_status(request, loan_id, action):

    if request.user.userprofile.role != "AGENT":
        return redirect('home')

    loan = get_object_or_404(Loan, id=loan_id)

    if action == "approve":
        loan.status = "Approved"
        loan.due_date = timezone.now().date() + timedelta(days=30)

    elif action == "reject":
        loan.status = "Rejected"

    loan.save()

    return redirect('agent_dashboard')






@login_required(login_url='login')
def my_loans(request):
    loans = Loan.objects.filter(user=request.user).order_by('-applied_at')
    return render(request, 'core/my_loans.html', {'loans': loans})













def download_emi_pdf(request):

    # Remove comma before converting
    loan_amount = request.GET.get("loan_amount").replace(",", "")
    interest_rate = request.GET.get("interest_rate")
    tenure = request.GET.get("tenure")

    loan_amount = float(loan_amount)
    interest_rate = float(interest_rate)
    tenure = int(tenure)

    emi, total_interest, total_payment, schedule = calculate_emi(
        loan_amount, interest_rate, tenure
    )

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=LoanEase_EMI_Report.pdf"

    doc = SimpleDocTemplate(response, pagesize=pagesizes.A4)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("LoanEase - EMI Report", styles['Title']))
    elements.append(Spacer(1, 20))

    data = [
        ["Loan Amount", f"₹ {loan_amount:,.2f}"],
        ["Interest Rate", f"{interest_rate}%"],
        ["Tenure", f"{tenure} Years"],
        ["Monthly EMI", f"₹ {emi:,.2f}"],
        ["Total Interest", f"₹ {total_interest:,.2f}"],
        ["Total Payment", f"₹ {total_payment:,.2f}"],
    ]

    table = Table(data, colWidths=[2.5 * inch, 2.5 * inch])
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 1, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 30))

    # ----------- ADD CHART TO PDF --------------

    principal = loan_amount
    interest = total_interest

    plt.figure(figsize=(4,4))
    plt.pie([principal, interest],
            labels=["Principal", "Interest"],
            autopct="%1.1f%%")
    plt.title("Loan Distribution")

    chart_buffer = io.BytesIO()
    plt.savefig(chart_buffer, format="png")
    plt.close()
    chart_buffer.seek(0)

    elements.append(Paragraph("EMI Distribution Chart", styles['Heading2']))
    elements.append(Spacer(1, 10))

    elements.append(Image(chart_buffer, width=4*inch, height=4*inch))

    doc.build(elements)

    return response



@login_required
def verify_loan(request, loan_id):

    if request.user.userprofile.role != "AGENT":
        return redirect("home")

    loan = get_object_or_404(Loan, id=loan_id)
    loan.is_verified = True
    loan.save()

    return redirect("agent_dashboard")



#CHatBot 
@login_required
def loan_chatbot(request):

    # Only CUSTOMER allowed
    if request.user.userprofile.role != "CUSTOMER":
        return redirect('home')

    ai_response = None

    if request.method == "POST":
        question = request.POST.get("question")

        client = Groq(
            api_key="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"
        )

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": """
You are LoanEase AI, a financial assistant specialized in loans.

Help users understand:
- EMI calculations
- Loan types
- Interest rates
- Loan eligibility
- Credit score basics
- Personal finance

Explain things in simple language.
Keep answers short and practical.
"""
                },
                {
                    "role": "user",
                    "content": question
                }
            ]
        )

        ai_response = completion.choices[0].message.content

    return render(request, "core/chatbot.html", {
        "response": ai_response
    })


