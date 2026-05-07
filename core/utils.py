import random
from datetime import date, timedelta





def calculate_emi(P, annual_rate, tenure_years):

    R = annual_rate / (12 * 100)  # monthly interest
    N = tenure_years * 12         # convert years to months

    emi = (P * R * (1 + R)**N) / ((1 + R)**N - 1)

    total_payment = emi * N
    total_interest = total_payment - P

    balance = P
    schedule = []

    for month in range(1, N + 1):

        interest = balance * R
        principal = emi - interest
        balance -= principal

        schedule.append({
            "month": month,
            "principal": round(principal, 2),
            "interest": round(interest, 2),
            "balance": round(max(balance, 0), 2)
        })

    return round(emi, 2), round(total_interest, 2), round(total_payment, 2), schedule




def calculate_eligibility(income, age, credit_score, loan_amount):

    score = 0

    # Income factor (40%)
    if income >= 100000:
        score += 40
    elif income >= 50000:
        score += 30
    else:
        score += 15

    # Age factor (20%)
    if 21 <= age <= 45:
        score += 20
    elif 46 <= age <= 60:
        score += 15
    else:
        score += 5

    # Credit score (30%)
    if credit_score >= 750:
        score += 30
    elif credit_score >= 650:
        score += 20
    else:
        score += 10

    # Loan to income ratio (10%)
    if loan_amount <= income * 5:
        score += 10

    # Risk Category
    if score >= 80:
        risk = "Low Risk"
    elif score >= 60:
        risk = "Medium Risk"
    else:
        risk = "High Risk"

    return score, risk





def simulate_credit_score():
    return random.randint(550, 850)


def calculate_eligibility(income, age, credit_score, loan_amount):

    score = 0

    # Income (40 marks)
    if income >= 100000:
        score += 40
    elif income >= 60000:
        score += 30
    elif income >= 30000:
        score += 20
    else:
        score += 10

    # Age (20 marks)
    if 25 <= age <= 45:
        score += 20
    elif 46 <= age <= 60:
        score += 15
    else:
        score += 10

    # Credit Score (30 marks)
    if credit_score >= 750:
        score += 30
    elif credit_score >= 650:
        score += 20
    elif credit_score >= 550:
        score += 10
    else:
        score += 5

    # Loan Risk (10 marks)
    if loan_amount <= income * 5:
        score += 10
    else:
        score += 5

    if score >= 80:
        category = "Low Risk"
    elif score >= 60:
        category = "Medium Risk"
    else:
        category = "High Risk"

    return score, category










def apply_penalty(loan):

    if loan.status == "Approved" and loan.is_verified:

        if loan.due_date and date.today() > loan.due_date:

            overdue_days = (date.today() - loan.due_date).days

            penalty = overdue_days * 50  # ₹50 per day

            loan.penalty_amount += penalty
            loan.outstanding_balance += penalty

            loan.due_date = date.today() + timedelta(days=30)

            loan.save()




